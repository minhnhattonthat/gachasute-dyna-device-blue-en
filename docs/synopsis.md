# Synopsis and chapter list (phase 9 story pass)

Written from the script (scripts 0-155 run in story order through the event table 0x080CED94; see
`docs/re/debug.md`). Scripts 156+ are not story order: shop, NPC, side-event and system texts, grouped by number.

## Plot
The player buys a **Dyna Pad**, a handheld that runs the online game **Dyna Device**: you build a **Dyna City** on the
**Dyna Net**, hatch creatures (**Dyna**) from the **Gachasute** machine, house them, develop **Devices** (equipment)
in the **Factory** and fight grid battles (scout squares, set traps, attack) in the **Colosseum**. **Navyu**, the Pad's
very polite guide AI, explains everything. Friend **Yurie** (calls the player "-kun") plays too; loudmouth rival
**Genio** ("the great me") and smug classmate **Ippa** show up to battle.

A hacker group, **Byler** (virus pun), invades Dyna Cities: grunt **Sigma** (", desu" tic), drawling **Jorna**, cool
**Terry**, under **Yamada-sama**. Terry hunts the **Giga Diamond**. The player wins tournaments (two Colosseum cups,
scripts 101-105 and 119-123) and becomes Champion. Stuffed-toy fake Dyna turn up (124-128), a news report warns of
Byler attacks (133), the **G-Force** (Dyna Net security) finds **Byler City**. Yurie stops coming to school (137);
Byler's goal is revealed (145): Yurie is taken over and attacks (146-147, "Stop it, Yurie-san!"). The player and
friends storm Byler City (149-151, "Attraction closed" restart prompts are the game's own wording), beat the boss
(152, a calm, childish boy: "Maybe I'll just erase you"), and the staff roll follows. Scripts 153/155: Navyu's
post-game greeting.

## Chapters (`tools/story.py`, story pass files in `work/qa/story/chapters/`)
| Chapter | Scripts | Contents |
|---|---|---|
| ch01 | 0-69 | intro, Navyu's tutorial, Gachasute, houses, sectors, Yurie's Colosseum and battle tutorial |
| ch02 | 70-109 | battle tutorial end, Device development, Genio's challenge, Byler grunts, first tournament |
| ch03 | 110-129 | Genio/Ippa after the cup, Jorna and Terry, second tournament, stuffed-toy Dyna |
| ch04 | 130-149 | Champion, Byler news, Yurie missing, Byler's goal, Yurie attacked, into Byler City |
| ch05 | 150-339 | Byler City, final battle, ending, post-game greeting; small system scripts 156-339 |
| ch06 | 340-419 | side scripts |
| ch07 | 420-449 | side scripts (NPC talk) |
| ch08 | 450-599 | side scripts |
| ch09 | 600-689 | side scripts, reception |
| ch10 | 690-749 | item shop, Colosseum desk, Device development texts |
| ch11 | 750-799 | travelling merchant, side events |
| ch12 | 800-839 | side events (816-817 continue-path scripts) |
