# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (boot, script and story-event warps work; menus, shops, minigames, endings
  not yet reachable). Last build: none yet.
- **Done:**
  - Step 0 and phase 1 recon (see `docs/re/`: text.md, compression.md, graphics.md).
  - Phase 2 so far (`docs/re/debug.md`): `tools/debug/warp.lua` boots cold, fills the profile form by RAM-gated
    input, and lands on: boot screens (date, form, keyboard, title), new game (intro), any script by index (kind
    `script`, hijacks start_script 0x0801A9D4), any story event whose pick case is decoded (kind `event`: sets the
    2-bit story flags at 0x0200A300 + day count, walks into the city). Verified with shots: date, form, keyboard,
    intro, e7, e13, e19, e33, e40, e56, s33, s152, s153, battle_place (`work/qa/w_<scene>/`). Logs `TEXT <ptr>` for
    every message string (phase-8 text coverage). `tools/scriptinfo.py` lists all 834 scripts with first lines.
- **Next (phase 2):**
  1. Menus: after the tutorial skip the player has no Dynas and a visiting challenger forces a battle (see
     debug.md "Field and menus"). Find the party/Dyna struct (script 1's tutorial gives them; RAM-diff before/after
     the tutorial with `ramsearch.py`), poke it in the `field` kind, then add scenes for the Start menu and every
     submenu (system, items, party, training, data/save, settings, map, Dyna Keeper), the sector build menu, shops
     (item buy/sell, script 765/771), device development (factory), the PDA tools (schedule, money log, address
     book) and link menus (mail, cards, exchange; may need a link-cable stub).
  2. Events 72-87 (scripts 147-153, 796-817: final chapter, ending, post-game rematches): decode the pick after
     0x0801EDFE; the e70 warp (needs previous room != 15 and 0x0801A988) did not fire.
  3. Battles (story, free battle, colosseum tournament scripts 102-105/150-151), minigames (ミニゲーム１２３),
     credits. Add `GOD`/`NOENC` if battles need it.
  4. A one-command regen of all scene shots/states (`tools/debug/regen.py`, parallel jobs, asserts ARRIVED in
     log.txt), then the done-when check: every scenes.tsv row reaches its scene from a cold boot with a shot.
- **Later phases need:** the runtime font (not in the ECD sweep's kana charsets? check 0x21C414/0x224B44/0x225EC4
  first) and a full opcode table for the script (inline strings shift jumps; handler table 0x080D2034, 59 ops).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
