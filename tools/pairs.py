"""pairs.py: write reviewer pairs files (JP / EN, in script order) for the phase-6 review pass.

    python -X utf8 tools/pairs.py [--size 300] [--out work/review/pairs]

One file per chunk of translated entries (status done), never crossing a script/ file:
  >> id | spk N | JP        (a line break in the text is shown as " / ")
  EN
Entries are consecutive, so the lines around each entry are its context.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def flat(s):
    return s.replace("\n", " / ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=300)
    ap.add_argument("--out", default=str(ROOT / "work" / "review" / "pairs"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.txt"):
        old.unlink()
    n = 0
    for f in sorted((ROOT / "script").glob("*.json")):
        done = [e for e in json.loads(f.read_text(encoding="utf-8")) if e.get("status") == "done"]
        for i in range(0, len(done), a.size):
            chunk = done[i:i + a.size]
            n += 1
            lines = []
            for e in chunk:
                spk = f" | spk {e['speaker']}" if "speaker" in e else ""
                lines.append(f">> {e['id']}{spk} | {flat(e['jp'])}")
                lines.append(flat(e["en"]))
            name = f"{n:02d}_{f.stem}_{chunk[0]['id']}.txt"
            (out / name).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            print(f"{name}\t{len(chunk)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
