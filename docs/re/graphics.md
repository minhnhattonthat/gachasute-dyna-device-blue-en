# Graphics text survey

Tile-drawn Japanese: every row needs English art in phase 8 (D5: translate all of it). Text the game draws from
its font at run time (dialogue, the boot date prompt, the profile popup) is string work, not listed here.

## Method
- **Static sweep** (`python -X utf8 tools/gfx_sweep.py`): all 851 ECD `IMG` blocks rendered with their following
  `PLT` into 22 sheets (`work/gfx_sweep/`, offsets in `index.tsv`); no block skipped. 845 are 4bpp (flag 0), 6 have
  flag 1. Sheets read by a fresh read-only reviewer (`codex exec`, sandbox read-only, 6 chunks); the controller
  re-read sheets 000 and 016 itself and agreed. Sheets 008-018 (effects, sprites, maps) hold no Japanese.
- **Tour** (boot to profile form): Smilesoft/Nintendo logos (English), boot date prompt (font), title/menu,
  name entry (kana keyboard + START/SELECT hints), profile form labels (なまえ, ニックネーム, せいべつ,
  けいたいばんごう, メールアドレス, たんじょうび, けつえきがた, おわる): these labels are tiles; match them to
  the rows below with `vramfind.py` against `work/ecd/` in phase 8.
- **Marker tour** (phase 5, `build.py --marker`, `work/qa/p5_mk`): text left Japanese in the marker build is
  graphics (or unextracted text; checked by SJIS search): the field menu bar (じゅうみん データベース システム
  もちもの パーティ), the item submenu (つかう ならびかえ すてる: ならびかえ is not SJIS anywhere in the ROM),
  the profile form labels above. Phase 8 maps each to its ECD block.
- Not yet covered: raw (uncompressed) tiles outside ECD, the unknown file at 0x0E7FA4, the one BIOS-LZ77 block
  at 0x0E6A58, sprites (OAM) on screens past the profile form. Extend with the debug tool's tour (phase 2/5).

## Field menu bar (phase 8 pilot notes, block 01E30D4)
- 01E30D4 is a 27x5-tile atlas (palette 01E3574; ink index 1 = white, 0 = transparent, 2-9 frame greys). It is
  copied into BG char block 2 (VRAM tile 1541 + 32*row + col) and BG0's map (screen block 0, 2 rows, hofs 16)
  picks atlas tiles per button. Dump: `work/qa/menu_probe/ppu_001820.*` (warp `menu`, CONT=1, ppudump DUMP_AT=1820).
- Buttons (atlas row,col; top row / bottom row of the 16 px bar):
  システム `0,0-0,5` / `1,0-1,5`; もちもの `0,0 0,6-0,9 0,5` / `1,0 1,6-1,9 1,5`; パーティ `0,0 0,10-0,13 0,5` /
  `1,0 1,10-1,13 1,5` (caps 0,0 / 0,5 shared: text only in the 4 middle tiles, 32 px);
  じゅうみん `0,14-0,19` / `1,14-1,19` (48 px); データベース `0,20-0,23 2,22 2,23` / `1,20 4,12 1,22 1,23 3,22 3,23`
  (the map shows frame-only tile 4,12 in place of 1,21: check whether another screen uses 4,12 before drawing
  ink into it, else move the ink of that column into rows 0-7 or patch the map).
- Glyphs: 7 rows at atlas y 3-9 of each 16 px band (crossing the tile-row boundary at y 8); VWF caps fit.
- Atlas rows 2-4 hold the submenu words (つかう ならびかえ すてる, データセーブ おわる, ステータス そうび
  かえらせる にがす, マップ ダイナ キーワード デバイス, バトルアニメ...): dump their screens the same way
  (`menu_items`, `menu_party`, `menu_save` scenes) to get their tile lists before redrawing.
- `tools/gfx.py export OFF` writes `work/gfx/orig/OFF.png` + x4; English art goes in `gfx/OFF.png` (same size,
  palette colours only); `gfx.apply()` (called by build.py) writes it in place or relocates it.
- **Done 2026-11-15 (English in game, `work/qa/gfx_en/`):** the maps are raw `SCR\0` blocks right after the
  palette (u16 = atlas row*32+col, 0x1FF blank): bar buttons 01E35C4-01E3644, submenus 01E3724 (System),
  01E3774 (Items), 01E37C4 (Party), 01E3834 (Residents), 01E38A4 (Database). `tools/gfx_text.py` clears the kana
  and draws bar + submenu words into `gfx/01E30D4.png`; `gfx.MAP_PATCHES` re-lays three rows (Save and Sort fit
  4 tiles, freeing 1,21 for the Database button and 2,13 / 2,18 to make Keywords 6 tiles). No atlas tile is spare:
  BG1 (the window) uses 4,23 and cols 24-26, and VRAM past col 26 holds other art. Submenu words sit at tile y 0-6
  (descenders y 7); bar words at y 3-9 of the 16 px band. `tools/lua/ppu_every.lua` + regen `--probe` dumps VRAM.

## Profile form (block 020EB44, not in the sweep table: the sweep listed it under 020E844)
- BG2 (char 0x4000, screen 0x2000, 64-row map): field lines are tiles 6,29 (start) 6,30 (line at tile y 2) 6,31
  (end); each label is one tile row of the atlas between them, ink index 4, kana at tile y 0-5.
  `python -X utf8 tools/bgmap.py work/qa/form_dump/form_scroll/ppu_001830 9000 --count 288 --full` lists them:
  なまえ 7,0-2; ニックネーム 7,3-7; せいべつ 8,0-3; じゅうしょ 8,4-7; でんわ 8,8-10 + ばんごう 8,11-13;
  けいたい 8,14-17 + the same ばんごう; メールアドレス 8,18-23; たんじょうび 8,24-28; けつえきがた 7,25-30.
