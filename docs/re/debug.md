# Debug tool: story flags, events, script start (phase 2)

Tool: `tools/debug/warp.lua` + `tools/debug/scenes.tsv` (kinds: boot, newgame, script, event, field, menu, fscript, mode,
resume, dmode). Probe for flag experiments from a state: `tools/debug/probe_flags.lua`. Command in
AGENTS.md. Each warp logs `WARP <stage>`, `SCRIPT <n> lr=.. room=..`, `ARRIVED <scene>`, and `TEXT <ptr>` for every
string the message drawer gets (text-coverage source for phase 8).

## Boot (verified by warp runs `date`, `form`, `keyboard`, `title`, 2026-11-14)
- No save: Smilesoft logo -> date prompt (code at 0x08040C28 loads its string) -> profile form (no title menu yet).
- Profile form idle key read: 0x0803C6B4 (runs only while no popup is up). Mandatory fields: name and nickname only
  (yellow icons); keyboard: A types the char under the cursor, START confirms, B cancels. Gender: A. Down from the
  postal-code row jumps to page 2 and stops on おわる; A there saves and goes to the Gachasute intro + title.
- Title: Start (A does nothing). With no save, Start goes straight into a new game (script 1).

## Scripts (verified)
- `start_script(r0 = file 2, r1 = index)` at **0x0801A9D4**; resource lookup `0x08003074(file, index)` reads the
  directory at 0x080BBDE8. Running script state at 0x02001C60 (+0 pc, +4 start, +0x10 current opcode, 0 = none).
- Interpreter: opcode handlers u32 table at **0x080D2034** (59 opcodes, handler(&pc) returns nonzero to yield),
  wait/continue table at 0x080D1F48, dispatch loop at 0x0801E5DA.
- Op 2 = message: `02 00 <u16 flag> <i16 speaker> SJIS..00`; handler 0x0801AA84 calls the drawer **0x08013488**
  (r0 = string). Op 0x14 = set flag `14 00 <flag> <value>` (handler 0x0801B6D8 -> set_flag). Op 0x0F reads flags.
- Hijacking r1 at 0x0801A9D4 runs any script from a cold boot (kind `script`); it plays in whatever room is
  loaded (the reception), so actors and the map can be wrong. Use `event` where an event exists.

## Story flags and events (verified with warps e7, e13, e19, e33, e40, e56)
- Flags: 2 bits each at **0x0200A300**, flag n in byte n>>2 at bit (n&3)*2. get 0x0801A930, set 0x0801A908.
- Flag 1: 0 = new game (intro runs), 3 = intro/tutorial done. Flag e (2..71) = state of story event e: 3 = pending,
  1/2 = in progress, 0 = done/never.
- Event pick at each room load: **0x0801E868** loops e = 2..71 with a jump table at 0x0801E8F0; a case fires when
  flag e is 3 (some cases: 0), a neighbour flag is 0, days (u8 at **0x0200A7A4**, getter 0x080109A0) exceed a
  threshold, and the room (i16 **0x02001C54**; 0 = city, 15 = reception, 0x12/0x13 others; previous room at
  0x02001CA0) matches. The result indexes the i16 table **0x080CED94** (event -> script; 90 entries) and the room
  load (0x0804FF9A) starts that script.
- Events with a jump-table case: 7 13 19 20 23 26 33 34 35 36 40 43 44 51 54 55 56 57 60 63 64 65 69 70 71. Room 0x13
  cases (20, 36, 57) test flag e == 0 and need room 0x13; 65 needs room 0x12; 51 and 70 also call 0x0801A988 and
  70 needs previous room != 15 (the e70 warp did not fire: not in the scene list yet). Events 72-87 (scripts
  147-153, 796-817) are picked after the switch (0x0801EDFE on), not decoded yet.

## Tutorial replay, menus, reception (verified 2026-11-14, `tools/debug/regen.py`)
- Kind `menu`: new game, A every 40 frames for 2997 frames from script 1, then the recorded route
  `tools/debug/tutorial_route.txt` (made with play.py from a state at f6000; emulation is deterministic, so it replays
  from a cold boot): Gachasute walk (script 10 "press A in front of the Gachasute": the machine is top right of the
  reception), address-book pick, naming two Dynas (アララフ, トリマン: START confirms), Dyna Keeper, the house (talk to
  the Dyna, pick つれていく), the sector-build menu (Item Shop 300 picked; it does not show on the map yet), ending on
  the city road south of the reception at f25866 with 4300 bits. Then the scene's arg route plays.
- Field controls: B = menu bar (cyclic tabs; opens on データベース): じゅうみん (ステータス そうび にがす マップ),
  データベース (ダイナ デバイス キーワード), システム (データセーブ バトルアニメ おわる), もちもの (つかう ならびかえ すてる),
  パーティ (ステータス そうび かえらせる にがす). START = pause (ポーズ, a graphic).
- Reception from the road: `90 up;50 right;60 up`. Its load runs script 331 (fades the room in, lr 0x0805003B).
  Talking to the receptionist (`60 up;a`) runs 633, then a native menu runs 635/638 (Dyna Keeper). Kind `fscript`
  swaps 633 for any script: the script's text shows in the reception, but shop/colosseum/factory UIs are native code
  entered from their buildings, so those scripts give greeting text only.
- Shop texts: 690 item shop, 705 colosseum, 723-741 device development, 762-772 travelling merchant, 275 game over.

