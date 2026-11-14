"""vwf.py: variable-width English text for the text-object renderer 0x080049AC (docs/re/font.md).

    from vwf import apply, encode_en, width
    rom = apply(bytearray(rom))     # hook + font at VWF_AT
    raw = encode_en("Hello!\\nBye{KP}\\n...")   # bytes for a message or string (tools/text.py form in)
    px = width("Hello!")             # ink advance in pixels (8x8 cells)

The game draws text through text objects (struct at e.g. 0x02008580): string pointer +0, unit count +4 (0 = up to
a 0000 unit), size +5 (1 = 16x16 cells, 12x12 SJIS font; 3 = 8x8 cells, 8x8 font), palette +6, fg +7, bg +8,
first tile +0xC. The renderer walks the string in **u16 units**, one cell per unit: tiles n*0x20 (size 3) or n*0x80
(size 1, 4 tiles per cell), map entries base+i (size 3) or a 2-row block (size 1). The message drawer also walks
u16 units and stops at the codes KG, KP, KN (and C0-C4 colour), so English keeps that unit grid:

  - a unit whose first byte is an SJIS lead (0x81+) is a full-width glyph from the game's font (cell width);
  - any other unit is two single bytes: printable ASCII from fonts/vwf8.txt at its own width, PAD (0x7F) or any
    other byte = nothing;
  - the hook keeps the original tile and map layout (n cells) and only changes the pixels: the text runs
    left-aligned through the cells at its own widths. So a segment (text between two codes) needs
    units * cell >= its pixel width: encode_en pads every segment with PAD units at its end;
  - size 1: trailing PAD PAD units are dropped from n (two ASCII letters never pass a 16-px cell, so the ink
    always fits, and the field keeps the width of the text);
  - message mode (obj = the drawer's 0x02008580 while the drawer runs): the drawer splits a line into several
    calls (at colour codes, where its 25-wide tile block wraps, and one unit per call in typewriter mode), so the
    hook lays out the whole line from its start (after KG/KP in the message buffer, found from the drawer's
    pointer 0x02001AC0+0x18) and draws only the calling cells' slice of it. A colour code snaps the pen to its
    cell, as the drawer places the next piece there.

encode_en also keeps every code and SJIS char on an even byte (a PAD before it when needed), and never lets two
ASCII letters form a code unit (KG KP KN C0-C4 at an even offset get a PAD between them). Register codes (%sRn,
%dRn) expand to an even number of bytes (SJIS digits; names are padded to even), so they count as even.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from text import TOKEN  # noqa: E402

FONT = ROOT / "fonts" / "vwf8.txt"
BUS = 0x08000000
VWF_AT = 0x7F0000          # ROM offset of the hook + font (end of the free space, docs/re/text.md)
VWF_END = 0x7F2000
HOOK_AT = 0x0049AC         # renderer entry (Thumb): replaced by ldr r1,[pc]; bx r1; .word VWF
PAD = 0x7F
MSGBUF = (0x02001ADC, 0x02002BD4)   # the drawer's expanded message buffer (0x02001AC0 + 0x1C) .. string registers
DRAW_STATE = 0x02001AC0             # message drawer state: +0 mode (0 = idle), +0x18 pointer to the unit being drawn
DRAW_OBJ = 0x02008580               # the drawer's text object
CODES = {b"KG", b"KP", b"KN", b"C0", b"C1", b"C2", b"C3", b"C4"}
CELL = 8


def load_font(path=FONT):
    """-> {char: (advance, [8 row ints, bit 7 = leftmost])}."""
    glyphs = {}
    lines = [ln.rstrip("\n") for ln in path.read_text(encoding="utf-8").splitlines()]
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.startswith("= "):
            i += 1
            continue
        name = ln[2:]
        ch = " " if name == "space" else name
        rows = lines[i + 1:i + 9]
        if len(rows) != 8 or len({len(r) for r in rows}) != 1 or any(set(r) - set("#.") for r in rows):
            raise ValueError(f"vwf8.txt: glyph {name!r} needs 8 rows of one length of '#'/'.'")
        w = len(rows[0])
        if w > 8:
            raise ValueError(f"vwf8.txt: glyph {name!r} is {w} px wide (max 8)")
        bits = [sum(0x80 >> c for c, p in enumerate(r) if p == "#") for r in rows]
        glyphs[ch] = (w + 1, bits)
        i += 9
    return glyphs


_FONT = None


def font():
    global _FONT
    if _FONT is None:
        _FONT = load_font()
    return _FONT


def char_width(ch, cell=CELL):
    if ord(ch) < 0x80:
        if ch not in font():
            raise ValueError(f"no VWF glyph for {ch!r} (fonts/vwf8.txt)")
        return font()[ch][0]
    return cell  # full-width SJIS glyph


def width(s, cell=CELL):
    """Pixel width of plain text (no codes) in cells of `cell` px."""
    return sum(char_width(ch, cell) for ch in s)


def encode_en(s, cell=CELL):
    """English in tools/text.py form -> bytes for the game (see the module doc). Raises on characters with no
    glyph and on stray syntax. `cell`: the cell width the text is drawn in (8 = messages and size-3 strings)."""
    out = bytearray()
    st = {"own": 0, "px": 0}   # the segment's own bytes (register expansions excluded) and ink pixels

    def byte(b):
        out.append(b)
        st["own"] += 1

    def odd():
        return st["own"] % 2 == 1   # register expansions are even, so the segment's own bytes give the parity

    def close_segment():
        if odd():
            byte(PAD)
        need = -(-st["px"] // cell)
        while st["own"] // 2 < need:
            byte(PAD)
            byte(PAD)
        st["own"] = st["px"] = 0

    def ascii(b):
        if odd() and bytes((out[-1], b)) in CODES:
            byte(PAD)   # out[-1] and b would form a code unit: push b into the next unit
        byte(b)
        if 0x20 <= b < 0x7F:
            st["px"] += char_width(chr(b), cell)

    def plain(text):
        for ch in text:
            if ch in "{}[]\\":
                raise ValueError(f"stray {ch!r} in {s!r}: write a control code or [XX]")
            if ord(ch) < 0x80:
                ascii(ord(ch))
            else:
                raw = ch.encode("cp932")
                if len(raw) != 2:
                    raise ValueError(f"{ch!r} is not a full-width SJIS character")
                if odd():
                    byte(PAD)
                byte(raw[0])
                byte(raw[1])
                st["px"] += cell

    pos = 0
    for m in TOKEN.finditer(s):
        plain(s[pos:m.start()])
        t = m.group()
        if m[1] is not None:            # register code: starts on an even byte, expands to an even length
            if odd():
                byte(PAD)
            out.extend(m[1].encode("ascii"))
        elif m[3] is not None:          # [XX] raw byte: part of the segment's own text (ASCII counts its width)
            b = int(m[3], 16)
            ascii(b) if b < 0x80 else byte(b)
        else:                           # KG KP KN Cn end the segment
            close_segment()
            out.extend(b"KG" if t == "\n" else b"KP" if t.startswith("{KP}") else b"KN" if t == "{KN}"
                       else m[2].encode("ascii"))
        pos = m.end()
    plain(s[pos:])
    close_segment()
    return bytes(out)


# ---------------------------------------------------------------- the hook (ARM code at VWF_AT)

def _asm(at):
    """ARM source of the renderer hook, assembled for ROM address BUS + at."""
    return f"""
