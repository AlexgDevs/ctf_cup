from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

with open("mmm", "rb") as f:
    e = ELFFile(f)
    syms = []
    st = e.get_section_by_name(".symtab")
    if st:
        for s in st.iter_symbols():
            if s.entry.st_info.type == "STT_FUNC" and s.entry.st_value:
                syms.append((s.entry.st_value, s.entry.st_size, s.name))
    print("funcs:", [(hex(a), n) for a, _, n in sorted(syms)][:60])
    text = e.get_section_by_name(".text")
    print(".text", hex(text["sh_addr"]), text["sh_size"])
    print("entry", hex(e["e_entry"]))
    data = text.data()
    addr = text["sh_addr"]
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    targets = [s for s in syms if s[2] in ("main",)]
    if not targets:
        targets = [(e["e_entry"], 0x200, "entry")]
    for a, sz, n in targets:
        print("==", n, hex(a))
        off = a - addr
        size = sz if sz else 0x400
        for ins in md.disasm(data[off:off + size], a):
            print(f"{ins.address:x}: {ins.mnemonic} {ins.op_str}")
