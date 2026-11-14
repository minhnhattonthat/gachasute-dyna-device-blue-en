# Style reference (phase 6)

Pilot: b001 (scripts 0-9, Navyu's tutorial), merged 2026-11-15, seen in game (`work/qa/p6_pilot2`, warp `intro`
with `MASHA=1`): wraps cleanly, the ▼ arrow clears the last line. Approved under D6 (pre-approved run).

## Voices (speaker id in script/ -> name, JP markers -> English devices)
| Speaker | Who | JP markers | English |
|---|---|---|---|
| 4 | Navyu, the Dyna Pad's guide | です/ます, させていただく, ございます, ごりょうしょうください | courteous shop-assistant English, no contractions in her own sentences ("I am", "please do"), light warmth ("There we are!") |
| 1 | Yurie, friend | くーん, のよ, かな | friendly, chatty, contractions, "Heyyy, {name}-kun!" |
| 2 | Genio, rival | オレさま, おまえ, ぜ, ！！ | loud braggart: "the great me", "you!", exclamations |
| 3 | Ippa, classmate | ボク, キミ, じゃないか | smug, a little condescending: "Well, well", "you know" |
| 6 | Byler grunt | デス (katakana) | a "-desu" tic in English: "Is this the place, desu?" -> keep it as "...it is, yes-yes" ; pick one tic per batch notes and keep it |
| 7 | Jorna (Byler) | drawled ぇ/ぉ, あなたぁ | drawl with doubled letters: "Excuuuse me", "Mr. Masterrr" |
| 8 | Terry (Byler) | オレ, cool | terse, cool |
| 10 | lady duelist | わたくし, ですわ, フフッ | prim, "Fufu", "I do declare" register |
| 17 | boss boy | ボク, けしちゃうか | calm, childish menace: "Maybe I'll just erase you." |
| -1 | no portrait | | narration / system: plain |

## Paired examples
- ようこそ　ダイナシティへ！{KP}このたびは　ダイナパッドを　おかいあげいただきまして{KP}まことにありがとうございます
  -> "Welcome to Dyna City!{KP}Thank you very much for purchasing a Dyna Pad!" (two thank-you pages merged: fine)
- ちなみに　アーマーとは　ぼうぐ　ウェポンとは　ぶきのことです -> 'By the way, "armor" means protective gear, and
  "weapon" means, well, weapons.' (a gloss that is empty in English gets a light touch instead of a tautology)
- Corrected: いちおう　そういう　きまりに　なっておりますので　ごりょうしょうください: not "It is the rule, please
  understand" but "Those are the rules, I'm afraid, so I hope you understand."

## Layout
- Write messages as one paragraph per JP page, joined with {KP}; `tools/batches.py` wraps them (188 px lines,
  176 px on a page's last line, 2 lines a page, extra pages added). Write `\n` only where a break must fall.
- Choice lines: keep them on their own line and place each option at the JP column with `<@N>` (N = full-width
  cells from the line start in the JP, e.g. `　　　　　はい　　　　いいえ` -> `<@5>Yes<@11>No`).
