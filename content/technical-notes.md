## Stage transitions

The stage-select menu is stored in **AFS entry 603**. Its nine screen scripts supply 97 unique destination IDs. Each destination is paired with `PLAYERPOINT SETGENERATEPOS "I<0>"`.

Leomon’s separate exit action is `057-dm-run.lua` in the same pack. It requests **`stagML11` at entry position 3**. Choosing `stagML11` from the stage-select list instead uses that list’s normal position 0.

The complete destination data is available as [JSON](assets/data/stages.json).

## Character-selection patch

The [access patcher](assets/tools/patch_dev_world.py) replaces the eight-byte string `stagML11` with `stag0000` in three character-selection packs. It checks the original USA ISO’s size and MD5 before creating a separate copy.

| AFS entry | ISO byte offset | Replacement |
| --- | --- | --- |
| 808 | `0x471DB773` | `stagML11` → `stag0000` |
| 810 | `0x4722B38B` | `stagML11` → `stag0000` |
| 812 | `0x4730C52F` | `stagML11` → `stag0000` |

The fixed-length replacements preserve the pack sizes and ISO layout. Across the image they change twelve bytes in total. These offsets apply only to the exact USA image accepted by the patcher.

## Unlocks and cheats

| Function | Script reference | Behaviour |
| --- | --- | --- |
| Unlock all Digivolutions | `030-msg-80031.lua`, AFS entry 603 | Calls `SYSctlShinka("SETSHINKA", ...)` for indices 0–15 for each joined player |
| Individual unlocks | `031-msg-80067.lua` through `046-msg-80082.lua`, AFS entry 603 | Calls `SETSHINKA` with the selected index for the interacting player |
| Money MAX | `028-damage-calc-2.lua`, AFS entry 603 | Sets BIT to 9,999,999 for each joined player |
| Item MAX | On-screen result message | Reports that all items became ×9; the exact effect on every individual item remains unverified |

## Functions that need more documentation

- **TIME00–TIME06 and Field Quest:** the menu names are visible, but their gameplay effects and the code that reads the values still need tracing.
- **NORMAL / MINIMUM:** the text-size choices are visible, but the affected text consumers are not yet identified.
- **Play mode:** the menu offers Hard and Very Hard; the exact storage variable and its relationship to normal difficulty selection still need documenting.
- **Other routes into the dev world:** a `NEXTSTAGE "stag0000"` reference outside the stage-select list has been reported; its context and reachability need establishing.
- **Individual level and unlock choices:** the menu pages are documented, but not every possible result has a separate capture or behaviour check.

## Screenshot notes

The English annotations preserve Japanese game text as image pixels and place translations beside it. They may use Japanese or regional Digimon names that differ from the USA localisation.

The screenshots include repeated menu screens. The stage-list filenames preserve capture sequence, not screen order. Use the [stage reference](stage-select.html) for the nine canonical screens.

## Corrections and contributions

[Open an issue](https://github.com/crashbashash/dw4-dev-world/issues) to suggest a correction or supply additional information. A screenshot, exact game version, or script reference helps document the behaviour precisely.

Game names, dialogue and screenshots belong to their respective rights holders. This is an unofficial guide to the dev world.
