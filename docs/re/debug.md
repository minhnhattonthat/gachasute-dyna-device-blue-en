# Debug tool: story flags, events, script start (phase 2)

Tool: `tools/debug/warp.lua` + `tools/debug/scenes.tsv` (kinds: boot, newgame, script, event, field). Command in
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

## Field and menus (open)
- After the tutorial skip the player has no Dynas, and a visiting challenger (script 791, from 0x080654A2 when
  0x08018FBC returns 0) walks up in the city and starts a battle (Dyna placement, script 181) even when its script
  is replaced: the field kind lands in that battle. Start/Select/L/R in the reception during the tutorial open
  nothing. To reach menus: give the player Dynas (find the party struct; the tutorial's script 1 hands them out) or
  let the tutorial run with the intro scene and mash.
