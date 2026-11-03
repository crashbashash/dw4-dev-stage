**Digi-Elf 2** exposes a real stage-selection menu. Its nine screens contain **97 unique destinations** in the order below. The first eight screens have eleven destinations each; screen nine has nine.

Every screen starts with **つぎのページ / Next page**, above the destinations. In this reference, **row 1 means one downward cursor step from Next page**. Confirming a destination triggers the game’s normal stage-load process.

The list was checked against the nine recovered menu scripts in **AFS entry 603**. Every listed destination is paired with `PLAYERPOINT SETGENERATEPOS "I<0>"`. Leomon’s separate return-to-lobby action uses position 3.

[Controller procedure and access notes →](access.html#using-the-stage-select-npc)

## Find a destination

[[STAGES]]

[View Digi-Elf 2’s dialogue and nine menu screenshots →](gallery.html#digi-elf-2)

## What a listed destination establishes

Selecting an entry loads that destination. For example, `stagGF01` displays the “Guard Room / Goblin Fortress” banner. Story events and quest behaviour can still depend on your progression flags; a debug warp does not automatically supply the required progression.
