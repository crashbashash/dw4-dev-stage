## Stage data across platforms

`stag0000` is included in the USA, European and Japanese PS2 releases, and the USA and Japanese GameCube and Xbox releases. In each of these versions, its stage manifest is **NDMW.AFS entry 137**, and the manifest loads its scene and debug scripts from **entry 603**.

Each version contains the same nine-screen stage-select list with 97 entries. The visible environment, floor collision, boundary collision, background and fog settings also match across the three PS2 releases.

## NPC visibility and flag 960

The **USA PS2, USA GameCube, USA Xbox and European PS2 releases** condition most of the developer stage’s NPC spawns on **flag 960 being clear**.

| Flag 960 | Characters and objects spawned |
| --- | --- |
| Clear (`0`) | All six Digi-Elves, Leomon, both Goblimon and both cheat rocks |
| Set (`1`) | The stage-select Digi-Elf and both cheat rocks |

Normal character data starts with flag 960 set. Redirecting that login into `stag0000` can therefore produce a partly populated developer stage even though all of the NPC data is present.

The Japanese PS2, GameCube and Xbox releases do not have these two flag checks in the developer stage startup script. They spawn the full roster regardless of flag 960.

This behaviour comes from the stage’s startup script: one check surrounds Leomon and the other five Digi-Elves, and the other surrounds the two Goblimon. The stage-select Digi-Elf and the rocks are outside both checks.

## Shared practice-stage environment

The developer stage (`stag0000`, NDMW.AFS entry 603) and practice stage (`stag0001`, entry 607) use the same visible environment layout. Their `BG02` background scenes have matching hierarchy, mesh data and world transforms. NPCs, enemies and separately placed objects differ between the stages.

| Environment data | Comparison |
| --- | --- |
| Visible background | Same 33-node scene, 12 geometry nodes and 3,219 vertices; positions, normals, UVs and triangle indices match |
| Floor collision | Same two geometry nodes and 42 vertices |
| Main boundary collision (`0x802`) | Same geometry and transforms |
| Kind-4 collision graph | Same geometry and transforms |
| Background and fog colour | Both store RGBA `(0.8, 0.7, 0.8, 1.0)`, giving the void a slight mauve tint |
| Additional practice-stage wall | The practice stage has one extra kind-2 collision graph; the developer stage does not |

The shared visible layout does not mean that every object, interaction or collision rule is the same.

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

## Functions that need more documentation

- **TIME00–TIME06 and Field Quest:** the menu names are visible, but their gameplay effects and the code that reads the values still need tracing.
- **NORMAL / MINIMUM:** the text-size choices are visible, but the affected text consumers are not yet identified.
- **Play mode:** the menu offers Hard and Very Hard; the exact storage variable and its relationship to normal difficulty selection still need documenting.
- **Other routes into the developer stage:** a `NEXTSTAGE "stag0000"` reference outside the stage-select list has been reported; its context and reachability need establishing.

## Corrections and contributions

[Open an issue](https://github.com/crashbashash/dw4-dev-stage/issues) to suggest a correction or supply additional information. A screenshot, exact game version, or script reference helps document the behaviour precisely.

Game names, dialogue and screenshots belong to their respective rights holders. This is an unofficial guide to the developer stage.
