import struct, re, os

IMG = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\my-own-fs\my-own-fs\disk.img"
ISZ, HEAD, CONT = 1337, 51, 5
OUT = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\my-own-fs\recovered"
os.makedirs(OUT, exist_ok=True)

data = open(IMG, "rb").read()
N = len(data) // (ISZ + 1)
bitmap = data[:N]

def u32(b, o): return struct.unpack_from("<I", b, o)[0]
def u64(b, o): return struct.unpack_from("<Q", b, o)[0]
def get_inode(i):
    off = N + i * ISZ
    return data[off:off+ISZ]

print("used inodes:", [i for i in range(N) if bitmap[i]==1])

# root
b0 = get_inode(0)
print("root type:", b0[4], "size:", u64(b0,15), "next:", u32(b0,0))

def read_full_chain(i):
    """Read ALL data bytes (not truncated to size) following next pointers."""
    out = bytearray()
    cur = i
    hdr = HEAD
    visited = set()
    while cur != 0 and cur < N and cur not in visited:
        visited.add(cur)
        b = get_inode(cur)
        out += b[hdr:]
        cur = u32(b, 0)
        hdr = CONT
    return bytes(out), list(visited)

hits = []
# follow chains from every inode that looks like a head, and also every inode as chain start
for i in range(N):
    b = get_inode(i)
    if b[4] not in (1, 2):
        continue
    content, chain = read_full_chain(i)
    if b"ctfcup" in content or b"CTFCUP" in content:
        hits.append((i, chain, content))
        print(f"HIT head inode {i} chain {chain}")
        idx = content.find(b"ctfcup")
        if idx == -1: idx = content.upper().find(b"CTFCUP")
        print("  context:", content[max(0,idx-50):idx+150])

print("total hits:", len(hits))

# save all recovered chain contents for inspection
for i in range(N):
    b = get_inode(i)
    if b[4] in (1, 2):
        content, chain = read_full_chain(i)
        if b"ctf" in content.lower() or b"{" in content:
            # save files that contain braces or ctf
            if b"ctf" in content.lower():
                with open(os.path.join(OUT, f"file_{i}.bin"), "wb") as f:
                    f.write(content)
                print("saved", i, "len", len(content))

# search for flag-like patterns in ALL chain contents
print("\n=== brace patterns in chain contents ===")
for i in range(N):
    b = get_inode(i)
    if b[4] not in (1, 2):
        continue
    content, chain = read_full_chain(i)
    for m in re.finditer(rb"[A-Za-z0-9_\-]{2,30}\{[^}]{3,120}\}", content):
        print(f"inode {i}: {m.group()}")

# also: dump slack of EVERY inode (bytes beyond used portion) - search for fragments
# for a continuation inode the whole data area may hold old content
print("\n=== scanning each inode's full data area for brace-flag patterns ===")
for i in range(N):
    b = get_inode(i)
    # consider all bytes after potential header (both head and cont interpretations)
    for off in (HEAD, CONT):
        region = b[off:]
        for m in re.finditer(rb"[A-Za-z]{3,10}\{[^}]{4,150}\}", region):
            s = m.group()
            if b"ctf" in s.lower() or s.count(b" ") < 8:
                print(f"inode {i} off {off}: {s[:160]}")
