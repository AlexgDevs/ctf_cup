path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
with open(path, "rb") as f:
    head = f.read(512)
print(head[:512].hex())
print(repr(head[:256]))
# check magic at common offsets
import struct
with open(path, "rb") as f:
    data = f.read(4096)
print("first 64 bytes repr:", repr(data[:64]))
# NTFS?
print("NTFS sig at 3:", data[3:7])
# VMware?
print("VMware sig:", b"VMware" in data[:4096])
# look for ELF
print("ELF:", data[:4])
# boot?
