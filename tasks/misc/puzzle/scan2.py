import re, mmap, collections
sigs = {"PNG": b"\x89PNG\r\n\x1a\n", "ZIP": b"PK\x03\x04", "PDF": b"%PDF-", "JPEG": b"\xff\xd8\xff", "GIF": b"GIF89a", "ELF": b"\x7fELF", "PE": b"MZ"}
kw = [rb"flag", rb"ctf", rb"CTF"]
with open("puzzle.vmem", "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    for name, s in sigs.items():
        offs = []
        i = m.find(s)
        while i != -1 and len(offs) < 2000:
            offs.append(i); i = m.find(s, i+1)
        print(name, "count", len(offs), "first", [hex(x) for x in offs[:8]])
    for k in kw:
        offs=[]; i=m.find(k)
        while i!=-1 and len(offs)<40:
            offs.append(i); i=m.find(k,i+1)
        print(k, "first offs", [hex(x) for x in offs[:15]])
        for o in offs[:15]:
            print("  ", hex(o), m[max(0,o-30):o+60])
