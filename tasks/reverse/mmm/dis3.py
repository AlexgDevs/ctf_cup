from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
with open("mmm","rb") as f:
    e = ELFFile(f)
    text = e.get_section_by_name(".text")
    data = text.data(); addr = text["sh_addr"]
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    a=0x18b1; end=0x1c00
    for ins in md.disasm(data[a-addr:end-addr], a):
        print(f"{ins.address:x}: {ins.mnemonic} {ins.op_str}")
        if ins.mnemonic=="ret" and ins.address>0x1a00: break
