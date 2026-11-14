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
| ヤマダ | Yamada | | Byler boss? "Yamada-sama" to the grunts | |
| シグマ | Sigma | | Byler grunt (speaker 6), デス tic -> ", desu" at sentence ends | |
| バイラー | Byler | | villain group (virus pun) | Biler |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ダイナシティ | Dyna City / Dyna Cities | | | |
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
  Genio is "Genio-kun" in Yurie's mouth.
- b004-b005 Factory menu (s083.01, 4 items at JP cols 2/13): かいはついらい -> New Request, かいはつじょうきょう ->
  Check Status, かいはつちゅうし -> Cancel Request, なんでもない -> Never mind; けんきゅういん ->
  researcher, デバイス -> Device (capital D), せんよう/はんようデバイス -> dedicated / general Device, しょきとうし ->
  starting investment, かいはつしんこうど -> development progress, プロジェクト -> project, しきんぶそく ->
  "Not enough funds", デバイスそざいのみせ -> Device parts shop; スタジアム -> Stadium, ブロック -> Block (Block A);
  choice しゅっぱつする/まだ -> `<@3>Let's go<@14>Not yet`; restart menu どこから さいかいしますか？ ->
  "Where do you want to restart from?" `<@2>Battle<@8>My House<@15>Save Data`; tournament: Round 1, Match 1,
  semifinal, final, champion; b007: エキスパートルール -> Expert Rules, とくしゅのうりょく -> special ability,
  ネットけいさつ -> net police, ちかてつのえき -> subway station; b009-b010: ぬいぐるみ -> stuffed toy, げきレア ->
  ultra-rare, レアアイテム -> rare item, Terry calls the player ボウズ -> "kid", Yurie calls Navyu おねえさん -> "Miss",
  the lady duelist of s122 is Jorna in disguise (prim "Fufu" until s123.04); そうび -> Equip, パーティー -> Party, ダブルアタック -> Double Attack, けんちくキット -> building kit. Choice lines: `<@5>Yes<@11>No` for はい/いいえ at JP cols 5/11.
- b011-b017: Jorna drawls with stretched vowels ("pleeease", "riiight"), calls Yurie "that girl" (あのコ) and
  "Yurie-san", Terry "Lord Terry"; Sigma laughs "Fuhihihi"; Navyu says "{name}-san". 〒NN-NN addresses ->
  "{%02dR4}-{%02dR5}" ("the Factory at 12-34"). アトラクション しゅうりょう/かいし -> "Attraction closed." /
  "Attraction open."; ワンサイドアタック -> One-Sided Attack; えんごこうげき -> Support Attack; ジョーカー -> Joker;
  とくしゅ (command) -> Special; nP -> "P{%dR4}"; status: poisoned, asleep, paralyzed/numb, confused, burned,
  frozen, shocked (かんでん), sand in its eyes, knocked out; ぼうぎょりょく/こうげきりょく/すばやさ -> Defense/Attack/Speed;
  プラスポイント -> Plus Points; sectors House, Hole, Water, Mega House; エクストラ -> Extra (Heat/Ice/Bolt/Sand);
  むぞくせい -> element "none"; resident Dyna talk in 4 voices (polite / rough / stern / girlish), each line set
  in id order.
- b018-b023: Extra names (Device name parts): Heat, Ice, Bolt, Sand, Flare, Aqua, Mist, Bomb, Gran, Elec, Earth;
  コンボ -> combo; ５月びょう -> the May blues; たなばた -> the Star Festival (wish on a paper strip); おつきみ ->
  moon viewing; Dyna Center menu `<@2>Withdraw<@13>Treat\n<@2>Auction<@13>Quit`, withdraw `<@3>Dyna<@9>Kits<@15>Quit`;
  やめる (menu) -> Quit; item prompts "Give/Take/Buy/Sell {%sR0}?", "Trade for {%sR2}?"; auction: opening bid,
  "goes to {%sR4}-san"; うまれた from address data -> "a Dyna of the {%sR1} style was born".
