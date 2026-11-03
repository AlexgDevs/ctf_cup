import os
path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
outdir = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\scripts"
regions = [
    (292200000, 262144, "broker_exe_region_292M"),
]
with open(path, "rb") as f:
    for off, size, name in regions:
        f.seek(off)
        data = f.read(size)
        # ascii runs
        out = []
        cur = []
        for b in data:
            if 32 <= b < 127 or b in (10, 13, 9):
                cur.append(chr(b))
            else:
                if len(cur) > 5:
                    out.append("A:" + "".join(cur))
                cur = []
        if len(cur) > 5:
            out.append("A:" + "".join(cur))
        # utf16le runs
        cur = []
        i = 0
        while i + 1 < len(data):
            c = data[i] | (data[i+1] << 8)
            if (32 <= c < 127) or c in (10, 13, 9):
                cur.append(chr(c))
                i += 2
            else:
                if len(cur) > 4:
                    out.append("W:" + "".join(cur))
                cur = []
                i += 1
        if len(cur) > 4:
            out.append("W:" + "".join(cur))
        with open(os.path.join(outdir, name + ".txt"), "w", encoding="utf-8", errors="replace") as w:
            w.write("\n".join(out))
print("done")
