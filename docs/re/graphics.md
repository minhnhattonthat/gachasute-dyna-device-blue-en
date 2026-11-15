# Graphics text survey

Tile-drawn Japanese: every row needs English art in phase 8 (D5: translate all of it). Text the game draws from
its font at run time (dialogue, the boot date prompt, the profile popup) is string work, not listed here.

## Method
- **Static sweep** (`python -X utf8 tools/gfx_sweep.py`): all 851 ECD `IMG` blocks rendered with their following
  `PLT` into 22 sheets (`work/gfx_sweep/`, offsets in `index.tsv`); no block skipped. 845 are 4bpp (flag 0), 6 have
  flag 1. Sheets read by a fresh read-only reviewer (`codex exec`, sandbox read-only, 6 chunks); the controller
  re-read sheets 000 and 016 itself and agreed. Sheets 008-018 (effects, sprites, maps) hold no Japanese.
- **Tour** (boot to profile form): Smilesoft/Nintendo logos (English), boot date prompt (font), title/menu,
  name entry (kana keyboard + START/SELECT hints), profile form labels (なまえ, ニックネーム, せいべつ,
  けいたいばんごう, メールアドレス, たんじょうび, けつえきがた, おわる): these labels are tiles; match them to
  the rows below with `vramfind.py` against `work/ecd/` in phase 8.
- **Marker tour** (phase 5, `build.py --marker`, `work/qa/p5_mk`): text left Japanese in the marker build is
  graphics (or unextracted text; checked by SJIS search): the field menu bar (じゅうみん データベース システム
  もちもの パーティ), the item submenu (つかう ならびかえ すてる: ならびかえ is not SJIS anywhere in the ROM),
  the profile form labels above. Phase 8 maps each to its ECD block.
- Not yet covered: raw (uncompressed) tiles outside ECD, the unknown file at 0x0E7FA4, the one BIOS-LZ77 block
  at 0x0E6A58, sprites (OAM) on screens past the profile form. Extend with the debug tool's tour (phase 2/5).

## Field menu bar (phase 8 pilot notes, block 01E30D4)
- 01E30D4 is a 27x5-tile atlas (palette 01E3574; ink index 1 = white, 0 = transparent, 2-9 frame greys). It is
  copied into BG char block 2 (VRAM tile 1541 + 32*row + col) and BG0's map (screen block 0, 2 rows, hofs 16)
  picks atlas tiles per button. Dump: `work/qa/menu_probe/ppu_001820.*` (warp `menu`, CONT=1, ppudump DUMP_AT=1820).
- Buttons (atlas row,col; top row / bottom row of the 16 px bar):
  システム `0,0-0,5` / `1,0-1,5`; もちもの `0,0 0,6-0,9 0,5` / `1,0 1,6-1,9 1,5`; パーティ `0,0 0,10-0,13 0,5` /
  `1,0 1,10-1,13 1,5` (caps 0,0 / 0,5 shared: text only in the 4 middle tiles, 32 px);
  じゅうみん `0,14-0,19` / `1,14-1,19` (48 px); データベース `0,20-0,23 2,22 2,23` / `1,20 4,12 1,22 1,23 3,22 3,23`
  (the map shows frame-only tile 4,12 in place of 1,21: check whether another screen uses 4,12 before drawing
  ink into it, else move the ink of that column into rows 0-7 or patch the map).
- Glyphs: 7 rows at atlas y 3-9 of each 16 px band (crossing the tile-row boundary at y 8); VWF caps fit.
- Atlas rows 2-4 hold the submenu words (つかう ならびかえ すてる, データセーブ おわる, ステータス そうび
  かえらせる にがす, マップ ダイナ キーワード デバイス, バトルアニメ...): dump their screens the same way
  (`menu_items`, `menu_party`, `menu_save` scenes) to get their tile lists before redrawing.
- `tools/gfx.py export OFF` writes `work/gfx/orig/OFF.png` + x4; English art goes in `gfx/OFF.png` (same size,
  palette colours only); `gfx.apply()` (not yet called by build.py) writes it in place or relocates it.

