# Compression and graphics containers

## BIOS LZ77
Only one block in the whole ROM (0x0E6A58, 0x3098 bytes out); one `swi 0x12` call site at 0x0801D870.
**verified** by `tools/lz77.py` scan (aligned 0x10 headers that decode cleanly).

## ECD (the game's own LZSS) - verified
- Decompressor: Thumb at **0x08005680** (`r0` = source, `r1` = destination); byte writer 0x08005618, input
  reader 0x0800565C. Found by watching EWRAM writes of title tiles (`tools/lua/lzss_log.lua` logs every call).
- Header, 16 bytes: `"ECD\x01"`, then big-endian u32 `raw_len`, `in_len`, `out_len`.
- Body: `raw_len` bytes copied verbatim (they do not enter the ring), then Okumura LZSS: flag byte LSB first,
  1 = literal; 0 = match `b1 b2`: ring position `b1 | (b2 & 0xC0) << 2`, length `(b2 & 0x3F) + 3`.
  Ring 0x400 bytes at IWRAM 0x03001410, zero-filled, first write position 0x3BE.
- 3114 blocks in 0x0EFF34 - 0x44B494: 851 IMG, 2241 PLT, 22 SCR. All decode to their declared size
  (`tools/ecd.py`); `compress_stored` (literal-only) round-trips every block. Title-screen VRAM tiles not found
  raw in ROM dropped from 1531 to 381 once the decompressed blocks were searched (`vramfind.py`), the rest being
  runtime-drawn text and sprites.
- **Encoder - verified**: the original tool was Okumura's LZSS.C (N=0x400, F=0x42, THRESHOLD 2, ring zero-filled
  instead of spaces), plus a final pad of the compressed body to an even length (a lone 00). `ecd.compress()`
  ports it and gives back all 3114 blocks byte for byte (`python -X utf8 tools/ecd.py verify ROM`, ~30 s; the
  test checks every 8th block).
- Block spacing: blocks sit 0-76 bytes apart (alignment/padding varies); a re-encoded block that grows must be
  relocated with its pointer fixed (graphics phase; the pointers are not mapped yet).

## Payloads
| Tag | Layout |
|---|---|
| `IMG\0` | byte 4 flag (0 = 4bpp), byte 5 width in tiles, byte 6 height in tiles, byte 7 0; then tiles row-major |
| `PLT\0` | u16 colour count at +4, colours (BGR555) from +8; usually follows its IMG |
| `SCR\0` | byte 5/6 = map width/height in tiles (32x32), u16 map entries from +8 |

Rendering: `tools/gfx_sweep.py` (contact sheets of every IMG with its following PLT, index in `index.tsv`).
