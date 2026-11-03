import mmap, struct
pat = "flag.png".encode("utf-16-le")
with open("puzzle.vmem", "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    offs = []; i = m.find(pat)
    while i != -1:
        offs.append(i); i = m.find(pat, i + 1)
    print("flag.png utf16 hits:", len(offs))
    for o in offs:
        # find FILE0 record start within 1024 bytes before
        base = m.rfind(b"FILE0", max(0, o - 1024), o)
        if base == -1:
            print(hex(o), "no FILE0 header nearby"); continue
        rec = m[base:base+1024]
        flags = struct.unpack("<H", rec[22:24])[0]
        recno = struct.unpack("<I", rec[44:48])[0]
        print(f"{hex(o)} FILE0@{hex(base)} recno={recno} flags={flags:#x} (1=inuse,2=dir)")
        # print attribute types in record
        off = struct.unpack("<H", rec[20:22])[0]
        attrs = []
        while off + 8 <= 1024:
            t, ln = struct.unpack("<II", rec[off:off+8])
            if t == 0xFFFFFFFF or ln == 0: break
            attrs.append((hex(t), ln, rec[off+8]))  # non-resident flag
            off += ln
        print("   attrs (type, len, nonres):", attrs)
        if any(a[0] == "0x80" for a in attrs):
            print("   has $DATA; first 64 bytes of record data area:", rec[off-8:off+56] if False else "")
        print("   PNG sig in record:", rec.find(b"\x89PNG") != -1, " IEND:", rec.find(b"IEND") != -1)
