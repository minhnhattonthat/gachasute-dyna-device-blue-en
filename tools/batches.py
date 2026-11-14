"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500] [--files events_000 ...]   work/tl/bNNN.tsv + build/terms_bNNN.txt
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/
    python -X utf8 tools/batches.py --selftest

Copied from the skill's assets/batches.py; the ADAPTER section fits this game (script/*.json lists, tools/lint.py
widths). In the TSVs a line break is the two characters \\n (the script writes a real backslash as [5C]).
Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

sys.path.insert(0, str(ROOT / "tools"))
import lint  # noqa: E402

vwf = lint.vwf

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\{[^{}\n]*\}|\[[0-9A-Fa-f]{2}\]")  # codes; lint checks the ones that must match
FREE = {"{KP}"}  # pages may be added freely
VARIABLE = r"\{%[^{}]*\}"  # a register the game fills in: no "1st"/"1th" suffix after it
HONORIFICS = {}  # kept (D1) but not machine-checked: さん/くん are inside common kana words (みなさん, たくさん)
SPEAKERS = {-1: "", 1: "Yurie", 2: "Genio", 3: "Ippa", 4: "Navyu", 5: "G-Force", 6: "Byler grunt", 7: "Jorna",
            8: "Terry", 9: "Announcer", 10: "Lady duelist", 11: "Shopkeeper", 12: "Receptionist",
            13: "Factory staff", 14: "Girl", 15: "?", 17: "Boss boy"}
_BUDGETS = None


