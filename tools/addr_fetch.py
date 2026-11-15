"""addr_fetch.py: one-off fetch of municipality kana from Wikidata for names the bulk queries missed.

    python -X utf8 tools/addr_fetch.py NAMES.txt     -> work/addr/src/wikidata_extra.csv (appends)

NAMES.txt: one municipality name per line as the game writes it (a county prefix 〜郡 is dropped for the search).
For each name: wbsearchentities (ja), then each hit's P1814 (name in kana) if its description says Japan.
Columns as the bulk CSVs (item, ja, kana, en, inja, end), so tools/addr_en.py reads it the same way.
"""
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work" / "addr" / "src" / "wikidata_extra.csv"
UA = {"User-Agent": "translation-qa/1.0 (data lookup)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    for wait in (5, 15, 45, 90, None):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait is None:
                raise
            time.sleep(wait)


def lookup(name):
    """-> [(qid, ja, kana, en)] for items labelled exactly `name` (ja)."""
    q = urllib.parse.urlencode({"action": "wbsearchentities", "search": name, "language": "ja",
                                "format": "json", "limit": 7})
    hits = get("https://www.wikidata.org/w/api.php?" + q).get("search", [])
    ids = [h["id"] for h in hits if "Japan" in h.get("description", "") or h.get("label") == name]
    res = []
    if ids:
        q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(ids), "format": "json",
                                    "props": "labels|claims", "languages": "ja|en"})
        for qid, e in get("https://www.wikidata.org/w/api.php?" + q).get("entities", {}).items():
            if e.get("labels", {}).get("ja", {}).get("value", "") != name:
                continue
            for c in e.get("claims", {}).get("P1814", []):
                kana = c["mainsnak"].get("datavalue", {}).get("value")
                if kana:
                    res.append((qid, name, kana, e.get("labels", {}).get("en", {}).get("value", "")))
    return res


def main():
    names = [x.strip() for x in Path(sys.argv[1]).read_text(encoding="utf8").splitlines() if x.strip()]
    new = not OUT.exists()
    with open(OUT, "a", encoding="utf8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["item", "ja", "kana", "en", "inja", "end"])
        for full in names:
            name = full.split("郡", 1)[1] if "郡" in full else full
            res = lookup(name)
            if not res and "ケ" in name:
                time.sleep(1.5)
                res = [(q, name, k, en) for q, _, k, en in lookup(name.replace("ケ", "ヶ"))]
            for qid, ja, kana, en in res:
                w.writerow([qid, ja, kana, en, "", ""])
            print(f"{full}\t{len(res)}", flush=True)
            time.sleep(1.5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
