# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build next (phase 2 debug tool done 2026-11-15). Last build: none yet.
- **Done:**
  - Step 0 and phase 1 recon (see `docs/re/`: text.md, compression.md, graphics.md).
  - Phase 2 (`docs/re/debug.md`): `tools/debug/warp.lua` + `scenes.tsv`, 147 rows, every one reached from a cold
    boot with a hold shot (`tools/debug/regen.py`). Kinds: `boot`, `newgame`, `script`, `event`, `field`, `menu`
    (tutorial replay + menu routes), `fscript` (reception talk swap), `mode` (top-level mode forced at boot, incl.
    the leftover AGB SYSTEM DEBUG MENU), and new this session:
    - `resume`: the game's continue handler 0x080522D4 restarts the story script in progress from the flags; rows
      r2..r817 (39) cover every branch: chapter resumes, final chapter 147-152, epilogues 153/155, 154.
    - Ending and credits: script 152 (final battle aftermath) runs into mode 22 = the staff roll (graphics credits,
      kana staff names, last card ©2002 スマイルソフト). Rows `ending_full` (152 mashed into the roll), `credits`
      (whole roll), `credits_mid`.
    - `dmode`: tutorial data, then quit, and the next set_mode becomes mode N: shops and menus with real party,
      money and items (d_customize, d_auction, d_dyna_shop, d_item_sell, d_kit, d_dev_status, d_shop_list,
      d_placement, d_team, d_get, d_dyna_status).
    - `battle_place_trap`: field battle placement with a Dyna and its trap set.
  - Verified this session: 42 resume/credits rows (work/qa/warpr) and 12 dmode/battle rows (work/qa/warpd), all
    reached. A 10-row sample of the older kinds after the warp.lua changes was stopped by the host for low memory
    (other projects' emulators were using ~7 GB) after `battle_place` passed; the new code is guarded by kind, and the
    resume/dmode runs go through the shared boot, form, title and tutorial paths. First thing next session: run
    `tools/debug/regen.py --jobs 2` over all rows when memory allows.
- **Next (phase 3):** identity build: unpack then repack the script container (file at 0x702BC4, 834 scripts) and
  any compressed blocks with no edits, byte-identical as a test (`references/pipeline.md` §Identity).
- **Later phases need:** the runtime font (check 0x21C414/0x224B44/0x225EC4 first) and a full opcode table for the
  script (inline strings shift jumps; handler table 0x080D2034, 59 ops). Graphics text: ポーズ, the opening movie's
  green spec panels, debug menu (romaji, debug build only: leave), and the **staff roll** (mode 22): its kana are
  not SJIS in the ROM, find their encoding or tiles (add to the graphics-text survey).
- **Known debug-tool gaps (non-blocking):** the field battle placement has no known "done" input (A places Dyna and
  trap per slot, then it loops to Dyna 1; START/SELECT/R do nothing), so a field battle past placement is not
  reached; the debug menu's BATTLE START (`dbg_battle`) reaches a real battle. Runs without `--sav` share
  `tools/mesen/Saves/<rom>.sav` (menu_saving writes it).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