hook:
    ldrb r1, [r0, #5]
    cmp r1, #1
    cmpne r1, #3
    bne orig
    push {{r4-r11, lr}}
    sub sp, sp, #32
    mov r4, r0
    ldr r5, [r4]
    ldrb r6, [r4, #4]
    cmp r6, #0
    bne have_n
    mov r0, r5
count:
    ldrh r1, [r0], #2
    cmp r1, #0
    addne r6, r6, #1
    bne count
have_n:
    ldrb r7, [r4, #5]
    cmp r7, #1
    moveq r0, #16
    movne r0, #8
    str r0, [sp, #8]
    bne no_trim
trim:
    cmp r6, #1
    ble no_trim
    add r0, r5, r6, lsl #1
    ldrh r1, [r0, #-2]
    ldr r2, lit_padpad
    cmp r1, r2
    subeq r6, r6, #1
    beq trim
no_trim:
    cmp r7, #1
    moveq r0, r6, lsl #7
    movne r0, r6, lsl #5
    mov r8, r0
    ldr r1, lit_malloc
    mov lr, pc
    bx r1
    mov r9, r0
    str r9, [r4, #0x18]
    mov r0, r6, lsl #3
    ldr r1, lit_malloc
    mov lr, pc
    bx r1
    mov r10, r0
    str r10, [r4, #0x1c]
    strh r8, [r4, #0x20]
    cmp r7, #1
    moveq r0, r6, lsl #2
    movne r0, r6, lsl #1
    strh r0, [r4, #0x22]
    moveq r0, #2
    movne r0, #1
    strh r0, [r4, #0x24]
    ldr r0, [r4, #0xc]
    ldrb r1, [r4, #6]
    add r0, r0, r1, lsl #12
    mov r1, #0
    cmp r7, #1
    beq map1
map3:
    cmp r1, r6
    bge map_done
    add r2, r0, r1
    mov r3, r1, lsl #1
    strh r2, [r10, r3]
    add r1, r1, #1
    b map3
map1:
    cmp r1, r6
    bge map_done
    add r2, r0, r1, lsl #2
    mov r3, r1, lsl #2
    strh r2, [r10, r3]
    add r3, r3, #2
    add r2, r2, #1
    strh r2, [r10, r3]
    add r3, r3, r6, lsl #2
    sub r3, r3, #2
    add r2, r2, #1
    strh r2, [r10, r3]
    add r3, r3, #2
    add r2, r2, #1
    strh r2, [r10, r3]
    add r1, r1, #1
    b map1
map_done:
    ldrb r0, [r4, #8]
    ldr r1, lit_nibbles
    mul r2, r0, r1
    mov r1, #0
fill:
    cmp r1, r8
    bge fill_done
    mov r3, r2
    cmp r7, #1
    bne fill_store
    and r0, r1, #0x50
    cmp r0, #0x50
    moveq r3, #0
fill_store:
    str r3, [r9, r1]
    add r1, r1, #4
    b fill
fill_done:
    mov r0, #0
    str r0, [sp, #12]
    str r0, [sp, #16]
    str r5, [sp, #24]
    ldr r1, lit_drawobj
    cmp r4, r1
    bne layout
    ldr r3, lit_state
    ldrb r0, [r3]
    cmp r0, #0
    beq layout
    ldr r5, [r3, #0x18]
    ldr r1, lit_msgbuf
    cmp r5, r1
    blo layout
    ldr r2, lit_msgend
    cmp r5, r2
    bhs layout
    mov r0, #1
    str r0, [sp, #16]
    mov r3, r5
back:
    cmp r3, r1
    bls back_done
    ldrh r0, [r3, #-2]
    ldr r2, lit_kg
    cmp r0, r2
    beq back_done
    ldr r2, lit_kp
    cmp r0, r2
    beq back_done
    sub r3, r3, #2
    b back
back_done:
    str r3, [sp, #24]
    mov r2, #0
kloop:
    cmp r3, r5
    bhs kdone
    ldrh r0, [r3], #2
    and r1, r0, #0xFF
    cmp r1, #0x43
    bne kcount
    mov r1, r0, lsr #8
    sub r1, r1, #0x30
    cmp r1, #4
    bls kloop
kcount:
    add r2, r2, #1
    b kloop
kdone:
    str r2, [sp, #12]
layout:
    ldr r0, [sp, #8]
    ldr r1, [sp, #12]
    mul r2, r1, r0
    str r2, [sp, #0]
    mul r2, r6, r0
    str r2, [sp, #4]
    ldr r5, [sp, #24]
    ldr r0, [sp, #16]
    cmp r0, #0
    addeq r8, r5, r6, lsl #1
    mvnne r8, #0
    mov r10, #0
    ldrb r11, [r4, #7]
    mov r0, #0
    str r0, [sp, #20]
rloop:
    cmp r5, r8
    bhs rdone
    ldrh r0, [r5]
    cmp r0, #0
    beq rdone
    ldr r1, lit_kg
    cmp r0, r1
    beq rdone
    ldr r1, lit_kp
    cmp r0, r1
    beq rdone
    ldr r1, lit_kn
    cmp r0, r1
    beq rdone
    and r1, r0, #0xFF
    cmp r1, #0x43
    bne notc
    mov r1, r0, lsr #8
    sub r1, r1, #0x30
    cmp r1, #4
    bhi notc
    add r11, r1, #1
    ldr r1, [sp, #20]
    ldr r2, [sp, #8]
    mul r10, r1, r2
    add r5, r5, #2
    b rloop
notc:
    ldr r1, [sp, #20]
    add r1, r1, #1
    str r1, [sp, #20]
    and r1, r0, #0xFF
    cmp r1, #0x81
    blo ascii_unit
    bl jp_char
    add r5, r5, #2
    b rloop
ascii_unit:
    bl en_char
    ldrh r1, [r5]
    mov r1, r1, lsr #8
    bl en_char
    add r5, r5, #2
    b rloop
rdone:
    add sp, sp, #32
    pop {{r4-r11, lr}}
    bx lr

orig:
    push {{r4-r7, lr}}
    mov r7, r10
    mov r6, r9
    mov r5, r8
    ldr r1, lit_resume
    bx r1

en_char:
    sub r1, r1, #0x20
    cmp r1, #0x5F
    bxhs lr
    mov r12, lr
    ldr r0, lit_widths
    ldrb r0, [r0, r1]
    str r0, [sp, #28]
    ldr r0, lit_glyphs
    add r0, r0, r1, lsl #3
    mov r1, #1
    cmp r7, #1
    moveq r2, #2
    movne r2, #0
    add r3, r2, #8
    bl plot
    ldr r0, [sp, #28]
    add r10, r10, r0
    bx r12

jp_char:
    mov r12, lr
    ldr r1, lit_lookup
    mov lr, pc
    bx r1
    ldr r1, lit_fonttab
    ldr r1, [r1, r7, lsl #2]
    cmp r7, #1
    moveq r2, #26
    movne r2, #10
    mla r0, r2, r0, r1
    add r0, r0, #2
    moveq r1, #2
    movne r1, #1
    mov r2, #0
    moveq r3, #12
    movne r3, #8
    bl plot
    ldr r0, [sp, #8]
    add r10, r10, r0
    bx r12

plot:
    push {{r4-r12, lr}}
    ldr r4, [sp, #40]
    sub r4, r10, r4
    ldr r5, [sp, #44]
    mov r6, r9
    mov r8, r7
    mov r7, r11
prow:
    cmp r2, r3
    bge pret
    ldrb r10, [r0]
    mov r10, r10, lsl #8
    cmp r1, #2
    ldrbeq r11, [r0, #1]
    orreq r10, r10, r11
    add r0, r0, r1
    mov r9, #0
    cmp r10, #0
    beq pnextrow
ppix:
    tst r10, #0x8000
    beq pnext
    adds r11, r4, r9
    bmi pnext
    cmp r11, r5
    bge pnext
    cmp r8, #1
    moveq r12, r11, lsr #4
    moveq r12, r12, lsl #7
    andeq lr, r11, #8
    addeq r12, r12, lr, lsl #2
    moveq lr, r2, lsr #3
    addeq r12, r12, lr, lsl #6
    movne r12, r11, lsr #3
    movne r12, r12, lsl #5
    and lr, r2, #7
    add r12, r12, lr, lsl #2
    and lr, r11, #7
    add r12, r12, lr, lsr #1
    add r12, r12, r6
    ldrb lr, [r12]
    tst r11, #1
    andeq lr, lr, #0xF0
    orreq lr, lr, r7
    andne lr, lr, #0x0F
    orrne lr, lr, r7, lsl #4
    strb lr, [r12]
pnext:
    add r9, r9, #1
    mov r10, r10, lsl #1
    bics r10, r10, #0x10000
    bne ppix
pnextrow:
    add r2, r2, #1
    b prow
pret:
    pop {{r4-r12, lr}}
    bx lr

lit_padpad: .word {PAD | PAD << 8:#x}
lit_malloc: .word 0x0800555D
lit_nibbles: .word 0x11111111
lit_drawobj: .word {DRAW_OBJ:#x}
lit_state: .word {DRAW_STATE:#x}
lit_msgbuf: .word {MSGBUF[0]:#x}
lit_msgend: .word {MSGBUF[1]:#x}
lit_kg: .word 0x474B
lit_kp: .word 0x504B
lit_kn: .word 0x4E4B
lit_resume: .word {BUS + HOOK_AT + 8 + 1:#x}
lit_widths: .word WIDTHS
lit_glyphs: .word GLYPHS
lit_lookup: .word 0x0800473D
lit_fonttab: .word 0x020001F0
"""


def tables():
    """-> (widths 96 bytes, glyphs 96*8 bytes) for bytes 0x20..0x7F (0x7F = PAD: width 0)."""
    widths, glyphs = bytearray(96), bytearray(96 * 8)
    for ch, (adv, rows) in font().items():
        i = ord(ch) - 0x20
        widths[i] = adv
        glyphs[i * 8:i * 8 + 8] = bytes(rows)
    return bytes(widths), bytes(glyphs)


def assemble(at=VWF_AT):
    """-> the blob placed at `at`: code, then widths (96) and glyphs (96*8), 4-aligned."""
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM
    ks = Ks(KS_ARCH_ARM, KS_MODE_ARM)
    probe, _ = ks.asm(_asm(at).replace("WIDTHS", "0").replace("GLYPHS", "0"), BUS + at)
    code_len = (len(probe) + 3) & ~3
    w_at = BUS + at + code_len
    g_at = w_at + 96
    code, _ = ks.asm(_asm(at).replace("WIDTHS", f"{w_at:#x}").replace("GLYPHS", f"{g_at:#x}"), BUS + at)
    code = bytes(code).ljust(code_len, b"\0")
    widths, glyphs = tables()
    return code + widths + glyphs


def apply(rom):
    """Install the hook and font into `rom` (bytearray, original bytes at both places). Returns rom."""
    blob = assemble()
    if VWF_AT + len(blob) > VWF_END:
        raise ValueError(f"VWF blob of {len(blob)} bytes passes {VWF_END:#x}")
    if any(rom[VWF_AT:VWF_AT + len(blob)]):
        raise ValueError("VWF area is not empty")
    rom[VWF_AT:VWF_AT + len(blob)] = blob
    # 080049AC: ldr r1, [pc, #0]; bx r1; .word hook (ARM)
    rom[HOOK_AT:HOOK_AT + 8] = bytes.fromhex("0049" "0847") + (BUS + VWF_AT).to_bytes(4, "little")
    return rom


def code_units(raw):
    """Offsets of even-aligned code units in encoded bytes (for tests and the lint)."""
    return [i for i in range(0, len(raw) - 1, 2) if raw[i:i + 2] in CODES]
