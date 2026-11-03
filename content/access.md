The developer stage is present on **PlayStation 2, GameCube and Xbox**, but there is no known route through ordinary gameplay. You can reach it with a compatible dev-world savestate or by redirecting a stage transition to `stag0000`.

## Create a dev-world ISO

The included **PS2 patcher** changes the character-selection transition so that it requests **`stag0000` instead of the Main Lobby**. It creates a separate ISO and leaves your original file unchanged.

1. Have an original **USA, European or Japanese PS2** image of Digimon World 4 (Digimon World X in Japan) and **Python 3.11 or newer**.
2. [Download the dev-world patcher](assets/tools/patch_dev_world.py) and put it beside your ISO.
3. Open a terminal in that folder and run:

```sh
python3 patch_dev_world.py "Digimon World 4 (USA).iso" --output "Digimon World 4 - Dev World.iso"
```

4. Boot **Digimon World 4 - Dev World.iso** in PCSX2.
5. Load your Digimon and finish normal character selection. The transition that normally takes you to the Main Lobby now targets the developer world.

Start by booting the patched image; loading an existing savestate in another area bypasses the changed character-selection transition. If “Call Digimon” reports no game file, you need valid saved character data to continue through that route.

Use your own ISO’s filename in the command above. The patcher detects the region automatically and uses the corresponding offsets.

| Region | Game ID | Original ISO MD5 |
| --- | --- | --- |
| USA | `SLUS-20836` | `3185f04230b1dabd853db750e4b51108` |
| Europe | `SLES-53405` | `bd95f00a8efa2ab6b502b7aade37f143` |
| Japan | `SLPS-25453` | `78543a26a08d82fb32f1f3b5035d7e3b` |

It refuses unsupported or modified images and existing output files. To check compatibility without creating a new image:

```sh
python3 patch_dev_world.py "Digimon World 4 (USA).iso" --check
```

The patch changes three same-length stage names in AFS entries **808, 810 and 812**.

## Access methods

| Method | How it works | What you need |
| --- | --- | --- |
| Developer-world savestate | Restore a state already inside `stag0000` | A compatible PCSX2 dev-world state, supplied separately |
| NPC-specific savestate | Restore a state standing in front of a particular debug NPC | A compatible state; `digi-elf-2` starts at the stage-select NPC |
| Redirect a stage transition in RAM | Change the stage-name pointer in an existing gate transition record, then confirm the gate | Requires identifying the live command record and a valid stage-name string; addresses can depend on the loaded state |
| Patch the character-select transition | Use the patcher above to replace the Main Lobby destination with `stag0000` | An original USA, European or Japanese PS2 ISO, Python, and saved character data for the normal login route |

Savestates and patched game images are not included with this guide.

## Using the stage-select NPC

Start inside the developer world, facing the Digi-Elf identified as **Digi-Elf 2**. The controls below use PS2 button names.

1. Press **Cross** to talk, advance the introduction, and confirm the highlighted **とびます!とびます! / I’ll warp!** choice. Three Cross presses open the first stage-list screen.
2. The cursor starts on **つぎのページ / Next page**. Confirm that line to advance a screen.
3. On the desired screen, use the **left stick** to move down once for the first destination, twice for the second, and so on. The [stage table](stage-select.html) gives these row numbers directly.
4. Press **Cross** to confirm the destination, then let the stage finish loading.
5. Check the resulting scene or loading banner to confirm the destination.

For example, **`dng102b3` is screen 5, row 1**: open the list, advance four screens, move down once, and confirm.

## Savestates and disc changes

A savestate restores a world that is already loaded in RAM. **Loading it does not refresh that world’s assets from the disc.** After changing discs, load your destination through the stage-select menu to use the new disc’s assets.

## Returning to normal play

Leomon’s menu offers to finish debug and transfer to `ML11`. The exit script requests **`stagML11`, entry position 3**. See the [NPC documentation](debug-npcs.html#leomon-return-to-the-lobby).
