from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
with open("mmm","rb") as f:
    e = ELFFile(f)
    text = e.get_section_by_name(".text")
    data = text.data(); addr = text["sh_addr"]
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    a=0x1c00; end=0x2680
    for ins in md.disasm(data[a-addr:end-addr], a):
        s = f"{ins.address:x}: {ins.mnemonic} {ins.op_str}"
        if any(k in ins.mnemonic for k in ("call","cmp","test","lea","jmp","ret")) or "rip" in ins.op_str:
            print(s)
    print("--- sections")
    for s in e.iter_sections():
        if s["sh_addr"]: print(s.name, hex(s["sh_addr"]), hex(s["sh_size"]))
