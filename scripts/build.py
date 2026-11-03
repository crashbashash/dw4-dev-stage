#!/usr/bin/env python3
"""Build the developer-world reference from Markdown and destination data."""
from html import escape
from pathlib import Path
from string import Template
import json
import re
import shutil

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
URL = 'https://crashbashash.github.io/dw4-dev-world/'
REPO = 'https://github.com/crashbashash/dw4-dev-world'
PAGES = [
    ('index', 'Overview', 'The developer world.', 'A hidden debug sandbox inside Digimon World 4’s retail PS2 release.'),
    ('debug-npcs', 'Debug NPCs', 'The debug NPCs', 'Characters, menu options and English translations.'),
    ('stage-select', 'Stage select', '97 places to go.', 'The complete developer stage-select list, in script order.'),
    ('access', 'Access & controls', 'Getting there.', 'How to access the dev world and use its menus.'),
    ('gallery', 'Screenshot gallery', 'The screenshot gallery.', 'The dev world’s Japanese dialogue and menus, with English annotations.'),
    ('technical-notes', 'Technical notes', 'Under the surface.', 'Stage transitions, cheat scripts and functions that need more documentation.'),
]
GROUPS = [
    ('digi-elf-1', 'Digi-Elf 1', 'Text-size options'),
    ('digi-elf-2', 'Digi-Elf 2', 'Stage-select dialogue and menu captures'),
    ('digi-elf-3', 'Digi-Elf 3', 'Play mode / difficulty'),
    ('digi-elf-4', 'Digi-Elf 4', 'TIME flag options'),
    ('digi-elf-5', 'Digi-Elf 5', 'Digivolution / evolution-arts unlocks'),
    ('digi-elf-6', 'Digi-Elf 6', 'EXP and level targets'),
    ('leomon-1', 'Leomon', 'Return-to-lobby prompt'),
    ('rock-1', 'Rock 1', 'Item MAX'),
    ('rock-2', 'Rock 2', 'Money MAX'),
    ('stage-list', 'Stage-list sequence', '40 capture frames, including repeated menu screens'),
]


def make_renderer():
    md = MarkdownIt('commonmark', {'html': True}).enable('table')
    seen = {}

    def heading(tokens, index, options, env):
        text = tokens[index + 1].content
        slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
        seen[slug] = seen.get(slug, 0) + 1
        suffix = '' if seen[slug] == 1 else f'-{seen[slug]}'
        tokens[index].attrSet('id', slug + suffix)
        return md.renderer.renderToken(tokens, index, options, env)

    def image(tokens, index, options, env):
        tokens[index].attrSet('loading', 'lazy')
        tokens[index].attrSet('decoding', 'async')
        return md.renderer.image(tokens, index, options, env)

    md.renderer.rules['heading_open'] = heading
    md.renderer.rules['image'] = image
    return md


def stage_markup(pages):
    markup = ['<div class="stage-search"><label for="stage-query">Filter by stage ID</label><input id="stage-query" type="search" placeholder="Try dng102b3 or stagGF" autocomplete="off" aria-describedby="stage-count"><p id="stage-count" role="status" aria-live="polite">97 of 97 destinations</p><noscript><p>The complete list is available below. Filtering requires JavaScript.</p></noscript></div><p id="stage-empty" hidden>No matching destinations. Try a shorter stage ID.</p><div class="stage-screens">']
    for page in pages:
        number = page['screen']
        markup.append(f'<section class="stage-screen" aria-labelledby="screen-{number}"><h3 id="screen-{number}">Screen {number:02d}</h3><p class="stage-script">{escape(page["script"])}</p><ol>')
        for row, stage in enumerate(page['stages'], 1):
            markup.append(f'<li value="{row}" data-stage="{escape(stage)}"><span id="{escape(stage)}">{escape(stage)}</span></li>')
        markup.append('</ol></section>')
    markup.append('</div>')
    return ''.join(markup)


