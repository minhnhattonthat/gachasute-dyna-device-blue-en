# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-14 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-14 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-14 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-14 | Abbreviations | engine work first (default), abbreviate | Default: engine work first; abbreviate only as a flagged last resort. |
| D5 | 2026-11-14 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the Japanese logo only if it has no official English version. |
| D6 | 2026-11-14 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint without asking. |
| D7 | 2026-11-14 | Existing saves / savestates | user's saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-14 | Git identity | ask | Already set by new-game.ps1; don't change it. |
| D9 | 2026-11-15 | English font (agent's call under D6, phase 5) | full-width Latin (8 px per letter, no code), 2 letters per 8 px cell (4 px letters), VWF | VWF: an ARM hook in the shared renderer redraws the game's own cells with a proportional 8-row font drawn for this project (fonts/vwf8.txt, MIT). Message lines hold ~188 px (about 38 letters) instead of 23 full-width cells; no layout code changes. docs/re/font.md. |
