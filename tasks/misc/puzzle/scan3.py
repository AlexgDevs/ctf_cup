import re, mmap
pats = {
 "utf16 ctfcup": "ctfcup".encode("utf-16-le"),
 "utf16 CTFCUP": "CTFCUP".encode("utf-16-le"),
 "utf16 flag{": "flag{".encode("utf-16-le"),
 "b64 ctfcup": b"Y3RmY3Vw",
 "hex ctf{": b"63746b7b",
 "ascii cup{": b"cup{",
 "ascii CTF{": b"CTF{",
 "ascii flag{": b"flag{",
 "ascii FLAG": b"FLAG",
 "hex ctfcup": b"6374666375",
}
with open("puzzle.vmem", "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    for name, p in pats.items():
        offs = []; i = m.find(p)
        while i != -1 and len(offs) < 30:
            offs.append(i); i = m.find(p, i + 1)
        print(name, "count>=", len(offs), [hex(x) for x in offs[:10]])
        for o in offs[:4]:
            print("   ", m[max(0,o-20):o+80])
