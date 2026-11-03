import struct, sys

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
hits = []
with open(path, "rb") as f:
    pos = 0
    chunk_size = 64 * 1024 * 1024
    overlap = 32
    prev_tail = b""
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        data = prev_tail + chunk
        start = 0
        while True:
            i = data.find(b"IHDR", start)
            if i == -1:
                break
            abs_pos = pos - len(prev_tail) + i
            ctx = data[i-8:i+20]
            # IHDR data starts at i+4: width height bitdepth colortype comp filter interlace
            if i + 17 <= len(data):
                w, h = struct.unpack(">II", data[i+4:i+12])
                bd, ct = data[i+12], data[i+13]
                if 16 <= w <= 4096 and 16 <= h <= 4096 and bd in (1,2,4,8,16) and ct in (0,2,3,4,6):
                    hits.append((abs_pos, w, h, bd, ct, ctx))
            start = i + 1
        prev_tail = data[-overlap:]
        pos += len(chunk)

print(f"plausible IHDR: {len(hits)}")
seen = {}
for abs_pos, w, h, bd, ct, ctx in hits:
    key = (w, h, bd, ct)
    seen.setdefault(key, []).append(abs_pos)
for k, v in sorted(seen.items(), key=lambda x: -len(x[1])):
    print(k, len(v), v[:6])
