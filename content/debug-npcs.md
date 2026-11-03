Names such as `digi-elf-1` identify individual characters in this guide. The six Digi-Elves all display デジルフ in the game.

## Digi-Elf 1: text size

The opening dialogue asks the player to choose a character size.

| Japanese option | English translation |
| --- | --- |
| NORMALでおねがいします | NORMAL, please |
| MINIMUMでおねがいします | MINIMUM, please |
| スミマセン、みるのやめます | Sorry, I’ll stop looking |

Selecting a size ends the conversation. Exactly which text responds to this setting remains undocumented.

![Annotated capture of the Digi-Elf text-size menu](assets/images/translated/digi-elf-1/03-menu-default.png)

[All text-size captures →](gallery.html#digi-elf-1)

## Digi-Elf 2: stage select

> ステージせんたくするよ！ほかのステージにどうする？
>
> “Let’s select a stage! What about another stage?”

After the opening dialogue, the game displays stage IDs and a **つぎのページ / Next page** option. There are **97 destinations on nine screens**, with eleven destinations on each of the first eight screens and nine on the last. Confirming an entry performs a real stage load.

Before opening the list, the Digi-Elf offers:

| Japanese option | English translation |
| --- | --- |
| とびます!とびます! | I’ll warp! I’ll warp! |
| まだここにいる! | I’ll stay here! |

Choose the first option to open the stage menu.

[Dialogue and all nine menu screenshots →](gallery.html#digi-elf-2)

[Complete stage list and menu procedure →](stage-select.html)

## Digi-Elf 3: play mode / difficulty

> プレイするモードをせんたくします
>
> “Select the mode to play.”

| Japanese option | English translation |
| --- | --- |
| へんこうしません | Don’t change |
| ハード | Hard |
| ベリーハード | Very Hard |

The exact storage variable and its relationship to the normal game’s difficulty selection remain undocumented.

[Difficulty-menu captures →](gallery.html#digi-elf-3)

## Digi-Elf 4: TIME flags

> TIMEフラグをへんこうします
>
> “Change the TIME flag.”

After a yes/no prompt, the menu offers three groups:

| Screen | Choices |
| --- | --- |
| 1 | Next page · TIME00 · TIME01 · TIME02 |
| 2 | Next page · TIME03 · TIME04 · TIME05 |
| 3 | TIME06 · フィールドクエスト / Field Quest · Cancel |

The gameplay effects of these flags remain undocumented. Their names alone do not establish a time-of-day system.

[TIME-flag captures →](gallery.html#digi-elf-4)

## Digi-Elf 5: Digivolution unlocks

The dialogue uses **しんかワザ**, rendered as “evolution arts” in the existing English annotations. The menu offers “learn all” or individual Digimon across six screens. The recovered scripts call `SYSctlShinka("SETSHINKA", ...)`.

| Screen | Individual choices |
| --- | --- |
| 1 | Agumon · V-mon |
| 2 | Guilmon · Dorumon · Wargarurumon |
| 3 | HerakleKabuterimon · WarGreymon · ClavisAngemon |
| 4 | Beelzemon Blast Mode · Alphamon · BlackWarGreymon |
| 5 | Imperialdramon Fighter Mode · Imperialdramon Paladin Mode · MetalGarurumon |
| 6 | Dukemon Crimson Mode · Susanoomon · Learn none |

These English names follow the screenshot translations and may differ from regional localisation names. One result message is デュークモンCMをおぼえました: “Learned Dukemon CM.”

![Japanese evolution-arts choices with English annotations](assets/images/translated/digi-elf-5/03.png)

[All unlock-menu captures →](gallery.html#digi-elf-5)

## Digi-Elf 6: EXP / level targets

> すきなLVまでのEXPをあげますよ…LVいくつになりたいですか？
>
> “I’ll give you EXP up to any LV you like… What LV do you want to be?”

| Screen | Level targets |
| --- | --- |
| 1 | LV16 · LV36 · LV46 |
| 2 | LV76 · LV106 · LV999 |
| 3 | LV50 · LV100 · LV200 · Stop |

These are the debug menu’s labels, not evidence that every listed level is supported as an ordinary progression cap.

After granting EXP, the NPC instructs the player to hit the neighbouring Goblimon:

> “I raised your EXP, so… please punch the Goblimon next to you… your LV will go up by 1…”

The grant does not directly complete the level-up. The two Goblimon have no recorded dialogue and provide combat targets for resolving it.

[EXP-menu captures →](gallery.html#digi-elf-6)

## Leomon: return to the lobby

> デバッグをしゅうりょうして ML11にてんそうします
>
> “Finish debug and transport to ML11.”

The prompt offers yes or no. The recovered exit script targets **`stagML11`**, the Main Lobby, using entry position **3**. This differs from the stage-select list, whose entries use position **0**.

The destination and position come from the exit script, `057-dm-run.lua` in AFS entry 603. The screenshots show its confirmation prompt.

The Japanese name レオモン identifies this character as **Leomon**.

[Leomon captures →](gallery.html#leomon-1)

## The two rocks: item and money cheats

| Object | Captured message | Translation |
| --- | --- | --- |
| Rock 1 | アイテム MAX / アイテム すべてx9 になりました | ITEM MAX / All items became ×9 |
| Rock 2 | おかね MAX / BITが 9999999 になりました | MONEY MAX / BIT became 9,999,999 |

The money script explicitly sets BIT to **9,999,999** for joined players. “All items ×9” is the item cheat’s displayed message; its effect on every individual item has not been verified.

[Item-cheat captures →](gallery.html#rock-1) · [Money-cheat captures →](gallery.html#rock-2)
