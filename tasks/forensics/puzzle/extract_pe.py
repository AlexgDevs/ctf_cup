import struct, os
path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
outdir = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\pes"
os.makedirs(outdir, exist_ok=True)
pe_offsets = [309592064, 569937920, 571334656, 572190720, 574099456]
with open(path, "rb") as f:
    for off in pe_offsets:
        f.seek(off)
        hdr = f.read(0x1000)
        e_lfanew = struct.unpack_from("<I", hdr, 0x3C)[0]
        coff = e_lfanew + 4
        nsec = struct.unpack_from("<H", hdr, coff+2)[0]
        optsz = struct.unpack_from("<H", hdr, coff+16)[0]
        opt = coff + 20
        magic = struct.unpack_from("<H", hdr, opt)[0]
        size_image = struct.unpack_from("<I", hdr, opt+56)[0]
        size_hdr = struct.unpack_from("<I", hdr, opt+60)[0]
        # sections
        sec_off = opt + optsz
        max_end = size_hdr
        secs = []
        for s in range(nsec):
            sh = hdr[sec_off+s*40:sec_off+(s+1)*40]
            name = sh[:8].rstrip(b"\x00").decode("ascii", "replace")
            vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", sh, 8)
            secs.append((name, vsize, vaddr, rsize, raddr))
            max_end = max(max_end, raddr + rsize)
        print(f"PE@{off}: nsec={nsec} size_image={size_image} filesize~{max_end}")
        for s in secs:
            print("   ", s)
        # extract full file (up to max_end, capped 4MB)
        f.seek(off)
        blob = f.read(min(max_end, 4*1024*1024))
        # identify by strings
        ident = "unknown"
        for probe, nm in [(b"broker:", "broker"), (b"brk.data", "cl"), (b"purge", "purge"), (b"flag.png", "flaguser")]:
            if probe in blob:
                ident = nm
                break
        fn = os.path.join(outdir, f"pe_{off}_{ident}.bin")
        with open(fn, "wb") as w:
            w.write(blob)
        print("   saved", fn, "len", len(blob))
