# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool (phase 1 recon done 2026-11-14). Last build: none yet.
- **Done:**
  - Step 0: rom.sha1, tools/check.py + pre-commit (failing test rejects a commit), guard hook (canary blocked),
    MesenCE 2.2.1 + GBA BIOS in tools/mesen, smoke boot of the original ROM with input and a Lua probe.
  - Phase 1 recon: `docs/re/text.md` (SJIS, script container at 0x702BC4 with 834 scripts, message op, control
    codes, string regions, address database), `docs/re/compression.md` (ECD LZSS codec, verified on all 3114
    blocks; `tools/ecd.py`, test in `tests/test_ecd.py`), `docs/re/graphics.md` (graphics-text survey from the
    static sweep `tools/gfx_sweep.py` + boot tour).
- **Next (phase 2, debug tool):** reach scenes from a cold boot without a playthrough. Leads: the profile form
  (name / nickname / phone / email are mandatory; navigation is fiddly, so poke the profile RAM or skip the form
  with Lua instead); the event script table (run script N directly: find the script-runner entry that takes an
  index into the 0x702BC4 table); a leftover test script (script 0 = テスト１/２/３) hints at debug code.
  Scene list in `tools/debug/scenes.tsv`, warp in `tools/debug/warp.lua`.
- **Later phases need:** the runtime font (not in the ECD sweep's kana charsets? check 0x21C414/0x224B44/0x225EC4
  first) and a full opcode table for the script (inline strings shift jumps).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the address database (~2.6 MB of real Japanese place names, 0x44C754):
  default plan is Hepburn romanization from Japan Post KEN_ALL readings by postal code; see docs/re/text.md.
