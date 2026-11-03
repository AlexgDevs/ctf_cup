path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
regions = [
    (357710800, 16384, "run.ps1_357711187"),
    (422256000, 16384, "orchestrate_422256689"),
    (552046000, 16384, "orchestrate_552046707"),
    (514293000, 8192, "orchestrate_514293993"),
    (357765000, 8192, "orchestrate_357765834"),
]
import os
outdir = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\scripts"
os.makedirs(outdir, exist_ok=True)
with open(path, "rb") as f:
    for off, size, name in regions:
        f.seek(off)
        data = f.read(size)
        # extract printable runs (ascii)
        out = []
        cur = []
        for b in data:
            if 32 <= b < 127 or b in (10, 13, 9):
                cur.append(chr(b))
            else:
                if len(cur) > 8:
                    out.append("".join(cur))
                cur = []
        if len(cur) > 8:
            out.append("".join(cur))
        with open(os.path.join(outdir, name + ".txt"), "w", encoding="utf-8", errors="replace") as w:
            w.write("\n\n---\n\n".join(out))
print("done")
