#!/bin/sh
# Story-pass reviewer for one chapter with codex exec (read-only), from the repo root:
#   sh tools/story_review.sh ch01 [ch02 ..]  -> work/qa/story/reports/<ch>.md (+ .log)
# Then write work/qa/story/verdicts/<ch>.tsv from the report's Assessment.
mkdir -p work/qa/story/reports
for ch in "$@"; do
  codex exec -s read-only --skip-git-repo-check --ephemeral -o "work/qa/story/reports/$ch.md" \
    "You are the story reviewer. Follow docs/story-reviewer-brief.md exactly. Chapter file: work/qa/story/chapters/$ch.txt (read ALL of it, in passes). Also read docs/synopsis.md, docs/style-reference.md and glossary.md. Return only the report." \
    > "work/qa/story/reports/$ch.log" 2>&1 < /dev/null
  echo "$ch exit $?"
done
