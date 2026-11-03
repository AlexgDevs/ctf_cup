import sys

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
needles = [b"u\x00s\x00a\x00g\x00e\x00:\x00", b"c\x00l\x00%\x00d", b"e\x00x\x00p\x00e\x00c\x00t\x00e\x00d\x00_\x00d\x00a\x00t\x00a", b"c\x00h\x00u\x00n\x00k\x00 \x00i\x00d\x00x", b"c\x00h\x00u\x00n\x00k\x00 \x00%\x00d"]
hits = []
with open(path, "rb") as f:
    pos = 0
    chunk_size = 64 * 1024 * 1024
    overlap = 128
    prev_tail = b""
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        data = prev_tail + chunk
        for needle in needles:
            start = 0
            while True:
                i = data.find(needle, start)
                if i == -1:
                    break
                abs_pos = pos - len(prev_tail) + i
                ctx = data[max(0, i-48):i+200]
                hits.append((abs_pos, needle, ctx))
                start = i + 1
        prev_tail = data[-overlap:]
        pos += len(chunk)

with open(r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\hits6.txt", "w", encoding="utf-8", errors="replace") as out:
    for abs_pos, needle, ctx in hits:
        out.write(f"@{abs_pos} [{needle}]: {ctx!r}\n")
print(f"total {len(hits)}")
