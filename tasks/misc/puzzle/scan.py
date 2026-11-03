import re, mmap
pat_ascii = re.compile(rb"ctfcup\{[^}\n]{0,200}\}?", re.I)
hits = []
with open("puzzle.vmem", "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    for mo in pat_ascii.finditer(m):
        hits.append((mo.start(), mo.group(0)[:120]))
        if len(hits) > 200: break
    print("ascii hits:", len(hits))
    for off, s in hits[:60]:
        print(hex(off), s)
    # utf-16le variant
    pat_u16 = re.compile("c\x00t\x00f\x00c\x00u\x00p\x00\\{".encode("latin-1"), re.I)
    cnt = sum(1 for _ in pat_u16.finditer(m))
    print("utf16 'ctfcup{' hits:", cnt)
