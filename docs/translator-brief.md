# Translator brief

Read first: `glossary.md` (binding), `docs/style-reference.md` (voices, layout), `build/terms_<batch>.txt`.

1. Input: `work/tl/bNNN.tsv` = id, speaker, form (msg|str), limit, JP. `\n` in the JP is a line break.
2. Output: `work/tl/bNNN.out.tsv`, `id<TAB>English`, every id once, same order, written with the file-write tool.
   Plain ASCII; no `%` (write "percent"); `{ } [ ] \` as `[7B] [7D] [5B] [5D] [5C]`.
   - msg: one paragraph per page joined by `{KP}`; the tool wraps. `\n` only for forced breaks (choice lines).
   - Keep every code from the JP: `{%sR4}` registers (64 px each), `{KN}`, `{C1}`; `{KP}` may be added freely.
   - str: one line unless the JP has `\n`; width per the limit column.
3. Check until it prints OK: `python -X utf8 tools/batches.py check bNNN`; then `merge bNNN`.
4. Report: `NEW TERM: jp -> en`, `UNSURE: id - note`, `CUT: id - what was dropped`.

Quality bar (past mistakes in other projects): names off by a letter; "1th" after a number register; a joke
translated literally and losing its punch; character quirks flattened to neutral English; stock phrases like
"TIPS ... GET!".

## Notes from earlier batches
- b001: registers {%sR4}/{%sR5} hold a Dyna or the player depending on the scene: keep pronouns neutral ("it",
  or repeat the name).
