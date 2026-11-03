import sys

path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
needles = {
    b"NTFS    ": "NTFS boot",
    b"FILE0": "MFT FILE",
    b"\x85\x00\x00\x00": None,
    b"Linux version": "Linux version",
    b"\x7fELF": "ELF",
    b"VMware VM": "VMware",
    b"QEMU": "QEMU",
    b"VirtualBox": "VirtualBox",
    b"ctf": "ctf",
    b"flag": "flag",
}
counts = {}
with open(path, "rb") as f:
    pos = 0
    chunk_size = 64 * 1024 * 1024
    overlap = 64
    prev_tail = b""
    total = 2147483648
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        data = prev_tail + chunk
        for needle, name in needles.items():
            if name is None:
                continue
            c = data.count(needle)
            counts[name] = counts.get(name, 0) + c
        prev_tail = data[-overlap:]
        pos += len(chunk)
        print(f"{pos*100//total}%: {counts}", file=sys.stderr)

print(counts)
