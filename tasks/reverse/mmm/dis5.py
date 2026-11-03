from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
with open("mmm","rb") as f:
    e = ELFFile(f)
    text = e.get_section_by_name(".text")
    data = text.data(); addr = text["sh_addr"]
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    a=0x1f00; end=0x2680
    for ins in md.disasm(data[a-addr:end-addr], a):
        s = f"{ins.address:x}: {ins.mnemonic} {ins.op_str}"
        if "rip" in ins.op_str:
            tgt = ins.address + ins.size + int(ins.op_str.split("rip")[1].split("]")[0].replace(" ","").replace("+","") or 0, 0) if False else None
            print(s, "  -> rip-target", hex(ins.address+ins.size + (int(ins.op_str.split("rip + ")[1].split("]")[0],0) if "rip + " in ins.op_str else -int(ins.op_str.split("rip - ")[1].split("]")[0],0))))
        elif ins.mnemonic in ("call","cmp","jne","je","ret","test","xor") :
            print(s)
