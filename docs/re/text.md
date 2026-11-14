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
  rewriting that one word. **verified** in game with the relocated stress build (docs/re/script.md).
- Body: little-endian u16 bytecode with **inline** strings; 2824 message ops
  `02 00 <flag u16> <speaker i16, FFFF = none> <SJIS text> 00 00`. Speaker ids 1..15 seen (portraits).
- All 59 opcodes' lengths and the two jump forms are decoded and verified: **docs/re/script.md**. Longer English
  text is fine: `tools/script.py` re-lays the ops and fixes every relative jump (phase 3 identity build).
- Text layout: 2 lines per page; longest JP line 21-23 full-width chars.

### In-string control codes (counts over all message ops)
| Code | Count | Meaning (guess from context) |
|---|---|---|
| `KG` | 2817 | line break |
| `KP` | 940 | wait for button, new page |
| `KN` | 395 | end of message without the usual wait / continue (often at the end) |
| `%sR<n>` | ~650 | insert string register n (names: player, Dyna, item) |
| `%dR<n>`, `%02dR<n>`, `%04dR<n>` | ~80 | insert number register n (postal-code style `〒%02dR0－%02dR1`) |
| `%` alone | 1 | script 341: `%02dR5%の` — a typo in the original; the expander reads it as `%dR?` (4 bytes) |

**Expander - verified (disassembly)**: 0x0801328C copies the text to a buffer, expanding `%sRn` (4 bytes,
recursive: string register n at 0x02002BD4 + 8n), `%0WdRn` (6), `%WdRn` (5) and anything else after `%` as
`%dRn` (4). KG/KP/KN are handled later by the drawer (0x08013488). Count over messages (phase 4): only KG, KP,
KN and the % forms occur; no other ASCII.

### Menu-string codes (string region, phase 4 tally)
| Code | Meaning |
|---|---|
| `%sRn`, `%WdRn`, `%0WdRn`, `%dRn` | registers, as above |
| `C0`-`C4` | colour (guess: `C1%3dR0C0／C1%3dR1` switches and returns to C0); confirm in phase 5 |
| `tb` `so` `ED` | name-entry keyboard layout string at 0x0B8C24 (row, key, end): data |
| `%d`, `%02X`, `%03d` ... | printf formats in debug / number labels |

Text form in `script/` JSON (`tools/text.py`): KG = newline, `{KP}` + newline, `{KN}`, `{%sR4}`, `{C1}`,
`[XX]` for any other byte; printable ASCII as itself.

## Other string regions
| Range | What | Format |
|---|---|---|
| 0x0AF6D0 - 0x0BB7C0 | 2712 strings: ヨロシク仮面 (0xAF6D0), the AGB debug menu (0xAF6E0-0xAFCA0, romaji, kept), menus, sector types, item / weapon / Dyna names, help and descriptions, name-entry keyboard | NUL-terminated SJIS, 4-aligned, zero-padded. **verified**: every string has a direct u32 pointer, 4-aligned, in code literal pools (0x008980-0x0A3254) or the data tables after the region (0x0BDAE8-0x0E4674); 5647 pointers (`tools/strtab.py`). Words elsewhere that equal a string start are coincidences in graphics. `FLASH_V126` (save-type signature) follows at 0x0BB7C4: never touch |
| 0x0D21F0 - 0x0D22F8 | pointer table of the name-entry keyboard pages: one 5- or 10-key row string per entry (kana, full-width Latin, digits, symbols, kanji for addresses 丁番号 etc.) | the rows are `data` in script/ (reworked with the font, phase 5) |
| 0x44C754 - 0x702BB4 | address database: postal codes with prefecture, municipality, town names | **verified** layout below (`tools/addrdb.py`, identity repack) |
| 0x747B44 - ? | data file read by the message system (pointers from 0x0A81A4..) | no text |
| 0x0E7FA4 | resource file 0: offset table; its first entry is the first ECD block (0x0EFF34), i.e. the graphics archive | no text (ECD blocks are IMG/PLT/SCR only) |
| 0x0E6A58 | the one BIOS-LZ77 block: ARM code | no text |

**Coverage (phase 4, `tools/extract.py verify`)**: a ROM-wide scan for runs of 3+ kana finds nothing outside the
three ranges above except tile-map bytes at 0x3BE700-0x3BED60 (looked like ロク / 地物 labels; they are BG map
data) and graphics noise at 0x3D97B7. A wider SJIS-run scan's other hits are random kanji in graphics.
Strings built in code (immediates) can only show up in the marker build (phase 5).

## Address database (resource file 2) - verified
Header: 4 u32 LE offsets from 0x44C754: towns 0x10, prefectures 0x2A5C50, municipalities 0x2A5E30, end 0x2B6460.
- Towns: 120701 records x 23 bytes: u32 **BE** postal code (e.g. 0x0009C7AD = 064-0941 旭ケ丘), u8 prefecture
  index (0-46), u16 BE municipality index (0-3355), 16-byte SJIS town name NUL-padded (empty = the code's
  catch-all), then 5 zero bytes. 69240 distinct town names.
- Prefectures: 48 x 10 bytes (北海道, 青森県...). Municipalities: 3356 x 20 bytes (札幌市中央区...).
- English: names are fixed-width (16 / 10 / 20 bytes); Hepburn often runs longer, so the reader's record size may
  need changing (find the reader in phase 5).

## Open questions (non-blocking)
- The address database: tens of thousands of real place names. Plan: romanize with Hepburn from Japan Post's
  KEN_ALL kana readings, keyed by postal code, once phase 4 maps the record format. Space: the ROM is 8 MiB and
  can grow to 16 MiB with BPS. Where the game shows these names (profile, sector names in Dyna City) is to be
  confirmed with the debug tool.