- **Done 2026-11-15:** Name, Nickname, Gender, Address, Home Tel., Mobile Tel., Email, Birthday, Blood Type
  (`gfx_text.py` entry 0x20EB44; in game `work/qa/gfx_en/form*/`). Open: tiles 7,17-20 / 7,21-24 (two tiny boxed
  words, map rows 36-37 beside the blood-type label: find the screen that scrolls them in), the おわる button.
- The form's popup (ユーザーとうろくを おこないます / あなたの データを にゅうりょくしてください) is **OBJ**
  art from block 02124B4 (pre-drawn sentences, not a charset: also このデータを けしても いいですか？, けす＝Aボタン
  けさない＝Bボタン, アドレスのついか, リセット データをけす). OAM uses 2D mapping (block tile n = OBJ tile 480+n),
  4-tile sprites with 8 px gaps between them, so English words break at the gaps. **Done 2026-11-15:** the
  registration popup ("Let's register as a user. / Please enter your details."). Open: the other sentences of
  02124B4 (PDA address book: delete prompt, add-address tab, reset/erase data button): find their scenes first.

## Name-entry keyboard (block 020BDD4, OBJ)
- All OBJ: block tile n = OBJ tile n (VRAM 0x10000), 2D mapping; OAM at scene `keyboard_select` f1260.
  Normal tabs = atlas x0-31 y0-55 (two 32x32 sprites), 9-row pitch from y1; the selected tab is a 32x8/32x16
  sprite from x32-63 (かな y0, the rest y16+8k). START/SELECT on screen = copy C (x128-159, sprites 32x64 + 32x16
  at tile 0,16 / 8,16); copies A (x4-37) and B (x43-80) are pressed states (B's SELECT is cut at row 88 in the art).
  前のページ / 次のページ (x160-255, two copies each) are not on the profile-name keyboard: its kanji tab is not
  reachable (L stops at Sym, R does nothing; kanji come from SELECT conversion, candidates in the right box).
- **Done 2026-11-15:** tabs Hira / Kata / Sym / Kanji (ABC, 123 kept), START "OK", SELECT "CONVERT" (3x5 caps,
  `gfx_text.MINI`), "Prev Page" / "Next Page" (`gfx_text.py` "redraw" boxes: the old lettering is cleared, the
  background rebuilt by a row-wise nearest fill or a per-pixel vote over the six tabs, then ink + shadow drawn).
  In game: `work/qa/warp/keyboard_select/hold.png`. Page buttons seen in the atlas only (`work/gfx/en/020BDD4_x4.png`).

## PDA screens (2026-11-15, worker 4)
- Debug modes 2-8 + 45 show the PDA apps from a cold boot (`work/qa/pda/modes.png`): address book (index tabs
  ア..ワ, セレクト データをけす, アドレスのついか R: 02124B4), calendar (L よていのついか / R ようじのついか,
  月火水木金土 header), money diary (mode 5: つかったお金ついか / もらったお金ついか, 021EA44), timetable (mode 8:
  時間割, ひとつけす, 月火水木金土), calculator (mode 7: やりなおし, 税込み), memo (mode 6: あたらしく かく). PDA home
  (boot with `work/states/tutorial_jp.sav`, ~f1350): アドレス / ダイナデバイス / データセーブ / 予定 / 用事.
  Scenes `pda_money`, `pda_errand_add`, `pda_sched_add` (icon tabs, おわる) added.
- **Done:** calendar header 0219CB4 "Add Plan" / "Add Errand" (both copies; outlined white ink 3, ring 14, fill
  `rowmode`), in game `work/qa/warp/mode_pda_calendar/hold.png`. Open in the same block: the faint delete prompt
  (このデータを けしても いいですか？ / けす＝Aボタン けさない＝Bボタン, ink 7 on 5): find its screen.
- **Done (worker 5):** money diary header 021EAA4 (the table's 021EA44 is a typo: the block is 021EAA4, OBJ tile
  480 + 32*row + col): L "Add Money Out" (both copies), R-band overlay strips y32-39 "This Month" / "This Week" /
  "Add Money In" (ring outline clipped to the 8 px strip). In game `work/qa/gfx_en/pda_money*/`,
  `mode_pda_schedule`. Same block, open: the faint ink-7 delete prompt (y104-119) and ・しゅうの▲ (x184-223, y32).
  The month-view panel label t0B924C has 4 tiles (32 px): "This month" ran into "Left", now "Month" (r07).
- **Done (worker 5):** calculator 02280B4 (mode 7): button words "Clear" / "+Tax" (OBJ pal 2 blue, `grad` row
  inks + white drop shadow), R band "Scroll" (screen not seen yet). Memo 0225EC4 (mode 6, 30 tiles wide: OBJ
  tile 480 + 32*row + col): R overlay "New Memo" (shown), "Backspace" (ひともじ けす, not seen), selected tab.
  Index tabs: the unselected ones are **BG1 tiles of 020EB44** (map 0xBC-0xF7 = block tile + 0x80), drawn with
  `gfx_text.py` "screens" (a map strip redrawn in screen coordinates, written back per tile; repeated tiles must
  stay identical). Tabs share side tiles, so each letter fits the middle tile: romaji initials A K S T N H M Y R W
  (also on the OBJ tab copies). In game `work/qa/gfx_en/mode_pda_list`, `mode_pda_calc`.
  Open: address book 02124B4 (same tabs, アドレスのついか R band x2, セレクト データをけす buttons x2), timetable
  (mode 8: 時間割 logo, 月..土 header, ひとつ けす R band, subject icons 国.. in 022CF64?), delete prompts.
- **Done (worker 6):** address book (scene `mode_pda_memo` = mode 3; block 02124B4): tabs A K S T N H M Y R W as the
  memo's (identical art), R band "Add Address" (ink 4, drop shadow 14; kana shading 5/11/12 cleared per box: an
  optional 8th "redraw" item is the box's own clear set), buttons "Select" / "Erase". The faint delete prompt
  "Erase this data?" / "A: Erase" / "B: Keep" is drawn but **not seen**: the only entry (the player's own card)
  can't be erased (scene `pda_addr_del` opens it instead). Same block, still JP: the form popup's later lines
  きいろいボタンの こうもくは / すべて にゅうりょくしてください (rows 8-10, x128-255): scene `form_start`
  (warp.lua now takes `form|ROUTE`) did not reach that page; its OAM layout is unknown.
- **Done (worker 6):** PDA home + app labels = **block 0208654** (OBJ, block tile n = OBJ tile n; white ink 7, the
  outline is added in game): Address, Schedule, Money, Calculator, Timetable, Music, Link, DynaDevice, Minigame,
  Save Data, MEMO (mini caps). Only Address / DynaDevice / Save Data seen (`work/qa/gfx_en/mode_pda_profile`);
  the others are on the Dyna Device app menu (tile runs assumed from the kana). Headers 予定 / 用事 = **block
  0206CF4** "Plans" / "To-do" (24 px each). Found by `tools/lua/vramwrite.lua` (CPU writes into an OBJ VRAM range:
  the decompressor wrote the label tiles at f306) + `lzss_log.lua`; vramfind missed them (VRAM tiles differ).
- **Done (worker 7):** PDA Save Data dialog **020A4D4** (scenes `pda_save`, `pda_saving` = PDA home Down, A):
  "Save | all your | data?" (OAM gaps), "A: Save" / "B: Cancel" (the buttons share 4-tile pieces, so the shared
  ones are blanked), "Saving..." / "Keep | the power on.". Link menu **0249C44** (scene `pda_link` = PDA home
  Down x2, A): title "Link Menu" (`vwf2` = doubled font), bands Link Battle / Card Trade / Item Trade / Dyna
  Trade (lettered tiles replaced by the blank band tile 3,10, then gradient ink + ring). The PDA home wheel:
  Down turns it one app on (Address -> DynaDevice -> Save Data -> Link ...).
- **Done (worker 7):** link check screen (every Link menu item opens it with no cable: scenes `pda_link_battle`
  / `_card` / `_item` / `_dyna`): headers **03B3624** "Link Check" (seen), "Select Rules", "Battle Animation"
  (drawn, unseen); status words **03B3164** (BG tiles, VRAM 0x8000 in 32-tile rows) "Not connected" (seen),
  "Connected", "Connecting..." (unseen). Still JP there: シンプル / エキスパート, ２３４Ｐ. The trade screens
  (024AF04, 024B834, 024D4B4, 024C1C4) and the link battle setup need a partner: no warp yet.
- **Done (worker 8): title block 0449734** (scene `mode_title`; `work/qa/gfx_en/mode_title/hold_x3.png`,
  `press_x3.png`): "Emblem", "©2002 SMILESOFT", blinking "PRESS START" (7-row strokes ink 5, sides 3, corners 4 =
  gfx_text `("ring2", 3, 4)`), the 10 planet names. Names: the title's PAT animation at 0x44BF24 (u32 offsets at
  +8; frame = s16 count + 8-byte entries u16 size code|0x2000, s16 x, s16 y, u16 tile|pal<<12, screen x = 120 + x)
  frames 3-12 = one planet each: symbol, emblem label (4 pieces), name = 32x8 at x8 + 8x8 at x40 + cap 413 at x48.
  English (gfx.TITLE_NAMES, patched by gfx.title_patches): one run of 5-7 tiles per name in rows 10-11 (all 64
  tiles: the RED logo's bottom rows 10-11 c24-29 are not on any Blue title frame), second piece 8x8/16x8/32x8, cap
  at x 8 + 8n (Capuchipean: two 32x8, the 8th tile transparent under the cap). Only Terioranus is seen on a cold
  boot (the emblem comes from the save): `tools/title_frames.py` draws all 10 frames from the build
  (`work/qa/gfx_en/title_frames.png`). PRESS START blinks: `tools/lua/shotwhen.lua` shoots every 10 frames once
  its tile is in OAM. Survey notes below.
- **Done (worker 9): PDA home wheel labels 0208654 all seen** (scenes `pda_up`, `pda_up3`, `pda_up6`,
  `pda_down4`: Calculator, Schedule, Timetable, Music, MEMO, Money, Minigame 1-3; `work/qa/gfx_en/wheel.png`).
  A on the start app (DynaDevice, scene `pda_dyna`) opens the Dyna Pad, not an app menu.
- **Done (worker 9): timetable 022CF64** (mode 8 = scene `mode_pda_calendar2`; `pda_tt_a` = A on a cell: the
  subject palette; `pda_tt_r`): logo "Timetable" (`tallb` = double-height bold font), header Mon..Sat (`tall`),
  palette title "Pick a Subject" (`vwf2`), R band "Erase One" (both frames), the 24 subjects + 委 as 3-letter
  abbreviations (D15), status line "Mon, period 1 = [icon]": its PAT (0x22F194: weekday frames 0x22F246..,
  digit frames 0x22F2E2 + 0x22n) re-laid by `gfx.tt_patches`. Gradient boxes take a list as ink (per-box
  gradient). `tools/pxdump.py OFF x0 y0 x1 y1` prints a block's palette indices.
- **Done (worker 9):** "Customize Dyna" title (01E9764, mode 13; no PLT: `gfx.PLT_FOR`; the title runs over two
  atlas pieces, so a redraw box may be a list of segments), "Team Setup" title (03B29B4) + menu Add/Swap / Remove /
  Done (BG tiles of 03B25A4 re-laid by MAP_PATCHES on the raw SCR 0x3B2854), "Place Dyna" title (025E304,
  mode 28). Still JP in 025E304: いどう, コマンドせんたく, てきのエリア, もどる, ステー.., small てきエリア (placement
  states not reached: need scenes). Same block 01E9764: てもちの アイテム▶▶ いっぱい なので / デバイスを はずすことが
  できません (a full-inventory popup, layout unknown).
- **Palette gotcha (worker 9):** a PLT that repeats a colour turned drawn indices into other ones on the PNG round
  trip (025E304 pale 7 -> navy 1; latent in 020EB44 / 02124B4 / 0219CB4). `gfx.palette_for` now nudges repeats
  (`gfx.distinct`) and `gfx_text.render` fails if any drawn index would not come back.
- **Minigames (done, worker 10):** all BG0, char base 0x4000. Block 03D5DB4 (29 tiles wide) sits at VRAM 0x9800
  and 03D7FD4 (19 wide) at 0x9400 (help page) or 0x6000 (title / level select), both with a **32-tile row stride**,
  so map word = 32 * atlas row + col | pal << 12 (`bgmap.py DUMP 9800`, rows exact). Every word is a raw SCR map
  at 0x3D6D64-0x3D8784 (header `SCR\0`, u8 0, w, h, 0; then w*h u16): ゲームスタート 3D6DF4, おわる 3D6E64,
  ゲームクリア 3D7194, げんざいの きろく 3D71D4, とくてん 3D71F4, クリアタイム 3D7204, しんきろく！！ 3D7224,
  こんかい てにはいった ビット 3D7244, げんざい もっている ビット 3D7274, ギブアップしますか？ / はい=Aボタン
  いいえ=Bボタン 3D7364, どのレベルに ちょうせんしますか？ 3D7474, レベル1-3 3D7524/64/A4, スタート！ 3D7954,
  タイムアップ！ 3D79A4, ゲームオーバー 3D7A04, title R line 3D8704, level-select legend 3D8754, help page 3D8784
  (そうさほうほう, ルール, じゅうじキー, A/Bボタン, スタート). ゲーム is one 6-tile prefix 8,11-13 + 4,26 + 8,14-15
  shared by Start / Clear / Over (4,26 was also inside オーバー). The code writes て ん (3,0-1) after the title
  score and ふ ん / び ょ う (5,19, 3,1-4) after the level-select times (0x08002402 via 0x08002A9D; probe
  `regen.py ... --probe` with an on_write hook on the BG0 cells). English: `gfx.MINI_ROWS` re-lays the maps,
  `gfx_text` draws big words in vwf2 (Game / Start / Clear / Over / Level / Time Up / Quit; HUD Score / Time
  Left in `tall`), the small words as VWF runs on freed kana tiles (`gfx._S5`: High, Score, Clear Time, New
  Record!, Bits Earned, Your Bits, Give up?, Yes, No, Which level?), code kana -> "m", "s" or blank (00m 00s; the
  title score is the bare number). Header: "Minigame N : How to Play". Seen in game (scenes `mode_minigame_a`,
  `mode_minigame_level`, `mini_help`, `mini_help_b`, `mini_play`, `mini_pause`, `mini_long` = Start! at f870):
  `work/qa/mini_en/`. **Drawn, unseen:** Game Clear, Time Up!, New Record!, Clear Time, Bits Earned / Your Bits,
  やめ -> Quit (the results need a real score: a dead player goes back to the title).
- **0203D14 (Dyna get / naming, worker 10 survey):** この ダイナに なまえを つけてください (blue box r1-3 c17-29),
  タイプ / スタイル / ぞくせい, このスタイルで…す！, この ぞくせいの ダイナは はじめて ゲットです, NEW! art. Archive
  index 2336 (PLT 2337 = literal 0x921 at 0x0803F6FC / 0x0803F868 / 0x0804067C): loaded by 0x0803F574 (called from
  state task 0x0803F3A4 of the task table at 0x080D2B48: 0x0803ED7D, 0x0803EDBD, 0x0803F3A5, 0x0803F871..),
  0x0803F704 (from 0x080404EC / 0x08040516) and 0x0804046C (mode 45 chain 0x08040A28 -> 0x080409AC -> 0x08040860;
  runs at f279 of `mode_pda_45` but the block is not in VRAM: the load sits behind a branch).
  **Done (worker 11):** mode 45's frame task (0x08040960) runs the 0x080D2B48 state machine (state u16 0x02011148)
  whenever 0x0801A9B8 returns 0; A presses walk it: state 4 (f809) = the NEW! panel, then a message and the
  naming keyboard (scenes `dyna_new`, `dyna_name`; `work/qa/gfx_en/dyna/`). OBJ tile = 480 + 32 * row + col.
  Panel sprites = PAT 0x204234 frame 2 (frame 1 = the three labels alone; frame 0 = the frame pieces); the naming
  prompt is 7 sprites placed by code at y0. English: Type / Style / Element, "This is your / first Dyna / of this
  / style & / element!" (r5 c6 ends lines 2 and 4, so it is blank), "Please give this Dyna a name." (the
  string in s-scripts says the same). gfx_text redraw boxes take a 9th item "left".
- **Done (worker 11): battle results 03B9D84** (not in the sweep table; mode 36 = scene `d_get`,
  `work/qa/gfx_en/results/d_get_x3.png`): "Results" header, column heads Dyna / Left, Wipeout / Turn (Points /
  Won drawn, unseen), outcome words Win / Lose / Draw (`vwf2`, gradient + ring outline), the big ターン after a
  turn count blanked. Found with the new `tools/blockfind.py DUMP_PREFIX` (which IMG blocks a ppu dump shows).
- **Title block 0449734 (worker 7 survey):** logo stays JP (D5: no official English logo). Text in it,
  scene `mode_title` (OBJ 2D, OBJ tile n = block tile n, ppu dump f930): copyright ©2002 スマイルソフト = rows
  12-13 c0-12 (outlined 16 px glyphs in shades 2-5), OAM x68 / x76 / x108 / x140 at y140; エンブレム label = r12
  c29 (edge bar) + r12 c30-31 + r13 c29-31, OAM y102 x64-112; planet symbol 16x16 at x112; planet name y102 from
  x128: rows 10-11 hold the 10 names separated by 2 px bars (colour 3/4), e.g. テリオラヌス = r10 c0-4 (x0-37),
  shown as r10 c0-3 + c4 then tile 413. Each name's tile run comes from a table (find it before fitting English:
  Terioranus, Sigmazon, Capuchipean, Bisaios, Jornaturn, Parmoon, Plutario, Mercurie, Byjupiter, Zaurak =
  t0B2710-t0B276C). スタートボタンを おしてください (rows 12-13, x~104-231) blinks: take dumps until it shows.
