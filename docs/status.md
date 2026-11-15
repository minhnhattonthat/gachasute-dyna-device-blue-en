# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress (text coverage 1952/5536, script sweep to resume past s451;
  field menu + profile form graphics done). Phase 7 done 2026-11-15. Last build: `build/dynadevice_blue_en.gba`
  2026-11-15 (form graphics), sha1 ce7675b7..., smoke ok, 53 tests ok, lint 0/0 (138 strings wider than JP under
  guessed budgets: `lint.py --guess`, `docs/review/guess_wide.txt`).
- **Latest session (2026-11-15, worker 3):** name-entry keyboard (OBJ block 020BDD4) in English: tabs Hira / Kata /
  ABC / 123 / Sym / Kanji, START "OK", SELECT "CONVERT", Prev Page / Next Page (`gfx_text.py` "redraw" boxes for
  outlined art; scenes `keyboard_select`, `keyboard_kanji` = boot keyboard + a route after `|`). Coverage sweep 4
  (`cover.py scripts --jobs 2`, log `work/qa/cover/sweep4.log`) was **left running in the background** at s472 when
  this worker handed off (context limit): if `work/qa/cover/m1/` keeps growing, let it finish; if no Mesen runs
  `cover`, rerun the same command (finished runs are skipped), then `cover.py report`.
