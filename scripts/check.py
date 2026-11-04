#!/usr/bin/env python3
"""Validate the built site's navigation, images, anchors and destination data."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids = []
        self.links = []
        self.images = []
        self.headings = 0
        self.stages = []
        self.in_main = False
        self.main = False
        self.title = False
        self.guide_nav = False
        self.guide_list_depth = 0
        self.guide_links = []

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'nav' and attrs.get('aria-label') == 'Guide sections':
            self.guide_nav = True
        if tag == 'ul' and self.guide_nav:
            self.guide_list_depth += 1
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'h1':
            self.headings += 1
        if tag == 'main':
            self.main = True
        if tag == 'title':
            self.title = True
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
            if self.guide_nav:
                self.guide_links.append((attrs, self.guide_list_depth))
        if tag in {'script', 'img'}:
            self.links.append(attrs.get('src', ''))
        if tag == 'link' and attrs.get('rel') in {'stylesheet', 'icon'}:
            self.links.append(attrs.get('href', ''))
        if tag == 'img':
            self.images.append(attrs)
        if 'data-stage' in attrs:
            self.stages.append(attrs['data-stage'])

    def handle_endtag(self, tag):
        if tag == 'ul' and self.guide_nav:
            self.guide_list_depth -= 1
        if tag == 'nav':
            self.guide_nav = False


def main():
    errors = []
    pages = {}
    for file in sorted(OUT.glob('*.html')):
        page = Page(file)
        text = file.read_text()
        page.feed(text)
        pages[file.resolve()] = page
        if page.headings != 1 or not page.main or not page.title:
            errors.append(f'{file.name}: needs one h1, a main landmark and a title')
        current = [attrs.get('href') for attrs, _ in page.guide_links if attrs.get('aria-current') == 'page']
        if current != [file.name]:
            errors.append(f'{file.name}: navigation must mark only the current page')
        guide_targets = [attrs.get('href') for attrs, _ in page.guide_links]
        patcher_links = [depth for attrs, depth in page.guide_links if attrs.get('href') == 'patcher.html']
        if patcher_links != [2] or 'access.html' not in guide_targets or guide_targets.index('patcher.html') != guide_targets.index('access.html') + 1:
            errors.append(f'{file.name}: patcher guide must be nested immediately under Access')
        duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
        if duplicates:
            errors.append(f'{file.name}: duplicate IDs {duplicates}')
        for image in page.images:
            if not image.get('alt') and image.get('aria-hidden') != 'true':
                errors.append(f'{file.name}: image needs alt text: {image.get("src")}')
        if re.search(r'\[\[[A-Z]+\]\]|/home/|/Users/|file://|\bsurvey\b|\b20\d\d\b', text, re.I):
            errors.append(f'{file.name}: unresolved marker, local path or unwanted dated/survey wording')
    expected_pages = {file.stem + '.html' for file in (ROOT / 'content').glob('*.md')}
    if {file.name for file in pages} != expected_pages:
        errors.append('Built pages must match the Markdown pages in content/')
    link_count = 0
    for file, page in pages.items():
        for link in page.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            link_count += 1
            target = (file.parent / unquote(parts.path)).resolve() if parts.path else file
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_relative_to(OUT.resolve()) or not target.is_file():
                errors.append(f'{file.name}: missing or escaping target {link}')
            elif parts.fragment and target in pages and unquote(parts.fragment) not in pages[target].ids:
                errors.append(f'{file.name}: missing anchor {link}')
    destinations = json.loads((ROOT / 'content/stages.json').read_text())
    expected = [stage['id'] for page in destinations for stage in page['stages']]
    actual = pages[(OUT / 'stage-select.html').resolve()].stages
    if actual != expected or len(actual) != 97 or len(set(actual)) != 97:
        errors.append('Stage reference does not match the 97 unique destinations in source order')
    gallery = pages[(OUT / 'gallery.html').resolve()]
    expected_images = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'assets/images/translated').glob('*/*.png'))
    gallery_images = [image for image in gallery.images if image.get('aria-hidden') != 'true']
    actual_images = [image['src'] for image in gallery_images]
    if sorted(actual_images) != expected_images:
        errors.append('Gallery must show each curated image exactly once')
    expected_screens = [f'assets/images/translated/digi-elf-2/screen-{screen:02d}.png' for screen in range(1,10)]
    actual_screens = [image for image in actual_images if '/screen-' in image]
    if actual_screens != expected_screens or [p['screenshot'] for p in destinations] != expected_screens:
        errors.append('Digi-Elf 2 needs nine unique screenshots in canonical menu order')
    if len(set((OUT / path).read_bytes() for path in actual_screens)) != 9:
        errors.append('Duplicate stage-menu screenshot')
    if 'stage-list' in gallery.ids:
        errors.append('The stage-list screenshots belong only in the Digi-Elf 2 section')
    for file in (OUT / 'assets/images').rglob('*.png'):
        header = file.read_bytes()[:24]
        if header[:8] != b'\x89PNG\r\n\x1a\n' or not all(struct.unpack('>II', header[16:24])):
            errors.append(f'Invalid PNG: {file.relative_to(OUT)}')
    forbidden = {'.iso', '.p2s', '.elf', '.irx', '.ps2', '.bin', '.env', '.pem', '.key'}
    for file in ROOT.rglob('*'):
        if not file.is_file() or any(part in {'.git', '.venv', '__pycache__'} for part in file.relative_to(ROOT).parts):
            continue
        if file.suffix.lower() in forbidden:
            errors.append(f'Unexpected private or game binary file: {file.relative_to(ROOT)}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Checked {len(pages)} pages, {link_count} local references, 97 unique stage entries and {len(gallery_images)} gallery screenshots: all valid.')


if __name__ == '__main__':
    main()
