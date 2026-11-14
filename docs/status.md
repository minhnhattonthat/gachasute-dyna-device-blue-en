# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike done (VWF in game), marker build boots; width gate and full marker tour in progress.
  Last build: `tools/build.py --marker --out build/marker.gba` 2026-11-15, sha1 8462835c..., smoke ok.
- **Done (phase 5 so far, `docs/re/font.md`, `docs/re/windows.md`, decision D9):**
  - Renderer found: all text goes through text objects and 0x080049AC, one SJIS glyph per u16 unit (size 1 =
    16x16 cells / 12x12 font 0x080F0A54, size 3 = 8x8 font 0x0811F304). ASCII had no glyphs.
  - `tools/vwf.py`: ARM hook at ROM 0x7F0000 redraws the same cells with a proportional font (`fonts/vwf8.txt`,
    drawn here, MIT); `encode_en` pads segments (units x 8 >= px), keeps codes even, splits text pairs that read
    as codes. Message mode lays out the whole line, so the drawer's split pieces join up. Every glyph verified in
    game (`work/qa/p5_vwf`); JP text through the hook unchanged.
  - `tools/insert.py` + `build.py`: default build = English (VWF + `en`); `--marker` (every todo -> id + filler;
    strings in their slot, 236 moved to free space with pointers rewritten), `--marker-px N` (wide string
    markers for the width gate), `--identity`, `--qa sSSS.KK[@speaker]=TEXT`.
  - `tools/lint.py` (+ tests/test_lint.py, in the check): codes, 2 lines/page, 188 px per line, 176 px on a
    page's last line; strings against `docs/re/budgets.tsv` (not written yet: every string warns).
  - Message box measured (portrait and no-portrait: same box, x 48, 2 lines, 188/176 px).
  - Marker tour, 14 scenes (date, form, keyboard, title, intro, menu, menu_items, e7, greets, gameover, keeper):
    all reached, ids show; left Japanese = graphics (menu bar, item submenu, form labels; docs/re/graphics.md).
  - Probes: `tools/lua/fontprobe.lua`, `drawprobe.lua`, `markerlog.lua` (logs id, size, map cell of every marker
    drawn); `regen.py --probe`.
