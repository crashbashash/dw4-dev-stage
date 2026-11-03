# Digimon World 4 — Developer World

A guide to `stag0000`, the hidden developer stage included in the PlayStation 2, GameCube and Xbox versions of Digimon World 4 (Digimon World X in Japan), its debug tools and how to access it.

**Website:** https://crashbashash.github.io/dw4-dev-world/

Includes the NPC menus and English translations, access notes, 97 stage-select entries in script order, annotated screenshots, and technical notes on the shared practice-stage environment.

The access guide includes a standalone Python patcher that detects original USA (`SLUS-20836`), European (`SLES-53405`) and Japanese (`SLPS-25453`) images and creates a separate dev-world ISO. It contains no game data and changes only three fixed-length destination strings.

## Edit the documentation

Edit the Markdown files in `content/` using GitHub’s file editor, then commit to `main`. The Publish website workflow builds, checks and deploys the site automatically. Edit `content/stages.json` for destination data; the published list and downloadable JSON are generated from the same file.

Images live in `assets/images/`. The gallery is built from the annotated PNGs under `assets/images/translated/`. Digi-Elf 2’s dialogue and nine unique stage-select screens appear together in its section. Its `screen-01.png` through `screen-09.png` filenames follow the menu order recorded in `content/stages.json`.

## Build and check locally

Requires Python 3.11 or newer.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python scripts/check.py
.venv/bin/python -m http.server 8000 --directory dist
```

Open http://localhost:8000/. The build writes the public website to `dist/` and needs no game files.

## Publishing

GitHub Pages uses **GitHub Actions** as its publishing source. `.github/workflows/pages.yml` builds and checks pull requests, and deploys successful builds on `main`. The live site uses the `/dw4-dev-world/` project path; internal links also work in a local preview.

## Game content

Destination counts and positions follow the stage-select scripts. See the Technical notes page for script references and functions that still need documenting.

This repository contains documentation and screenshots, with no game discs, executable game files, BIOS images, memory cards or savestates. Game dialogue and screenshots belong to their respective rights holders. No licence grant for those materials is implied.