def gallery_markup():
    markup = ['<nav class="archive-index" aria-label="Screenshot groups">']
    for group, title, description in GROUPS:
        markup.append(f'<a href="#{group}">{escape(title)}</a>')
    markup.append('</nav>')
    for group, title, description in GROUPS:
        folder = ROOT / 'assets/images/translated' / ('digi-elf-2/stage-list-pages' if group == 'stage-list' else group)
        files = sorted(folder.glob('*.png'))
        opened = ' open' if group == 'digi-elf-1' else ''
        markup.append(f'<section class="gallery-group" aria-labelledby="{group}"><h2 id="{group}">{escape(title)}</h2><p>{escape(description)}</p><details{opened}><summary>Browse {len(files)} captures</summary><div class="gallery-grid">')
        for file in files:
            path = file.relative_to(ROOT).as_posix()
            caption = f'{title} · {file.stem}'
            extra = 'Capture sequence number; see the stage reference for screen order.' if group == 'stage-list' else 'Japanese game text with English annotations.'
            markup.append(f'<figure class="capture"><a href="{path}" aria-label="Open {escape(caption)} at full size"><img src="{path}" loading="lazy" decoding="async" alt="{escape(caption)}: {escape(description)}"></a><figcaption>{escape(file.name)}<span>{escape(extra)}</span></figcaption></figure>')
        markup.append('</div></details></section>')
    return ''.join(markup)


def main():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
    pages = json.loads((ROOT / 'content/stages.json').read_text())
    assert [len(p['stages']) for p in pages] == [11] * 8 + [9]
    assert len({stage for page in pages for stage in page['stages']}) == 97
    (OUT / 'assets/data').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'content/stages.json', OUT / 'assets/data/stages.json')
    template = Template((ROOT / 'templates/page.html').read_text())
    for page_index, (slug, label, title, description) in enumerate(PAGES):
        body = make_renderer().render((ROOT / 'content' / f'{slug}.md').read_text())
        body = body.replace('<p>[[STAGES]]</p>', stage_markup(pages))
        body = body.replace('<p>[[GALLERY]]</p>', gallery_markup())
        body = body.replace('<table>', '<div class="table-scroll" role="region" aria-label="Reference table" tabindex="0"><table>').replace('</table>', '</table></div>')
        navigation = ''.join(f'<a href="{s}.html"' + (' aria-current="page"' if s == slug else '') + f'><span aria-hidden="true">{i:02d}</span>{escape(l)}</a>' for i, (s, l, _, _) in enumerate(PAGES, 1))
        header = f'<header class="page-header"><p class="page-eyebrow">Dev world / {page_index + 1:02d}</p><h1>{escape(title)}</h1><p class="lede">{escape(description)}</p></header>'
        if slug == 'index':
            header = f'<header class="page-header home-header"><div><p class="page-eyebrow">Digimon World 4 / stag0000</p><h1>{escape(title)}</h1><p class="lede">{escape(description)}</p><dl class="facts"><div><dt>Destinations</dt><dd>97</dd></div><div><dt>Menu screens</dt><dd>9</dd></div><div><dt>Captures</dt><dd>90</dd></div></dl></div><figure class="overview-figure"><img src="assets/images/dev-world.png" width="640" height="478" alt="The developer stage: a green grid over a pink void, with Digi-Elves, Leomon and debug objects."><figcaption>STAG0000 · THE DEVELOPER STAGE</figcaption></figure></header>'
        footer_links = []
        if page_index:
            previous = PAGES[page_index - 1]
            footer_links.append(f'<a href="{previous[0]}.html">← {escape(previous[1])}</a>')
        else:
            footer_links.append('<span></span>')
        if page_index < len(PAGES) - 1:
            following = PAGES[page_index + 1]
            footer_links.append(f'<a href="{following[0]}.html">{escape(following[1])} →</a>')
        footer = '<nav class="page-footer" aria-label="Adjacent pages">' + ''.join(footer_links) + '</nav>'
        html = template.substitute(title=escape(title), description=escape(description), canonical=URL + ('' if slug == 'index' else slug + '.html'), navigation=navigation, page_header=header, page_class='home-page' if slug == 'index' else 'reference-page', body=body, page_footer=footer)
        (OUT / f'{slug}.html').write_text(html)
    (OUT / '.nojekyll').touch()
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {URL}sitemap.xml\n')
    locations = ''.join(f'<url><loc>{URL}{"" if slug == "index" else slug + ".html"}</loc></url>' for slug, *_ in PAGES)
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + locations + '</urlset>\n')
    print(f'Built {len(PAGES)} pages, 97 stage destinations and 90 gallery captures into dist/.')


if __name__ == '__main__':
    main()
