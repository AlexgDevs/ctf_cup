import struct, os

IMG = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\my-own-fs\my-own-fs\disk.img"
OUT = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\my-own-fs\recovered"
os.makedirs(OUT, exist_ok=True)
ISZ, HEAD, CONT = 1337, 51, 5

data = open(IMG, "rb").read()
N = len(data) // (ISZ + 1)

def u32(b, o): return struct.unpack_from("<I", b, o)[0]
def u64(b, o): return struct.unpack_from("<Q", b, o)[0]
def get_inode(i):
    off = N + i * ISZ
    return data[off:off+ISZ]

def read_chain(start, size=None):
    out = bytearray()
    cur = start
    hdr = HEAD
    visited = set()
    first = True
    while (first or cur != 0) and cur < N and cur not in visited:
        first = False
        visited.add(cur)
        b = get_inode(cur)
        chunk = b[hdr:]
        if size is not None:
            chunk = chunk[:max(0, size - len(out))]
        out += chunk
        cur = u32(b, 0)
        hdr = CONT
        if size is not None and len(out) >= size:
            break
    return bytes(out)

def parse_dir(d):
    ents = []
    p = 0
    while p + 5 <= len(d):
        ino = u32(d, p)
        ln = d[p+4]
        if p + 5 + ln > len(d): break
        ents.append((d[p+5:p+5+ln], ino))
        p += 5 + ln
    return ents

# root
b0 = get_inode(0)
sz0 = u64(b0, 15)
d = read_chain(0, sz0)
print("root size:", sz0, "data:", d)
for name, ino in parse_dir(d):
    nb = get_inode(ino)
    print(f"  {name} -> ino {ino} type={nb[4]} size={u64(nb,15)}")
    if nb[4] == 1:
        c = read_chain(ino, u64(nb,15))
        print("    content:", c)

# extract PNG
png = read_chain(2979)
# find PNG end: IEND chunk
end = png.find(b"IEND")
if end != -1:
    png = png[:end+8]
with open(os.path.join(OUT, "recovered_2979.png"), "wb") as f:
    f.write(png)
print("\nPNG saved, size:", len(png))
print("header:", png[:16])
