"""insert.py: script/ JSON -> message bytes for the build (docs/re/font.md, docs/re/text.md).

    from insert import load_entries, message_scripts
    scripts = message_scripts(rom, load_entries(), marker=False)

Per message entry: "en" set -> vwf.encode_en(en); marker mode and status "todo" -> a marker (its id plus filler
text, one marker line per original line, codes kept); otherwise the original bytes.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import script  # noqa: E402
import vwf  # noqa: E402

SCRIPT_DIR = ROOT / "script"
FILLER = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. " * 3
MARKER_PX = 184     # marker line width; the width gate measures the real budget (docs/re/font.md)
LINE = re.compile(r"(\{KP\}\n|\n)")
TAG = re.compile(r"\{[^{}]*\}")


def load_entries(directory=SCRIPT_DIR):
    """-> {id: entry} over every script/*.json file."""
    out = {}
    for path in sorted(directory.glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8")):
            out[e["id"]] = e
    return out


def fill(prefix, px):
    """prefix + filler words up to px pixels."""
    s = prefix
    for word in FILLER.split(" "):
        cand = (s + " " + word) if s else word
        if vwf.width(cand) > px:
            break
        s = cand
    return s


def marker(entry_id, jp, px=MARKER_PX):
    """Marker text in text.py form: each original line becomes filler (the first starts with [id]); KP/KN, colour
    and register codes stay where they were (codes inside a line move to its end)."""
    parts = LINE.split(jp)
    out = []
    first = True
    for i, part in enumerate(parts):
        if i % 2:                       # a separator: keep it
            out.append(part)
            continue
        tags = TAG.findall(part)
        regs = [t for t in tags if t.startswith("{%")]
        rest = [t for t in tags if not t.startswith("{%")]
        reg_px = 8 * 6 * len(regs)      # room for the expansion (6 full-width cells each)
        if not part.strip() and not tags:
            out.append(part)
            continue
        text = fill(f"{entry_id}:" if first else "", max(px - reg_px, 0))
        first = False
        out.append(text + "".join(" " + r for r in regs) + "".join(rest))
    return "".join(out)


def message_text(entry, original, marker_mode):
    if entry is not None and entry.get("en"):
        return vwf.encode_en(entry["en"])
    if marker_mode and entry is not None and entry.get("status") == "todo":
        return vwf.encode_en(marker(entry["id"], entry["jp"]))
    return original


def string_marker(entry, wide=None):
    """Marker for a string-region entry: its offset (5 hex digits) then filler to the Japanese line's width
    (8 px per full-width char), or to `wide` px (the width-gate build), per line; codes kept at the line ends."""
    tag = entry["id"][2:]
    out, first = [], True
    for i, part in enumerate(LINE.split(entry["jp"])):
        if i % 2:
            out.append(part)
            continue
        tags = TAG.findall(part)
        plain = TAG.sub("", part)
        if not plain.strip() and not tags:
            out.append(part)
            continue
        px = wide or max(8 * len(plain), vwf.width(tag) if first else 0)
        text = fill(tag if first else "", px)
        first = False
        out.append(text + "".join(tags))
    return "".join(out)


def string_bytes(entry, marker_mode):
    """-> encoded bytes (NUL NUL terminated) for a string entry, or None to keep the original. marker_mode:
    False, True (markers at the JP width), a pixel width for every marker line, or a dict {id: px} (those ids
    wide, the rest at the JP width: a size-1 field given 240 px overruns its object and hangs the form)."""
    if entry.get("en"):
        txt = entry["en"]
    elif marker_mode and entry.get("status") == "todo":
        if isinstance(marker_mode, dict):
            wide = marker_mode.get(entry["id"])
        else:
            wide = None if marker_mode is True else marker_mode
        txt = string_marker(entry, wide)
    else:
        return None
    return vwf.encode_en(txt) + b"\0\0"


def place_strings(out, entries, marker_mode, free_at, free_end):
    """Write every changed string: in its slot when it fits, else at free_at (4-aligned) with each pointer word
    rewritten. Returns (next free offset, number in place, number moved)."""
    inplace = moved = 0
    for e in entries.values():
        if not e["id"].startswith("t"):
            continue
        raw = string_bytes(e, marker_mode)
        if raw is None:
            continue
        at = int(e["id"][1:], 16)
        if len(raw) <= e["slot"]:
            out[at:at + e["slot"]] = raw + bytes(e["slot"] - len(raw))
            inplace += 1
            continue
        if free_at + len(raw) > free_end:
            raise ValueError(f"string {e['id']} does not fit in the free space")
        out[free_at:free_at + len(raw)] = raw
        for p in e["ptrs"]:
            p = int(p, 16)
            out[p:p + 4] = (0x08000000 + free_at).to_bytes(4, "little")
        free_at = (free_at + len(raw) + 3) & ~3
        moved += 1
    return free_at, inplace, moved


def message_scripts(rom, entries, marker=False):
    """-> the 834 op lists with message texts replaced."""
    scripts = script.unpack(rom)
    for i, ops in enumerate(scripts):
        k = 0
        for op in ops:
            if op.code != script.MSG:
                continue
            e = entries.get(f"s{i:03d}.{k:02d}")
            op.text = message_text(e, op.text, marker)
            if len(op.text) % 2:
                op.text += bytes([vwf.PAD])
            k += 1
    return scripts
