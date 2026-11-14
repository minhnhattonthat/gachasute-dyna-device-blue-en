# Font, text renderer and the English VWF (phase 5)

## The renderer (verified: disassembly + runtime probes `tools/lua/fontprobe.lua`, `tools/lua/drawprobe.lua`)
- All runtime text goes through **text objects** and the renderer **0x080049AC**. Object fields: +0 string ptr,
  +4 unit count (0 = up to a 0000 unit), +5 size, +6 palette, +7 fg colour, +8 bg colour, +0xC first tile number,
  +0x10 tile VRAM address, +0x14 map VRAM address, +0x18/+0x1C malloc'd tile/map buffers (0x0800555C), +0x20 tile
  bytes, +0x22 map row bytes, +0x24 map rows. Uploads: 0x08004B34 (tiles), 0x08004B5C (map, dst stride 0x40).
  Setters: 0x080046D8 string, 0x080046DC count, 0x080046E8 fg, 0x08004704 tile pos (tile = row*32+col),
  0x08004720 map pos.
- The string is walked in **u16 units, one cell per unit**; the glyph index is a linear SJIS index (0x0800473C:
  188 per lead byte). Font tables per size at 0x020001F0 + 4*size (copied from ROM):
  - size 1: 16x16 cell (4 tiles: TL, TR, BL, BR), glyphs 12x12 at **0x080F0A54**, 26 B each (u16 SJIS code,
    12 rows x 2 bytes); rows 12-15 are written as colour 0. Map: 2 rows of 2n entries. Used by menus / HUD.
  - size 3: 8x8 cell (1 tile), glyphs at **0x0811F304**, 10 B each (u16 code, 8 rows x 1 byte, MSB = left; rows
    0-6 used, baseline under row 6). Used by messages and most windows.
  - size 4: 8x16 (2 tiles), 18 B glyphs; no font loaded (table entry 0) in any scene probed.
- ASCII bytes have no glyphs: an ASCII pair is read as one bogus SJIS code (garbage tiles, `work/qa/p5_ascii`).
- Numbers from `%dRn` expand to full-width SJIS digits (0x08013384: 824F + digit), so expansions stay even.

## Message drawer (0x080135A0, state 0x02001AC0, text object 0x02008580)
- Setup 0x08013488 expands the message (0x0801328C) into the buffer at 0x02001ADC and fills the state:
  +0 mode (0 idle, 1 drawing, 3 waiting), +1 font size (3), +3 typewriter flag (FF = whole line per call, else one
  unit per call), +4 tile counter, +5 column, +6 line, +8 tile block width (25), +9/+0xA map col/row of the text
  area (6, 16), +0xE/+0x10 tile block col/row, +0x18 pointer to the unit being drawn.
- Instant mode copies units from +0x18 into a **0x44-byte stack buffer** until a code (KG KP KN C0-C4) or the
  tile block wraps (+4 reaches a multiple of +8), then renders that piece at the column. So one line can be split
  in two calls: at most 33 units per piece fit the stack buffer.
- Codes are compared as u16 units: KG (474B), KP (504B), KN (4E4B), C0-C4 (3043..3443).

## The English VWF (`tools/vwf.py`, font `fonts/vwf8.txt`)
- The hook replaces the first 8 bytes of 0x080049AC (`ldr r1,[pc]; bx r1; .word`) with a jump to ARM code at
  ROM 0x7F0000 (code + width table + 8-row glyphs, ~2 KB). Sizes 1 and 3 go through it, others run the original.
- English bytes: printable ASCII (one char per byte), PAD 0x7F (zero width); a unit whose first byte is 0x81+ is
  an SJIS glyph from the game's font at the cell width. The hook keeps the game's tile and map layout (n cells for
  n units) and only redraws the pixels, so English must give **units x cell >= pixels** per segment:
  `vwf.encode_en` pads each segment (text between codes) with PAD units. Size 1 drops trailing PAD PAD units.
- encode_en keeps codes, register codes and SJIS chars on even bytes and splits text pairs that would read as a
  code (KG KP KN C0-C4).
- Message mode: for the drawer's own object, the hook lays out the whole line from its start and draws the
  calling cells' slice, so split pieces and typewriter steps join up (verified: "jumps" across the block wrap,
  `work/qa/p5_vwf`).
- Proven in game: build with `--qa`, intro scene: every glyph of fonts/vwf8.txt renders (`work/qa/p5_vwf/z.png`);
  JP text through the hook looks as before.

## Width gate
See the table in docs/re/windows.md (measured in-game with the marker build and `build.py --qa`).
