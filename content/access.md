The developer stage is present on **PlayStation 2, GameCube and Xbox**, but there is no known route through ordinary gameplay. You can reach it with a compatible developer-stage savestate or by redirecting a stage transition to `stag0000`.

## Create a developer-stage ISO

The patcher automatically detects the **platform and region**, then changes the character-selection transition so that it requests **`stag0000` instead of the Main Lobby**. It creates a separate image and leaves your original file unchanged.

**Requirements:** Python 3.11 or newer, with no additional Python packages, and a supported game image:

| Platform | Releases supported | Input formats |
| --- | --- | --- |
| PlayStation 2 | USA · Europe · Japan | ISO |
| GameCube | USA · Japan | ISO/GCM · CISO |
| Xbox | USA · Japan | Game-partition XISO |

**Convert first:** RVZ, GCZ, WIA and NKit images must be converted to plain GameCube ISO/GCM before using the patcher. GameCube CISO input is supported and expanded to a plain ISO.

You also need valid saved character data for the normal character-selection route.

1. Have an image of Digimon World 4 (Digimon World X in Japan) in one of the supported formats above.
2. [Download the Developer Stage patcher](assets/tools/patch_dev_stage.py) and put it beside your ISO.
3. Open a terminal in that folder and run:

```sh
python3 patch_dev_stage.py "Digimon World 4 (USA).iso" --output "Digimon World 4 - Developer Stage.iso"
```

4. Open **Digimon World 4 - Developer Stage.iso** in the emulator for that platform.
5. Load your Digimon and finish normal character selection. The transition that normally takes you to the Main Lobby now targets the developer stage.

Use your own image’s filename in the command above. No platform or region flags are needed; detection uses the disc’s contents rather than its filename.

The patcher recognises the retail developer-stage and login packs and boot executable, and refuses altered patch targets or existing output files. To show the detected platform, region and patch plan without creating a new image:

```sh
python3 patch_dev_stage.py "Digimon World 4 (USA).iso" --check
```

The patch redirects the native login destination and enables the full NPC roster in releases where flag 960 would hide it. Saved progression flags are unchanged. [NPC visibility details →](technical-notes.html#npc-visibility-and-flag-960)

## Access methods

| Method | How it works | What you need |
| --- | --- | --- |
| Developer Stage savestate | Restore a state already inside `stag0000` | A developer-stage state compatible with your emulator, supplied separately |
| NPC-specific savestate | Restore a state standing in front of a particular debug NPC | A compatible state; `digi-elf-2` starts at the stage-select NPC |
| Redirect a stage transition in RAM | Change the stage-name pointer in an existing gate transition record, then confirm the gate | Requires identifying the live command record and a valid stage-name string; addresses can depend on the loaded state |
| Patch the character-select transition | Use the patcher above to replace the Main Lobby destination with `stag0000` | A supported disc image, Python, and saved character data for the normal login route |

Savestates and patched game images are not included with this guide.

## Savestates and disc changes

A savestate restores a world that is already loaded in RAM. **Loading it does not refresh that world’s assets from the disc.** After changing discs, load your destination through the stage-select menu to use the new disc’s assets.

## Returning to normal play

Leomon’s menu offers to finish debug and transfer to `ML11`. The exit script requests **`stagML11`, entry position 3**. See the [NPC documentation](debug-npcs.html#leomon-return-to-the-lobby).
