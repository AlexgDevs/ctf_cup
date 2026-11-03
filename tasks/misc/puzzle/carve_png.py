import mmap, struct, zlib, os
SIG = b"\x89PNG\r\n\x1a\n"
out_dir = "carved"
valid = []
with open("puzzle.vmem", "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    size = len(m)
    i = m.find(SIG)
    while i != -1:
        p = i + 8
        ok = False; end = None; chunks = []
        while p + 8 <= size and p - i < 20_000_000:
            ln = struct.unpack(">I", m[p:p+4])[0]
            typ = m[p+4:p+8]
            if ln > 0x7fffffff or not typ.isalpha():
                break
            data = m[p+8:p+8+ln]
            crc = struct.unpack(">I", m[p+8+ln:p+12+ln])[0] if p+12+ln <= size else None
            if crc is None or (zlib.crc32(typ + data) & 0xffffffff) != crc:
                break
            chunks.append(typ)
            p = p + 12 + ln
            if typ == b"IEND":
                ok = True; end = p; break
        if ok and chunks[0] == b"IHDR":
            valid.append((i, end - i, chunks))
        i = m.find(SIG, i + 1)
    print("valid complete PNGs:", len(valid))
    for n, (off, ln, chunks) in enumerate(valid):
        with open(os.path.join(out_dir, f"png_{n:03d}_{off:x}.png"), "wb") as g:
            g.write(m[off:off+ln])
        print(n, hex(off), ln, b",".join(sorted(set(chunks))).decode(errors="replace")[:80])
