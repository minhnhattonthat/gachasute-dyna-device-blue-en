# Event-script bytecode (phase 3)

Code: `tools/script.py` (parse, repack, `verify`, `dis`). Interpreter: docs/re/debug.md (handler table 0x080D2034,
dispatch loop 0x0801E5DA; each handler gets `&pc`, advances it, returns nonzero to yield).

## Op lengths - verified
- **All 834 scripts parse** with the table below: every script ends on op 0 followed by < 16 zero bytes, every
  jump lands on an op start, and the repack is byte-identical (`tests/test_script.py`).
- **Runtime check**: `tools/lua/opstep.lua` logs (op, pc, new pc) for every op the game runs; `script.py verify
  --logs work/qa/ops` checks each logged pc is an op start of the parse and each step equals the parsed length
  (or the jump target). Runs: `tools/debug/opstep_run.py SCENE..`.
- 2824 message ops, 574 jumps.
- Static: lengths read from the handlers (pc register `adds #2` chain up to the `str` back to `[r0]`).

| Bytes | Ops |
|---|---|
| 2 | 0 (end: clears the running script), 4, 21, 25, 26, 36, 37, 38, 39, 40, 41, 43, 45, 49, 52, 58 |
| 4 | 1, 3, 5, 15, 16, 19, 28, 30, 33, 35, 48, 50, 51, 54, 57 |
| 6 | 6, 17, 18, 20, 24, 31, 32, 34, 42, 44, 46, 55, 56 |
| 8 | 7-13, 27, 53 |
| 12 | 14 (two arg layouts, both 12), 47 |
| 14 | 22, 29 |
| 4 + 10n | 23 (n = u16 at +2) |
| variable | 2 message |

Known meanings: 2 message (`02 00 <flag> <speaker> SJIS 00 00`, handler 0x0801AA84 -> drawer 0x08013488), 20 set
story flag, 7-12 compare `0x08013D60(var)` with `value` and jump (one comparison each: ==, !=, and the four
orderings; exact mapping not needed for repacking), 13 jump always, 57 set the skip target, 58 clear it, 0 end.

## Jumps - verified
- Ops 7-13: `op var value rel`; target = address of the op + (rel & ~1) (handler 0x0801B0D8).
- Op 57: `57 rel`; stores op address + (rel & ~1) at 0x02001C6C; the dispatcher jumps there when the player
  presses the skip button (0x0801E598). Op 58 clears it.
- No other handler computes a pc from an argument (searched the handlers for `lsrs #1; lsls #1` + add, and the
  runtime logs show no other non-sequential step). Jumps are relative, so `build_script` remaps each target to
  its op's new offset.

## Messages
- The handler skips the text by scanning byte by byte for the first `00 00` pair from the text start and resumes
  2 bytes after it. Original text is always even-length (SJIS pairs, 2-letter codes), encoded `text 00 00`.
- Exception: script 341's last message has odd-length text, so the following op 5 and op 0 sit on odd addresses
  (LDRH reads them rotated; it works by luck). Repack keeps unedited messages byte-for-byte.
- **Insertion rule**: English text must be padded to an even byte length (`message_bytes` refuses odd text);
  the pad byte is decided with the font in phase 5.

## File placement - verified
- The directory word at ROM 0x0BBDF0 is the only pointer to the file (xref of 0x08702BC4; the other 0x0870xxxx-
  0x0874xxxx words in the ROM are code bytes or graphics data).
- The packed file goes back to 0x702BC4 if it fits (0x44F80 bytes), else to the zero-filled free space at
  0x747DA0-0x800000 with the directory word rewritten (`tools/build.py`). **Verified in game**: `build.py --stress`
  appends ＊ to 2823 of the 2824 messages (all but script 341's odd one; the file grows past its slot and moves); warp e7 on that build runs the script from
  0x0874xxxx, shows the ＊, and the following menu opens (work/qa/stress/e7).
