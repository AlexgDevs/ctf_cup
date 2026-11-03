import mmap, re
pats = [("u16 cup", "cup"), ("u16 ctf", "ctf"), ("u16 flag", "flag"), ("u16 CTF", "CTF"), ("u16 Flag", "Flag")]
with open("puzzle.vmem", "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    for name, s in pats:
        p = s.encode("utf-16-le")
        offs = []; i = m.find(p)
        while i != -1 and len(offs) < 500:
            offs.append(i); i = m.find(p, i + 1)
        print(name, "count", len(offs))
        for o in offs[:6]:
            ctx = m[max(0,o-40):o+60]
            try: t = ctx.decode("utf-16-le", errors="replace")
            except: t = repr(ctx)
            print("   ", hex(o), repr(t))
    # ascii cup
    p = b"cup"; offs=[]; i=m.find(p)
    while i!=-1 and len(offs)<2000:
        offs.append(i); i=m.find(p,i+1)
    print("ascii cup count", len(offs))
    hits = [o for o in offs if m[o-1:o] and (m[o-1:o].isalpha()==False)]
    for o in hits[:20]:
        print("   ", hex(o), m[max(0,o-30):o+40])
