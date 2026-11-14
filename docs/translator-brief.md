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
- b018-b023: registers must stay in JP order (check enforces it): rewrite the sentence, don't reorder codes. No
  a/an right before a register (check enforces it): "my type is {%sR4}", "a Dyna of the {%sR1} style".
- Resident gossip (s461-s592) fills registers from the word lists at t0B4948-t0B4BE0 (relatives, places like
  ゲームセンター, activities like サッカー/宿題, events like 運動会, nicknames): the strings batch must render
  them as bare nouns that read after "for", "at", "busy with", "graduating from", "collecting" (no article:
  "the arcade" only if it fits 64 px; activities as nouns: "soccer", "homework", "shopping").
- An entry with any `\n` is not wrapped by the tool: lay out every line yourself and put `\n` after `{KP}` before
  a choice line (`<@N>` counts from the line start).
