import sys, re

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
needle = b"ctfcup"
found = []
with open(path, "rb") as f:
    pos = 0
    chunk_size = 64 * 1024 * 1024
    overlap = 256
    prev_tail = b""
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        data = prev_tail + chunk
        start = 0
        while True:
            i = data.find(needle, start)
            if i == -1:
                break
            abs_pos = pos - len(prev_tail) + i
            ctx = data[max(0, i-64):i+200]
            found.append((abs_pos, ctx))
            start = i + 1
        prev_tail = data[-overlap:]
        pos += len(chunk)
        print(f"scanned {pos/1024/1024:.0f} MB, found {len(found)}", file=sys.stderr)

with open(r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\hits.txt", "w", encoding="utf-8", errors="replace") as out:
    for abs_pos, ctx in found:
        out.write(f"@{abs_pos}: {ctx!r}\n")

print(f"total {len(found)} hits")