- 020B0F4 tabs (なまえ ばしょ すること イベント カスタム) drawn as "Name / Place / To Do / Event / Custom" (map SCR
  0x20BAB4, menu-bar layout), **not yet seen in game**: archive index 2395 is loaded by 0x08023F20, reached from
  the mode 2 chain (0x08021370..) and from 0x080283B0 / 0x0802DDB0 / 0x08032834 / 0x0803B6A0. Not on the PDA
  home, address book, calendar add-plan / add-errand screens. Next: a Lua exec hook on 0x08023F20 in those modes.

## Scene scan (worker 12)
`tools/blockscan.py DIR..` lists, per Rows block, the scenes whose ppu dumps hold its own tiles (tiles no other block
has). Original ROM, `regen.py <scenes> --out work/qa/survey --probe tools/lua/ppu_every.lua` over 32 scenes:
- 0231524 fortune box: every save boot (scene `fortune`, new: boot kind, regen.py gives it tutorial_jp.sav).
- 01EA8C4 + 01EAA04: `d_dyna_shop`, `d_kit`. 01EB9E4: `d_item_sell`. 01ECD84: `d_auction`, `d_shop_list`.
  01EE624: `d_dev_status`. 01EFFF4: `dbg_colo_free`. 01F4284: `dbg_world_map`, `menu_resident_map`.
  024C1C4 + 024D4B4: `mode_card`, `mode_card2` (card trade).
