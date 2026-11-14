# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| text.md | SJIS encoding, resource directory, event-script container and message op, control codes, string regions, address database | container + encoding verified; opcodes beyond the message op, menu pointer tables and the font not yet |
| compression.md | ECD LZSS codec, IMG/PLT/SCR payloads, the single BIOS LZ77 block | verified (all 3114 blocks decode; `tests/test_ecd.py`) |
| graphics.md | graphics-text survey: 44 ECD blocks with Japanese, method and gaps | static sweep complete; tour only to the profile form |
