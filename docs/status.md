# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (boot, script, story-event, tutorial-replay menu, reception, every game mode
  and the leftover debug menu work; endings/credits and in-game shops with real data not yet). Last build: none yet.
- **Done:**
  - Step 0 and phase 1 recon (see `docs/re/`: text.md, compression.md, graphics.md).
  - Phase 2 (`docs/re/debug.md`): `tools/debug/warp.lua` kinds `boot`, `newgame`, `script`, `event`, `field`,
    `menu` (tutorial replay, ~26k frames, 20 menu rows), `fscript` (reception talk script swapped), and new this
    session `mode`: the top-level game mode (0x03001AD0, 50 modes) is replaced at a cold boot. Mode 50 is the
    leftover **AGB SYSTEM DEBUG MENU** (city setup with scenario field, battle setup + real battle, monster set,
    world map, subway demo, free battle, minigames, sound test, data view). 55 `mode`/`dbg_` rows: every PDA app,
    item auction/sell, Dyna shop, customise, development status, team, placement, roulette, rewards, link screens,
    business cards, minigame titles and level select, opening movie, title, battle test.
  - `tools/debug/regen.py`: now resolves `--out/--states` to absolute paths (relative ones landed nowhere, since
    Mesen runs in tools/mesen). All 55 mode rows verified by cold-boot regen with hold shots (work/qa/warpm,
    warpm2). The full `regen.py --jobs 2` run of every row: see the result line below.
- **Next (phase 2):**
  1. Endings and credits: decode the event pick after 0x0801EDFE (flags 0x4F-0x54 + room 0x13 -> event 0x4F, more
     cases follow; events 72-87 -> scripts 147-153, 796-817) and add event rows that play the final battle,
     epilogue and any staff roll (BGM スタッフロール exists in the sound test; no staff text in SJIS, so credits are
     graphics if present). Try the debug menu's CITY SETUP `SCENARIO = %03d` field as a chapter warp.
  2. Shops with real data: mode rows run with an empty save. For text coverage, enter modes 13/15/16/17/20/21/23/33
     from the post-tutorial state (e.g. hook the dispatcher when the field task ends, or find the building-entry
     code that calls set_mode 0x08002C1C; callers listed by `disasm.py xref ... 08002C1C`).
  3. Story battle (event 7 / colosseum 102-105/150-151) with GOD/NOENC if needed; FAST poke to fill the database.
  4. Then phase 2 is done: every row reached from a cold boot with a shot. Phase 3 (identity build) next.
- **Later phases need:** the runtime font (check 0x21C414/0x224B44/0x225EC4 first) and a full opcode table for the
  script (inline strings shift jumps; handler table 0x080D2034, 59 ops). Graphics text seen: ポーズ (pause), the
  opening movie's green spec panels, debug menu (romaji, debug build only: leave).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
