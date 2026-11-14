# Text: encoding, script container, control codes, string regions

ROM: 8 MiB (0x800000), header title `DINODEVICE B`, code `ABIJ`. No prior fan patch found (web search 2026-11-14).

## Encoding
- **Shift-JIS (cp932)** everywhere, NUL-terminated. **verified**: every sample in this file decodes as readable
  Japanese with Python `cp932` (e.g. the profile popup きいろいボタンの　こうもくは / すべて　にゅうりょくしてください
  seen in `work/qa/tour2/f001200.png`). Full-width spaces (8140) separate words. ASCII bytes inside strings are
  control codes (below), so the engine's parser already accepts single-byte ASCII.
- Glyph rendering: runtime-drawn from a font not yet located (the static graphics sweep does not hold the kana
  font). Find it in phase 5 by hooking the message draw (guess: a 12 px SJIS font, ~21 full-width chars per line).

## Resource directory
`0x0BBDE8`: u32 pointers to three files, each ending in an `end\x1a` marker + 12 bytes of padding:

| Pointer | File | Notes |
|---|---|---|
| 0x080E7FA4 | unknown | not yet examined |
| 0x0844C754 | address database | Japanese municipality / town names, to 0x702BB4 (~2.6 MB), see below |
| 0x08702BC4 | event script | below |

## Event script file (0x702BC4 .. 0x747B34, `end\x1a` at 0x747B34) - verified
- Header: 836 u32 offsets **relative to the file start 0x702BC4**: 834 scripts, then the end sentinel 0x44F70
  (= file length to the marker), then a 0 pad word. First script at file+0xD10 = 0x7038D4. Scripts are 16-byte
  aligned. **verified**: offsets chain exactly; script 0 is a test script (テスト１/２/３).
- The directory pointer 0x08702BC4 at ROM 0x0BBDF0 is the only absolute reference: relocating the file means
  rewriting that one word (plus the table). **guess** until a corrupt-and-boot test confirms.
- Body: little-endian u16 bytecode with **inline** strings. Message op (verified by pattern, 2871 hits):
  `02 00  00 00  <speaker u16, FFFF = none>  <SJIS text> 00 [pad to even]`. Speaker ids 1..15 seen (portraits).
- Other opcodes (e.g. `0E 00 04 00 ...`, `14 00 ...`, `16 00 ...`, `17 00 ...`) are not decoded yet. Inline
  strings mean longer English shifts every later op: any in-script jump offsets must be found and fixed, or
  the strings moved out of line (decide in phase 5; a disassembler of all opcodes and their lengths is needed
  either way to make the identity build trustworthy).
- Text layout: 2 lines per page; longest JP line 21-23 full-width chars.

### In-string control codes (counts over all message ops)
| Code | Count | Meaning (guess from context) |
|---|---|---|
| `KG` | 2817 | line break |
| `KP` | 940 | wait for button, new page |
| `KN` | 395 | end of message without the usual wait / continue (often at the end) |
| `%sR<n>` | ~650 | insert string register n (names: player, Dyna, item) |
| `%dR<n>`, `%02dR<n>`, `%04dR<n>` | ~80 | insert number register n (postal-code style `〒%02dR0－%02dR1`) |
| `%` alone | 4 | check in phase 4 |
| `\x02` | 43 hits | false matches from the regex (operands), not text |

## Other string regions
| Range | What | Format |
|---|---|---|
| 0x0AF6D0, 0x0AFCA0 - 0x0BB7A8 | menus, sector types, item / weapon / Dyna names, help and descriptions, name-entry keyboard (full-width Latin at 0xB7FE0) | NUL-terminated SJIS, 4-byte aligned, reached by pointer tables in code/data (not yet mapped) |
| 0x44C754 - 0x702BB4 | address database: municipality and town names keyed by postal code (e.g. 0x700008 富山市, 20-byte records there; other record shapes earlier) | fixed-size records, SJIS kanji/kana, not NUL-run text |
| 0x747B44 - ? | data file read by the message system (pointers from 0x0A81A4..) | no text |
| 0x3BEB94 - 0x3BED4C, 0x16EB51, 0x22FAB4 | candidates from the run scan; 0x3BEB94 looks like a short label table (ロク, 物青, 地物); the others are graphics noise | check in phase 4 |

## Open questions (non-blocking)
- The address database: tens of thousands of real place names. Plan: romanize with Hepburn from Japan Post's
  KEN_ALL kana readings, keyed by postal code, once phase 4 maps the record format. Space: the ROM is 8 MiB and
  can grow to 16 MiB with BPS. Where the game shows these names (profile, sector names in Dyna City) is to be
  confirmed with the debug tool.
