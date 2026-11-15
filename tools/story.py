"""story.py: write the phase-9 story-pass chapter files (chapter list in docs/synopsis.md).

    python -X utf8 tools/story.py [--out work/qa/story/chapters]

One file per chapter, scripts in number order (story order for 0-155):
  >> id | speaker | JP        (a line break is shown as " / ")
  EN
Then: qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (chapter, first script, last script): keep in step with docs/synopsis.md
CHAPTERS = [
    ("ch01", 0, 69), ("ch02", 70, 109), ("ch03", 110, 129), ("ch04", 130, 149),
    ("ch05", 150, 339), ("ch06", 340, 419), ("ch07", 420, 449), ("ch08", 450, 599),
    ("ch09", 600, 689), ("ch10", 690, 749), ("ch11", 750, 799), ("ch12", 800, 9999),
]

# speaker id -> name (docs/style-reference.md)
SPEAKERS = {-1: "-", 1: "Yurie", 2: "Genio", 3: "Ippa", 4: "Navyu", 6: "Sigma", 7: "Jorna", 8: "Terry",
            10: "lady duelist", 17: "boss boy"}


def flat(s):
    return s.replace("\n", " / ")


def chapter_of(script):
    for name, lo, hi in CHAPTERS:
        if lo <= script <= hi:
            return name
    raise ValueError(script)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "story" / "chapters"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    lines = {name: [] for name, _, _ in CHAPTERS}
    for f in sorted((ROOT / "script").glob("events_*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            spk = e.get("speaker", -1)
            who = SPEAKERS.get(spk, f"spk {spk}")
            ch = chapter_of(int(e["id"][1:4]))
            lines[ch].append(f">> {e['id']} | {who} | {flat(e['jp'])}")
            lines[ch].append(flat(e["en"]))
    for name, body in lines.items():
        p = out / f"{name}.txt"
        text = "\n".join(body) + "\n"
        if not p.exists() or p.read_text(encoding="utf-8") != text:
            p.write_text(text, encoding="utf-8", newline="\n")
        print(f"{name}\t{len(body) // 2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
