"""List the event scripts (file at ROM 0x702BC4): index, ROM offset, size, message count, first lines.

    python -X utf8 tools/scriptinfo.py [--rom ROM] [--first N] [--all] [IDX ...]

Messages are found by the message-op pattern (02 00 00 00 <speaker u16> SJIS text 00), as in docs/re/text.md;
this is a survey aid for the debug tool's scene list, not the extractor.
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / 'rom' / 'Gachasute! Dyna Device Blue (Japan).gba'
BASE = 0x702BC4
COUNT = 834

MSG = re.compile(rb'\x02\x00\x00\x00(..)((?:[\x81-\x9f\xe0-\xfc][\x40-\xfc]|[\x20-\x7e])+)\x00', re.S)


def scripts(rom):
    offs = [int.from_bytes(rom[BASE + 4 * i:BASE + 4 * i + 4], 'little') for i in range(COUNT + 1)]
    for i in range(COUNT):
        yield i, BASE + offs[i], offs[i + 1] - offs[i]


def messages(body):
    for m in MSG.finditer(body):
        spk = int.from_bytes(m.group(1), 'little')
        yield spk, m.group(2).decode('cp932', 'replace')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', default=str(ROM))
    ap.add_argument('--first', type=int, default=1, help='messages to show per script')
    ap.add_argument('--all', action='store_true', help='show every message')
    ap.add_argument('idx', nargs='*', type=int)
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    want = set(a.idx)
    for i, off, size in scripts(rom):
        if want and i not in want:
            continue
        msgs = list(messages(rom[off:off + size]))
        shown = msgs if a.all else msgs[:a.first]
        text = ' / '.join(f'[{spk if spk != 0xFFFF else "-"}]{t}' for spk, t in shown)
        print(f'{i:3d} {off:06X} {size:5d} m{len(msgs):3d} {text}')


if __name__ == '__main__':
    main()
