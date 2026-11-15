# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress (coverage masha-1 sweep done, masha-2 sweep running; field menu,
  profile form, keyboard, PDA home + wheel / address book / calendar / money diary / calculator / memo / timetable
  / save dialog / link menu / link check / title screen / Customize Dyna / Team Setup / Place Dyna / minigames /
  Dyna get + naming / battle results / fortune box / item shop / Dyna Center / auction / device list / dev status /
  free battle / resident map / card trade / tactics battle board / staff roll done). Phase 7 done 2026-11-15. Last
  build: `build/dynadevice_blue_en.gba` 2026-11-15 (worker 15), sha1 a5a5c9a7..., check.py ok (58 tests), lint
  0/0 (137 strings wider than JP under guessed budgets: `lint.py --guess`, `docs/review/guess_wide.txt`).
- **Latest session (2026-11-15, worker 15, handed off at the context budget):** **Staff roll in English** (docs/re/
  graphics.md "Staff roll"): OBJ charset 0432534 + the PAT at 0x432D44 (11 cards); new `tools/credits.py` draws
  an English charset and a new PAT that gfx.apply writes into free space (archive word 0x0EFEB4); names Western
  order, Hepburn (D1/D2). Seen in game over the whole roll: `work/qa/credits_en/` (f*.png every 300 frames).
  `gfx.distinct` looped for ever on a PLT with 8+ repeats (that is why `gfx.py export 0432534` hung): fixed + test.
  **Survey finished** (111/111 + credits_mid/gameover in `work/qa/survey_c/`); `blockscan.py --all` over all of it
  is in `work/qa/blockscan_all.txt`; triage (greyscale sheets of every not-redrawn block): all art except
  **0215E74** (PDA calendar charset: gradient 16x16 年 月 ( ) の 予 定, weekday kanji 日月火水木金土 at y48 x144+,
  boxed 無し / 毎週 / 月 / 年 at y96, a small yellow おわる box at y24 x136) and **021C414** (money diary: ( ) 日月火
  水木金土, small 年). Seen JP on the English build (fresh shots in `work/qa/warp/`): calendar header "2000年 0月" +
  weekday row, money diary "12月31日 (土)", errand screen red おわる button. Note 月/日 double as date units and
  weekdays in 021C414: check whether the code uses the same tile before choosing "/" (the errand screen already
  shows dates as 2000/00/00). New polish line: money-diary week-view weekday words clipped. **Careful:**
  `regen.py` defaults to the ORIGINAL ROM and writes `work/states/`: always pass `--rom build/dynadevice_blue_en.gba`
  (this worker overwrote 9 states that way and re-made them on the English build). masha-2 sweep (pid 25948) still
  running, 152 runs in `work/qa/cover/m2/`; `cover.py report` at hand-off: 2524/5536 shown or waived.
  Next: redraw 0215E74 / 021C414 kanji + おわる, then the old graphics rows left (01EA6B4, 01EE624 r6-7, 024D4B4
  buttons, all unseen), then phase-8 steps 2, 4, 5.
