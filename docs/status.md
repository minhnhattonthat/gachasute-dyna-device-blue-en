# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9. Release: done 2026-11-15 (worker 27). `python -X utf8 tools/release.py --skip-build` ran every gate
  and wrote `release/Gachasute_Dyna_Device_Blue_EN_v1.0.zip` (BPS 421674 bytes + README.txt; re-applied to a clean
  original = build). Release build `build/dynadevice_blue_en.gba` sha1 55ab465e..., CRC32 739D295D; smoke ok,
  check.py ok, lint 0/0, jp_left 0 runs (8 known), story gate 12/12, visual tour gate 197/197 + waiver for this
  text-only build, textcover 5375 shown + 161 waived, polish.md all ticked. **Published 2026-11-16:** repo made
  public (description now uses the game title), release v1.0
  (https://github.com/minhnhattonthat/gachasute-dyna-device-blue-en/releases/tag/v1.0) with the zip (sha1
  873f702d..., patch sha1 45b739e2...); a rebuild from HEAD reproduced build sha1 55ab465e, uploaded zip hash checked.
  Next: player bug reports (`gh issue list --label bug`).
- **Open (not blocking):** Address database place names kept Japanese for
  v1.0 (**D20**, known issue in both READMEs; romanizing is a v1.1 candidate). 16 round-3 story Minors deferred
  (`work/qa/story/reports/r3/`, polish.md). The last **95 strings are waived although reachable in play** (hand rows
  under "Worker 26" in `docs/text_unshown.tsv`, each with its context): item bag-full / discard messages, item-use
  results, Device help hints, keyboard word-register prompts, money diary totals, combo attack names, status
  ailments, minigame help page, Card Trade + multiplayer link lobby (link cable: can't be emulated with one Mesen),
  "Debug Mode Kai" (debug). No warp scene reaches them; 50 of them were force-drawn in a foreign text slot by
  `rotate.py --any SCENE` (logs `work/cover_any/`, kept outside `work/qa` so they never count as coverage), 45 not
  (the run was stopped for low memory). The skill wants waivers only for unreachable text: to tighten, rerun
  `rotate.py --any <list scene>` (menu_db_device / mode_shop_list / menu_party gave 10-15 each) and/or add scenes.
- **Latest session (2026-11-15, worker 27, phase 9):** **Story pass**: `docs/synopsis.md` (12 chapters by script
  range), `tools/story.py` -> `work/qa/story/chapters/`, reviewers by `sh tools/story_review.sh chNN..` (`codex exec`
  read-only, brief `docs/story-reviewer-brief.md`; no subagents under Orca). Round 1: 3 issue (Navyu contractions,
  Terry's "toy Dyna" callback s149.15); round 2: ch04 issue (s149.13); round 3: all ok. Fixes in `work/tl/r09`-`r12`
  (r09 = the 31 open (gNN) polish Minors; 109 entries in all) merged with `batches.py merge rNN --overwrite`.
  polish.md: every line ticked (fixed / verified / waived with reason). **Coverage logs are address-based**: text
  edits moved 2802 strings, so `tools/cover_remap.py` maps the phase-8 logs (all on build 7f22f56c, whose
  strings.tsv was rebuilt byte-exact from commit dfa4777 into `work/qa/cover/remap/strings_7f22f56c.tsv`) by id to
  the new layout; release.py runs it before textcover. New coverage runs on a later build need a new old-table or a
  real rerun. `tools/release.py` (from fantastic-children-en): gates, debug-off check (no marker text, mode
  dispatcher 0x4DB8 = original), BPS, re-apply, zip. README filled (base ROM hashes, status table). D20 added.
  `regen.py` defaults to the JP ROM: pass `--rom build/dynadevice_blue_en.gba`.
- **Session before (2026-11-15, worker 26):** Reran `rotate.py --run --gap 0x400` over the 131 scenes left:
  **strings 170 -> 95 unshown** (dbg_battle 31, d_center_out 6, mode_link / mode_card2 4 ...). The 95 left sit in
  code literal pools no scene draws, so new **`rotate.py --any SCENE`**: one group of every string, `ROT_WAIT`
  (no substitution before warp.lua's WARP_DONE: early ones broke the warp at the title) and `ROT_HOLD = 0` (the
  rewind chain stalled in any-mode: after arrival the scene never re-entered a hooked draw, watchdog gave up);
  one substitution per draw call, ~10-15 strings per list scene. Then waived the 95 (see Waiting on the user).
  Gate command uses `work/qa` as the log root (`work/qa/cover` alone misses 6 strings shown only in
  `work/qa/warp`). Background batches were again **stopped by Claude Code for low system memory** (~0.5 GB free).
- **Session before (2026-11-15, worker 25):** **Strings 1066 -> 170 unshown** (5366/5536). `tools/lua/rotate.lua`
  now has a **rewind mode** (`ROT_HOLD`, default 3): at the first substitution it snapshots the machine
  (`emu.createSavestate` inside the exec hook), and every 3 frames reloads it and substitutes the next sibling, for
  every group drawn since the snapshot, so one draw of a list or help page covers the whole table
  (menu_db_keyword_help alone: 878 -> 337). Snapshots only after warp.lua's `WARP_DONE` (stage "done": a rewind past
  its RAM writes stalls the warp), rewinds only after `WARP_ARRIVED` and the route is done; warp.lua waits on
  `ROT_BUSY()` before the hold shot; watchdog gives up a stalled chain (a sibling in the wrong slot can crash the
  game: hold shots of rotation runs are coverage only). New third hook **0x08013D18** (text slot setter, r2 = string):
  description boxes (item / shop / sell / DB help) take lines from the flat table 0x0BDAE8 through it. Use **`--gap
  0x400`** (joins the split description / Device-name tables). `rotate.py --redo` now moves the old log to
  `work/qa/cover/rot/_prev/<scene>-N/` (a redo overwrote menu_items_discard and lost ~46 strings before this).
  **Sweep `rotate.py --run --gap 0x400` stopped by Claude Code for low system memory** after 56 scenes (other
  projects' Mesen; ~0.5 GB free): **131 scenes left**, rerun the same command (scenes with a log are skipped; r2's
  partial log is `log.partial`). Left (`work/qa/cover/unshown_now.txt` is an older 284 list): mostly code-referenced
  UI messages (item use results 0x48xxx-0x4Axxx, Dyna Center take/release 0x090xxx, card trade 0x039xxx, link
  0x0E42xx, debug "Debug Mode Kai" 0x0554xx = waive as debug), Device names 0C2864, combo names 0D6340, status
  ailments 0E3FA4. Then scenes or waivers (`docs/text_unshown.tsv`, reason required), `textcover.py` exit 0 = done.
- **Session before (2026-11-15, worker 24):** **Message coverage done**: `cover.py msgs` sweep finished, **0
  messages unshown**; coverage 4470/5536, **1066 strings left**. Strings: UI text is copied through the expander
  0x0801328C (r1 = source) into a stack buffer before the renderer, so new **`tools/debug/rotate.py` +
  `tools/lua/rotate.lua`**: groups strings by pointer table (as `cover_tables.py`, gap 0x10, so neighbouring tables
  can join), and the probe swaps r1 (`emu.setState`) / the text object pointer for the next unshown sibling whenever
  the game draws an entry of a group with unshown strings left. The game's own code reads and draws it (often in a
  neighbouring slot: rotation shots are coverage only, not visual QA). Test `menu_db_keyword_help`: 13 strings in one
  run. `rotate.py --run [SCENE..]` runs every scenes.tsv scene one at a time, rewriting `work/qa/rotate_probe.lua`
  before each (logs `work/qa/cover/rot/<scene>`, finished scenes skipped). **Stopped by Claude Code for low system
  memory after 4 scenes** (7 Mesen of other projects, ~6 GB). Next: rerun `rotate.py --run` (check no gachasute
  Mesen/python is alive), then `--gap 0x40` pass for tables with 0 shown (they join a neighbour), then scenes or
  waivers (`docs/text_unshown.tsv`, reason required) for what's left; static screens give one rotation per draw, so
  list scenes that scroll / redraw cover most. Then `textcover.py` exit 0 = phase 8 done.
