# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (boot, script, story-event, tutorial-replay menu and reception warps work;
  shop/colosseum/factory UIs, battles, minigames, endings not yet reachable). Last build: none yet.
- **Done:**
  - Step 0 and phase 1 recon (see `docs/re/`: text.md, compression.md, graphics.md).
  - Phase 2 (`docs/re/debug.md`): `tools/debug/warp.lua` kinds `boot`, `newgame`, `script` (hijack at boot, now
    takes `N route`), `event`, `field`, and new this session:
    - `menu`: replays the whole tutorial from a cold boot (A-mash, then `tools/debug/tutorial_route.txt`, ~26k
      frames, deterministic), then the scene's route. 20 menu rows (every field-menu tab and leaf, pause).
    - `fscript`: tutorial replay, walk into the reception, swap the receptionist's talk script (633) for script N.
      Shows any script's text in a lit room (greeting texts of shops 690/705/723/762, game over 275, Dyna Keeper).
  - `tools/debug/regen.py`: one command runs all/named scenes in parallel (4 jobs; 8 made Mesen runs die), asserts
    ARRIVED + HOLD in the log, writes `work/qa/warp/<scene>/hold.png` + `work/states/<scene>.mss`, retries once.
  - `tools/debug/probe_routes.py`: try several routes from one state, one contact sheet (menu mapping).
  - Verified by cold-boot warp with shots this session: menu, menu_party_equip, menu_resident_map, pause, the five
    `*_greet`/gameover fscript rows. The other menu rows were verified with the same routes from the post-tutorial
    state (`work/qa/pm1`, `pm2`) but not yet by cold-boot regen.
- **Next (phase 2):**
  1. Run `python -X utf8 tools/debug/regen.py --jobs 4` and check every row (the full run this session was stopped
     by Claude Code for low system memory, not by a failure; try `--jobs 2` if memory is short). Fix any row whose
     hold shot is wrong.
  2. Shop/colosseum/factory UIs are native code entered from buildings: the tutorial picks Item Shop at a sector
     but no shop shows on the map yet (maybe built after a day passes: try sleeping/day advance, or set the days
     u8 0x0200A7A4). Find the building entry (room ids) and add scenes: item shop buy/sell, colosseum, device
     development (event 13 / script 74 gives the factory tutorial), Gachasute, travelling merchant visitor
     (scripts 780-795 visitors; 762 merchant).
  3. Events 72-87 (scripts 147-153, 796-817: final chapter, ending, post-game): decode the pick after 0x0801EDFE.
  4. Battles (story, free battle, colosseum 102-105/150-151; battle_place exists), minigames (ミニゲーム１２３),
     credits. Add `GOD`/`NOENC` if needed. Database entries show "---" until seen: a FAST poke to fill them helps
     phase-8 text coverage.
- **Later phases need:** the runtime font (check 0x21C414/0x224B44/0x225EC4 first) and a full opcode table for the
  script (inline strings shift jumps; handler table 0x080D2034, 59 ops). Graphics text seen: ポーズ (pause).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
