# Polish list

Minor issues to revisit before release (phase 9 needs every line ticked). `[ ]` open, `[x]` done or waived with reason.

## Cuts forced by the 64 px name slots (phase 6, b033-b035)
- [ ] t0B3DAC メガフレアルビー -> "Flare Ruby" ("Mega" cut). Wider name slot or a narrower font would restore it.
- [ ] t0B3D84 サンダートパーズ -> "Bolt Topaz" (Thunder -> Bolt, the game's own thunder Extra word).
- [ ] マシンガン -> "Rapid Gun" (descriptions and item list), アース -> Gran in Gran Launcher / Gran Stun Gun.
- [ ] Armor list names keep the JP grade letters E/O/S/R; meaning unknown (element?). Check in game.

## Unsure names
- [ ] Star names サイド -> Said, ジャバル -> Jabal, ウナルベクサ -> Unalbeksa: no confirmed source star.
- [ ] Byler Dyna puns (Parmoon, Bisaios, Capuchipean): check what the JP pun is once seen in game.

## UI strings to look at in game (phase 6, b042)
- [ ] Line order of multi-line help/panel fragments was assumed to follow pointer order (ascending table address);
  check the link-trade panel (t0B9424-t0B9664), party help (t0B9B64-t0B9D84), PDA help (t0B99A8-t0B9A88).
- [ ] t0B9700-t0B970C: ／ページ drawn one glyph per cell -> "/" "P" "a" "ge"; may look spaced out.
- [ ] t0B8254 weekday row: "Sun"+3 PAD per day (the code copies 6 bytes a day, 0x0801FFA4).
- [ ] t0B9D9C/t0B9DE0 field build rows "> Hole"/"> Land" + register at col 6: what the register holds.
- [ ] t0B8150/t0B8158 "{name} got" / "{item}!": real width of that window.
- [ ] t0B9944 date prompt: fields padded to JP cols 6/10 so the cursor should sit over them; check.
- [ ] Panel lines end in spaces to col 10 so a shorter line still covers the 11 cells the JP redrew.
- [ ] Kept JP (code slices them): calendar digit rows t0B8F78/t0B9124, digits t0B967C, "／" t0B9694.

## b044-b045 (phase 6)
- [ ] t0BB224 "{C2}Elem. {%sR0}" (Dyna Database): abbreviated because lint counts the register as 64 px; it only
  holds element words (longest "thunder"), so "Element {%sR0}" probably fits: check in game, then raise the budget.
- [ ] t0BB280 "<@2>Take<@10>Status<@18>Free": "Release" (as in t0BA7C4 / t0BB2AC) overruns 168 px at col 18.
- [ ] t0BAF6C "Linking...<@10>" + kept blank t0BAF84 (11 cells): check the link status line clears.
- [ ] t0BAF9C/t0BB0C8/t0BB180 "(^^)", "Ashibe Boy", "Iced Latte", "Shady Buyer": default names in the link
  battle / minigame screens (unsure where they show; しょうねんアシベ is a manga title parody).
- [ ] Minigame help pages t0BB4C4-t0BB7A8 (3 games): line order assumed by pointer order, 4 lines a page.
