import struct, os, re
path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
outdir = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\pes"
pe_offsets = [104615936, 105603072, 105656320, 106473896, 107110400, 107307008, 107491328, 107945984]
with open(path, "rb") as f:
    for off in pe_offsets:
        f.seek(off)
        hdr = f.read(0x1000)
        e = struct.unpack_from("<I", hdr, 0x3C)[0]
        nsec = struct.unpack_from("<H", hdr, e+6)[0]
        optsz = struct.unpack_from("<H", hdr, e+20)[0]
        opt = e + 24
        size_image = struct.unpack_from("<I", hdr, opt+56)[0]
        sec_off = opt + optsz
        max_end = 0x1000
        for s in range(nsec):
            sh = hdr[sec_off+s*40:sec_off+(s+1)*40]
            rsize, raddr = struct.unpack_from("<II", sh, 16)
            max_end = max(max_end, raddr + rsize)
        size = min(max_end, 4*1024*1024)
        f.seek(off)
        blob = f.read(size)
        ws = re.findall(rb"(?:[\x20-\x7e]\x00){5,}", blob)
        dec = [w.decode("utf-16-le") for w in ws]
        interesting = [s for s in dec if any(k in s.lower() for k in ["broker", "brk", "flag.png", "chunk", "mailslot", "usage", "alpc", "remnant", "wirelog", "rounds"])]
        print(f"PE@{off}: size_image={size_image} blob={len(blob)} wstr={len(dec)} interesting={len(interesting)}")
        for s in interesting[:20]:
            print("   ", s[:130])
        fn = os.path.join(outdir, f"pe2_{off}.bin")
        with open(fn, "wb") as w:
            w.write(blob)
