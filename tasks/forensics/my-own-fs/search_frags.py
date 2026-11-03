import struct, re

IMG = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\my-own-fs\my-own-fs\disk.img"
ISZ = 1337

data = open(IMG, "rb").read()
N = len(data) // (ISZ + 1)

def get_inode(i):
    off = N + i * ISZ
    return data[off:off+ISZ]

# search for fragments of "ctfcup"
frags = [b"ctf", b"cfc", b"cup", b"ctfc", b"fcup", b"ctfcu", b"fcupe"]
print("=== fragment search ===")
for i in range(N):
    b = get_inode(i)
    for f in frags:
        pos = b.find(f)
        while pos != -1:
            # show surrounding printable context
            ctx = b[max(0,pos-20):pos+40]
            print(f"inode {i} frag {f} at {pos}: {ctx}")
            pos = b.find(f, pos+1)

# search all strings containing '{' or '}' in inode data
print("\n=== brace strings in inodes ===")
for i in range(N):
    b = get_inode(i)
    for m in re.finditer(rb"[\x20-\x7e]{4,}", b):
        s = m.group()
        if b"{" in s or b"}" in s or b"ctf" in s.lower():
            print(f"inode {i}: {s[:150]}")