## Rows (ROM offset of the ECD block)
| Offset | Sheet | Japanese | Gloss | Kind |
|---|---|---|---|---|
| 01E30D4 | sheet_000 | システム　もちものパーティじゅうれん　データへ　データセーブ　おわる　つづき　はじめから　そだてる　データクリア　そうび　アクセサリー　せってい　マップ　ダイナキーパー　ロード　インパルス | System; belongings; party; training; data; save; quit; continue; new game; raise; clear data; equipment; accessories; settings; map; Dyna Keeper; load; impulse | menu-label |
| 01E9764 | sheet_000 | ダイナカスタマイズ　こうきのう　マテリアル　ないぞう［以下判読困難］ | Dyna Customize; high performance; material; built-in [remaining text unclear] | menu-label |
| 01EA6B4 | sheet_000 | つれてい［断片］　データ［断片］ | Bring along [fragment]; data [fragment] | menu-label |
| 01EA8C4 | sheet_000 | ［大きな文字状の断片・判読困難］ | [Large lettering fragment; illegible] | sign/other |
| 01EAA04 | sheet_000 | あずかっている けんちくキット　ダイナのうりょう | Stored construction kits; Dyna capacity | menu-label |
| 01EB9E4 | sheet_000 | アイテムここにゅう　アイテムはいきゃく | Item purchase; item sale | menu-label |
| 01ECD84 | sheet_001 | アイテム［断片］　コウカン　オンライン［以下判読困難］ | Items [fragment]; exchange; online [remaining text unclear] | menu-label |
| 01EE624 | sheet_001 | かいはつ［断片］　はっきょう　プリント［以下判読困難］ | Development [fragment]; [unclear menu word]; print [remaining text unclear] | menu-label |
| 01EFFF4 | sheet_001 | フリーバトル | Free Battle | menu-label |
| 01F4284 | sheet_001 | ズームアウト　ズームイン　みているダイナデバイス［断片］ | Zoom out; zoom in; currently viewed Dyna Device [fragment] | button-hint |
| 0203D14 | sheet_003 | この ダイナに な［断片］　まえを つけてください　このゲームをつづけてのぞむには［判読困難］ | Name this Dyna [split text]; [additional instruction unclear] | menu-label |
| 0206CF4 | sheet_003 | けってい　用事 | Confirm; errand | menu-label |
| 0208654 | sheet_003 | ［小さなカタカナの項目名・判読困難］　ミニゲーム１２３ | [Small katakana item labels; illegible]; minigames 1, 2, 3 | menu-label |
| 020A4D4 | sheet_003 | すべてのデータをセーブします　セーブする→ボタン　しない→Ｂ | Save all data; button to save; B to cancel | menu-label |
| 020B0F4 | sheet_003 | なまえ　せいよう　ちょうさくへん　カスタム［一部判読不確実］ | Name; [uncertain menu terms]; custom | menu-label |
| 020BDD4 | sheet_003 | かな　カナ　ＡＢＣ　１２３　きごう　かんじ　前のページ　次のページ | Hiragana; katakana; ABC; numbers; symbols; kanji; previous page; next page | button-hint |
| 020E844 | sheet_003 | charset | Kana character set | font/charset |
| 02124B4 | sheet_003 | charset | Kana character set | font/charset |
| 0215E74 | sheet_003 | charset | Japanese character set | font/charset |
| 0219CB4 | sheet_003 | よていのついか　よびのついか　よびじかんのせってい　よびじかんクリア　このデータを けしても いいですか？　はい　いいえ | Add schedule; add reminder; set reminder time; clear reminder time; erase this data?; yes; no | menu-label |
| 021C414 | sheet_003 | charset | Japanese character set | font/charset |
| 021EA44 | sheet_003 | つかったお金ついか　こんげつぶん　こんしゅうぶん　もっともおおいつき［一部判読困難］ | Add money spent; this month; this week; highest-spending month [partly unclear] | menu-label |
| 0224B44 | sheet_003 | charset | Kana character set | font/charset |
| 0225EC4 | sheet_003 | charset | Kana character set | font/charset |
| 02280B4 | sheet_004 | スクロール／やりなおし／[一部判読不能] | Scroll / Redo / [partly illegible] | menu-label |
| 022CF64 | sheet_004 | charset | Character set | font/charset |
| 0231524 | sheet_004 | [下端に日本語あり・判読不能] | [Illegible Japanese along bottom edge] | sign/other |
| 0249C44 | sheet_004 | コラムんメニュー／ダイナメール／めいしこうかん／アイテムこうかん／ダイナこうかん | Koramun menu / Dyna mail / Exchange business cards / Exchange items / Exchange Dynas | menu-label |
| 024AF04 | sheet_004 | アイテムこうかん／じぶんのあいてのアイテム | Exchange items / Your items / Partner’s items | menu-label |
| 024B834 | sheet_004 | ダイナこうかん／じぶんのあいてのダイナ | Exchange Dynas / Your Dynas / Partner’s Dynas | menu-label |
| 024C1C4 | sheet_004 | アドレス／データ／[大型文字は一部判読不能] | Address / Data / [large lettering partly illegible] | menu-label |
| 024D4B4 | sheet_004 | めいしこうかん／めいしの／じぶんの | Exchange business cards / Business card… / Your… | menu-label |
| 0250924 | sheet_004 | ていさつちょう／いどう／とくしゅ／こうげき | Reconnaissance… / Move / Special / Attack | menu-label |
| 025E304 | sheet_004 | ダイナはいち／[判読不能]せんたく／いどう／こうげきエリア／たいきエリア | Dyna placement / Select [illegible] / Move / Attack area / Standby area | menu-label |
| 03B25A4 | sheet_019 | ついか／はずす／［断片・判読困難］ | Add / Remove / [fragmented, unclear] | menu-label |
| 03B29B4 | sheet_019 | チームへんせい | Team setup | menu-label |
| 03B3164 | sheet_019 | せつぞくちゅう／つながっています／つながっていません／シンプルモード／［断片・判読困難］ | Connecting / Connected / Not connected / Simple mode / [fragmented, unclear] | menu-label |
| 03B3624 | sheet_019 | せつぞくかくにん／ルールせんたく／バトルアニメせってい | Check connection / Select rules / Battle animation settings | menu-label |
| 03B7F64 | sheet_019 | だい／ターン／［小字判読困難］ | Ordinal prefix / Turn / [small text unclear] | menu-label |
| 03B9D04 | sheet_019 | charset | Character set | font/charset |
| 03D5DB4 | sheet_020 | charset | Character set | font/charset |
| 03D7FD4 | sheet_020 | Rボタンをおすとゲームのせつめいが／ミニゲーム／のあそびかた／はじめるＡＢスタート／［断片・判読困難］ | Press R for game instructions / Minigame / How to play / Start; A, B, Start / [fragmented, unclear] | menu-label |
| 0432534 | sheet_021 | charset | Character set | font/charset |
| 0449734 | sheet_021 | ガチャステ！／ダイナデバイス／ブルー／レッド／［小字判読困難］ | Gachasute! / Dyna Device / Blue / Red / [small text unclear] | title/logo |

Counts by kind: menu-label 29, font/charset 10, sign/other 2, button-hint 2, title/logo 1. Total 44 blocks.
