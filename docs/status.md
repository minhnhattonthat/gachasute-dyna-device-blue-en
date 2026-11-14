# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate in progress: all 45 batches merged (5285 done, 179 keep, 72 data, 0 todo); review
  pass running (`tools/pairs.py` -> `work/review/pairs/`, `sh tools/review_run.sh` -> codex exec read-only,
  reports in `work/review/reports/gNN.md`; brief `docs/reviewer-brief.md`).
  Last build: `build/dynadevice_blue_en.gba` 2026-11-15 (all batches), sha1 68d1683b..., smoke ok; pilot seen in game
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
- **Choice lines verified in game** (scene `choice_s37`, `work/qa/p6_s37/sheet.png`): `<@5>Yes<@11>No` puts the
  cursor just left of "Yes"; `<@N>` columns work as designed.
- **Debug-tool bug found (fix before phase 8):** every `menu`/`fscript`/`dmode` scene (38) replays the timed
  `tutorial_route.txt`, which desyncs on the English build (pages differ). The route start is now synced to the
  script-10 nag (warp.lua), which gets through the Gachasute walk, but it still loops later (script 365 in room 3,
  `work/qa/p6_choice6`). Fix idea: replace timed waits with event-driven segments (wait for SCRIPT n / room), or
  finish the tutorial on the original ROM, save in game, and start these scenes from that .sav (text-independent).
- **Next:**
  1. Review pass: read each `work/review/reports/gNN.md`, fix Critical/Important in script/ (Edit tool;
     `python -X utf8 tools/batches.py check` and `tools/check.py` after), Minors to `docs/polish.md`. Codex's
     Windows read-only sandbox can't start a shell, so `review_run.sh` pipes brief + glossary + style + pairs on
     stdin. Never `taskkill /IM codex.exe` (other sessions' codex): kill by PID.
  2. Phase 7 (name entry): t0B7FE4-t0B8044 (ｇｎｙｃｕｓ＜☆↓＋ ... ｓｅｒｕｓｐｅ▽＞％, pointers 0x0D1EA8-0x0D1ED8,
     next to the keyboard table) look like a keyboard grid; set to status keep for now, decide with the
     keyboard layout. `tools/width.py "text" ...` prints a line's pixel width.
  3. After all batches: review pass (fresh read-only, per file group, `assets/reviewer-brief.md`), Minors to
     `docs/polish.md`; `tools/lint.py` 0 errors; `batches.py check` 0 problems. Then phase 7.
- **Done (phase 6, latest session):** b044-b045: combo Extra names (Earth Rai, Bomb Mist...), status-ailment
  words, link-battle rules and messages, Dyna Database labels, Dyna menu `<@2>Take<@10>Status<@18>Free`
  ("Release" too wide), minigame help (3 games). Blanks t0BAAB0/t0BAF84 kept. Notes in `docs/polish.md` "b044-b045".
- **Done (phase 6, session before):** b042-b043: item/PDA/calendar/blood type/money diary, link-trade panels,
  Card Trade messages, Dyna Pad jukebox names, party/City help, field build menu, item-use messages, debug
  menu strings. Code checked: weekday row t0B8254 is copied 6 bytes a day (0x0801FFA4), calendar digits 4
  bytes a day (0x0802914C): both kept in shape. In-game checks listed in `docs/polish.md` "UI strings to look
  at in game". `tools/budgets.py` ID_WINDOW: t0B8150/58 and t0B9D9C/DE0 are now "guess" rows.
- **Done (phase 6, session before):** b038-b041: all Database help pages (keywords, sectors, elements, Extras,
  ability types, style rarity, the 5 profile pages of every style). Line patterns in glossary "b038-b041". The
  per-line glossary check forces each fragment to carry its own term, so pages are written line by line.
  Phase 8: look at a few help pages in game (Database > keyword list), e.g. Extra and a style's food page.
- **Done (phase 6, session before):** b029-b037: armor/weapon/food/material descriptions (parts pattern reworked
  in b028: "Igarm types and" / "Zero-E types'" / "dedicated Devices" / "need this part."), device names, star
  and constellation names, Extra weapon names, skills, items, gossip word lists, nicknames, keyword names.
  Glossary sections b029-b036 hold every name decision. 64 px cuts and unsure names listed in new
  `docs/polish.md`. Keyword list names t0B539C-t0B5618 re-budgeted 64 -> 96 px (`tools/budgets.py`: their only
  pointers are the keyword table 0x0D0008 and help pages). `desc_view.py` covers the help pages.
- **Done (phase 6, session before):** b024-b028 (shops, Colosseum/Ranking Battle prizes, Factory, regular
  reports and city ranks, tournament, travelling merchant, challengers, G-Force, link messages, sector types,
  first description fragments). New terms in glossary (Hall of Fame, Hero's Crown, Draco style, the 10 body
  types). Sector-type field header: the code right-aligns it at col 13 (0x0804E4E6), budget raised 32 -> 56 px;
  **phase 8: look at the "Mega House" / "Colosseum" header** in the field build menu. `tools/desc_view.py` added.
- **Done (phase 6, session before):** b018-b023 (resident tips and gossip in 4 voices, monthly talk, item
  requests/trades, Dyna Center menus, auction). `tools/batches.py` now rejects a/an right before a register.
- **Done (phase 6, session before):** b011-b017 (story end, post-game Navyu, battle/system messages, item use,
  resident Dyna tips). The original's stray `{%}` in s341.00 (a typo that eats 3 bytes) is dropped in English;
  `tools/lint.py` and `tools/batches.py` no longer require it.
- **Done (phase 6, earlier session):** `tools/batches.py` (skill asset adapted: lint widths, \n escaping, wrap,
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