- **Session before (2026-11-15, worker 23):** English tour finished (129 left scenes; `docs/tour_left.txt` had CRLF:
  strip `\r` before passing names). **inkbox** on every choice / centred box: field submenus (01E30D4 rows are 48 px
  but the box border leaves x 3..44: "Battle Anim" 46 px and "Send Home" 44 px spilled over -> **Animation** / **Go
  Home**, margins 2/1), minigame pause box (03D5DB4: "Give up?" 36 px can't centre on the tile grid -> **Give up**
  in cells 7-11 + a 3-cell gap in "A=Yes   B=No": margins 53/53, 29/27; gfx.MINI_ROWS note). Message-window choice
  lines (`choice_s37`, `menu_save`, `tact_confirm`) are column-laid like the JP, not centred. Re-shot `menu*` and
  minigame scenes on the new build, `vqa_run.py` on the 136 changed sheets (chunks renamed `w23_*` so they don't
  overwrite the old `chunk_NNN.tsv` verdicts), second look in `work/qa/verdicts/zz23*_review.tsv` (7 false
  positives: player-typed JP names, page-spanning sentence, keyboard grid fading in, colons present, title colon).
  Coverage sweep `cover.py msgs --hold 1500 --jobs 1` resumed, **stopped by Claude Code for low system memory at
  s803** (other projects' Mesen): **4425/5536 shown or waived, 28 messages + 1083 strings left**. Next: rerun the
  same command (finished scripts are skipped; check no `cover.py` python is alive first), then the strings
  (`cover_tables.py --unshown`: item/food descriptions, Dyna/Device lists, Database help pages; ideas in worker 21's
  entry), then `textcover.py` exit 0 = phase 8 done.
- **Session before (2026-11-15, worker 22):** **Open VQA bugs (2)-(6) fixed** (verdicts in
  `work/qa/verdicts/zz_review.tsv`, shots `work/qa/fix22/`): date rows t0B90B4 / t0B8F50 / t0B98C4 spaced so the
  code-drawn 16 px digits sit in the JP cells ("2000 / 00 / 00"; lint now accepts full-width ０-９ and －, which
  encode_en keeps as game-font SJIS units), time placeholder t0B90D8 "－－:－－"; money diary week cells S M T W T
  F S (**D19**: one 8 px tile per cell, table 0x0D2614; the header "200/ 12" hiding a digit matches the JP 年);
  profile form おわる = 020EB44 tiles 7,17-24 (the "two tiny boxed words") -> Quit; `ending_full` holds at 11200
  (English ending runs longer). Found with a pixel-shape matcher (screenshot 8x8 blocks vs VRAM tiles): worth
  promoting to tools/ if needed again. Possible leftover: block 0224BA4 is a copy of the JP kana index tabs (ア カ
  サ..) loaded at the same VRAM base as 020EB44 on the form: check whether any screen shows it.
  **Both background runs were stopped by Claude Code for low system memory** (~1.2 GB free, other projects'
  Mesen running). **Text coverage sweep** (`cover.py msgs --hold 1500 --jobs 1`) reached **s620** of s833: rerun
  the same command (finished scripts are skipped). **English tour re-run on build eb9071f3**
  (`work/qa/tour/tour_build.gba`): 68/197 scenes re-shot; the 129 left are in `docs/tour_left.txt`: resume with
  `regen.py $(cat docs/tour_left.txt) --rom work/qa/tour/tour_build.gba --out work/qa/tour --states
  work/qa/tour/_states --jobs 1` (regen redoes every named scene, so pass only those). When it's done,
  `qa_gate.py init work/qa/manifest.tsv work/qa/tour --build work/qa/tour/tour_build.gba`, `todo`, review the
  changed sheets, `check`.
- **Session before (2026-11-15, worker 21):** **JP tour finished** (197/197 in `work/qa/tour_jp`). **Visual QA run
  over all 17 chunks** (`tools/vqa_run.py`, verdicts in `work/qa/verdicts/`); my second look is
  `work/qa/verdicts/zz_review.tsv` (newest file wins: false positives, player-typed JP names from the JP-made save,
  two-letter weekday cells = new **D17**). Fixed: minigame help note t0BB4FC " (Timer keeps going.)" (crossed the
  frame; `work/qa/fix21/mini_help`). `qa_gate.py check`: 197 sheets, **8 not ok**, and STALE (tour on bc6b43c7).
  PDA home "To-do" / "DynaDevice" labels ruled **D18** (space-limited, not bugs).
  **Open VQA bugs (real, graphics/code):** (2) deadline date
  row on the errand/schedule add screens "20 0 0 / 0 0 /   0 0": digits and separators misplaced (pda_errand_add,
  pda_errand_ra, pda_sched_add; JP "2000年00月00日", code in `gfx.DATE_PATCHES` area, graphics.md "Money diary
  dates"); (3) money diary week view (pda_money_rr): weekday words under the dates clipped ("Sc3", "Mc") and the
  header year "200Ч 12" garbled (the 年 tile); (4) mode_pda_schedule: weekday words under the dates clipped (same
  cells as (3)?); (5) おわる button on the
  profile form (mode_form, form_scroll; known form leftover); (6) `ending_full`: the English capture shows an empty
  lobby where the JP shows the ending art + credits (warp timing on the longer English text?). After fixing: re-run
  the English tour (all scenes, new build) + `qa_gate.py init --build`, re-run `vqa_run.py` on changed sheets.
  **Text coverage: new jump mode** `cover.py msgs [S..] --hold 1500 --jobs 1`: hijacks script S, then warp.lua
  `JUMP` replaces its first op's pc (dispatch loop top 0x0801E5E0, pc in [sp]) with an unshown message op
  (strings.tsv address - 6), A mashed; logs `work/qa/cover/j/sSSS.KK/`. Test s748: 38/38 in 7 runs. **Full sweep
  running at hand-off** (background python of this worker's shell, log `work/qa/cover/msgs.log`; ~30 scripts done):
  before resuming, check no `cover.py msgs` python is alive, then rerun the same command (finished runs are skipped).
  Coverage 3859/5536 at hand-off (590 messages left; sweep at s122, scripts go to s833). **Strings (1087 unshown)** need scenes: `cover_tables.py --unshown` (biggest:
  food/item descriptions in the mixed table 0x0BDAE8-0x0BFAEC, referenced from code at 0x4E2A0 / 0x4E5C0 / 0x5B538
  / 0x5B568 / 0x96488 literal pools; family-word list 0CEE48; skills 0C2864; Database help pages 0D05A0 / 0D0684 /
  constellation pages 0D0CB0..). Idea: hook the ldr that indexes the table and step the index (or stock every item
  in RAM: inventory address not found yet). Also `inkbox.py` on choice/menu boxes is still to do.
- **Session before (2026-11-15, worker 20):** **English tour finished** on build bc6b43c7: 197/197 scenes in
  `work/qa/tour/<scene>/hold.png` (scenes.tsv has a header row `name`: skip it when listing scenes). `qa_gate.py
  init` + `todo` done: `work/qa/manifest.tsv` (197), chunks `work/qa/chunks/chunk_001..016.txt`. **JP tour stopped
  by Claude Code for low memory at 104/198** (`work/qa/tour_jp`). **Next:** rerun the JP tour for scenes with no
  `work/qa/tour_jp/<scene>/hold.png` only (`--jobs 1`, original ROM is the default), then `tools/vqa_run.py --jobs
  2`, fix issues, `qa_gate.py check`.
- **Session before (2026-11-15, worker 19):** **Field HUD status word in English** (Healthy / Hungry / Sick) and
  **field pause "Pause"**: both were raw (uncompressed) IMG blocks, now handled by `gfx.load` / `gfx.apply`
  (in place); drawn by new `tools/hud.py`; `gfx.HUD_PATCHES` re-lays status SCRs 0x710 / 0x711. All 215 raw IMG
  blocks surveyed (`tools/rawimg_sheet.py`): no other Japanese. Notes: docs/re/graphics.md "Raw IMG blocks".
  Probes: `vramwrite.lua` now logs regs + stack callers, `mapwrite.lua` takes `MW_VAL` (exact word) / `MW_TO`.
  Gotcha: `regen.py` defaults to the original ROM; pass `--rom build/dynadevice_blue_en.gba` for English shots.
  The worker-18 English tour had died at 35/198 scenes (its build is stale now anyway). **English tour on build
  bc6b43c7** (`work/qa/tour/tour_build.gba`, `--jobs 2`) was **stopped by Claude Code for low system memory at
  125/198 scenes** (another project's 5 Mesen share the machine; ~3 GB free). Resume with only the scenes that
  have no `work/qa/tour/<scene>/hold.png` (regen.py redoes every named scene): `regen.py <missing..> --rom
  work/qa/tour/tour_build.gba --out work/qa/tour --states work/qa/tour/_states --jobs 1`. **Next:** finish that,
  JP tour, `qa_gate.py init/todo`, `tools/vqa_run.py`, as listed under worker 18 below.
- **Session before (2026-11-15, worker 18, handed off at the context budget):** **Dev status small words 01EE624
  r6-7 in English and seen** (PAT 01EF514 frames 17-21; graphics.md "Scene scan"): No Issues / Low Funds / Low Parts
  / Complete (shared piece moved first by PAT x patches) + detail-page panel Source Dyna / Equip Type / Arms Type /
  Element. New `tools/lua/devproj.lua` fakes projects (`regen.py d_dev_status|d_dev_proj_c --probe
  tools/lua/devproj.lua`; shots `work/qa/gfx_en/d_dev_status_proj`, `d_dev_proj_c`). **Card trade button**
  024D4B4 "Check Cards" (PAT 024DD84, link-only, unseen). Every graphics row in graphics.md is now drawn.
  masha-2 sweep had finished: **3671/5536 shown or waived** (778 messages, 1087 strings unshown).
  **New bug found by the visual-QA pilot: the field HUD shows "けんこう" (Healthy) twice** at the top of every field
  scene (e.g. `work/qa/tour/colosseum_greet/hold.png`). It is not a string: block **01E5464 is a raw (uncompressed)
  "IMG\0" block** (archive index 1803, header `IMG\0 00 0a 05 00`, 4bpp tiles from 0x1E546C: HUD frame, HP bar,
  digits, then the status-word kana around tile 0x29+), copied to BG VRAM 0xEDC0 by the loader (lr 0x080031F5) and
  expanded per pixel by 0x08002160 (the HUD's 4 tiles are BG0 0x3EF-0x3F2 at VRAM 0xFDE0). `gfx.py` only handles
  ECD-compressed blocks: add raw-IMG support (export + in-place write, same palette lookup), find which status
  words the HUD can show (other ailments: poison etc., tile runs), redraw them, check in game (`blockscan` /
  `blockfind` skip raw blocks, so grep the archive for other raw `IMG\0` blocks with Japanese at the same time).
  **Visual-QA gate set up:** `docs/visual-qa-brief.md` (game non-bugs listed) and new **`tools/vqa_run.py`** (one
  read-only `codex exec` per chunk with the EN shot + its `work/qa/tour_jp` twin attached; writes
  `work/qa/verdicts/<chunk>.tsv`; piloted on 3 scenes: works, found the HUD bug). **English tour running** at
  hand-off (background job of this worker's shell: `regen.py --rom work/qa/tour/tour_build.gba --out work/qa/tour
  --states work/qa/tour/_states --jobs 1`, log `work/qa/tour/regen.log`, 29/198 scenes done; one Mesen at a time,
  1.4 GB free). `tour_build.gba` = build 4753332e. If it died, rerun the same command (it redoes every scene).
  **Next:** fix the HUD block, rebuild, then (tour again on the new build if the HUD changed) run the JP tour
  (`regen.py --out work/qa/tour_jp --states work/qa/tour_jp/_states --jobs 1`, original ROM is the default), then
  `qa_gate.py init work/qa/manifest.tsv work/qa/tour --glob "hold.png" --build build/dynadevice_blue_en.gba`,
  `qa_gate.py todo work/qa/manifest.tsv work/qa/verdicts --size 12 --out-dir work/qa/chunks`, `tools/vqa_run.py
  --jobs 2`, fix issues, `qa_gate.py check`. Then inkbox on choice / menu boxes, textcover, steps 4-5 below.
- **Session before (2026-11-15, worker 17, handed off at the context budget):** **PDA calendar block 0215E74 all
  English** (docs/re/graphics.md "Money diary dates", D16): month header "2000/ 0" (static SCR 0x217E54: 年 -> "/",
  月 cells blanked by `gfx.MAP_PATCHES`), day view "0/ 0 (Mo) Plans" (SCR 0x2197F4, 16x16 weekdays Su..Sa, の予定),
  schedule repeat row None / per Wk / per Mo / per Yr, おわる button -> Quit (split 4x2 button: new gfx_text
  `{"stack": [...]}` boxes). New scenes `pda_cal_day`, `pda_sched_d4(a)`, `d_center_out(_a)`. Seen: `work/qa/cal_en/`.
  **01EA6B4** = Dyna Center counter (mode 14) stored-Dyna menu: drawn Take / Status / Free, **unseen** (tutorial
  save stores no Dyna). **Next:** 01EE624 r6-7 small words (runs unknown, notes in graphics.md "Scene scan"),
  024D4B4 buttons (めいしの / かくにん pieces, card trade), then phase-8 steps 2, 4, 5. masha-2 sweep: pid 25948
  still alive at hand-off, 189 runs in `work/qa/cover/m2/`.
- **Session before (2026-11-15, worker 16, handed off at the context budget):** **Money diary dates in English**
  (docs/re/graphics.md "Money diary dates"): code patches `gfx.DATE_PATCHES` + the glyph table moved to free space
  with a "/" entry; day view "12/31 (Sa)", month view "2000/12", weekdays Su..Sa (021C414); **calendar weekday row
  Su..Sa** (0215E74). Seen: `work/qa/gfx_en_dates/` (regen with `--states work/qa/gfx_en_dates/_states`, so
  `work/states/` untouched). New `tools/lua/mapwrite.lua` (who writes a tile number into a map or queue, with the
  stack's return addresses). **Next:** the calendar header "2000年 0月" (0215E74: 年 4,2 + 月 6,20, builder not
  found yet: start from the VRAM write pc 0x08002462 / lr 0x0800560F, notes in graphics.md), boxed 無し / 毎週 /
  月 / 年 + おわる in 0215E74 (errand screen), then 01EA6B4, 01EE624 r6-7, 024D4B4 buttons, then phase-8 steps 2,
  4, 5. masha-2 sweep (pid 25948) still alive at hand-off, 159 runs in `work/qa/cover/m2/`.
- **Session before (2026-11-15, worker 15, handed off at the context budget):** **Staff roll in English** (docs/re/
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
- **Open bugs:** none known (visual-QA bugs (2)-(6) fixed by worker 22, inkbox issues by worker 23).
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
