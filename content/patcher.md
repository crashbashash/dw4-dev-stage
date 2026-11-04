The [Developer Stage patcher](assets/tools/patch_dev_stage.py) creates a separate disc image with two targeted changes: the character-selection destination becomes `stag0000`, and releases with conditional debug NPC spawns receive the full roster. The implementation uses only Python’s standard library.

For the commands and supported input formats, see [Access](access.html#create-a-developer-stage-iso).

## From input image to patch plan

The patcher separates inspection from writing:

1. `Disc` exposes the input as logical disc bytes, expanding GameCube CISO blocks as they are read.
2. `identify()` recognises the platform and reads its filesystem.
3. `inspect()` fingerprints the relevant game data and executable, checks each patch location, and returns an ordered patch plan.
4. `copy_patched()` copies the logical image to a new file, substituting the planned bytes as it reaches each location.

Every patch records a label, an absolute offset in the logical image, the expected original bytes and the replacement bytes. Running with `--check` performs inspection and prints this plan without creating an output image.

## Detecting the disc layout

Detection uses the contents of the image. The input filename and extension do not select the platform or region.

| Platform | Recognition | Filesystem and executable lookup |
| --- | --- | --- |
| PlayStation 2 | ISO9660 `CD001` signature in sector 16 | Read the primary volume descriptor and root directory; locate `NDMW.AFS` and the release’s boot ELF by filename. ISO version suffixes such as `;1` are removed during lookup. |
| GameCube | Disc magic `C2 33 9F 3D` at `0x1C` | Read the filesystem table offset and size at `0x424`; locate `NDMW.AFS`. The boot DOL offset comes from `0x420`, and its file extent is calculated from its section offsets and sizes. |
| Xbox | `MICROSOFT*XBOX*MEDIA` at sector 32 | Read the game-partition XISO root directory tree; locate `NDMW.AFS` and `default.xbe`. |

Disc sectors in the ISO9660 and XISO readers are 2,048 bytes. Directory records, names and file extents are checked before use. The Xbox reader also rejects repeated directory-node offsets, preventing a cyclic tree from being followed indefinitely.

### GameCube CISO input

`Disc` recognises the `CISO` header and its `0x8000`-byte header area. The header supplies a block size and a byte-per-block presence map. Present blocks are stored consecutively after the header; absent blocks read as zeroes.

`Disc.read()` translates each logical read into the corresponding stored blocks. Inspection and patch offsets therefore use the same logical addresses for plain ISO/GCM and CISO input. When writing, the patcher expands the logical image to `0x57058000` bytes and produces a plain ISO/GCM, rather than writing another CISO container.

RVZ, WIA, GCZ and NKit layouts are rejected. The [Access instructions](access.html#create-a-developer-stage-iso) describe conversion requirements.

## Identifying the release

The patcher reads the `NDMW.AFS` entry table, then follows four stage manifests:

| AFS entry | Stage ID | Purpose |
| --- | --- | --- |
| 137 | `stag0000` | Developer stage |
| 169 | `stagis11` | Login scene |
| 170 | `stagis12` | Login scene |
| 171 | `stagis13` | Login scene |

Each manifest must identify the expected stage and contain exactly one scene reference in the form `[0.N]`. References ending in `/s` are excluded. The four references must lead to distinct scene packs.

The release fingerprint is a SHA-256 digest of those four packs in manifest order. Each pack is prefixed with its AFS entry number and byte length, encoded as two little-endian 32-bit integers:

```python
digest.update(struct.pack('<II', entry_number, len(pack)))
digest.update(pack)
```

Including the entry numbers and lengths makes the input boundaries explicit. Hashing the referenced packs makes the fingerprint independent of their physical offsets and surrounding archive padding. Each login pack must also contain exactly one length-prefixed `stagML11` marker: `09 00 00 00`, followed by the eight ASCII characters and a terminating zero byte.

The resulting digest must match an entry in `BUILDS`. That entry selects the platform, region, release identifier, expected boot filename, executable SHA-256 and destination offset. GameCube’s six-character disc ID must agree with the selected build. The entire boot executable is then checked against its separate SHA-256 before any patch plan is accepted. The exact fingerprints are listed in the [patcher source](https://github.com/crashbashash/dw4-dev-stage/blob/main/assets/tools/patch_dev_stage.py).

## Redirecting character selection

Create Digimon and Call Digimon reach the same final stage transition. The patcher changes the destination string used by that native login controller:

```text
Before: stagML11\0
After:  stag0000\0
```

Both stage IDs occupy eight ASCII bytes. The patch replaces those eight bytes and leaves the terminating zero byte in place, so executable sections and following data retain their original positions.

| Platform | Region | Executable | Destination file offset |
| --- | --- | --- | --- |
| PlayStation 2 | USA | `SLUS_208.36` | `0x004182F0` |
| PlayStation 2 | Europe | `SLES_534.05` | `0x004190A0` |
| PlayStation 2 | Japan | `SLPS_254.53` | `0x00419BE0` |
| GameCube | USA | Main DOL | `0x00455B10` |
| GameCube | Japan | Main DOL | `0x004559F0` |
| Xbox | USA | `default.xbe` | `0x00367C8C` |
| Xbox | Japan | `default.xbe` | `0x00381DE4` |

These offsets are relative to the start of the executable file. They are neither RAM addresses nor absolute disc offsets. The image patch position is the executable’s disc offset plus the value in this table.

The login scene packs are checked during identification but are not rewritten. The patch targets the native controller’s destination in the executable. Stage-select destinations and Leomon’s scripted return to the Main Lobby keep their existing values.

## Enabling the full NPC roster

USA PS2, European PS2, USA GameCube and USA Xbox gate two developer-stage spawn blocks on flag 960. One contains Leomon and five Digi-Elves; the other contains the two Goblimon. The stage-select Digi-Elf and the two cheat rocks are outside these blocks. See [NPC visibility and flag 960](technical-notes.html#npc-visibility-and-flag-960).

The patcher replaces each Lua `JMPNE` comparison instruction with `POP 2`. Both instructions consume two comparison operands, but `POP 2` falls through into the spawn block. The replacement preserves the stack effect, the four-byte instruction size and all following instruction positions.

```python
replacement = struct.pack('<I', 5 | (2 << 6))
# Encoded word: 0x00000085; bytes: 85 00 00 00
```

| Release | First instruction offset | Second instruction offset |
| --- | --- | --- |
| PlayStation 2 USA | `0x002468C2` | `0x002469BA` |
| PlayStation 2 Europe | `0x00240BDE` | `0x00240CD6` |
| GameCube USA | `0x00180678` | `0x00180770` |
| Xbox USA | `0x0018C7DC` | `0x0018C8D4` |

These offsets are relative to the start of the developer-stage scene pack referenced by AFS entry 137. The expected original words are `0x80000BE0` for the first instruction and `0x800003E0` for the second, read as little-endian values. Both must match before the replacements are planned.

Japanese PS2, GameCube and Xbox startup scripts already spawn the full roster, so their patch plans contain no NPC visibility changes. This approach changes the stage’s spawn logic without writing flag 960 or other character progression flags.

## Updating the Xbox section digest

Changing `default.xbe` also requires updating the SHA-1 digest for the section containing the destination string. The patcher reads the XBE section table, locates the one section covering all eight destination bytes, and verifies its existing digest before computing the replacement.

The digest input is the section’s raw byte length as a little-endian 32-bit integer, followed by its raw file bytes:

```python
digest = hashlib.sha1(
    struct.pack('<I', section_size) + section_bytes
).digest()
```

For the replacement digest, `section_bytes` includes the changed destination. The 20-byte digest is stored at offset `+36` in that section’s 56-byte header record. Updating this field does not re-sign the XBE or change its other header fields.

## Writing and checking the output

Inspection completes before the output file is opened. The patch plan is sorted by logical image offset, and writing checks that each replacement has the same length as its original bytes, is inside the image and does not overlap an earlier patch.

The output is opened in exclusive creation mode (`xb`), so an existing file cannot be overwritten. The input is opened for reading. Unchanged ranges are copied in chunks of at most one MiB; each patch’s original bytes are read and checked again immediately before substitution.

The input’s size and modification time are compared with their initial values during inspection and copying. The final output length must match the planned logical image length. These checks detect common input changes and incomplete output; they are not a full read-back hash of the completed file. An interrupted or failed copy can leave a partial output file, which should be discarded.

For plain ISO/GCM and XISO input, the output retains the input’s logical length and file layout. For CISO input, the output contains the expanded plain GameCube image described above.

The named patch ranges are:

| Release group | Patch ranges |
| --- | --- |
| PS2 USA/Europe and GameCube USA | Eight-byte destination plus two four-byte NPC instructions |
| PS2 Japan and GameCube Japan | Eight-byte destination |
| Xbox USA | Eight-byte destination, two four-byte NPC instructions and one 20-byte section digest |
| Xbox Japan | Eight-byte destination and one 20-byte section digest |

These are replacement lengths. Some bytes within each range already equal their replacement values, so the number of differing bytes can be smaller. For CISO input, comparisons should use the expanded logical image.

## Source reference

| Code | Responsibility |
| --- | --- |
| `Disc`, `identify()` and the three filesystem readers | Container handling and file lookup |
| `BUILDS`, `SPAWN_GUARDS`, `inspect()` | Release checks, patch locations and Xbox digest calculation |
| `copy_patched()` | Copying the logical image and applying checked replacements |
| `main()` | Command-line arguments, compatibility report and output-size check |

[Read the source on GitHub](https://github.com/crashbashash/dw4-dev-stage/blob/main/assets/tools/patch_dev_stage.py) · [Download the patcher](assets/tools/patch_dev_stage.py) · [Return to Access](access.html)
