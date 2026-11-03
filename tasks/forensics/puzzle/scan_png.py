import sys

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
needles = {
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"IHDR": "IHDR",
    b"IEND": "IEND",
    b"IDAT": "IDAT",
    b"\xff\xd8\xff": "JPEG",
    b"BM": None,
    b"brk.ctrl": "brk.ctrl",
    b"\\RPC Control\\": "RPC Control",
}
counts = {}
png_pos = []
with open(path, "rb") as f:
    pos = 0
    chunk_size = 64 * 1024 * 1024
    overlap = 64
    prev_tail = b""
    total = 2147483648
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        data = prev_tail + chunk
        for needle, name in needles.items():
            if name is None:
                continue
            start = 0
            c = 0
            while True:
                i = data.find(needle, start)
                if i == -1:
                    break
                abs_pos = pos - len(prev_tail) + i
                if name == "PNG":
                    png_pos.append(abs_pos)
                counts[name] = counts.get(name, 0) + 1
                start = i + 1
        prev_tail = data[-overlap:]
        pos += len(chunk)
        print(f"{pos*100//total}%", counts, file=sys.stderr)

print(counts)
print("PNG positions:", png_pos[:50])
