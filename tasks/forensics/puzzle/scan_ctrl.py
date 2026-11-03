import struct

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
magics = [b"CTRL", b"END\x00", b"DATA", b"CHNK", b"PIEC"]
hits = []
with open(path, "rb") as f:
    pos = 0
    chunk_size = 64 * 1024 * 1024
    overlap = 64
    prev_tail = b""
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        data = prev_tail + chunk
        for magic in magics:
            start = 0
            while True:
                i = data.find(magic, start)
                if i == -1:
                    break
                abs_pos = pos - len(prev_tail) + i
                tail = data[i:i+40]
                # heuristic: plausible header -> small ints after magic
                if len(tail) >= 24:
                    a, b, c, d, e = struct.unpack_from("<IIIII", tail, 4)
                    if (a <= 16 and b < 100000 and c < 30000000 and d <= 16 and e < 100000):
                        hits.append((abs_pos, magic, tail))
                start = i + 1
        prev_tail = data[-overlap:]
        pos += len(chunk)

print("candidates:", len(hits))
for abs_pos, magic, tail in hits[:80]:
    print(f"@{abs_pos} [{magic}]: {tail.hex(' ')}")
