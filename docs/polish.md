# Polish list

Minor issues to revisit before release (phase 9 needs every line ticked). `[ ]` open, `[x]` done or waived with reason.

## Cuts forced by the 64 px name slots (phase 6, b033-b035)
- [ ] t0B3DAC メガフレアルビー -> "Flare Ruby" ("Mega" cut). Wider name slot or a narrower font would restore it.
- [ ] t0B3D84 サンダートパーズ -> "Bolt Topaz" (Thunder -> Bolt, the game's own thunder Extra word).
- [ ] マシンガン -> "Rapid Gun" (descriptions and item list), アース -> Gran in Gran Launcher / Gran Stun Gun.
- [ ] Armor list names keep the JP grade letters E/O/S/R; meaning unknown (element?). Check in game.

## Field padding and widths to check in game (phase-7 review)
- [ ] r06 pads with `[7F]` to the JP's cells: link-trade lines t0B949C-t0B95EC (11 cells), KO/Sick/Hungry
  t0B9AF4-t0B9B0C (4), t0BA504 `Item=` (8), t0BB414 Armor Device (9). Switch between siblings and look for stale
  letters (e.g. KO after Hungry, Armor Device after Weapon Device 2).
- [ ] (^^) indent restored on t0BAF9C, t0BB0C8, t0BB180; button legends t0B8B5C/t0B8B94/t0B8BC8 and t0B99D4 drop
  the JP indent (lint BLANK_WAIVE): check they line up.
- [ ] 138 strings are wider than their JP under a guessed budget (`python -X utf8 tools/lint.py --guess`, list in
  `docs/review/guess_wide.txt`): measure those windows or see each one in game.
- [ ] s468.00 `busy with {%sR5} or something.` has 8 px spare at the 64 px R5 guess: find R5's source table
  (activity names) or shorten.

- [ ] Timetable subject icons (022CF64, D15) are 3-letter abbreviations (Jpn, Ari, Hlth, HEc, JpH, Clb, Act,
  Cmt...): full names need a wider cell or a subject name line on the palette screen (engine work).

## Unsure names
- [ ] Star names サイド -> Said, ジャバル -> Jabal, ウナルベクサ -> Unalbeksa: no confirmed source star.
- [ ] Byler Dyna puns (Parmoon, Bisaios, Capuchipean): check what the JP pun is once seen in game.

## UI strings to look at in game (phase 6, b042)
- [ ] Line order of multi-line help/panel fragments was assumed to follow pointer order (ascending table address);
  check the link-trade panel (t0B9424-t0B9664), party help (t0B9B64-t0B9D84), PDA help (t0B99A8-t0B9A88).
- [ ] t0B9700-t0B970C: ／ページ drawn one glyph per cell -> "/" "P" "a" "ge"; may look spaced out.
- [x] t0B8254 weekday row: "Sun"+3 PAD per day (the code copies 6 bytes a day, 0x0801FFA4). 3 letters is the
  ruling now (glossary b042 line updated, phase-6 review); the in-game look is a phase-8 calendar check.
- [ ] Money diary week view (`mode_pda_schedule`, worker 15 shot): the day cells' weekday words are clipped to
  ~10 px ("Mc", "Tι", "Wε"; "Fr" / "Sa" fit) and the "Su" cell shows a stray "3": find the string and its window
  (2 letters max, or 1-letter forms), and the header "200５年" (big 5 drawn over 年: same in JP?).
- [ ] t0B9D9C/t0B9DE0 field build rows "> Hole"/"> Land" + register at col 6: what the register holds.
- [ ] t0B8150/t0B8158 "{name} got" / "{item}!": real width of that window.
- [ ] t0B9944 date prompt: fields padded to JP cols 6/10 so the cursor should sit over them; check.
- [ ] Panel lines end in spaces to col 10 so a shorter line still covers the 11 cells the JP redrew.
- [ ] Kept JP (code slices them): calendar digit rows t0B8F78/t0B9124, digits t0B967C, "／" t0B9694.

## b044-b045 (phase 6)
- [x] t0BB224 "{C2}Elem. {%sR0}" (Dyna Database): now "{C2}Element: {%sR0}" (71 px); lint counts this register
  at its longest element word (`tools/lint.py` REG_WORDS). Phase 8: look at it in the Dyna Database.
- [ ] t0BB280 "<@2>Take<@10>Status<@18>Free": "Release" (as in t0BA7C4 / t0BB2AC) overruns 168 px at col 18.
- [ ] t0BAF6C "Linking...<@10>" + kept blank t0BAF84 (11 cells): check the link status line clears.
- [ ] t0BAF9C/t0BB0C8/t0BB180 "(^^)", "Ashibe Boy", "Iced Latte", "Shady Buyer": default names in the link
  battle / minigame screens (unsure where they show; しょうねんアシベ is a manga title parody).
- [ ] Minigame help pages t0BB4C4-t0BB7A8 (3 games): line order assumed by pointer order, 4 lines a page.

## Review round 1 Minors (phase 6, codex, docs/review/gNN.md)
- [ ] (g01) s052.06; s057.00 - 「ふつうじゃないばあい」 means exceptions to the usual scouting result - “not-normal case(s)” sounds translated - “I'll explain the exceptions later.” / “Bingo! This is the exception I mentioned earlier.”
- [ ] (g01) s054.00 - 「ぜんぜん かんけいないところ」 means a completely irrelevant spot, here an empty square - “somewhere totally unrelated” is unnatural in battle dialogue - “Oops, he hit a spot with nothing there...”
- [ ] (g01) s074.12 - 「てもち アイテムを へらしてから」 asks the player to reduce their inventory - “Please have fewer items on hand” is awkward - “Please make room in your inventory, then come back to pick it up.”
- [ ] (g01) s090.00 - 「ぶじ かんせい」 means successfully completed despite the trouble - “finished safely” suggests physical safety - “There was a little trouble, but it is complete now.”
- [ ] (g02) s104.05 - 「オレさまの　いきざま　みとけ！」 demands that the player witness his determination - “Watch how the great me lives” sounds like a lifestyle demonstration - “I'll climb right back up! Watch the great me make my comeback!{KP}See ya!!”
- [ ] (g02) s106.05 - 「シティのほうも　まけちゃいそう」 fears being outdone at city building too - “on the city side” is awkward - “You might outdo me at building a city too, not just in battle...”
- [ ] (g02) s113.07 - 「ノーコメントって　やつですぅ」 invokes the stock phrase “no comment” - “it's a no comment” is unidiomatic - “...is what they told me, so I can't answer thaaat.{KP}It's a trade secret, so 'no comment,' as they saaay... Teehee!”
- [ ] (g02) s121.06 - 「ライバルであるコイツには　わかってる」 insists his rival understands his excuse - the fronted “That...” clause makes Genio sound stiff - “Sh-shut up! My rival here knows the great me couldn't show my true power!{KP}Right!?”
- [ ] (g02) s124.02 - 「さきほどから…できなくなってしまっている」 describes an inability continuing since earlier - “a little while ago, I suddenly cannot” mixes incompatible time frames - “The truth is... for some reason, I have been unable to connect to the Dyna Net at all since a little while ago.”
- [ ] (g03) s128.29 - 「もう てにはいらないと きまったわけでは ない」 means obtaining it again is still possible - “it is not decided that you can never get it” is stiff translationese - “No, you may still have another chance to obtain it.”
- [ ] (g03) s133.06 - 「バトルを うけるか」 asks whether the player accepts a challenge - “take a battle” is unnatural - “What do you say, kid... Will you accept my challenge?{KP}I'll show you what a Device made from the Giga Diamond can do.”
- [ ] (g03) s143.25, s147.64 - 「やぼうを くいとめて」 means thwart Byler’s ambitions - “stop Byler's ambitions” is an awkward collocation - Use “Please thwart Byler's ambitions.”
- [ ] (g04) s150.29 - 「いっきにいくよ？」 means rushing in together/in one go - “We go all at once” sounds stiff and obscures the intended rush - Suggested EN: “{%sR4}-kun... ready?{KP}Let's rush in!”
- [ ] (g04) s152.06 - 「こんなものは・・・こうだっ！！」 accompanies a furious action against the game - “This whole thing... can go like THIS” is unnatural and weakens the tantrum - Suggested EN: “I won't allow it! Things have to go my way!{KP}Take... THIS!!”
- [ ] (g04) s153.07, s155.10 - 「ダイナデバイスをたのしんで」 means enjoying the game Dyna Device - “the Dyna Device” makes the title sound like a physical device - Suggested EN: “You can get there by subway, so please visit if you like.{KP}Well then, please keep enjoying Dyna Device!”
- [ ] (g04) s231.00 - 「リカバリーされました」 reports restoration - “has been recovered” sounds like a lost object was retrieved - Suggested EN: “{%sR4} has been restored.{KN}”
- [ ] (g04) s272.01 - 「アンタのホンキはしょせんそんなもの」 taunts the player's best effort - “your ‘serious’ amounts to” is awkward English - Suggested EN: “Is that really your best, desuuu?{KN}”
- [ ] (g04) s275.00–01 - 「このゲーム ボクのかちだ」「まだあきらめずにちょうせんしてくる？」 means “I win; will you challenge me again?” - “This game is my win” and “keep trying, not giving up” sound translated - Suggested EN: “Game over... It's done.{KP}I win.” / “Or do you still want to challenge me?{KN}”
- [ ] (g05) s406.00 - 「なんでぇ {%sR4}かよ」 means “Oh, it's you” with disappointment - “Whaddaya want” loses the recognition beat - Suggested EN: “...Oh, it's you, {%sR4}.{KP}...Sorry, but can it wait till later?”
- [ ] (g05) s457.01 - 「ほかの セクタタイプに かえて」 asks to change the nearby sectors - “it” disagrees with the preceding “There are ... sectors” - Suggested EN: “Could you possibly change them to another sector type?”
- [ ] (g05) s513.00 - 「かっこいいですよね」 is friendly, polite agreement - “Is that not cool?” sounds stiff - Suggested EN: “That is pretty cool, right?”
- [ ] (g06) s656.00, s659.00 - 「アイテムが いっぱい」: inventory capacity reached - “Your items are full” unnaturally describes the items themselves as containers - Suggested EN: “Your bag is full!”; “Your bag is full. You cannot carry any more.”
- [ ] (g06) s667.00, s670.00 - 「だれか またせているのではないですか？」: reminder that someone is waiting - “is someone not waiting” is an awkward negative question - Suggested EN: “By the way, is someone waiting for you at the Colosseum?{KP}Please do not forget to go and see them.”
- [ ] (g07) s719.01–s719.02 - 「ゆうしょうでのみ てにはいる」 describes the prize Dyna - “As your prize, available only…” dangles before “the Dyna Net” - “Your prize is available only to Ranking Battle champions:” / “the Dyna Net has sent you a Draco style Dyna of the {%sR1} element.{KN}”
- [ ] (g07) s778.00 - 「さっそくですが」 introduces the next step politely - “Right away, please…” sounds like an urgent command - “Now then, please give this little one a name.”
- [ ] (g07) s814.01 - 「そんな つよい {%sR4}に」 means a gift for the strong player - “for sooo strong {%sR4}” is unnatural English - “For someone as strooong as {%sR4}, here's a present from little old me.”
- [ ] (g07) s814.05 - 「わたくしの がんばりに…まけちゃった」 playfully says her effort surpassed the player's - “lost…to how hard I tried” is awkward - “{%sR4} tried really haaard, too...{KP}But I tried juuust a teeny bit harder and won. Hehehe.”
- [ ] (g08) t0B39A4 - 「ついばむ」 = peck at food - “Pick” obscures the bird’s action - suggested EN: “Peck”.
- [ ] (g09) t0B6AF4 - 「じりょくで かいてんして」 means spinning through magnetism - “spinning by magnets” is unnatural - suggested EN: “spun by magnetism,”.
- [ ] (g09) t0B6B68 - 「ファクトリーなどの」 means Factory and similar sectors - “Factory-like” suggests resemblance rather than including Factory itself - suggested EN: “or Factory”.
- [ ] (g10) t0B9C44, t0B9C30, t0B9C18 - 「Ｒボタンを おすと バトルリストから はずすことが できます」 explains removal using R - Assembled English lacks a subject: “With the R Button, from the Battle List can be removed.” - `Remove it` / `from the Battle List` / `with R.`
