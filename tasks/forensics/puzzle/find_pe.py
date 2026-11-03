import struct
path = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\forensics\puzzle\extracted\puzzle.vmem"
regions = [(104*1024*1024, 12*1024*1024), (288*1024*1024, 10*1024*1024), (540*1024*1024, 8*1024*1024)]
for off, size in regions:
    with open(path, "rb") as f:
        f.seek(off)
        data = f.read(size)
    pos = 0
    while True:
        i = data.find(b"MZ", pos)
        if i == -1:
            break
        if i + 0x40 < len(data):
            e_lfanew = struct.unpack_from("<I", data, i+0x3C)[0]
            if 0x40 < e_lfanew < 0x400 and i + e_lfanew + 4 <= len(data):
                if data[i+e_lfanew:i+e_lfanew+4] == b"PE\x00\x00":
                    machine = struct.unpack_from("<H", data, i+e_lfanew+4)[0]
                    print(f"PE @ {off+i} machine={machine:#x}")
        pos = i + 1
