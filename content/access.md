The developer stage is present in the USA retail game, but there is no known route through ordinary gameplay. You can reach it with a compatible dev-world savestate or by redirecting a stage transition to `stag0000`.

## Create a dev-world ISO

The included patcher changes the character-selection transition so that it requests **`stag0000` instead of the Main Lobby**. It creates a separate ISO and leaves your original file unchanged.

1. Have an original **USA PS2** image of Digimon World 4 and **Python 3.11 or newer**.
2. [Download the dev-world patcher](assets/tools/patch_dev_world.py) and put it beside your ISO.
3. Open a terminal in that folder and run:

```sh
python3 patch_dev_world.py "Digimon World 4 (USA).iso" --output "Digimon World 4 - Dev World.iso"
```

4. Boot **Digimon World 4 - Dev World.iso** in PCSX2.
5. Load your Digimon and finish normal character selection. The transition that normally takes you to the Main Lobby now targets the developer world.

Start by booting the patched image; loading an existing savestate in another area bypasses the changed character-selection transition. If “Call Digimon” reports no game file, you need valid saved character data to continue through that route.

The patcher accepts the exact original USA image with MD5 **`3185f04230b1dabd853db750e4b51108`**. It refuses other versions, modified images, and existing output files. To check compatibility without creating a new image:

```sh
python3 patch_dev_world.py "Digimon World 4 (USA).iso" --check
```

The changes are three same-length stage-name replacements in AFS entries **808, 810 and 812**. The patch’s output has been checked against the original image for those changes only. This guide does not claim a new emulator boot test of the generated image.

## Access methods

| Method | How it works | What you need |
| --- | --- | --- |
| Developer-world savestate | Restore a state already inside `stag0000` | A compatible PCSX2 dev-world state, supplied separately |
| NPC-specific savestate | Restore a state standing in front of a particular debug NPC | A compatible state; `digi-elf-2` starts at the stage-select NPC |
| Redirect a stage transition in RAM | Change the stage-name pointer in an existing gate transition record, then confirm the gate | Requires identifying the live command record and a valid stage-name string; addresses can depend on the loaded state |
| Patch the character-select transition | Use the patcher above to replace the Main Lobby destination with `stag0000` | An original USA PS2 ISO, Python, and saved character data for the normal login route |

Savestates and patched game images are not included with this guide.

## Using the stage-select NPC

Start inside the developer world, facing the Digi-Elf identified as **Digi-Elf 2**.

1. Press **Cross** to talk, then advance the two dialogue lines. Three Cross presses open the first stage-list screen.
2. The cursor starts on **つぎのページ / Next page**. Confirm that line to advance a screen.
3. On the desired screen, move down once for the first destination, twice for the second, and so on. The [stage table](stage-select.html) gives these row numbers directly.
4. Press **Cross** to confirm the destination, then let the stage finish loading.
5. Check the resulting scene or loading banner to confirm the destination.

For example, **`dng102b3` is screen 5, row 1**: open the list, advance four screens, move down once, and confirm.

## Controller observations

- **Left stick:** verified for moving the stage-list cursor. Short taps avoid auto-repeat; the original automation measured a roughly 0.10-second flick for one row.
- **Cross:** talks, advances dialogue, and confirms a choice.
- **D-pad:** early tests used a defective virtual pad. The dev menu’s D-pad behaviour was not subsequently re-tested, so the old “D-pad ignored” observation does not establish a game restriction.

## Savestates and disc changes

A savestate restores a world that is already loaded in RAM. **Loading it does not refresh that world’s assets from the disc.** To inspect a changed destination pack, use the stage-select menu to load the destination after starting with the intended disc.

The screenshots use a level-99 character with modified stats. Use fresh destination loads and check your player settings when comparing behaviour with ordinary gameplay.

## Returning to normal play

Leomon’s menu offers to finish debug and transfer to `ML11`. The exit script requests **`stagML11`, entry position 3**. See the [NPC documentation](debug-npcs.html#leomon-return-to-the-lobby).
