## Stage data across platforms

`stag0000` is included in the USA, European and Japanese PS2 releases, and the USA and Japanese GameCube and Xbox releases. In each of these versions, its stage manifest is **NDMW.AFS entry 137**, and the manifest loads its scene and debug scripts from **entry 603**.

Each version contains the same nine-screen stage-select list with 97 entries. Across PS2, GameCube and Xbox, the developer stage uses the practice stage’s environment layout, with different NPCs and objects.

## NPC visibility and flag 960

The **USA PS2, USA GameCube, USA Xbox and European PS2 releases** condition most of the developer stage’s NPC spawns on **flag 960 being clear**.

| Flag 960 | Characters and objects spawned |
| --- | --- |
| Clear (`0`) | All six Digi-Elves, Leomon, both Goblimon and both cheat rocks |
| Set (`1`) | The stage-select Digi-Elf and both cheat rocks |

Normal character data starts with flag 960 set. Redirecting that login into `stag0000` can therefore produce a partly populated developer stage even though all of the NPC data is present.

The Japanese PS2, GameCube and Xbox releases do not have these two flag checks in the developer stage startup script. They spawn the full roster regardless of flag 960.

This behaviour comes from the stage’s startup script: one check surrounds Leomon and the other five Digi-Elves, and the other surrounds the two Goblimon. The stage-select Digi-Elf and the rocks are outside both checks.

## Stage transitions

The stage-select menu is stored in **AFS entry 603**. Its nine screen scripts supply 97 unique destination IDs. Each destination is paired with `PLAYERPOINT SETGENERATEPOS "I<0>"`.

Leomon’s separate exit action is `057-dm-run.lua` in the same pack. It requests **`stagML11` at entry position 3**. Choosing `stagML11` from the stage-select list instead uses that list’s normal position 0.

The complete destination data is available as [JSON](assets/data/stages.json).

## Character-selection patch

The [access patcher](assets/tools/patch_dev_stage.py) detects the platform from the disc filesystem, then identifies the region using SHA-256 fingerprints of the developer-stage, login packs and boot executable.

It changes the native login controller’s `stagML11` destination to `stag0000`. The destination is in the PS2 ELF, GameCube DOL or Xbox XBE. Xbox outputs also receive an updated section digest for the changed executable data.

For USA PS2, USA GameCube, USA Xbox and European PS2, the patcher makes the two developer stage NPC-spawn blocks unconditional. It replaces each flag-960 comparison branch with a Lua `POP 2` instruction, preserving the stack effect and instruction count. The full roster then appears without changing flag 960 or any other saved progression flag. Japanese startup scripts already spawn the full roster and need no visibility change.

The patch leaves the stage-select destinations and Leomon’s scripted return to the Main Lobby intact. Its output keeps the existing logical disc layout; GameCube CISO input is expanded into a plain ISO. See the [access guide](access.html) for supported releases and formats.

## Unlocks and cheats

| Function | Script reference | Behaviour |
| --- | --- | --- |
| Unlock all Digivolutions | `030-msg-80031.lua`, AFS entry 603 | Calls `SYSctlShinka("SETSHINKA", ...)` for indices 0–15 for each joined player |
| Individual unlocks | `031-msg-80067.lua` through `046-msg-80082.lua`, AFS entry 603 | Calls `SETSHINKA` with the selected index for the interacting player |
| Money MAX | `028-damage-calc-2.lua`, AFS entry 603 | Sets BIT to 9,999,999 for each joined player |
| Item MAX | On-screen result message | Says “All items ×9”; exact item coverage is undocumented |

## Debug menu behaviour

The following scripts are named resources in the developer-stage pack, **NDMW.AFS entry 603**. Their behaviour matches across the seven releases listed above.

| Function | Script resource | Behaviour |
| --- | --- | --- |
| NORMAL / MINIMUM | `n_digilfm_01.lua` | Displays twelve sample text pages using `TEXTCTL TEXTSET` and waits for the `i_messky` confirmation selector between pages. NORMAL targets `STWINFONT02`; MINIMUM uses `STWINFONT04` for eight pages and `STWINFONT02` for the final four. It restores the interface and controls at the end. |
| TIME00–TIME06 | `time00.lua` through `time06.lua` | Applies story presets through `FLGset` and persistent `SYSctlFlagFolder("SET"/"CLR", index)` writes. These are progression presets; they do not change a clock or request a stage transition. |
| Field Quest | `fieldquest.lua` | Counts joined players at LV16 or above. If the count is nonzero, sets flags `63`, `64`, `97` and `98`; otherwise displays its refusal message. |
| Hard / Very Hard | `hard.lua`, `veryhard.lua` | Writes progression flags, including `70`, `406` and `407`. Neither script calls `SYSsetDifficulty`. |

The TIME presets select successive story phases using flags `1`–`6`. TIME02 and later set boss flag `67`; TIME04 and later also set `68`; TIME05 and later set `69`. TIME06 sets `70`, `83` and `86` as well. Persistent markers are cleared or set to match each preset, and TIME04–TIME06 call `SYSctlDeviceFolder("SET", player, "armor2", 42, 0, 0)` to give a Filter Board to player slots `0`–`3`.

The Field Quest flags have identifiable readers: `63` selects field-event behaviour in Grief Wasteland (`stag0202`), `64` does the same in Mangrove Forest (`stag0302`), and `97`/`98` control two rescue states in Numenume River (`stag0103`) and related lobby dialogue.

Hard and Very Hard both set flags `70`, `406` and `501`–`507`, and clear `508`. Hard clears `407` and `77`; Very Hard sets `407` and leaves `77` unchanged. The active difficulty is a separate common-player property, `DIFFICULTY`, read and written by `SYSgetDifficulty` / `SYSsetDifficulty`. Normal character selection publishes `0`, `1` or `2` to that property for Normal, Hard or Very Hard.

[Menu choices and progression-preset summaries →](debug-npcs.html#digi-elf-4-time-flags)

## Corrections and contributions

[Open an issue](https://github.com/crashbashash/dw4-dev-stage/issues) to suggest a correction or supply additional information. A screenshot, exact game version, or script reference helps document the behaviour precisely.

Game names, dialogue and screenshots belong to their respective rights holders. This is an unofficial guide to the developer stage.
