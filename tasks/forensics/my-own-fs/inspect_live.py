import struct, re

IMG = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\my-own-fs\my-own-fs\disk.img"
ISZ, HEAD, CONT = 1337, 51, 5

data = open(IMG, "rb").read()
N = len(data) // (ISZ + 1)
bitmap = data[:N]

def u32(b, o): return struct.unpack_from("<I", b, o)[0]
def u64(b, o): return struct.unpack_from("<Q", b, o)[0]
def get_inode(i):
    off = N + i * ISZ
    return data[off:off+ISZ]

def read_chain(i, size=None):
    out = bytearray()
    cur = i
    hdr = HEAD
    visited = set()
    while cur != 0 and cur < N and cur not in visited:
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
print("ROOT: used=", bitmap[0], "type=", b0[4], "size=", u64(b0,15))
d = read_chain(0, u64(b0,15))
print("root raw data:", d)
print("root entries:")
for name, ino in parse_dir(d):
    nb = get_inode(ino)
    print(f"  {name} -> ino {ino} (used={bitmap[ino]}, type={nb[4]}, size={u64(nb,15)})")

# used inodes 1611, 1834
for i in [1611, 1834]:
    b = get_inode(i)
    print(f"\ninode {i}: type={b[4]} next={u32(b,0)} size={u64(b,15)} mode={struct.unpack_from('<H',b,5)[0]}")
    sz = u64(b, 15)
    content = read_chain(i, sz)
    print("content head:", content[:300])
    if b[4] == 2:
        print("dir entries:", parse_dir(content))

# find all file signatures in recovered content
sigs = {
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"\xff\xd8\xff": "JPEG",
    b"PK\x03\x04": "ZIP",
    b"GIF8": "GIF",
    b"%PDF": "PDF",
    b"BM": "BMP",
    b"Rar!": "RAR",
    b"\x1f\x8b": "GZIP",
}
print("\n=== signatures in chain contents ===")
for i in range(N):
    b = get_inode(i)
    if b[4] not in (1,2):
        continue
    content = read_chain(i)
    for sig, name in sigs.items():
        if content.startswith(sig):
            print(f"inode {i}: {name}, chain len {len(content)}")
