## Stage data across platforms

`stag0000` is included in the USA, European and Japanese PS2 releases, and the USA and Japanese GameCube and Xbox releases. In each of these versions, its stage manifest is **NDMW.AFS entry 137**, and the manifest loads its scene and debug scripts from **entry 603**.

Each version contains the same nine-screen stage-select list with 97 entries. The visible environment, floor collision, boundary collision, background and fog settings also match across the three PS2 releases.

## Shared practice-stage environment

The dev world (`stag0000`, NDMW.AFS entry 603) and practice stage (`stag0001`, entry 607) use the same visible environment layout. Their `BG02` background scenes have matching hierarchy, mesh data and world transforms. NPCs, enemies and separately placed objects differ between the stages.

| Environment data | Comparison |
| --- | --- |
| Visible background | Same 33-node scene, 12 geometry nodes and 3,219 vertices; positions, normals, UVs and triangle indices match |
| Floor collision | Same two geometry nodes and 42 vertices |
| Main boundary collision (`0x802`) | Same geometry and transforms |
| Kind-4 collision graph | Same geometry and transforms |
| Background and fog colour | Both store RGBA `(0.8, 0.7, 0.8, 1.0)`, giving the void a slight mauve tint |
| Additional practice-stage wall | The practice stage has one extra kind-2 collision graph; the dev world does not |

The shared visible layout does not mean that every object, interaction or collision rule is the same.

## Stage transitions

The stage-select menu is stored in **AFS entry 603**. Its nine screen scripts supply 97 unique destination IDs. Each destination is paired with `PLAYERPOINT SETGENERATEPOS "I<0>"`.

Leomon’s separate exit action is `057-dm-run.lua` in the same pack. It requests **`stagML11` at entry position 3**. Choosing `stagML11` from the stage-select list instead uses that list’s normal position 0.

The complete destination data is available as [JSON](assets/data/stages.json).

## Character-selection patch

The [access patcher](assets/tools/patch_dev_world.py) replaces the eight-byte string `stagML11` with `stag0000` in three character-selection packs. It identifies the USA, European or Japanese image by size and MD5, then applies that release’s offsets to a separate copy.

| Region | AFS entry 808 | AFS entry 810 | AFS entry 812 |
| --- | --- | --- | --- |
| USA | `0x471DB773` | `0x4722B38B` | `0x4730C52F` |
| Europe | `0x469B7B6B` | `0x46A35867` | `0x46AC745F` |
| Japan | `0x471C7957` | `0x47240177` | `0x473A3AD3` |

Each entry replaces `stagML11` with `stag0000`. The fixed-length replacements preserve the pack sizes and ISO layout, changing twelve bytes in total. The offsets apply to the original images listed in the [access guide](access.html).

## Unlocks and cheats

| Function | Script reference | Behaviour |
| --- | --- | --- |
| Unlock all Digivolutions | `030-msg-80031.lua`, AFS entry 603 | Calls `SYSctlShinka("SETSHINKA", ...)` for indices 0–15 for each joined player |
| Individual unlocks | `031-msg-80067.lua` through `046-msg-80082.lua`, AFS entry 603 | Calls `SETSHINKA` with the selected index for the interacting player |
| Money MAX | `028-damage-calc-2.lua`, AFS entry 603 | Sets BIT to 9,999,999 for each joined player |
| Item MAX | On-screen result message | Says “All items ×9”; exact item coverage is undocumented |

## Functions that need more documentation

- **TIME00–TIME06 and Field Quest:** the menu names are visible, but their gameplay effects and the code that reads the values still need tracing.
- **NORMAL / MINIMUM:** the text-size choices are visible, but the affected text consumers are not yet identified.
- **Play mode:** the menu offers Hard and Very Hard; the exact storage variable and its relationship to normal difficulty selection still need documenting.
- **Other routes into the dev world:** a `NEXTSTAGE "stag0000"` reference outside the stage-select list has been reported; its context and reachability need establishing.

## Corrections and contributions

[Open an issue](https://github.com/crashbashash/dw4-dev-world/issues) to suggest a correction or supply additional information. A screenshot, exact game version, or script reference helps document the behaviour precisely.

Game names, dialogue and screenshots belong to their respective rights holders. This is an unofficial guide to the dev world.
