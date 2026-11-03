import re
src = open("wsclient.py", encoding="utf-8").read()
old = src[src.index("    def recv_text(self):"):src.index("    def _send_ctrl")]
new = '''    def recv_text(self):
        parts = []
        while True:
            b1, b2 = self._recv_exact(2)
            fin = bool(b1 & 0x80)
            opcode = b1 & 0x0F
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._recv_exact(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._recv_exact(8))[0]
            masked = b2 & 0x80
            mask = self._recv_exact(4) if masked else None
            data = self._recv_exact(n)
            if mask:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            if opcode == 0x8:
                raise ConnectionError("server closed")
            if opcode == 0x9:  # ping -> pong
                self._send_ctrl(0xA, data)
                continue
            if opcode == 0xA:  # pong
                continue
            if opcode in (0x0, 0x1, 0x2):
                parts.append(data)
                if fin:
                    return b"".join(parts).decode(errors="replace")

'''
src = src.replace(old, new)
open("wsclient.py", "w", encoding="utf-8").write(src)
print("patched")
