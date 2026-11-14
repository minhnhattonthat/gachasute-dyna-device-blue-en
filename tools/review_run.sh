#!/bin/sh
# review_run.sh: phase-6 review pass with codex exec, one run per group of pairs files.
#   python -X utf8 tools/pairs.py first; then: sh tools/review_run.sh [GROUP..]
#   GROUP = name:NN,NN (pairs file numbers); reports: work/review/reports/<name>.md
# Everything the reviewer needs goes in on stdin: codex's Windows sandbox can't start a shell to read files.
cd "$(dirname "$0")/.." || exit 1
mkdir -p work/review/reports
groups="${*:-g01:01,02 g02:03 g03:04 g04:05,06,07,08,09 g05:10,11,12,13 g06:14,15 g07:16,17,18 g08:19,20,21,22,23 g09:24,25,26,27 g10:28,29,30,31}"
run() {
  name=${1%%:*}; nums=${1#*:}
  {
    echo "=== docs/reviewer-brief.md ==="; cat docs/reviewer-brief.md
    echo "=== glossary.md ==="; cat glossary.md
    echo "=== docs/style-reference.md ==="; cat docs/style-reference.md
    for n in $(echo "$nums" | tr ',' ' '); do
      for f in work/review/pairs/${n}_*.txt; do echo "=== pairs file $f ==="; cat "$f"; done
    done
  } | codex exec --sandbox read-only --skip-git-repo-check -o "work/review/reports/$name.md" \
    "Everything you need is in the stdin block; do not run commands or read files. Follow docs/reviewer-brief.md from it and review every pairs file in it." \
    > "work/review/reports/$name.log" 2>&1
  echo "$name exit $?"
}
for g in $groups; do
  run "$g" &
  while [ "$(jobs -p | wc -l)" -ge 4 ]; do sleep 5; done
done
wait
