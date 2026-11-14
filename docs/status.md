# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate in progress: b001-b003 of 45 merged (266 of 5305 entries; scripts 0-55).
  Last build: `build/dynadevice_blue_en.gba` 2026-11-15 (b001 only), sha1 8b8b8bd1...; pilot seen in game
  (`work/qa/p6_pilot2`, warp `intro` + `MASHA=1`, 6000 frames): English wraps cleanly, ▼ clears the last line.
- **How phase 6 runs (D11):** one agent translates batches in order, itself (Orca: no helpers).
  - Batches: `work/tl/b001..b045.tsv` (gitignored, made once by `tools/batches.py split`; b001-b027 events,
    b028-b045 strings). Do NOT re-split. If work/tl/ is lost, `split` again: it numbers on and skips nothing that
    is merged (merged entries are status done).
  - Per batch: read `cut -f1,2,5 work/tl/bNNN.tsv` (via ctx_execute, ~50 lines at a time), write
    `work/tl/bNNN.out.tsv` with the Write tool, `python -X utf8 tools/batches.py merge bNNN` (checks first:
    codes, widths via lint, glossary), commit. Brief: `docs/translator-brief.md`; voices: `docs/style-reference.md`.
  - Messages are written as paragraphs ({KP} between pages); the tool wraps them to 188/176 px, 2 lines a page.
    Choice lines are manual (`\n` in the entry) with `<@N>` JP-column markers.
  - Context: one worker gets through ~3-4 batches after setup; hand back at ~150k with `worker_done --outcome
    failed`, body "context limit, resume from docs/status.md".
- **Next:**
  1. **Verify one choice line in game first** (s034.11 / s037.00, Yurie's Yes/No before the first Colosseum battle,
     or any shop menu s690): the cursor must sit left of "Yes" and "No" laid out with `<@5>Yes<@11>No`. If the
     cursor positions come from code rather than text, adjust `pad_cols` and re-merge with `--overwrite`.
     Scene `choice_yesno` (fscript 37) was added; on the b001-b003 build it had not ARRIVED by frame 9000
     (`work/qa/p6_choice3`, log still in tutorial TEXT at f8984): try `--frames 15000`, and if fscript can't get
     there, check warp.lua's tutorial skip (line ~217-286) against the longer English tutorial.
  2. Continue at b004 (s055.01-s080.09), in order to b027, then strings b028-b045 (Dyna species = constellation
     names per D10, armor/weapon parts, menus: menu verbs must match glossary "Decisions from earlier batches").
  3. After all batches: review pass (fresh read-only, per file group, `assets/reviewer-brief.md`), Minors to
     `docs/polish.md`; `tools/lint.py` 0 errors; `batches.py check` 0 problems. Then phase 7.
- **Done (phase 6, this session):** `tools/batches.py` (skill asset adapted: lint widths, \n escaping, wrap,
  `<@N>` columns, selftest in `tests/test_batches.py`), glossary rulings + ~50 terms, D10 (source-word names),
  D11 (batch policy), `docs/style-reference.md`, `docs/translator-brief.md`, b001-b003 merged.
- **Done (phase 5):** VWF hook (`docs/re/font.md`), English encoder, lint, marker tour 147/147, width gate
  (`docs/re/windows.md`, `docs/re/budgets.tsv`: 152 measured rows; registers `{%sRn}` = 64 px). `%` can't be text.
- **Done (earlier phases):** recon (`docs/re/`), debug warp (`tools/debug/warp.lua`, 147 scenes), identity build,
  extract (`script/`: 2824 messages `sSSS.KK`, 2712 strings `tOOOOOO`; 5305 todo, 159 keep, 72 data).
- **Later phases need:** name entry (phase 7): keyboard rows (`data` entries, table 0x0D21F0) need an English
  layout with the 8-char limit; English species names <= 64 px and <= 16 bytes; the address DB reader (record
  sizes 16/10/20 bytes). Graphics text: ポーズ, opening movie spec panels, menu bar / item submenu / form labels
  (docs/re/graphics.md), and the **staff roll** (mode 22): its kana are not SJIS, find their encoding or tiles.
- **Known debug-tool gaps (non-blocking):** field battle placement has no known "done" input; the debug menu's
  BATTLE START (`dbg_battle`) reaches a real battle. Runs without `--sav` share `tools/mesen/Saves/<rom>.sav`.
  Warp `intro` reaches script 1 at ~f3000 (form + title first): use `--frames 6000`.
- **Memory:** the host's AWPerformance.SCSubAgent (Dell service) held 3-7 GB; run tours one emulator at a time.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