## Game modes and the leftover debug menu (verified 2026-11-14, kind `mode`, 55 rows)
- Top-level mode: u32 **0x03001AD0** (+ a per-mode byte at 0x03001830[mode]); set by `set_mode(r0 mode, r1)` at
  0x08002C1C. Dispatcher **0x08004DB8**: mode 0 = power-on init then mode 29 (logo); modes 1..50 index the jump
  table **0x08004DF0**, each case starts that mode's task via 0x080028A4(task). Writing the mode var mid-task does
  nothing; kind `mode` replaces the dispatcher's first pick (r0 at **0x08004DD4**) at a cold boot.
- Modes (cold boot, so no profile/party/items: lists are empty): 1 date prompt, 2-8 PDA apps (profile card, lists,
  calendar, schedule, calculator), 9 Dyna Pad frame, 10/14/47 field (house room), 11 Dyna status, 12 garbage (needs
  data), 13 ダイナカスタマイズ, 15 アイテムオークション, 16 Dyna list shop, 17 アイテムばいきゃく, 18 subway demo,
  19 blank, 20 kept kits, 21 かいはつじょうきょう, 22 colosseum crowd, 23 shop list + sector map, 24/43 めいしこうかん,
  25/26/38 none, 27 3D field, 28/35 ダイナはいち, 29 logo, 30-32 link (TSUUSIN), 33 チームへんせい, 34 roulette,
  36 ゲット list, 37 battle (garbage without setup), 39 title, 40/42 minigame titles, 41 minigame level select,
  44 profile form, 45 PDA page, 46 opening movie (then 39), 47 map test, 48 battle test (CASE=), 49 DATA VIEW,
  **50 = "AGB SYSTEM DEBUG MENU"** (strings at 0x0AF6F0, code 0x08008820..0x0800AD9C).
- Debug menu rows (cursor starts on row 1, wraps): 0 GAME START 1 PDA SYSTEM 2 MONSTER CITY (CITY SETUP MENU: map,
  money, monster num, scenario; A on START = a game in the city) 3 BATTLE SYSTEM (BATTLE SETUP MENU; up + A =
  BATTLE START, a real battle) 4 TACTICS (MONSTER SET MENU) 5 TSUUSIN (TOOL MONSTER SET MENU) 6 RASTER TUSIN
  (title) 7 ETC (first entry = item auction) 8 WORLD MAP (battle board) 9 SUBWAY DEMO 10 COLO EVENT DEMO
  (フリーバトル) 11 MINI GAME = n (right changes n) 12 TEST2 13 TEST1 14 SOUND MENU 15 DATA VIEW.
  The CITY SETUP `SCENARIO = %03d` field is a possible chapter warp (not tried yet).
- Text: no staff names exist as SJIS text (no スタッフ/ディレクター strings); the sound test lists a スタッフロール
  BGM, so credits, if any, are graphics. Script 153 (epilogue) ends at once when hijacked; the ending chain is in
  the event pick after 0x0801EDFE (flags 0x4F-0x54 with room 0x13 -> event 0x4F, then more cases), not decoded.

## Continue path, endings and credits (verified 2026-11-15, kinds `resume`, `dmode`)
- The event pick's switch covers events 2..71 only; the code after 0x0801EDFE adds side events 79 (room 0x13,
  flag 79 == 2 or flags 81-84 == 1) and 81-84 (reception, random, flag 95 == 0) and 86. Events 72-78 (scripts
  147-153) are never picked at a room load.
- The field init (its branch at **0x08055D84**) branches on an entry code in r4: 57 = new game (-> 0x0800DDDC,
  0x08042518, then the room-load event pick), 0x27 with flag 3 == 2, 0x2E, 0x33, 0x37 with flag 2 == 2, 0x3B (59),
  0x32 with flag 14 == 2 -> **continue handler 0x080522D4** (via 0x080522B0, table 0x080D32C4[2]).
- The continue handler restarts the story script in progress, first match wins: flag 2==2 -> 2, 2==1 -> 3, 3==2 -> 4,
  9==2 -> 35, 14==2 -> 78/79/80 (flag 15 2/1/else), 24..31==1 -> 98, 101-105, 36 -> 112, 41 -> 115, 45..49 -> 119-123,
  61 -> 135, 65==2 -> 140, 66 -> 141, 67 -> 142, 71 -> 147, 73 -> 149, 74 -> 150, 75 -> 152 (flag 93 == 0) / 151,
  89==2 -> 756, 89/90/91/92==1 -> 758/759/760/761 (flag 93 != 0: 757), 86 -> 817, 95==3 -> 153 or, with the score
  0x0801A6C4 > 99, 155; else 154 (アトラクション しゅうりょう). Kind `resume` (rows r2..r817) sets entry 59 on a new
  game and pokes the flags, so each script starts through this handler.
- Ending: script 152 (final battle aftermath) ends in **mode 22 = the staff roll**: credits are drawn as graphics
  (kana staff names, e.g. ゲームデザイン あかいし たつや) over illustrations, ~9500 frames, last card ©2002 スマイルソフト.
  Mode 22 forced at a cold boot plays the same roll (rows `credits`, `credits_mid`). The credits text is not SJIS
  in the ROM: find its encoding or tiles before phase 8 (graphics text list).
- System > おわる > yes quits the field to mode 2 (PDA) -> 46 -> 39. Kind `dmode` replaces that set_mode
  (0x08002C1C) call with mode N, so shop and menu modes open with the tutorial's party, money and items in RAM.

## Field and menus (open, older notes)
- After the tutorial skip the player has no Dynas, and a visiting challenger (script 791, from 0x080654A2 when
  0x08018FBC returns 0) walks up in the city and starts a battle (Dyna placement, script 181) even when its script
  is replaced: the field kind lands in that battle. Start/Select/L/R in the reception during the tutorial open
  nothing. To reach menus: give the player Dynas (find the party struct; the tutorial's script 1 hands them out) or
  let the tutorial run with the intro scene and mash.
