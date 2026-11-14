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
- Description lines (0x0AFD40-0x0B211C, 88 px each) are shared fragments: an item/device record is 4 line
  pointers read as one JP phrase (`work/tl/desc_records.txt`: record -> its 4 ids; rebuild it from the table at
  0x0BDB2C, 16 bytes a record). Translate a fragment so it reads in EVERY record that uses it, in its line slot;
  English may move meaning between lines. Patterns set in b028: kits "For a Shop:" / "the kit you need" / "to build
  one."; stat items "A Dyna's" / "max HP" / "goes up by 1."; Plus Points "A Weapon Device's" / "Plus Points can" /
  "be raised by 1" / "with this item."; gems "<Elem>-element" (fire/water/thunder/earth: "Fire-element", むぞくせい:
  "Non-element") / "energy pours" / "from this" / "red gem."; parts "Igarm type" / "and Zero-E type:" / "a part for
  their" / "dedicated Devices."; armor metal "Very light, but" / "not very strong." / "Sturdy, but" / "very heavy.".
  ダイナの (t0AFE90) is also line 1 of the House keyword ("A Dyna's" / "home sector."). Device records:
  [type][category][line 1][line 2], line 2 often ends in the device name (ほのおが ふきだす / トリックスター).
  A JP blank line "　" is status keep (t0AFEE4); never leave English empty.
  b029 changed the parts pattern to "Igarm types and" / "Zero-E types'" / "dedicated Devices" / "need this part."
  (the 2nd type line is shared with food records: "<Type> types'" / "favorite." / "top favorite!"), and
  metal to "Sturdy." / "Very heavy." Armor records: [style][Armor Device][L3][L4]; element variants
  "Fire-element" / "<name>". Open for later batches: t0B0D5C should read "Its smooth surface" (+ "deflects
  attacks."); t0B185C sits in "Very light, so" / [t0B185C] / "it suits big" / "weapons and such." (e.g. "worn
  on the back,").
- Dyna body types (b028): イグアーム Igarm, テトロトップ Tetrotop, シェルブック Shellbook, バーディス Birdis,
  キックバグ Kickbug, ゼロイー Zero-E, デュアロン Dualon, エコロード Ecoroad, メタボール Metaball, ゴストフリー Ghostfree.
- An entry with any `\n` is not wrapped by the tool: lay out every line yourself and put `\n` after `{KP}` before
  a choice line (`<@N>` counts from the line start).
