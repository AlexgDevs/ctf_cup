import sys

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
needles = [b"DATA", b"PIEC", b"CHNK", b"FRAG", b"HELO", b"INFO", b"HEAD", b"PART", b"ctfcup"]
hits = []
counts = {}
with open(path, "rb") as f:
    pos = 0
    chunk_size = 64 * 1024 * 1024
    overlap = 8
    prev_tail = b""
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        data = prev_tail + chunk
        for needle in needles:
            c = data.count(needle)
            if c:
                counts[needle] = counts.get(needle, 0) + c
                if needle == b"ctfcup":
                    start = 0
                    while True:
                        i = data.find(needle, start)
                        if i == -1:
                            break
                        abs_pos = pos - len(prev_tail) + i
                        ctx = data[max(0, i-32):i+96]
                        hits.append((abs_pos, ctx))
                        start = i + 1
        prev_tail = data[-overlap:]
        pos += len(chunk)

print(counts)
for abs_pos, ctx in hits[:40]:
    print(f"@{abs_pos}: {ctx!r}")