def docs():
    for path in sorted(SCRIPT.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        yield path, doc, doc


def needs_english(entry):
    return bool(entry.get("jp")) and not entry.get("en") and entry.get("status") == "todo"


def group_of(entry):
    return entry["id"]


def budgets():
    global _BUDGETS
    if _BUDGETS is None:
        _BUDGETS = lint.load_budgets()
    return _BUDGETS


def limit_label(entry):
    if entry["id"].startswith("s"):
        return f"{lint.LINE_PX}px x{lint.PAGE_LINES}/page"
    b = lint.budget_for(entry["id"], budgets())
    return f"{b[0]}px x{b[1]}" if b else ""


def width_problems(entry, en):
    errs, _ = lint.check_entry({**entry, "en": en}, budgets())
    return errs


def encodable(char):
    return " " <= char <= "~" and char not in "%"


COL = re.compile(r"<@(\d+)>")


def pad_cols(line):
    """<@N> -> spaces up to JP column N (8 px per full-width cell), so a choice starts where the JP one did."""
    out = ""
    pos = 0
    for m in COL.finditer(line):
        out += line[pos:m.start()]
        gap = int(m[1]) * vwf.CELL - lint.line_width(out)
        if gap < 0:
            raise ValueError(f"<@{m[1]}>: text before it is {lint.line_width(out)} px, past column {m[1]}")
        sp = vwf.char_width(" ")
        out += " " * -(-gap // sp)  # round up: at most sp-1 px right of the JP column
        pos = m.end()
        continue
        pos = m.end()
    return out + line[pos:]


def wrap(text):
    """A message authored as paragraphs (no \\n): {KP} splits pages, words fill lines of LINE_PX, a page's last
    line LAST_PX, and a page that needs a third line continues on a new page."""
    pages = []
    for para in re.split(r"\{KP\}", text):
        words, lines, cur = para.split(), [], ""
        for w in words:
            lim = lint.LAST_PX if len(lines) % 2 else lint.LINE_PX
            cand = f"{cur} {w}" if cur else w
            if cur and lint.line_width(cand) > lim:
                lines.append(cur)
                cur = w
            else:
                cur = cand
        lines.append(cur)
        # the text's last line opens a page (filled to LINE_PX) but is that page's last line too: LAST_PX
        last = lines[-1].split()
        if len(lines) % 2 and lint.line_width(lines[-1]) > lint.LAST_PX and len(last) > 1:
            k = len(last) - 1
            while k > 1 and lint.line_width(" ".join(last[:k])) > lint.LINE_PX:
                k -= 1
            lines[-1:] = [" ".join(last[:k]), " ".join(last[k:])]
        pages += ["\n".join(lines[i:i + 2]) for i in range(0, len(lines), 2)]
    return "{KP}\n".join(pages)


def layout(entry, en):
    """Messages written without \\n are wrapped; <@N> columns are padded in every line."""
    if entry["id"].startswith("s") and "\n" not in en:
        en = wrap(en)
    return "\n".join(pad_cols(line) for line in en.split("\n"))
# ---- end of ADAPTER ----


def esc(s):
    return s.replace("\n", "\\n")


def unesc(s):
    return s.replace("\\n", "\n")


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def problems(entry, en, terms):
    """Every rule, on one entry's English."""
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en)
    if bad := sorted({c for c in plain if not encodable(c) and c != "\n"}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en:
        out.append("escape sequence or tab in the English")
    # {%} is the original's typo in s341.00 (docs/re/text.md): the expander would eat the next 3 bytes; drop it
    want = Counter(t for t in TOKEN.findall(jp) if t not in FREE and t != "{%}")
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if want != have:
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. {%dR0}")')
    if re.search(r"\b[Aa]n? " + VARIABLE, en):
        out.append("a/an right before a variable (the article can't match every value)")
    jp_plain = TOKEN.sub("", jp)
    flat = re.sub(r"\s+", " ", en.replace("{KP}", " ")).lower()  # a term may wrap across lines
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(e.lower() in flat for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for jp_form, en_form in HONORIFICS.items():
        if jp_form in jp_plain and en_form.lower() not in en.lower():
            out.append(f"honorific {jp_form} needs {en_form}")
    return out + width_problems(entry, en)


def index():
    return {e["id"]: e for _, _, entries in docs() for e in entries}


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size, files=None):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for path, _, entries in docs():
        if files and path.stem not in files:
            continue
        for e in entries:
            if needs_english(e) and e["id"] not in taken:
                groups.setdefault(group_of(e), []).append(e)
    batches, cur, chars = [], [], 0
    for group in groups.values():
        c = sum(len(TOKEN.sub("", e["jp"])) for e in group)
        if cur and (chars + c > size or len(cur) + len(group) > MAX_ENTRIES):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{e['id']}\t{SPEAKERS.get(e.get('speaker'), '') if e.get('speaker') is not None else ''}\t"
                f"{'msg' if e['id'].startswith('s') else 'str'}\t{limit_label(e)}\t{esc(e['jp'])}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(TOKEN.sub("", e["jp"]) for e in batch)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], unesc("\t".join(r[1:]))) for r in read_tsv(TL / f"{batch}.out.tsv")]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    laid = []
    for eid, en in rows:
        if eid in entries:
            try:
                en = layout(entries[eid], en)
            except ValueError as x:
                bad.append(f"{eid}: {x}")
            bad += [f"{eid}: {p}: {en!r}" for p in problems(entries[eid], en, terms)]
        laid.append((eid, en))
    return bad, dict(laid)


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written."""
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if e["id"] in new and e.get("en") and e["en"] != new[e["id"]]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, doc, entries in docs():
        touched = False
        for e in entries:
            if e["id"] in new and e.get("en") != new[e["id"]]:
                e["en"], e["status"] = new[e["id"]], "done"
                touched = True
                changed += 1
        if touched:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        files = args[args.index("--files") + 1:] if "--files" in args else None
        size = int(args[args.index("--size") + 1]) if "--size" in args else 3500
        return split(size, files)
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e.get("en") and e.get("status") == "done"
               for p in problems(e, e["en"], terms)]
        print(f"{len(entries)} entries, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    new, failed = {}, 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        new.update(rows)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
    if failed:
        return 1
    if cmd == "merge":
        merge(new, overwrite)
    return 0


def _selftest():
    import tempfile
    global ROOT, TL, SCRIPT, GLOSSARY
    with tempfile.TemporaryDirectory() as d:
        ROOT = Path(d)
        TL, SCRIPT, GLOSSARY = ROOT / "work/tl", ROOT / "script", ROOT / "glossary.md"
        SCRIPT.mkdir()
        GLOSSARY.write_text("| JP | EN | max | notes | Avoid |\n|---|---|---|---|---|\n| ミン | Min | | | Minn |\n",
                            encoding="utf-8")
        script = [{"id": "s001.00", "jp": "ミンが来た{KP}\nよ", "en": "", "status": "todo", "speaker": 4},
                  {"id": "s001.01", "jp": "タイミング", "en": "", "status": "todo", "speaker": -1},
                  {"id": "s001.02", "jp": "", "en": "", "status": "todo"},
                  {"id": "s001.03", "jp": "{%dR0}ばん", "en": "", "status": "todo"},
                  {"id": "s001.04", "jp": "ABC", "en": "", "status": "keep"}]
        (SCRIPT / "events_000.json").write_text(json.dumps(script), encoding="utf-8")
        assert main(["split"]) is None
        assert [r[0] for r in read_tsv(TL / "b001.tsv")] == ["s001.00", "s001.01", "s001.03"]
        assert "\\n" in (TL / "b001.tsv").read_text(encoding="utf-8")
        assert "ミン\tMin" in (ROOT / "build/terms_b001.txt").read_text(encoding="utf-8")
        split(3500)
        assert len(existing()) == 1  # a repeat run makes no duplicate batch
        out = TL / "b001.out.tsv"
        out.write_text("s001.00\tHe came\ns001.01\tTiming\n", encoding="utf-8")
        assert main(["check", "b001"]) == 1  # s001.03 missing, s001.00 lacks the glossary term
        out.write_text("s001.00\tMin came!\ns001.01\tTiming\ns001.03\t{%dR0}th\n", encoding="utf-8")
        assert main(["merge", "b001"]) == 1  # ordinal after a variable: nothing written
        assert index()["s001.00"]["en"] == ""
        out.write_text("s001.00\tMin came!\ns001.01\tTiming\ns001.03\t" + "x" * 60 + " No. {%dR0}\n", encoding="utf-8")
        assert main(["check", "b001"]) == 1  # wider than the message line
        out.write_text("s001.00\tMin came!{KP}\\nYo.{KP}\\nMore.\ns001.01\tThe timing\ns001.03\tNo. {%dR0}<@8>Go\n",
                       encoding="utf-8")
        assert main(["merge", "b001"]) == 0 and index()["s001.00"]["en"] == "Min came!{KP}\nYo.{KP}\nMore."
        assert index()["s001.03"]["en"] == "No. {%dR0}" + " " * ((64 - lint.line_width("No. {%dR0}")) // 4) + "Go"
        long = " ".join(["word"] * 60)
        for page in wrap(long + "{KP}" + long).split("{KP}\n"):
            ls = page.split("\n")
            assert len(ls) <= 2 and lint.line_width(ls[-1]) <= lint.LAST_PX
            assert all(lint.line_width(x) <= lint.LINE_PX for x in ls)
        assert main(["check"]) == 0
        out.write_text("s001.00\tMin arrived\ns001.01\tThe timing\ns001.03\tNo. {%dR0}\n", encoding="utf-8")
        try:
            main(["merge", "b001"])
            raise AssertionError("merge replaced English")
        except SystemExit:
            pass
        assert main(["merge", "b001", "--overwrite"]) == 0 and index()["s001.00"]["en"] == "Min arrived"
    print("selftest ok")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        sys.exit(main(sys.argv[1:]))
