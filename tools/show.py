"""show.py: print script/ entries by id or id prefix (file, speaker, JP, EN; line breaks shown as \\n).

    python -X utf8 tools/show.py s106.44 s437. t0BB6
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    for f in sorted((ROOT / "script").glob("*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            if any(e["id"].startswith(p) for p in argv):
                spk = f" spk {e['speaker']}" if "speaker" in e else ""
                print(f"{e['id']} [{f.stem}{spk} {e.get('status')}]")
                print("  JP " + e["jp"].replace("\n", "\\n"))
                print("  EN " + e["en"].replace("\n", "\\n"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
