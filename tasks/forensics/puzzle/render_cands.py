import zlib, struct, sys

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
positions = [1839194384, 1033167088, 680656896, 1344164432, 825431696, 1754144960, 1988755456, 1509029162, 2045767240, 1942970800, 1991775712]

def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc: return a
    if pb <= pc: return b
    return c

def render(prefix, w, h, bpp, outfn):
    raw = zlib.decompressobj().decompress(prefix)
    rowbytes = 1 + w * bpp
    rows = len(raw) // rowbytes
    if rows == 0:
        print("no rows"); return
    out_rows = []
    prev = bytearray(w * bpp)
    pos = 0
    ok = True
    for r in range(rows):
        ft = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos + w * bpp]); pos += w * bpp
        if ft == 0:
            pass
        elif ft == 1:
            for i in range(bpp, len(line)):
                line[i] = (line[i] + line[i - bpp]) & 0xff
        elif ft == 2:
            for i in range(len(line)):
                line[i] = (line[i] + prev[i]) & 0xff
        elif ft == 3:
            for i in range(len(line)):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) // 2)) & 0xff
        elif ft == 4:
            for i in range(len(line)):
                a = line[i - bpp] if i >= bpp else 0
                c = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + paeth(a, prev[i], c)) & 0xff
        else:
            ok = False
            break
        out_rows.append(bytes(line))
        prev = line
    if not out_rows:
        print("bad"); return
    # convert to RGB png
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    rr = []
    for line in out_rows:
        if bpp == 4:
            rgb = bytearray()
            for x in range(w):
                rgb += line[x*4:x*4+3]
            rr.append(bytes(rgb))
        elif bpp == 3:
            rr.append(line)
        elif bpp == 1:
            rr.append(b"".join(bytes([line[x]])*3 for x in range(w)))
        elif bpp == 2:
            rr.append(b"".join(bytes([line[x*2]])*3 for x in range(w)))
    ct = 2
    raw2 = b"".join(b"\x00" + r for r in rr)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, len(rr), 8, ct, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw2)) + chunk(b"IEND", b"")
    open(outfn, "wb").write(png)
    print(f"{outfn}: {w}x{len(rr)} from declared {w}x{h}")

with open(path, "rb") as f:
    for p in positions:
        f.seek(p + 8)
        hdr = f.read(25)
        w, h = struct.unpack(">II", hdr[4:12])
        bd, ct = hdr[12], hdr[13]
        bppmap = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
        bpp = bppmap.get(ct) * (bd // 8)
        # IDAT starts at p+33
        f.seek(p + 33 + 8)  # skip len+type
        prefix = f.read(200000)
        outfn = rf"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\cand_{p}_{w}x{h}.png"
        try:
            render(prefix, w, h, bpp, outfn)
        except Exception as e:
            print(p, "err", e)
