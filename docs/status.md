# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate: ready to start (phase 5 width gate done 2026-11-15).
  Last build: `build/torture.gba` (`build.py --marker --qa s001.00=<torture> --qa t0B8F38=...`) 2026-11-15, sha1
  bec9720e...; all 147 warps reached on the marker build earlier the same day.
- **Done (phase 5 close, this session):**
  - Glyph torture line (`docs/re/font.md` §Torture line, `tests/test_vwf.py` TORTURE): `fonts/vwf8.txt` now has
    every printable ASCII glyph except `%` (the game's expander eats every `%`: write "percent"). `{ } [ ] \` go
    in script/ as `[7B] [7D] [5B] [5D] [5C]`. All render in a message (warp intro, `MASHA=1`) and in a size-1
    field (form gender). Bug fixed by it: `[XX]` bytes added no width in `encode_en` and lint (clipped line ends).
  - Register widths (`docs/re/windows.md` §String registers, probe `tools/lua/regprobe.lua`): a register = pointer
    + type; nickname max 8 chars (form keyboard), name 12 (form only), Dyna name field 16 bytes (8 chars), ROM
    names 64 px lists -> every `{%sRn}` = 64 px, measured. Phase 7 must keep the 8-character keyboard limit and
    English species names <= 64 px and <= 16 bytes.
  - Guessed windows measured (cols 2, 3, 7-9, 13, 15, 19, 20, 22 + per-id exceptions `ID_WINDOW` in
    tools/budgets.py; table in docs/re/windows.md). Keyword help box is 100 px (a 12-char JP line fits), so the
    keyword/style class is 96. Sector type names: 32 px (field build menu header).
  - `docs/re/budgets.tsv`: 152 measured rows, 3 guess classes left (strings no tour drew): ヨロシク仮面, PDA
    places/event types 0x0B4A70-0x0B4CA8 (60), 459 undrawn UI strings 0x0B8044+ at 88. A LONG line against these
    means warp there and measure (lint warns on guesses).
- **Done (phase 5 earlier, `docs/re/font.md`, `docs/re/windows.md`, decision D9):** VWF hook at ROM 0x7F0000
  (`tools/vwf.py`, `fonts/vwf8.txt`), English encoder (`encode_en` pads segments, keeps codes even), `insert.py` +
  `build.py` (default English, `--marker`, `--marker-px`, `--marker-ids`, `--identity`, `--qa ID=TEXT`), lint
  (`tools/lint.py`: codes, 2 lines/page, 188 px per line, 176 px on a page's last line, string budgets), full
  marker tour 147/147 (`docs/re/marks_p5.tsv`, `tools/marks.py`, `tools/edge.py`, `tools/budgets.py`).
- **Done (earlier phases):** phase 1 recon (`docs/re/`), phase 2 debug warp (`tools/debug/warp.lua`,
  `scenes.tsv` 147 rows incl. resume, credits, dmode shops, debug menu; `docs/re/debug.md`), phase 3 identity
  build + script repack + ECD compressor (`docs/re/script.md`, `compression.md`), phase 4 extract (`script/`: 2824
  messages `sSSS.KK`, 2712 strings `tOOOOOO`; 5305 todo, 159 keep, 72 data; `docs/re/text.md`).
- **Next (phase 6, `references/translation.md`):**
  - Read `docs/decisions.md` and `glossary.md` first; settle the per-project questions not yet recorded there
    (honorifics, credits language, romanization; pre-approved run: pick the skill defaults and record them).
  - Batches by script/ file; width limits = lint (messages 188/176 px, 2 lines; strings per budgets.tsv; registers
    64 px). Messages can add pages (`{KP}`) freely.
  - Tooling for the run: frozen. `tools/lint.py` is the batch check.
- **Later phases need:** name entry (phase 7): keyboard rows (`data` entries, table 0x0D21F0) need an English
  layout with the 8-char limit; the address DB reader (record sizes fixed at 16/10/20 bytes). Graphics text:
  ポーズ, the opening movie's green spec panels, menu bar / item submenu / form labels (docs/re/graphics.md), and
  the **staff roll** (mode 22): its kana are not SJIS in the ROM, find their encoding or tiles.
- **Known debug-tool gaps (non-blocking):** the field battle placement has no known "done" input, so a field battle
  past placement is not reached; the debug menu's BATTLE START (`dbg_battle`) reaches a real battle. Runs without
  `--sav` share `tools/mesen/Saves/<rom>.sav`. `emu.py --route-str` beside warp.lua replaces warp's own input (the
  warp then fails): use warp's `MASHA=1` and `--shots` at frames after ARRIVED instead.
- **Memory:** the host's AWPerformance.SCSubAgent (Dell service) held 3-7 GB; run tours one emulator at a time.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
