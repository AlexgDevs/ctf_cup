import struct, re

IMG = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\my-own-fs\my-own-fs\disk.img"
ISZ, HEAD, CONT = 1337, 51, 5
T_CONT, T_FILE, T_DIR = 0, 1, 2

data = open(IMG, "rb").read()
N = len(data) // (ISZ + 1)

def u32(b, o): return struct.unpack_from("<I", b, o)[0]
def u64(b, o): return struct.unpack_from("<Q", b, o)[0]
def get_inode(i):
    off = N + i * ISZ
    return data[off:off+ISZ]

# search entire raw image for flag
for m in re.finditer(rb"ctfcup\{", data):
    print("RAW at", m.start(), "context:", data[m.start():m.start()+200])

# also search all inode data regions individually
for i in range(N):
    b = get_inode(i)
    if b"ctfcup" in b:
        print("inode", i, "contains ctfcup")
        idx = b.find(b"ctfcup")
        print("  ", b[idx:idx+200])

# search for flag-like strings (printable with braces)
print("\n=== flag-like strings ===")
for m in re.finditer(rb"[ -~]{0,20}\{[ -~]{5,120}\}", data):
    s = m.group()
    if b"ctf" in s.lower() or b"flag" in s.lower():
        print(m.start(), s)
