import struct, os, zlib

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
outdir = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\carved"
os.makedirs(outdir, exist_ok=True)

SIG = b"\x89PNG\r\n\x1a\n"

def parse_png(data, start):
    # returns (end_offset, chunks) or None
    pos = start + 8
    chunks = []
    if data[start:start+8] != SIG:
        return None
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos+4])[0]
        if length > 100_000_000:
            return None
        ctype = data[pos+4:pos+8]
        if pos + 12 + length > len(data):
            return None
        cdata = data[pos+8:pos+8+length]
        crc_stored = struct.unpack(">I", data[pos+8+length:pos+12+length])[0]
        crc_calc = zlib.crc32(ctype + cdata) & 0xffffffff
        chunks.append((ctype, length, crc_stored == crc_calc))
        pos += 12 + length
        if ctype == b"IEND":
            return pos, chunks
    return None

found = []
with open(path, "rb") as f:
    # stream through, keep a window
    window = b""
    base = 0
    chunk_size = 64 * 1024 * 1024
    pos = 0
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        window += chunk
        # process all signatures in window that are complete enough
        start = 0
        while True:
            i = window.find(SIG, start)
            if i == -1:
                break
            abs_pos = base + i
            res = parse_png(window, i)
            if res:
                end, chunks = res
                png = window[i:end]
                ok = all(c[2] for c in chunks)
                types = [c[0].decode('ascii', 'replace') for c in chunks]
                ihdr = None
                for t, l, cok in chunks:
                    pass
                # parse IHDR
                if chunks and chunks[0][0] == b'IHDR':
                    w, h, bd, ct = struct.unpack(">IIBB", window[i+16:i+26])
                    ihdr = (w, h, bd, ct)
                found.append((abs_pos, len(png), ok, ihdr, types[:8], png))
            start = i + 1
        # keep last 100MB for cross-boundary
        keep = 100 * 1024 * 1024
        if len(window) > keep + chunk_size:
            drop = len(window) - keep
            window = window[drop:]
            base += drop
        pos += len(chunk)
        print(f"scanned {pos/1024/1024:.0f} MB, pngs: {len(found)}", flush=True)

# save valid PNGs
saved = 0
report = []
for idx, (abs_pos, size, ok, ihdr, types, png) in enumerate(found):
    report.append(f"@{abs_pos} size={size} crc_ok={ok} ihdr={ihdr} chunks={types}")
    if ok and ihdr and 3 <= ihdr[0] <= 4000 and 3 <= ihdr[1] <= 4000:
        fn = os.path.join(outdir, f"png_{idx}_{abs_pos}_{ihdr[0]}x{ihdr[1]}.png")
        with open(fn, "wb") as w:
            w.write(png)
        saved += 1

with open(os.path.join(outdir, "report.txt"), "w") as w:
    w.write("\n".join(report))
print(f"total {len(found)}, saved {saved}")
