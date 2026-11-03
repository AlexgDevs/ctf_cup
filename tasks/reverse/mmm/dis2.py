from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
with open("mmm","rb") as f:
    e = ELFFile(f)
    text = e.get_section_by_name(".text")
    ro = e.get_section_by_name(".rodata")
    data = text.data(); addr = text["sh_addr"]
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    for a, end in [(0x1230, 0x14e0), (0x14e0, 0x267c)]:
        print("== func", hex(a))
        off = a - addr
        for ins in md.disasm(data[off:off+(end-a)], a):
            print(f"{ins.address:x}: {ins.mnemonic} {ins.op_str}")
    print("== rodata", hex(ro["sh_addr"]), ro["sh_size"])
    rd = ro.data()
    for va in [0x2000, 0x1f21, 0x1fb6, 0x1efe, 0x1f48]:
        o = va - ro["sh_addr"]
        if 0 <= o < len(rd):
            end = rd.find(b"\0", o)
            print(hex(va), repr(rd[o:end]))
