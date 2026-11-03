import sys

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
needles = [
    b"b\x00r\x00k\x00",
    b"P\x00I\x00E\x00C",
    b"F\x00R\x00A\x00G",
    b"p\x00i\x00e\x00c\x00e",
    b"C\x00T\x00R\x00L",
    b"E\x00N\x00D\x00",
]
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
                ctx = data[max(0, i-24):i+120]
                hits.append((abs_pos, needle, ctx))
                start = i + 1
        prev_tail = data[-overlap:]
        pos += len(chunk)

with open(r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\hits7.txt", "w", encoding="utf-8", errors="replace") as out:
    for abs_pos, needle, ctx in hits:
        out.write(f"@{abs_pos} [{needle}]: {ctx!r}\n")
print(f"total {len(hits)}")