- **Session before (2026-11-15, worker 2):** profile form labels (Name, Nickname, Gender, Address, Home Tel.,
  Mobile Tel., Email, Birthday, Blood Type; block 020EB44) and the registration popup (OBJ block 02124B4) in
  English (`work/qa/gfx_en/form*/`); notes in docs/re/graphics.md "Profile form". New `tools/bgmap.py` (which
  screen cells of each BG show a block's tiles, from a ppu dump; `--full` for the whole map), scene `form_scroll`,
  gfx_text rows take an alignment (`left`/`right` for a word split by shared tiles or OAM gaps, `tight`) and
  per-atlas `ink`/`bg`. Coverage sweep run 3 reached s451 (stopped by me to hand off; finished runs are kept).
  Remember: `regen.py` defaults to the ORIGINAL ROM; pass `--rom build/dynadevice_blue_en.gba` for English shots.
- **Session before (2026-11-15, worker):** field menu bar + every submenu (System/Items/Party/Residents/Database)
  English in game (`work/qa/gfx_en/*/hold.png`): `tools/gfx_text.py` draws labels into `gfx/01E30D4.png`,
  `gfx.MAP_PATCHES` re-lays 3 SCR rows (docs/re/graphics.md "Field menu bar"). `cover.py scripts` now skips
  scripts with a finished run at that masha (`--redo` forces): the s001-s391 runs are kept, the next resume starts
  past them. VRAM dumps beside a scene: `regen.py SCENE --probe tools/lua/ppu_every.lua`.
- **Text fixes go through fix batches:** `work/tl/rNN.tsv` (ids) + `rNN.out.tsv` (id TAB paragraph, `{KP}` between
  pages, no `\n` unless a choice line), `python -X utf8 tools/batches.py merge rNN --overwrite`. Last: r05.
  Messages are paragraphs; `batches.wrap` fills 188/176 px, 2 lines a page, and balances the lines (no widows).
  `tools/show.py ID..` prints entries; `tools/width.py "text"` a line's px. Re-review: `tools/pairs.py`, then
  `sh tools/review_run.sh NAME:NN` (codex exec, inputs on stdin); triage under the report in `docs/review/`.
- **Phase 7 checks (keep them green):** `tools/romwrite.py` (every build write logged; build fails on wrong
  original bytes, overwritten/overlapping writes, unlogged bytes, or a write outside `tools/allowed_ranges.txt` +
  the extracted pointer words); `tests/test_romwrite.py` (English build passes the gate, every string with English
  written, no stale pointer to a moved string, no branch into the VWF hook span); lint stub-last-line rule.
  `jp_left.py build/... --sjis --gba-ptrs --known tools/jp_known.txt`: 6 runs left, all in the address database
  (0x44C754-0x702BB4, see "Waiting on the user").
- **Choice lines verified in game** (scene `choice_s37`, `work/qa/p6_s37/sheet.png`): `<@5>Yes<@11>No` puts the
  cursor just left of "Yes"; `<@N>` columns work as designed.
- **Debug tool (fixed 2026-11-15):** `menu`/`fscript`/`dmode` scenes continue from `work/states/tutorial_jp.sav`
  (warp.lua `CONT=1`; make it with `tools/debug/mksave.py`, original ROM, ~5 min) instead of replaying the timed
  tutorial: 38/38 reached on the English build, ~1.7k frames each. Boot with a save: date, fortune (きょうの
  うんせい), PDA home (Planet OS: アドレス/ダイナデバイス/データセーブ, 予定/用事 labels), title (Start), field.
  regen.py runs each job on its own ROM copy (`work/qa/warp/_roms/`) with a fresh `--sav` (an erased flash for
  the rest), and the textcover probe; the build writes `build/strings.tsv` (tools/strings_tsv.py).
- **Next (phase 8, done-when in SKILL.md):**
  1. Text coverage, in progress. `tools/debug/cover.py`: `scripts` = one hijacked-script run per message script
     with an unshown message (warp kind `script`, from savestate `work/states/cov_pre.mss` taken just before script
     1, MASHA=1, stops after 300 idle frames: ~15 s a run, logs `work/qa/cover/m1/sSSS/`); `report`; `waive`
     (auto rows in `docs/text_unshown.tsv`: data, blank, kept format/debug strings, 133 rows). The first sweep was
     **stopped by Claude Code for low system memory** after 322 scripts (other projects' Mesen runs share the
     machine): **1735/5536 shown or waived** (1555 messages, 2246 strings left). The second sweep (2026-11-15)
     was stopped the same way after reaching s391: **1792/5536** (1498 messages, 2246 strings left); run it with
     `--jobs 1` when memory is short (2026-11-15: 1.8 GB free, 3 Mesen of another project running). Third sweep
     (`--jobs 2`, 3.9 GB free, ~1.5 scripts a minute) stopped at s451: **1952/5536** (1336 messages, 2248 strings
     left; scripts go up to s833, so expect a few hours: start it in the background first thing). Resume:
     `cover.py scripts --jobs 1` (scripts with unshown messages and no finished run; the build is newer than
     `cov_pre.mss`, so it first remakes that state, a few minutes); then `--masha 2` (Down+A: second choice) for branches.
     Strings: `tools/debug/cover_tables.py --unshown` groups them by pointer table. Keyword list entries show
     when their story flag is set (table 0x080D0008 +4, flags 2 7 18 20 22 33 34 35 68): menu scenes now take
     `flags N=V .. | route` (warp.lua) for an all-keywords Database scene (A on each entry, help pages). Then
     item/Dyna/Device lists, Database style pages, shops. Then the original ROM tour for reviewers.
     Earlier: full regen 149/149 scenes on the English build (`work/regen_en.txt`).
     Graphics text seen still JP: menu bar, PDA home labels, fortune box, title logo (docs/re/graphics.md rows).
  2. Tours through changed scenes with contact sheets, `qa_gate.py init/check`, verdicts by a fresh read-only pass
     (no subagents in Orca: do it yourself or `codex exec`). Text coverage (`textcover.py`), `inkbox.py` on every
     choice and centred menu box.
  3. Graphics text (`docs/re/graphics.md`). **Field menu (01E30D4) and profile form (020EB44 labels, 02124B4
     popup) done**; form leftovers: おわる button, two tiny boxed words 7,17-24 of 020EB44, the other 02124B4
     sentences (PDA address book). **Name-entry keyboard 020BDD4 done** (tabs, START OK / SELECT CONVERT, page
     buttons; `gfx_text.py` "redraw" boxes for outlined art; docs/re/graphics.md). Next rows: 020B0F4 (なまえ/ばしょ/すること/イベント/カスタム: PDA schedule headers), PDA home labels, fortune box,
     title logo, then the sheet rows. Same method: regen the scene on the
     original ROM with ppu_every.lua, find the BG map (search ROM for the u16 tile sequence: menu maps were raw
     `SCR\0` blocks after the palette), add an ATLASES entry to gfx_text.py. Older notes: **Pipeline (2026-11-15):** every ECD block is reached through
     archive 0 at 0x0E7FA4 (docs/re/compression.md "Pointers"); `tools/gfx.py` exports a block to PNG and
     `gfx.apply` (called by build.py, a no-op until `gfx/<OFFSET>.png` exist) writes edited art in place or
     relocates it (tests/test_gfx.py). Pilot = field menu bar 01E30D4: its BG0 tile lists per button are in
     docs/re/graphics.md "Field menu bar". Next: a label generator (`tools/gfx_text.py`: label = atlas tile
     grid + English text, drawn with fonts/vwf8.txt in ink index 1 at y 3-9 of each 16 px band), System / Items /
     Party / Residents / Database, build, warp `menu` + `menu_items`, zoomed shot. Then the submenu words (atlas
     rows 2-4: dump `menu_items`, `menu_party`, `menu_save` with ppudump for their tile lists). Others: ポーズ, opening movie spec panels, menu bar / item submenu / form labels,
     name-entry keyboard tabs + field labels (かな/カナ/ABC..., なまえ/ニックネーム/せいべつ, START けってい; scene
     `keyboard`, `work/qa/p7_kb/hold.png`), staff roll (mode 22, kana not SJIS).
  4. In-game checks listed in `docs/polish.md` (r06 field pads, the 138 guess-budget strings, s468 R5 width,
     calendar weekday row "Sun", Dyna Database "Element: thunder",
     field build headers, help pages, link panels...). Timed cutscenes: English pages must finish typing.
  5. Name entry (D12): full-width Latin pages kept; check a typed name round trip (form -> messages -> save/load).
     t0B7FE4-t0B8044 (ｇｎｙｃｕｓ..., pointers 0x0D1EA8-0x0D1ED8) are still `keep`: find what shows them.
- **Done (phase 7, this session):** phase-6 review fixes (r03: s438-s440 combos, t0BB224 "Element: {%sR0}";
  glossary weekdays Sun..Sat, D13; g09 Critical none; codex re-review of r01+r03 in `docs/review/r03.md`, its
  items fixed as r04); romdiff gate + tests; balanced wrap (r05, 1620 messages re-laid out, 376 widows gone);
  lint warnings 322 -> 0 (messages' `{KP}` count no longer warned: they are re-paginated paragraphs).
- **Review notes:** never `taskkill /IM codex.exe` (other sessions' codex): kill by PID.
- **Done (phase 6, last session):** fix batch r02 (s437.02-.09 combos "when X and Y Extras come back to back";
  activity register verb "enjoying {%sR5}" / "warms up with {%sR5}" / "lose all interest in {%sR4}"; t0B57EC
  `the "none"`). 31 review Minors added to `docs/polish.md`. t0BB224 "Elem." and t0B8254 weekdays stay in polish.md.
- **Done (phase 6, session before):** b044-b045: combo Extra names (Earth Rai, Bomb Mist...), status-ailment
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
- **Later phases need:** name entry decided (D12: game's full-width Latin pages, 8 chars = 64 px; every Dyna,
  type and name-list string is <= 64 px and <= 16 bytes, checked phase 7); the address DB reader (record
  sizes 16/10/20 bytes). Graphics text: ポーズ, opening movie spec panels, menu bar / item submenu / form labels
  (docs/re/graphics.md), and the **staff roll** (mode 22): its kana are not SJIS, find their encoding or tiles.
- **Known debug-tool gaps (non-blocking):** field battle placement has no known "done" input; the debug menu's
  BATTLE START (`dbg_battle`) reaches a real battle. Runs without `--sav` share `tools/mesen/Saves/<rom>.sav`.
  Warp `intro` reaches script 1 at ~f3000 (form + title first): use `--frames 6000`.
- **Memory:** the host's AWPerformance.SCSubAgent (Dell service) held 3-7 GB; run tours one emulator at a time.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
