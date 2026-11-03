import struct, sys, os

IMG = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\my-own-fs\my-own-fs\disk.img"
ISZ = 1337
HEAD = 51
CONT = 5
T_CONT, T_FILE, T_DIR = 0, 1, 2

data = open(IMG, "rb").read()
size = len(data)
N = size // (ISZ + 1)
print("N inodes:", N)

bitmap = data[:N]

def inode_off(i):
    return N + i * ISZ

def get_inode(i):
    off = inode_off(i)
    return data[off:off+ISZ]

def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]

def u64(b, o):
    return struct.unpack_from("<Q", b, o)[0]

def i64(b, o):
    return struct.unpack_from("<q", b, o)[0]

# list bitmap status
used = [i for i in range(N) if bitmap[i] == 1]
free = [i for i in range(N) if bitmap[i] == 0]
print("used:", len(used), "free:", len(free))

# analyze all inodes: type byte
from collections import Counter
types = Counter()
heads = []
for i in range(N):
    b = get_inode(i)
    t = b[4]
    types[t] += 1
    if t in (T_FILE, T_DIR):
        nxt = u32(b, 0)
        mode = struct.unpack_from("<H", b, 5)[0]
        uid = u32(b, 7); gid = u32(b, 11)
        sz = u64(b, 15)
        atime = i64(b, 23); mtime = i64(b, 31); ctime = i64(b, 39)
        nlink = u32(b, 47)
        heads.append(dict(i=i, used=bitmap[i]==1, type=t, next=nxt, mode=mode,
                          uid=uid, gid=gid, size=sz, atime=atime, mtime=mtime,
                          ctime=ctime, nlink=nlink))
print("type counts:", dict(types))
print("heads:", len(heads))

# chain reader
def read_chain(i, size):
    out = bytearray()
    cur = i
    hdr = HEAD
    visited = set()
    while len(out) < size:
        if cur == 0 or cur >= N or cur in visited:
            break
        visited.add(cur)
        b = get_inode(cur)
        take = min(ISZ - hdr, size - len(out))
        out += b[hdr:hdr+take]
        cur = u32(b, 0)
        hdr = CONT
    return bytes(out)

# parse dir entries
def parse_dir(d):
    ents = []
    p = 0
    while p + 5 <= len(d):
        ino = u32(d, p)
        ln = d[p+4]
        if p + 5 + ln > len(d):
            break
        name = d[p+5:p+5+ln]
        ents.append((name, ino))
        p += 5 + ln
    return ents

# walk from root (inode 0)
def walk(i, path, seen):
    if i in seen or i >= N:
        return
    seen.add(i)
    b = get_inode(i)
    if b[4] != T_DIR:
        return
    sz = u64(b, 15)
    d = read_chain(i, sz)
    for name, ino in parse_dir(d):
        try:
            nm = name.decode("utf-8", "replace")
        except Exception:
            nm = repr(name)
        nb = get_inode(ino)
        if nb[4] == T_DIR:
            print(f"DIR  {path}/{nm} -> inode {ino}")
            walk(ino, f"{path}/{nm}", seen)
        elif nb[4] == T_FILE:
            fsz = u64(nb, 15)
            content = read_chain(ino, fsz)
            print(f"FILE {path}/{nm} -> inode {ino} size {fsz}")
            print("  content:", content[:500])
        else:
            print(f"??   {path}/{nm} -> inode {ino} type {nb[4]}")

seen = set()
print("\n=== LIVE TREE ===")
walk(0, "", seen)

print("\n=== FREE HEADS (deleted) ===")
for h in heads:
    if not h["used"]:
        print(h)
        if h["type"] == T_FILE:
            content = read_chain(h["i"], h["size"])
            print("  content:", content[:800])
        elif h["type"] == T_DIR:
            d = read_chain(h["i"], h["size"])
            print("  entries:", parse_dir(d))
