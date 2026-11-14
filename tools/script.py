"""script.py: the event-script file (ROM 0x702BC4, 834 scripts): parse into ops, repack with jumps fixed.

    python -X utf8 tools/script.py verify [--logs work/qa/ops]   # identity repack + every logged pc on an op boundary
    python -X utf8 tools/script.py dis IDX [IDX ..]                # list a script's ops

File layout (docs/re/text.md): 836 u32 offsets from the file start (834 scripts, the offset of the "end\\x1a"
marker, then 0), scripts 16-byte aligned and zero-padded, the marker + 12 zero bytes. The directory word at ROM
0x0BBDF0 is the only pointer to the file. Bytecode: u16 opcodes, 59 handlers at 0x080D2034 (docs/re/script.md).
Lengths in bytes, including the opcode; two are variable:
  op 2  message: 02 00 <u16 flag> <i16 speaker> SJIS text 00, then zero bytes up to the first 00 00 pair that ends
        on an even offset (the handler scans byte by byte for 00 00 from the text start).
  op 23 4 + 10 * count (count = u16 at +2).
Jumps are relative to the jumping op's own address (handler clears bit 0): ops 7..13 `op var value rel` (13 =
always), op 57 `op rel` (target the dispatcher jumps to when the player skips). Repacking maps every target to its
op's new offset, so text may change length freely.
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
BASE = 0x702BC4      # file start in ROM (original position)
END = 0x747B44       # first byte after the file (marker + padding); the next file starts here
DIR_WORD = 0x0BBDF0  # resource directory entry holding 0x08000000 + file start
COUNT = 834
MARKER = b"end\x1a" + bytes(12)

OPLEN = {0: 2, 1: 4, 3: 4, 4: 2, 5: 4, 6: 6, 14: 12, 15: 4, 16: 4, 17: 6, 18: 6, 19: 4, 20: 6, 21: 2, 22: 14,
         24: 6, 25: 2, 26: 2, 27: 8, 28: 4, 29: 14, 30: 4, 31: 6, 32: 6, 33: 4, 34: 6, 35: 4, 36: 2, 37: 2, 38: 2,
         39: 2, 40: 2, 41: 2, 42: 6, 43: 2, 44: 6, 45: 2, 46: 6, 47: 12, 48: 4, 49: 2, 50: 4, 51: 4, 52: 2, 53: 8,
         54: 4, 55: 6, 56: 6, 57: 4, 58: 2}
OPLEN.update({op: 8 for op in range(7, 14)})
JUMP_FIELD = {op: 6 for op in range(7, 14)}
JUMP_FIELD[57] = 2
MSG = 2
LOOP = 23


class Op:
    """One instruction. `raw` holds its bytes; a message also has flag, speaker and text (SJIS bytes, no NUL)."""
    __slots__ = ("off", "code", "raw", "flag", "speaker", "text", "target")

    def __init__(self, off, code, raw):
        self.off, self.code, self.raw = off, code, raw
        self.flag = self.speaker = self.text = self.target = None

    def __repr__(self):
        if self.code == MSG:
            return f"{self.off:05X} MSG flag={self.flag} spk={self.speaker} {self.text.decode('cp932', 'replace')!r}"
        if self.target is not None:
            return f"{self.off:05X} JUMP{self.code} -> {self.target:05X} {self.raw.hex(' ')}"
        return f"{self.off:05X} op{self.code} {self.raw.hex(' ')}"


def message_bytes(flag, speaker, text):
    """Encode a message op the way the original does: text, NUL, NUL. Text must have an even length: the handler
    resumes 2 bytes after the first 00 00 pair it finds, so a NUL at an odd offset would leave the next op on an
    odd address (only script 341 does that, on its last message). The inserter pads odd text (phase 5)."""
    if len(text) % 2:
        raise ValueError(f"message text has odd length {len(text)}: pad it to even before packing")
    out = bytearray(struct.pack("<HHh", MSG, flag, speaker)) + text + b"\0"
    while len(out) % 2 or out[-2:] != b"\0\0":
        out.append(0)
    return bytes(out)


def parse_script(body):
    """-> list of Op. Raises ValueError on an unknown opcode, an overrun, a jump off an op boundary, or non-zero
    bytes after the final end op."""
    ops = []
    j = 0
    while True:
        if j >= len(body) or (ops and ops[-1].code == 0 and not body[j:].strip(b"\0")):
            break
        code = struct.unpack_from("<H", body, j)[0]
        if code == MSG:
            k = j + 6
            while body[k] or body[k + 1]:
                k += 1
            n = k + 2 - j
            op = Op(j, code, body[j:j + n])
            op.flag, op.speaker = struct.unpack_from("<Hh", body, j + 2)
            op.text = body[j + 6:body.index(b"\0", j + 6)]
            if len(op.text) % 2 == 0 and message_bytes(op.flag, op.speaker, op.text) != op.raw:
                raise ValueError(f"message at {j:X} has a layout message_bytes does not reproduce")
        elif code == LOOP:
            n = 4 + 10 * struct.unpack_from("<H", body, j + 2)[0]
            op = Op(j, code, body[j:j + n])
        elif code in OPLEN:
            n = OPLEN[code]
            op = Op(j, code, body[j:j + n])
        else:
            raise ValueError(f"unknown opcode {code} at {j:X}")
        if j + n > len(body):
            raise ValueError(f"op {code} at {j:X} runs past the script end")
        if code in JUMP_FIELD:
            rel = struct.unpack_from("<H", body, j + JUMP_FIELD[code])[0]
            op.target = j + (rel & ~1)
        ops.append(op)
        j += n
    if not ops or ops[-1].code != 0:
        raise ValueError("script does not end with op 0")
    if len(body) - j >= 16 or body[j:].strip(b"\0"):
        raise ValueError(f"{len(body) - j} bytes after the last op are not zero padding")
    starts = {op.off for op in ops}
    for op in ops:
        if op.target is not None and op.target not in starts:
            raise ValueError(f"jump at {op.off:X} lands at {op.target:X}, not an op boundary")
    return ops


def op_bytes(op):
    """An op's bytes: a message whose fields still match its raw bytes keeps them (script 341 ends on a message
    with an odd length, which message_bytes would not make); an edited message is re-encoded."""
    if op.code != MSG:
        return op.raw
    if op.raw[2:6] == struct.pack("<Hh", op.flag, op.speaker) and op.raw[6:7 + len(op.text)] == op.text + b"\0":
        return op.raw
    return message_bytes(op.flag, op.speaker, op.text)


def build_script(ops):
    """Lay the ops out again (messages re-encoded from flag/speaker/text) and rewrite every jump field."""
    raws = [op_bytes(op) for op in ops]
    new_off = {}
    pos = 0
    for op, raw in zip(ops, raws):
        new_off[op.off] = pos
        pos += len(raw)
    out = bytearray()
    for op, raw in zip(ops, raws):
        if op.target is not None:
            f = JUMP_FIELD[op.code]
            old_rel = struct.unpack_from("<H", raw, f)[0]
            rel = (new_off[op.target] - new_off[op.off]) | (old_rel & 1)
            if not 0 <= rel <= 0xFFFF:
                raise ValueError(f"jump at {op.off:X} out of u16 range after repack: {rel}")
            raw = raw[:f] + struct.pack("<H", rel) + raw[f + 2:]
        out += raw
    return bytes(out)


def offsets(rom, base=BASE):
    return [struct.unpack_from("<I", rom, base + 4 * i)[0] for i in range(COUNT + 2)]


def unpack(rom, base=BASE):
    """-> list of 834 op lists."""
    offs = offsets(rom, base)
    return [parse_script(rom[base + offs[i]:base + offs[i + 1]]) for i in range(COUNT)]


def pack(scripts):
    """-> the whole file (header, 16-aligned scripts, end marker)."""
    pos = 4 * (COUNT + 2)
    offs, bodies = [], []
    for ops in scripts:
        body = build_script(ops)
        body += bytes(-len(body) % 16)
        offs.append(pos)
        bodies.append(body)
        pos += len(body)
    offs += [pos, 0]
    return struct.pack(f"<{COUNT + 2}I", *offs) + b"".join(bodies) + MARKER


def check_logs(rom, logdir):
    """Every pc the opstep probe logged (tools/lua/opstep.lua) must start an op of the parse, and a non-jump op's
    logged step must equal its length. Returns (ops checked, list of problems)."""
    offs = offsets(rom)
    where = {}
    for i, ops in enumerate(unpack(rom)):
        for op in ops:
            where[0x08000000 + BASE + offs[i] + op.off] = (i, op)
    problems, n = [], 0
    for log in sorted(Path(logdir).glob("*/log.txt")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("OP "):
                continue
            _, code, pc, npc, _ret = line.split()
            pc, npc, code = int(pc, 16), int(npc, 16), int(code)
            n += 1
            hit = where.get(pc)
            if not hit or hit[1].code != code:
                problems.append(f"{log.parent.name}: pc {pc:08X} op {code} is not an op start in the parse")
                continue
            i, op = hit
            step = npc - pc
            if op.code in JUMP_FIELD and npc - (0x08000000 + BASE + offs[i]) == op.target:
                continue
            if op.code == 0 or step == len(op.raw):
                continue
            problems.append(f"{log.parent.name}: script {i} op {code} at {op.off:X} stepped {step}, parse says "
                            f"{len(op.raw)}")
    return n, problems


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--logs", help="opstep log folder (work/qa/ops)")
    d = sub.add_parser("dis")
    d.add_argument("idx", nargs="+", type=int)
    ap.add_argument("--rom", default=str(ROM))
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    if a.cmd == "dis":
        scripts = unpack(rom)
        for i in a.idx:
            print(f"# script {i}")
            for op in scripts[i]:
                print(op)
        return 0
    packed = pack(unpack(rom))
    same = packed == rom[BASE:END]
    print(f"identity repack: {'identical' if same else 'DIFFERENT'} ({len(packed)} bytes)")
    bad = not same
    if a.logs:
        n, problems = check_logs(rom, a.logs)
        print(f"opstep logs: {n} ops checked, {len(problems)} problems")
        for p in problems[:40]:
            print("  " + p)
        bad |= bool(problems)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