- **Session before (2026-11-15, worker 14):** masha-2 sweep still alive (pid 25948, 100 runs in `work/qa/cover/m2/`;
  same rule as below). **Tactics battle board reached and in English** (docs/re/graphics.md "Tactics battle
  board"): debug TACTICS SYSTEM with one monster (the A on MONSTER NUMBER is what makes TACT START work); new
  scenes `tact_place`, `tact_confirm`, `tact_cmd`, `tact_enemy`, `tact_move`, `tact_status` (shots in
  `work/qa/gfx_en/tact_*`). 025E304 titles Move Dyna / Select Command / Enemy Area + L/R words Status / Back /
  Enemies (PAT patches in `gfx.MAP_PATCHES`, test `test_battle_board_titles_have_their_own_tiles`); battle commands
  are block **025D924** (the sweep table said 0250924): Attack / Scout / Cure / Move / Special. New
  `tools/pat.py` lists PAT sprite frames (the quickest way to a sprite title's layout). **Link-only blocks drawn,
  unseen** (no cable in Mesen; TSBTL debug menu stops at TSUSIN MODE SELECT): 03B7F64 Turn N + Joker / King /
  Queen / Jack / Ghost, 024AF04 Item Trade, 024B834 Dyna Trade + Your / Their / Items / Dyna (layouts from their
  PAT frames). Graphics rows left: 01EA6B4 (unseen small words), 01EE624 r6-7 and 024D4B4 buttons (unseen); then
  the ppu_every survey of the other `scenes.tsv` scenes + `blockscan.py --all`, chapter cards, game over, credits,
  phase-8 steps 2, 4, 5. **Survey started at hand-off** (background job of this worker's shell, original ROM, 111
  scenes in `work/qa/survey_todo.txt`, log `work/qa/survey_run2.log`, dumps into `work/qa/survey/<scene>`, states
  kept out of `work/states/` via `--states work/qa/survey/_states`): when its log says "N/111 scenes reached" (or
  no regen.py runs), run `python -X utf8 tools/blockscan.py work/qa/survey/* --all` and redraw every JP block it
  lists that is not in `gfx/` (rerun the same regen command for scenes missing a dir; finished ones can be
  skipped by trimming the list). Never run a survey without `--states`: it overwrites `work/states/` with
  original-ROM states.
- **Session before (2026-11-15, worker 13, handed off near the context limit):** masha-2 sweep still alive (pid
  25948, `work/qa/cover/m2/` 98 runs; same rule: if no python runs `cover.py`, rerun `cover.py scripts --masha 2
  --jobs 1`, then `cover.py report`). **In English, seen in game** (`work/qa/gfx_en/<scene>/hold.png`): 01ECD84
  Item Auction header + small words (Start / Price, Funds, Device + Name, Element, Equip / Arms + shared Type),
  01EE624 Dev. Status + Project, 01EFFF4 Free Battle, 01F4284 Zoom Out / Zoom In / Resident Dyna, 024D4B4 Card
  Trade header, 024C1C4 Address Data / Dyna panels. gfx_text redraw boxes take "right" as the 9th item.
  `blockscan.py --all` over the 32 survey scenes: every other block they show is art / digits / an 8bpp map (no
  JP), so those scenes are clean. **Graphics rows left** (graphics.md Rows without gfx/*.png, charsets aside):
  0250924 battle commands (ていさつ / いどう / とくしゅ / こうげき: field battle board, scene unknown), 03B7F64
  turn counter (だい N ターン: during a battle), 01EA6B4 small つれていく / データをみる / にがす (unseen),
  024AF04 / 024B834 link trade (need a partner), plus unseen small words in 01EE624 r6-7 and 024D4B4 buttons. Then
  a ppu_every survey of the rest of `scenes.tsv` (153 scenes not surveyed) + `blockscan.py --all`, chapter cards,
  game over, credits (mode 22), and the phase-8 steps 2, 4, 5 below.
- **Session before (2026-11-15, worker 12, handed off near the context limit):** masha-2 sweep still alive (the
  worker-11 job, `work/qa/cover/m2/` 88 runs; same rule: if no python runs `cover.py`, rerun `cover.py scripts
  --masha 2 --jobs 1`, then `cover.py report`). New **`tools/blockscan.py DIR..`**: which graphics-text blocks
  each scene's ppu dumps hold (own tiles only); a 32-scene survey on the original ROM (`work/qa/survey/`) maps
  the remaining JP blocks to scenes (docs/re/graphics.md "Scene scan"). **Fortune box 0231524 in English** (new
  scene `fortune`: boot kind, regen.py gives it tutorial_jp.sav; `gfx.FORTUNE_ROWS` re-lays the BG1 SCR
  0x234034; test `test_fortune_labels_have_their_own_tiles`). **Item shop 01EB9E4** Buy Items / Sell Items,
  **Dyna Center 01EAA04** Stored Building Kits / Treat Dyna (`gfx.PLT_FOR` stand-in palette for the 01EA6B4..
  01F4284 group). Next graphics, scenes known: 01ECD84 (`d_auction`, `d_shop_list`), 01EE624 (`d_dev_status`),
  01EFFF4 (`dbg_colo_free`), 01F4284 (`dbg_world_map`), 024C1C4 + 024D4B4 card trade (`mode_card`); unseen:
  01EA6B4, 0250924, 03B7F64, 024AF04 / 024B834 (link trade); then `blockscan.py --all` over every scene for
  blocks not in the Rows table.
- **Latest session (2026-11-15, worker 11, handed off near the context limit):** the masha-2 sweep had died
  again (49 runs): restarted (`cover.py scripts --masha 2 --jobs 1`, log `work/qa/cover/sweep_m2c.log`, 67 runs in
  `work/qa/cover/m2/` at hand-off; a background job of this worker's shell: next worker, if no python runs
  `cover.py`, rerun it, then `cover.py report`). **Dyna get / naming 0203D14 in English** (mode 45 + A presses
  walks the 0x080D2B48 state machine; scenes `dyna_new` = NEW! panel: Type / Style / Element, "This is your
  first Dyna of this style & element!"; `dyna_name` = "Please give this Dyna a name." over the keyboard).
  **Battle results 03B9D84** (scene `d_get`): Results, Dyna Left, Wipeout Turn, Win / Lose / Draw. New
  `tools/blockfind.py DUMP_PREFIX` lists the IMG blocks a ppu dump shows: the quick way to find a screen's block
  (`regen.py SCENE --out D --probe tools/lua/ppu_every.lua`, then blockfind on the last dump). gfx_text redraw
  boxes take a 9th item "left". Still JP, noted: the naming keyboard's R box "あぁ" (small-kana toggle) is not
  in 020BDD4 or any string (likely the charset 0215E74). Debug battle (`dbg_battle`) has no tile-drawn JP: the
  command menu 0250924 is on another battle screen (field battle board?). Next graphics: 0250924, the rest of
  025E304 (placement states), 020B0F4's screen, fortune box, 01E9764 full-inventory popup, the remaining sheet
  rows (01EA6B4.. 01F4284, 024AF04.. 024D4B4 link trade, 03B7F64 turn counter); a scan of every scene with
  ppu_every + blockfind would list JP blocks not yet in `gfx/`.
- **Session before (2026-11-15, worker 10):** the masha-2 sweep had died after 6 runs: restarted (`cover.py scripts
  --masha 2 --jobs 1`, log `work/qa/cover/sweep_m2b.log`, a background job of this worker's shell: next worker,
  if no Mesen of this repo runs `cover`, rerun it, then `cover.py report`). **Minigame graphics in English**
  (docs/re/graphics.md "Minigames"): blocks 03D5DB4 + 03D7FD4, 27 SCR rows re-laid by `gfx.MINI_ROWS`
  (title Game Start / Quit / High Score / R Button How to Play, level select Which level? / Level 1-3 / 00m 00s,
  help header + Controls / Rules / D-Pad / A Button / B Button / Start, HUD Score / Time Left, Start!, Game Over,
  Give up? A=Yes B=No); results words drawn but unseen (need a scoring run). Text fix r08: t0BB4FC "(The timer
  won't stop.)". New scenes `mini_help`, `mini_help_b`, `mini_start`, `mini_play`, `mini_pause`, `mini_giveup`,
  `mini_long`; test `test_minigame_words_have_their_own_tiles`. Next graphics: the rest of 025E304 (placement
  states: add scenes), 0203D14 Dyna naming, battle 0250924, 020B0F4's screen, fortune box, 01E9764 full-inventory
  popup, then the remaining sheet rows (01EA6B4.. 01F4284, 024AF04.. 024D4B4 link trade, 03B7F64 turn counter).
- **Session before (2026-11-15, worker 9, handed off at the context limit):** sweep 9 had died at s728: sweep 10
  finished the masha-1 pass (**2522/5536 shown or waived; 778 messages, 2236 strings unshown**, `cover.py report`).
  **Masha-2 sweep started** (`cover.py scripts --masha 2 --jobs 1`, log `work/qa/cover/sweep_m2.log`, a
  background job of this worker's shell: next worker, if no Mesen of this repo runs `cover`, rerun the same command
  (finished runs are skipped), then `cover.py report`). Graphics (docs/re/graphics.md "PDA screens", worker 9):
  PDA wheel labels all seen (scenes `pda_up*`, `pda_down4`); **timetable 022CF64** (logo, Mon..Sat, "Pick a
  Subject", "Erase One", status line "Mon, period 1 = [icon]" via PAT x patches `gfx.tt_patches`, subject icons
  as 3-letter abbreviations, **D15**); **Customize Dyna** title 01E9764; **Team Setup** title 03B29B4 + menu
  Add/Swap / Remove / Done (03B25A4, SCR 0x3B2854 re-laid); **Place Dyna** title 025E304. Fixed a palette bug:
  repeated PLT colours turned drawn indices into others on the PNG round trip (`gfx.distinct`; `gfx_text.render`
  now asserts the round trip). New: `tools/pxdump.py` (palette indices of a block region), gfx_text fonts `tall` /
  `tallb`, list ink = per-box gradient, segment boxes. Next graphics: minigames (03D5DB4 charset + maps, 03D7FD4
  help header; scene `mode_minigame_a`), the rest of 025E304 (placement states: add scenes), 0203D14 Dyna naming,
  battle 0250924, 020B0F4's screen, fortune box.
- **Session before (2026-11-15, worker 8):** sweep 8 had died with its worker (631 dirs): restarted as **sweep 9**
  (`cover.py scripts --jobs 1`, log `work/qa/cover/sweep9.log`, 702+ dirs at hand-off; same rule: if no Mesen of
  this repo runs `cover`, rerun it, then `cover.py report`). Free RAM was 0.8 GB (other projects' Mesens).
  **Title screen 0449734 in English** (docs/re/graphics.md "PDA screens" title entry): Emblem, ©2002 SMILESOFT,
  PRESS START, all 10 planet names (title PAT frame entries patched: `gfx.TITLE_NAMES` / `title_patches`, range
  44C0A0-44C309 added to allowed_ranges). New: `tools/title_frames.py` (all 10 name frames from a build),
  `tools/lua/shotwhen.lua` (shots once a tile is in OAM: blinking sprites), `tools/lua/oamword.lua` (who writes
  an OAM attribute value), `tools/lua/animframe.lua` (sprite objects' PAT frame data). Sprite drawer 0x0800169C:
  object +0x18 = PAT base, +0x24 = frame, +0x38 = tile base. Next graphics: 020B0F4's screen, the Dyna Device app
  menu (0208654 labels), timetable mode 8, then the sheet rows (01E9764.. menus, 0203D14 Dyna naming, 03D7FD4
  minigame help, battle 0250924 / 025E304, team 03B25A4 / 03B29B4).
- **Session before (2026-11-15, worker 7):** sweep 7 had died with its worker (598 dirs): restarted as **sweep 8**
  (`cover.py scripts --jobs 1`, log `work/qa/cover/sweep8.log`, 624+ dirs in `work/qa/cover/m1/` at hand-off; a
  background job of this worker's shell: next worker, check whether a Mesen runs `cover`, else rerun the same
  command, then `cover.py report`). Graphics (docs/re/graphics.md "PDA screens"): PDA Save Data dialog 020A4D4
  (scenes `pda_save`, `pda_saving`), Link menu 0249C44 (`pda_link`; new `vwf2` doubled font for big titles),
  link check screen 03B3624 headers + 03B3164 status words (`pda_link_battle` / `_card` / `_item` / `_dyna`: no
  cable needed). Title block 0449734 surveyed, not drawn (graphics.md "Title block": emblem label, planet names,
  copyright, Press Start; the logo itself stays JP per D5). Next graphics: title block, 020B0F4's screen, the Dyna
  Device app menu (0208654 labels), timetable mode 8, then the sheet rows (01E9764.. menus, 0203D14 Dyna naming,
  03D7FD4 minigame help, battle 0250924 / 025E304, team 03B25A4 / 03B29B4). Link trade screens need a partner.
  New `tools/oam.py DIR|DUMP_PREFIX`: visible sprites of a ppu dump (tile -> r/c for 2D OBJ mapping).
- **Session before (2026-11-15, worker 6):** sweep 6 had died with its worker: restarted as **sweep 7**
  (`cover.py scripts --jobs 2`, log `work/qa/cover/sweep7.log`, a background job of this worker's shell, so it
  dies when the worker ends: next worker, check `work/qa/cover/m1/` (597 dirs at hand-off) and rerun the same
  command, then `cover.py report`). Graphics (docs/re/graphics.md "PDA screens", worker 6): address book 02124B4
  (tabs, "Add Address", Select / Erase, delete prompt drawn but unseen), PDA home + app labels **0208654**
  (Address, DynaDevice, Save Data seen; Schedule, Money, Calculator, Timetable, Music, Link, Minigame, MEMO on
  the Dyna Device app menu, unseen), headers **0206CF4** "Plans" / "To-do". New: `tools/lua/vramwrite.lua`
  (who writes an OBJ VRAM range), warp `form|ROUTE`, scenes `pda_addr_del`, `form_start`; gfx_text "redraw"
  items take an optional own clear set; MINI has M. Next graphics: the Dyna Device app menu (find its mode: the
  0208654 labels, check the assumed tile runs), timetable mode 8, the form popup's page 2 (02124B4 rows 8-10),
  fortune box, title logo, then the sheet rows (graphics.md table). PDA home date panel shows "20-- 0C / 0- 0 Fri"
  on a cold boot (no date set): check it with a save before calling it a bug.
- **Session before (2026-11-15, worker 5):** sweep 4/5 had died (empty log); restarted as **sweep 6**
  (`cover.py scripts --jobs 2`, log `work/qa/cover/sweep6.log`), at s566 of s833 when this worker handed off
  (context limit): same rule (if `work/qa/cover/m1/` stops growing and no Mesen runs `cover`, rerun it, then
  `cover.py report`). Graphics (docs/re/graphics.md "PDA screens"): money diary 021EAA4 (the table said 021EA44),
  calculator 02280B4 (`grad` option: per-row inks), memo 0225EC4 + its BG index tabs in 020EB44 (new gfx_text
  "screens": redraw a BG map strip in screen coords; D14 romaji initials A K S T N H M Y R W). Text fix r07:
  money-diary panel t0B924C "Month" (4 tiles; "This month" ran into "Left"), budget class 0x0B924C-0x0B9260 = 32
  measured. New scenes `pda_money_r`, `pda_money_rr`. Next graphics: address book 02124B4 (tabs: copy the 0225EC4
  tab boxes after checking its ink indices with a dumpidx-style print; アドレスのついか R band x2; セレクト
  データをけす buttons x2), timetable mode 8 (時間割 logo, 月..土, ひとつ けす band, subject icons), the faint
  delete prompts (021EAA4 / 0219CB4 / 0225EC4 / 02124B4, ink 7). Tip: OAM listing = decode `ppu_*.oam.bin`
  (OBJ tile 480 + 32*row + col for these PDA blocks); BG tiles: render the BG from the dump to see which layer.
- **Session before (2026-11-15, worker 4):** sweep 4 had died at s473 (no Mesen running): restarted as sweep 5
  (`cover.py scripts --jobs 2`, log `work/qa/cover/sweep5.log`), at s492 when this worker handed off; same rule as
  below (if `work/qa/cover/m1/` stops growing and no Mesen runs `cover`, rerun it, then `cover.py report`). Graphics:
  PDA calendar header 0219CB4 "Add Plan" / "Add Errand" in game; 020B0F4 tabs drawn but their screen not found;
  PDA screen survey + new scenes (docs/re/graphics.md "PDA screens"). `gfx_text.py`: `text_y` per atlas, redraw
  shadow `("ring", idx)` = full outline, fill `rowmode` (row's commonest colour, for vertical gradients).
- **Session before (2026-11-15, worker 3):** name-entry keyboard (OBJ block 020BDD4) in English: tabs Hira / Kata /
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
     Graphics text seen still JP: fortune box (menu bar, PDA home labels, title text since done; the logo stays JP).
  2. Tours through changed scenes with contact sheets, `qa_gate.py init/check`, verdicts by a fresh read-only pass
     (no subagents in Orca: do it yourself or `codex exec`). Text coverage (`textcover.py`), `inkbox.py` on every
     choice and centred menu box.
  3. Graphics text (`docs/re/graphics.md`). **Field menu (01E30D4) and profile form (020EB44 labels, 02124B4
     popup) done**; form leftovers: おわる button, two tiny boxed words 7,17-24 of 020EB44, the other 02124B4
     sentences (PDA address book). **Name-entry keyboard 020BDD4 done** (tabs, START OK / SELECT CONVERT, page
     buttons; `gfx_text.py` "redraw" boxes for outlined art; docs/re/graphics.md). **Calendar header 0219CB4 done.** Next rows: find
     020B0F4's screen (drawn, unseen: graphics.md "PDA screens"), the other PDA apps (money diary 021EA44,
     timetable, calculator, memo, address-book index tabs; all warpable by mode), PDA home labels, fortune box,
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