- Not in any of those scenes: 01EA6B4, 024AF04 / 024B834 (link item / Dyna trade: need a partner), 0250924, 03B7F64.
  020B0F4 only shows its window-frame tiles (form screen), not the tabs.
- Field-mode headers (OBJ 2D at 0x10000, italic f..b gradient + shadow 2 on navy 1 = gfx_text TT_GRAD / vwf2;
  no PLT of their own: `gfx.PLT_FOR` borrows 022CF64's for the PNG): **done (worker 12)** 01EB9E4 Buy Items /
  Sell Items (`d_item_sell`; Buy unseen), 01EAA04 Stored Building Kits (`d_kit`) / Treat Dyna (`d_dyna_shop`: the
  balls hide the run's ends, keep to the JP span x64-184). 01EA8C4 is the HP/Lv bar art: no Japanese.
  **Done (worker 13)**, `work/qa/gfx_en/<scene>/hold.png`: 01ECD84 Item Auction header + small words (Start /
  Price, Funds, Device / Item + Name, Element, Equip / Arms + shared "Type" tile; auction-only words Auction, Bid,
  Bits, Time Left, Current drawn but unseen; r6 c10 の left), 01EE624 Dev. Status + Project (its small words r6-7
  もんだいなし / しきんぶそく ... unseen, still JP), 01EFFF4 Free Battle (tallb: the balls hide the ends), 01F4284
  Zoom Out / Zoom In buttons + Resident / Dyna / Devices. Small words are 8 px, gradient f f e e d c b at y1-7
  (gfx_text SMALL_GRAD), composed by the code from separate tile runs: each run gets its own English word.
  `blockscan.py --all` on the 32 survey scenes: their other blocks hold no JP (art, digits, 8bpp maps).
  01EA6B4 (worker 17): archive index 1835, loaded by 0x080902EC from mode 14 (jump table 0x08004DF0, entry =
  mode - 1) = the **Dyna Center counter** (scene `d_center_out`: ひきだす > ダイナ). The tutorial save stores no
  Dyna ("げんざい こちらで あずかっている ダイナは いません"), so the つれていく / データをみる / にがす menu is
  unseen; drawn as Take / Status / Free (white 10, 8 px, left-aligned in c7-11 / c7-10 / c7-10). To see it: get a
  stored Dyna (RAM poke or a save with 3+ Dynas), then scene `d_center_out_a`.
  01EE624 rows 6-7 (unseen, still JP): row 6 white 8 px words もんだいなし しきんぶそく しゅうりょう そざいぶ.. (one
  kana per 8 px, 6-kana runs?), row 7 gradient f..b words データさいしゅう ダイナそくせい そうび.. ぶきブラ..; the
  runs the code composes are not known yet: find them from the dev-status code (d_dev_status) before drawing.

## Tactics battle board (worker 14)
The debug menu's TACTICS SYSTEM (MONSTER SET MENU) starts a 1-Dyna battle vs COM: Down x3 to MONSTER NUMBER,
Right, **A** (adds it: without that A, TACT START does nothing), Up x4, A. Scenes `tact_place` (ダイナはいち),
`tact_confirm` (これで いいですか？), `tact_cmd` (turn 1 command menu), `tact_enemy` (R), `tact_move` (いどう),
`tact_status` (L); a real battle follows (A on Attack, A, A: the attack animation). Sprites come from PAT blocks
right after the art: `tools/pat.py --scan 25F000 260500` lists every frame (size code 0x00 8x8, 0x41 16x8, 0x52
32x8, 0x66 32x16; tile word = entry + 6, x = entry + 2).
- **025E304** (OBJ tile 32 * row + col): titles Place Dyna (c0-9), Move Dyna (JP ダイナいどう reused c0-4: the PAT
  025F094 entries now point at the free c10-14), Select Command (r0-1 c21-23 + r2-3 c0-11), Enemy Area (r2-3
  c12-23); L/R button words (ink 4 over shade 3): Status (r5 c29-31 + r6 c31; JP ステータス repeated ス at x 9, now
  at x -23 under the first), Back (r4 c29-31, both buttons), Enemies (r6 c26-30: "Enemy Area" is 48 px, the run 40).
- **025D924** (the sweep's "0250924"; loaded at OBJ 0x11C00 = rows 7-16 c0-7 of the 2D layout): command words
  Attack / Scout / Cure / Move / Special, each its own 32x8 sprite (Special unseen: no Special Dyna in the test).
- **03B7F64** (だい N ターン, ジョーカー / キング / クイーン / ジャック / ゴースト, 1P-4P) is archive index 7629 and is not
  loaded by the tactics battle, dbg_battle, the link check, team, roulette, results or battle-field scenes
  (`tools/lua/lzss_log.lua` over 13 scenes): it is the link battle's board (Joker etc. are link roles, s210 /
  s228). The TSBTL debug menu (`dbg_tsuusin`) TACT START goes to TSUSIN MODE SELECT, which waits for a cable.

## Staff roll (mode 22, block 0432534 + PAT 0432D44, done worker 15)
The credits are OBJ sprites, not BG text: block 0432534 (IMG 224x48 = 28x6 tiles, at OBJ VRAM 0x10000, 2D
mapping) holds 8x16 kana glyphs (tile n over n + 32), small 8x8 dakuten pieces in row 5, digits 2 / 0 (r4 c15-16)
and a 16x16 (c) mark (r4 c25). The words are the raw PAT at ROM 0x432D44 (archive-0 word 0x0EFEB4, right after
the charset's PLT 0x432D14): 11 frames = 11 cards, one sprite per kana, anchor at screen 120,51, cards scroll up
over the pictures (scenes `credits` 9600 frames, `credits_mid`). `tools/credits.py` draws an English charset
(fonts/vwf8.txt letters, white with a 1 px black shadow, the (c) mark kept) into gfx/0432534.png and builds a new
PAT (403 sprites, 3298 bytes; the old slot holds 0x8E0) that gfx.apply writes to free space, repointing the
archive word. Names: Western order, Hepburn without macrons (D1/D2). Shots: `work/qa/credits_en/`.
The palette of 0432534 repeats magenta 11 times: gfx.distinct used to loop for ever on it (fixed, tested).

## Fortune box (block 0231524, done worker 12)
Boot with a save: date prompt, A, then きょうの うんせい (scene `fortune`, `work/qa/gfx_en/fortune/hold_x3.png`).
BG3 = the swirl background (block rows 0-10), BG1 = the box text from SCR 0x234034 (30x20, words 32 * row + col,
palette 2): title r13 c12-21, labels r14 (icon tiles c0 / c5 / c9 / c13 kept), ink 1 at tile y0-6. Health
けんこう and Study べんきょう shared ん/う tiles, so `gfx.FORTUNE_ROWS` re-lays Study (c6-8 + c21) and Money
(c10-12 + c22); r14 c21-31 were flat. English: Today's Fortune / Health / Study / Money / Lucky Dyna (the Dyna
itself is a sprite). Rows 11-13 c0-11 / c24-31 hold glyph-like tiles no map of this screen uses: left alone.

## Money diary dates (block 021C414) + calendar weekday row (block 0215E74), worker 16
- **021C414 (BG, char base 0x8000 in the money scenes):** glyphs are drawn by **0x0802DF10** (r0 BG, r1 glyph, r2 x
  cell, r3 y cell) from a table at **0x080D2590** (33 entries: u16 tile|pal<<12, u16 kind 0=16x16 1=8x16 2=8x8;
  0-9 big digits, 10-19 small digits, 20-21 list markers, 22 = the list rows' end dot, 23-29 weekdays 日..土, 30
  small 年, 31-32 ( )). Its only pointer is the pool word 0x0802DF68. The date units are the weekday glyphs
  (月 = 24, 日 = 23), passed as literals: 0x08030B92 / 0x08030BF6 (day view "12月31日 (土)", 32 calls listed by
  `disasm.py xref ROM 0802DF10`), 0x0802E218 (week view), 0x08030402 / 0x0803045E (month view). Found with
  `tools/lua/mapwrite.lua` (who writes a tile number into a map / the 0x03002450 tile queue, with the stack's
  return addresses).
- **Done:** `gfx.DATE_PATCHES` + the moved table (one more entry, 33 = 16x16 "/" in the free tiles 3,14-4,15):
  day view "12/31 (Sa)", the 日 call and the month views' 月 calls nopped, small 年 drawn as "/" ("2000/12"),
  weekdays Su..Sa (`tallb`). Seen: `work/qa/gfx_en_dates/dates_x2.png` (scenes `pda_money`, `pda_money_r`,
  `pda_money_rr`). The week view's year shows "200" + "/" on top of the last digit: the original overlaps too.
- **0215E74 (calendar, BG1 char base 0x8000 in `mode_pda_calendar`):** the weekday row is 16x8 glyphs (日 0,32
  月 0,40 火 0,48 水 0,56 木 16,48 金 16,56 土 32,48) -> Su..Sa, seen. **Still JP:** the header "2000年 0月": 年 =
  tile 4,2 (16x16, x16 y32) and 月 = the 16x16 weekday 月 at 6,20 (x160 y48; the 16x16 weekdays 6,18-31 and
  の予定 4,6-11 are on a screen not yet seen, likely the calendar day view). Its map words are not queued through
  0x03002450 (mapwrite on that queue and on EWRAM caught nothing; the VRAM write at f304 is pc 0x08002462,
  lr 0x0800560F): find the builder from there, then the same fix (年 -> "/", 月 unit -> nothing or a copy).
- **Done (worker 17):** the header is a static raw SCR at **0x217E54** (`SCR\0`, 30x20 words from +8; the 8 SCRs
  0x2174D4-0x2197F4 are the calendar / form screens), only the digits are code (BG0). 年 (4,2) is used by that
  SCR alone -> big "/"; the 月 cells (row 3-4 col 21-22) blanked by `gfx.MAP_PATCHES`: "2000/ 0" (the 1-digit
  month slot leaves the original's gap). Schedule form repeat row (scene `pda_sched_d4`, Down x6 after L): 16x16
  units copied by code into BG2 tiles, 無|し (144,96 + 160,96), 毎 (176,96, left half of 毎週 / 毎月 / 毎年), 週 / 月
  / 年 right halves (192 / 208 / 224) -> None, per + Wk / Mo / Yr (D16). おわる button (errand + schedule forms) is
  a 4x2 tile button split in the atlas: top row 3 col 17-20 (136,24), bottom row 11 col 19-22 (152,88) -> Quit
  (gfx_text `{"stack": [...]}` boxes). Seen: `work/qa/cal_en/`.

## Rows (ROM offset of the ECD block)
| Offset | Sheet | Japanese | Gloss | Kind |
|---|---|---|---|---|
| 01E30D4 | sheet_000 | システム　もちものパーティじゅうれん　データへ　データセーブ　おわる　つづき　はじめから　そだてる　データクリア　そうび　アクセサリー　せってい　マップ　ダイナキーパー　ロード　インパルス | System; belongings; party; training; data; save; quit; continue; new game; raise; clear data; equipment; accessories; settings; map; Dyna Keeper; load; impulse | menu-label |
| 01E9764 | sheet_000 | ダイナカスタマイズ　こうきのう　マテリアル　ないぞう［以下判読困難］ | Dyna Customize; high performance; material; built-in [remaining text unclear] | menu-label |
| 01EA6B4 | sheet_000 | つれてい［断片］　データ［断片］ | Bring along [fragment]; data [fragment] | menu-label |
| 01EA8C4 | sheet_000 | ［大きな文字状の断片・判読困難］ | [Large lettering fragment; illegible] | sign/other |
| 01EAA04 | sheet_000 | あずかっている けんちくキット　ダイナのうりょう | Stored construction kits; Dyna capacity | menu-label |
| 01EB9E4 | sheet_000 | アイテムここにゅう　アイテムはいきゃく | Item purchase; item sale | menu-label |
| 01ECD84 | sheet_001 | アイテム［断片］　コウカン　オンライン［以下判読困難］ | Items [fragment]; exchange; online [remaining text unclear] | menu-label |
| 01EE624 | sheet_001 | かいはつ［断片］　はっきょう　プリント［以下判読困難］ | Development [fragment]; [unclear menu word]; print [remaining text unclear] | menu-label |
| 01EFFF4 | sheet_001 | フリーバトル | Free Battle | menu-label |
| 01F4284 | sheet_001 | ズームアウト　ズームイン　みているダイナデバイス［断片］ | Zoom out; zoom in; currently viewed Dyna Device [fragment] | button-hint |
| 0203D14 | sheet_003 | この ダイナに な［断片］　まえを つけてください　このゲームをつづけてのぞむには［判読困難］ | Name this Dyna [split text]; [additional instruction unclear] | menu-label |
| 0206CF4 | sheet_003 | けってい　用事 | Confirm; errand | menu-label |
| 0208654 | sheet_003 | ［小さなカタカナの項目名・判読困難］　ミニゲーム１２３ | [Small katakana item labels; illegible]; minigames 1, 2, 3 | menu-label |
| 020A4D4 | sheet_003 | すべてのデータをセーブします　セーブする→ボタン　しない→Ｂ | Save all data; button to save; B to cancel | menu-label |
| 020B0F4 | sheet_003 | なまえ　せいよう　ちょうさくへん　カスタム［一部判読不確実］ | Name; [uncertain menu terms]; custom | menu-label |
| 020BDD4 | sheet_003 | かな　カナ　ＡＢＣ　１２３　きごう　かんじ　前のページ　次のページ | Hiragana; katakana; ABC; numbers; symbols; kanji; previous page; next page | button-hint |
| 020E844 | sheet_003 | charset | Kana character set | font/charset |
| 02124B4 | sheet_003 | charset | Kana character set | font/charset |
| 0215E74 | sheet_003 | charset | Japanese character set | font/charset |
| 0219CB4 | sheet_003 | よていのついか　よびのついか　よびじかんのせってい　よびじかんクリア　このデータを けしても いいですか？　はい　いいえ | Add schedule; add reminder; set reminder time; clear reminder time; erase this data?; yes; no | menu-label |
| 021C414 | sheet_003 | charset | Japanese character set | font/charset |
| 021EAA4 | sheet_003 | つかったお金ついか　こんげつぶん　こんしゅうぶん　もっともおおいつき［一部判読困難］ | Add money spent; this month; this week; highest-spending month [partly unclear] | menu-label |
| 0224B44 | sheet_003 | charset | Kana character set | font/charset |
| 0225EC4 | sheet_003 | charset | Kana character set | font/charset |
| 02280B4 | sheet_004 | スクロール／やりなおし／[一部判読不能] | Scroll / Redo / [partly illegible] | menu-label |
| 022CF64 | sheet_004 | charset | Character set | font/charset |
| 0231524 | sheet_004 | [下端に日本語あり・判読不能] | [Illegible Japanese along bottom edge] | sign/other |
| 0249C44 | sheet_004 | コラムんメニュー／ダイナメール／めいしこうかん／アイテムこうかん／ダイナこうかん | Koramun menu / Dyna mail / Exchange business cards / Exchange items / Exchange Dynas | menu-label |
| 024AF04 | sheet_004 | アイテムこうかん／じぶんのあいてのアイテム | Exchange items / Your items / Partner’s items | menu-label |
| 024B834 | sheet_004 | ダイナこうかん／じぶんのあいてのダイナ | Exchange Dynas / Your Dynas / Partner’s Dynas | menu-label |
| 024C1C4 | sheet_004 | アドレス／データ／[大型文字は一部判読不能] | Address / Data / [large lettering partly illegible] | menu-label |
| 024D4B4 | sheet_004 | めいしこうかん／めいしの／じぶんの | Exchange business cards / Business card… / Your… | menu-label |
| 025D924 | sheet_004 | ていさつ／ちりょう／いどう／とくしゅ／こうげき (the sweep table had it as 0250924) | Scout / Cure / Move / Special / Attack | menu-label |
| 025E304 | sheet_004 | ダイナはいち／[判読不能]せんたく／いどう／こうげきエリア／たいきエリア | Dyna placement / Select [illegible] / Move / Attack area / Standby area | menu-label |
| 03B25A4 | sheet_019 | ついか／はずす／［断片・判読困難］ | Add / Remove / [fragmented, unclear] | menu-label |
| 03B29B4 | sheet_019 | チームへんせい | Team setup | menu-label |
| 03B3164 | sheet_019 | せつぞくちゅう／つながっています／つながっていません／シンプルモード／［断片・判読困難］ | Connecting / Connected / Not connected / Simple mode / [fragmented, unclear] | menu-label |
| 03B3624 | sheet_019 | せつぞくかくにん／ルールせんたく／バトルアニメせってい | Check connection / Select rules / Battle animation settings | menu-label |
| 03B7F64 | sheet_019 | だい／ターン／［小字判読困難］ | Ordinal prefix / Turn / [small text unclear] | menu-label |
| 03B9D04 | sheet_019 | charset | Character set | font/charset |
| 03D5DB4 | sheet_020 | charset | Character set | font/charset |
| 03D7FD4 | sheet_020 | Rボタンをおすとゲームのせつめいが／ミニゲーム／のあそびかた／はじめるＡＢスタート／［断片・判読困難］ | Press R for game instructions / Minigame / How to play / Start; A, B, Start / [fragmented, unclear] | menu-label |
| 0432534 | sheet_021 | charset (staff roll kana, done: "Staff roll") | Character set | font/charset |
| 0449734 | sheet_021 | ガチャステ！／ダイナデバイス／ブルー／レッド／［小字判読困難］ | Gachasute! / Dyna Device / Blue / Red / [small text unclear] | title/logo |

Counts by kind: menu-label 29, font/charset 10, sign/other 2, button-hint 2, title/logo 1. Total 44 blocks.
