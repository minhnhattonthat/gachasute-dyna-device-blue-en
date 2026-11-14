# Glossary - Gachasute! Dyna Device Blue

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables below (JP as a whole kana/kanji run -> one of the EN forms present).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (D1): くん -> -kun, さん -> -san, ちゃん -> -chan, さま -> -sama after a name.
  Not machine-checked (みなさん, たくさん are ordinary words). Name order: Western.
- Romanisation source (D2): no official English release, no earlier patch -> Hepburn without macrons, except where
  a name is a plain English or Latin word in katakana (constellations, English loanwords): use that word (D10).
- Credits: English (D3).
- Register / flavour: a cheerful kids' game (all-kana text). Plain, lively English; keep each character's quirk
  (see Style rules). Sound effects in asterisks: *Boom!*
- Abbreviations: full names and terms everywhere (D4); none so far.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ -> ..., ！？ -> !?, ー (long drawl) -> doubled vowel or
  "~" is not in the font: write "Heyyy", "Mr. Masterrr". ～ -> drop or "...". ♪ is not in the font: drop it.
- `%` is not in the font (the expander eats it): write "percent".
- No suffix glued to a register: not "{%dR0}th"; write "No. {%dR0}", "Round {%dR0}".
- No a/an right before a register; registers hold up to 64 px (8 letters).
- Voice table: docs/style-reference.md.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ナビュウ | Navyu | | guide AI of the Dyna Pad, very polite; speaker 4 | Nabyu |
| ユリエ | Yurie | | friend (girl), speaker 1, calls the player "-kun" | |
| ゲニオ | Genio | | rival, オレさま -> "the great me"; speaker 2 | |
| イッパ | Ippa | | classmate, ボク, smug; speaker 3 | |
| ジョルナ | Jorna | | Byler agent, drawling "~ぇ" speech; speaker 7 | |
| テリー | Terry | | Byler agent, cool; speaker 8 | |
| ヤマダ | Yamada | | | |
| バイラー | Byler | | villain group (virus pun) | Biler |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ダイナシティ | Dyna City | | | |
| バイラーシティ | Byler City | | | |
| ダイナセンター | Dyna Center | | | Dyna Centre |
| コロシアム | Colosseum | | | Coliseum |
| ファクトリー | Factory | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ダイナデバイス | Dyna Device | | the game in the game | |
| ダイナパッド | Dyna Pad | | handheld | Dynapad |
| ダイナネット | Dyna Net | | | |
| ダイナサーバー | Dyna Server | | | |
| ガチャステーション | Gacha Station | | | |
| ガチャステ | Gachasute | | short form, title word | Gachaste |
| ダイナ | Dyna | | creatures; plural "Dyna" | Dynas |
| マスター | Master | | of a city | |
| セクタ | sector | | city grid area | |
| ビット | bit / bits | | money | |
| エサ | food | | Dyna feed | |
| スタイル | style | | | |
| タイプ | type | | | |
| トラップ | trap | | | |
| ウワサ | rumor | | | rumour |
| ランク | rank | | D to A | |
| ランキングバトル | Ranking Battle | | | |
| フリーバトル | Free Battle | | | |
| ショップキット | Shop Kit | | | |
| ファクトリキット | Factory Kit | | | |
| コロシアムキット | Colosseum Kit | | | |
| サブウェイキット | Subway Kit | | | |
| メガハウス | Mega House | | | |
| ギガダイヤモンド | Giga Diamond | | | |
| ゴーストプレイヤー | Ghost Player | | | |
| マルチワクチン | Multi Vaccine | | | |
| アドレスちょう | address book | | | |
| Ｇフォース | G-Force | | | |
| アーマーデバイス | Armor Device | | | |
| ウェポンデバイス | Weapon Device | | | |
| テトロトップタイプ | Tetrotop type | | four-legged, rideable (fast) | |
| シェルブックタイプ | Shellbook type | | water, rideable (over water) | |
| バーディスタイプ | Birdis type | | flying, rideable | Bardis |
| バトルリスト | Battle List | | mark "BT" | |
| バトルコロシアム | Battle Colosseum | | | |
| グラウンド | Ground | | sector type after Level | |
| ダスト | Dust | | sector type after Demolish | |
| データベース | Database | | menu | |
| キーワード | Keyword | | Database entries | |
| オークション | auction | | | |

## Decisions from earlier batches
- b001-b002 menu commands, quoted in tutorials (the strings batches must use the same words; not table-checked
  because the kana are ordinary verbs): せいちする -> Level, しせつをたてる -> Build, こわす -> Demolish,
  かたづける -> Clean Up, つれていく -> Take, はなす -> Talk, じゅうみん -> Residents, おわる -> Quit,
  システム -> System, アドレス -> Address, つうしん -> Link, めいしこうかん -> Card Trade, ダイナリスト -> Dyna List,
  バトルリストとうろく -> Battle List Entry. ランド (sector) -> Land. ショップ kinds: Device parts shop, food shop,
  medicine shop, general store (なんでもや). ぞくせい -> element: fire, water, thunder, earth, none.
- b003 battle: ていさつ -> Scout, こうげき -> Attack, ちりょう -> Cure (poison/sleep, not HP), いどう -> Move,
  はいち -> place, エリア -> area, マス -> square, D = Dyna / T = trap counts; チーム -> team.
  Genio is "Genio-kun" in Yurie's mouth. Choice lines: `<@5>Yes<@11>No` for はい/いいえ at JP cols 5/11.