- **Done (earlier phases):**
  - Phase 4 (`docs/re/text.md`): `tools/extract.py dump|verify` -> `script/` (30 files, 5536 entries):
    `events_NNN.json` = the 2824 messages (id `sSSS.KK`, flag, speaker), `strings_XXX.json` = the 2712 strings
    of 0x0AF6D0-0x0BB7C0 (id `tOOOOOO`, `ptrs` = every u32 pointer word, `slot` = bytes free in place).
    Status: 5305 todo, 159 keep (debug menu, ASCII formats), 72 data (name-entry keyboard rows / layout).
    Codec `tools/text.py` (KG = newline, `{KP}`, `{KN}`, `{%sR4}`, `{C1}`, `[XX]`); `tools/strtab.py` (pieces,
    pointers: code literal pools + data tables 0x0BDAE8-0x0E4674 only); `tools/addrdb.py` (address DB parse and
    identity repack: 120701 towns, 48 prefectures, 3356 municipalities). `tests/test_extract.py`: roundtrip of
    every string, JSON = ROM, no id missing, kana-run coverage scan (proven to catch injected text), every string
    has a pointer, address DB repack.
  - Step 0 and phase 1 recon (see `docs/re/`: text.md, compression.md, graphics.md).
  - Phase 3 (`docs/re/script.md`, `compression.md`):
    - `tools/script.py`: all 59 opcode lengths, jumps (ops 7-13 and 57, relative to the op), parse of all 834
      scripts, repack with jump fix-ups; identity repack byte-identical. `script.py verify --logs work/qa/ops`
      checks the parse against runtime op logs (`tools/lua/opstep.lua`, run by `tools/debug/opstep_run.py`).
    - `tools/build.py`: identity build = original ROM (`tests/test_script.py`); the script file moves to the free
      space 0x747DA0-0x800000 when it outgrows its slot. `build.py --stress` (every message + ＊) verified in game
      (warp e7: relocated script runs, ＊ shows, menu follows).
    - `tools/ecd.py compress()`: port of the original encoder (Okumura LZSS.C + even pad), re-creates all 3114 ECD
      blocks byte for byte (`ecd.py verify ROM`).
    - Engine rule found: message text must be even-length (the skip scans for `00 00`); `message_bytes` refuses odd
      text. Script 341 ends on an odd message in the original (kept raw).
  - Phase 2 (`docs/re/debug.md`): `tools/debug/warp.lua` + `scenes.tsv`, 147 rows, every one reached from a cold
    boot with a hold shot (`tools/debug/regen.py`). Kinds: `boot`, `newgame`, `script`, `event`, `field`, `menu`
    (tutorial replay + menu routes), `fscript` (reception talk swap), `mode` (top-level mode forced at boot, incl.
    the leftover AGB SYSTEM DEBUG MENU), and new this session:
    - `resume`: the game's continue handler 0x080522D4 restarts the story script in progress from the flags; rows
      r2..r817 (39) cover every branch: chapter resumes, final chapter 147-152, epilogues 153/155, 154.
    - Ending and credits: script 152 (final battle aftermath) runs into mode 22 = the staff roll (graphics credits,
      kana staff names, last card ©2002 スマイルソフト). Rows `ending_full` (152 mashed into the roll), `credits`
      (whole roll), `credits_mid`.
    - `dmode`: tutorial data, then quit, and the next set_mode becomes mode N: shops and menus with real party,
      money and items (d_customize, d_auction, d_dyna_shop, d_item_sell, d_kit, d_dev_status, d_shop_list,
      d_placement, d_team, d_get, d_dyna_status).
    - `battle_place_trap`: field battle placement with a Dyna and its trap set.
  - Verified this session: 42 resume/credits rows (work/qa/warpr) and 12 dmode/battle rows (work/qa/warpd), all
    reached. A 10-row sample of the older kinds after the warp.lua changes was stopped by the host for low memory
    (other projects' emulators were using ~7 GB) after `battle_place` passed; the new code is guarded by kind, and the
    resume/dmode runs go through the shared boot, form, title and tutorial paths. First thing next session: run
    `tools/debug/regen.py --jobs 2` over all rows when memory allows.
- **Next (phase 5, `references/pipeline.md` §Marker/§Width gate):**
  - Full marker tour, when memory allows (this session's run was stopped by the host at 2.2 GB free, after 14
    scenes): `python -X utf8 tools/build.py --marker --marker-px 240 --out build/marker.gba`, then
    `python -X utf8 tools/debug/regen.py --rom build/marker.gba --out work/qa/p5_mk --states work/qa/p5_states
    --jobs 2 --probe tools/lua/markerlog.lua`. Collect `MARK` lines from `work/qa/p5_mk/*/log.txt`: they give
    each string's window (size, map col/row). Look at every hold shot for Japanese left (graphics or unextracted
    text) and broken screens (non-text strings: set their status to "keep" with a note).
  - Width gate for strings: group the MARK placements into windows (item list, help box, status, shop, DB,
    keyword, date...), measure each window's budget from the wide-marker shots (pixels to the next element or
    the frame), write `docs/re/budgets.tsv` (start, end, px, lines, variant per id range) and the table in
    docs/re/windows.md. Then the glyph torture line in one size-1 field (size 1 draws English 2 rows down in the
    16x16 cell: check it looks right next to JP glyphs; a taller font is optional).
  - Register widths: find what %sR4/%sR5/%sR0 hold (player name, Dyna name...) and set `lint.REG_PX` from the
    longest English value (now a 64 px guess).
  - Name entry (can wait for phase 7): keyboard rows (`data` entries, table 0x0D21F0) and the address DB reader
    (record sizes fixed at 16/10/20 bytes) need English layouts.
  - The phase-2 full regen (`regen.py --jobs 2` on the original) is still owed when memory allows.
- **Later phases need:** graphics text: ポーズ, the opening movie's
  green spec panels, debug menu (romaji, debug build only: leave), and the **staff roll** (mode 22): its kana are
  not SJIS in the ROM, find their encoding or tiles (add to the graphics-text survey).
- **Known debug-tool gaps (non-blocking):** the field battle placement has no known "done" input (A places Dyna and
  trap per slot, then it loops to Dyna 1; START/SELECT/R do nothing), so a field battle past placement is not
  reached; the debug menu's BATTLE START (`dbg_battle`) reaches a real battle. Runs without `--sav` share
  `tools/mesen/Saves/<rom>.sav` (menu_saving writes it).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
