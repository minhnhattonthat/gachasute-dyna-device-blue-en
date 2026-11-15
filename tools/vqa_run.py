"""vqa_run.py: the phase-8 visual-QA pass with `codex exec` (Orca workers can't start reviewer subagents).

    python -X utf8 $SKILL/scripts/qa_gate.py todo work/qa/manifest.tsv work/qa/verdicts --size 12 --out-dir work/qa/chunks
    python -X utf8 tools/vqa_run.py [work/qa/chunks/chunk_001.txt ..] [--jobs 2]   # default: every chunk with no verdicts

Each chunk is one fresh read-only codex run: docs/visual-qa-brief.md + glossary.md on stdin, every English shot of
the chunk attached with its original-ROM twin (work/qa/tour_jp/<same id>.png) when there is one. The reply (TSV
verdict lines only) goes to work/qa/verdicts/<chunk>.tsv; lines whose id isn't in the chunk are dropped, and a chunk
whose reply misses an id is reported (rerun it). Codex's Windows sandbox can't start a shell, so it gets everything
attached and is told not to run commands.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUR, TOUR_JP = ROOT / "work" / "qa" / "tour", ROOT / "work" / "qa" / "tour_jp"
VERDICTS = ROOT / "work" / "qa" / "verdicts"


def ids_of(chunk):
    out = []
    for line in chunk.read_text(encoding="utf-8").splitlines():
        p = Path(line.split("\t")[-1].strip())
        if line.strip():
            p = p if p.is_absolute() else ROOT / p
            out.append((p.relative_to(TOUR).with_suffix("").as_posix(), p))
    return out


def run(chunk):
    items = ids_of(chunk)
    imgs, legend = [], []
    for i, p in items:
        imgs.append(str(p))
        legend.append(f"image {len(imgs)}: id {i} (English build)")
        jp = TOUR_JP / (i + ".png")
        if jp.exists():
            imgs.append(str(jp))
            legend.append(f"image {len(imgs)}: id {i} ORIGINAL Japanese ROM, same scene (reference, no verdict)")
    stdin = "\n".join(["=== docs/visual-qa-brief.md ===", (ROOT / "docs" / "visual-qa-brief.md").read_text("utf-8"),
                       "=== glossary.md ===", (ROOT / "glossary.md").read_text("utf-8"),
                       "=== attached images, in order ===", *legend])
    prompt = ("You are the visual-QA reviewer of docs/visual-qa-brief.md (in the stdin block, with glossary.md). Do not "
              "run commands or read files: everything is attached. Each English image is one GBA screen (240x160) of "
              "a debug-warp scene; the Japanese twin, when attached, shows the original game at the same point. Judge "
              "every English id. Reply with ONLY the verdict lines, one per id, exactly: id<TAB>ok|issue<TAB>note "
              "(note: what and where; for ok a few words of what the screen shows).")
    out = VERDICTS / (chunk.stem + ".tsv")
    raw = out.with_suffix(".raw.txt")
    cmd = ["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-o", str(raw)]
    for im in imgs:
        cmd += ["-i", im]
    cmd.append(prompt)
    r = subprocess.run(cmd, input=stdin, text=True, encoding="utf-8", capture_output=True, cwd=ROOT)
    want = {i for i, _ in items}
    got = {}
    if raw.exists():
        for line in raw.read_text(encoding="utf-8").splitlines():
            parts = line.strip().strip("`").split("\t")
            if len(parts) >= 2 and parts[0] in want and parts[1] in ("ok", "issue"):
                got[parts[0]] = "\t".join([parts[0], parts[1], " ".join(parts[2:])])
    if got:
        out.write_text("".join(got[i] + "\n" for i, _ in items if i in got), encoding="utf-8")
    missing = sorted(want - set(got))
    issues = sum(1 for v in got.values() if v.split("\t")[1] == "issue")
    return f"{chunk.name}: {len(got)}/{len(want)} verdicts, {issues} issue(s)" + \
        (f", MISSING {missing} (codex exit {r.returncode})" if missing else "")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chunks", nargs="*")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args(argv)
    VERDICTS.mkdir(parents=True, exist_ok=True)
    chunks = [Path(c) for c in a.chunks] or sorted((ROOT / "work" / "qa" / "chunks").glob("chunk_*.txt"))
    chunks = [c for c in chunks if a.chunks or not (VERDICTS / (c.stem + ".tsv")).exists()]
    bad = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for line in ex.map(run, chunks):
            print(line, flush=True)
            bad += "MISSING" in line
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
