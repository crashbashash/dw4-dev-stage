#!/usr/bin/env python3
"""Build the developer-stage reference from Markdown and destination data."""
from html import escape
from pathlib import Path
from string import Template
import json
import re
import shutil

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
URL = 'https://crashbashash.github.io/dw4-dev-stage/'
REPO = 'https://github.com/crashbashash/dw4-dev-stage'
PAGES = [
    ('index', 'Overview', 'Developer Stage', 'A hidden debug sandbox inside Digimon World 4.'),
    ('debug-npcs', 'Debug NPCs', 'Debug NPCs', 'Characters, menu options, controls and English translations.'),
    ('stage-select', 'Stage select', 'Stage select', 'The complete developer stage-select list, in script order.'),
    ('access', 'Access', 'Access', 'How to access the developer stage.'),
    ('gallery', 'Screenshot gallery', 'Screenshot gallery', 'The developer stage’s Japanese dialogue and menus, with English annotations.'),
    ('technical-notes', 'Technical notes', 'Technical notes', 'Stage data, progression presets and debug-script behaviour.'),
]
GROUPS = [
    ('digi-elf-1', 'Digi-Elf 1', 'NORMAL / MINIMUM font preview'),
    ('digi-elf-2', 'Digi-Elf 2', 'Stage-select dialogue and nine menu screens'),
    ('digi-elf-3', 'Digi-Elf 3', 'Hard / Very Hard flag presets'),
    ('digi-elf-4', 'Digi-Elf 4', 'Story-progression presets and Field Quest flags'),
    ('digi-elf-5', 'Digi-Elf 5', 'Digivolution / evolution-arts unlocks'),
    ('digi-elf-6', 'Digi-Elf 6', 'EXP and level targets'),
    ('leomon-1', 'Leomon', 'Return-to-lobby prompt'),
    ('rock-1', 'Rock 1', 'Item MAX'),
    ('rock-2', 'Rock 2', 'Money MAX'),
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
    markup = ['<div class="stage-search"><label for="stage-query">Filter by stage name or ID</label><input id="stage-query" type="search" placeholder="Try Goblin Pass or stagGF" autocomplete="off" aria-describedby="stage-count"><p id="stage-count" role="status" aria-live="polite">97 of 97 destinations</p><noscript><p>The complete list is available below. Filtering requires JavaScript.</p></noscript></div><p id="stage-empty" hidden>No matching destinations. Try a shorter name or stage ID.</p><div class="stage-screens">']
    for page in pages:
        number = page['screen']
        markup.append(f'<section class="stage-screen" aria-labelledby="screen-{number}"><h3 id="screen-{number}">Screen {number:02d}</h3><p class="stage-script">{escape(page["script"])}</p><ol>')
        for row, stage in enumerate(page['stages'], 1):
            stage_id = stage['id']
            name = stage['name'] or stage['description']
            search = ' '.join((stage_id, name))
            markup.append(f'<li value="{row}" data-stage="{escape(stage_id)}" data-search="{escape(search, quote=True)}"><span class="stage-label"><code id="{escape(stage_id)}">{escape(stage_id)}</code><span class="stage-separator" aria-hidden="true">|</span><span class="stage-name">{escape(name)}</span></span></li>')
        markup.append(f'</ol><p class="stage-screenshot-link"><a href="{escape(page["screenshot"])}">View screen {number} screenshot →</a></p></section>')
    markup.append('</div>')
    return ''.join(markup)


def gallery_markup():
    markup = ['<nav class="archive-index" aria-label="Screenshot groups">']
    for group, title, description in GROUPS:
        markup.append(f'<a href="#{group}">{escape(title)}</a>')
    markup.append('</nav>')
    for group, title, description in GROUPS:
        folder = ROOT / 'assets/images/translated' / group
        files = sorted(folder.glob('*.png'))
        opened = ' open' if group in {'digi-elf-1', 'digi-elf-2'} else ''
        markup.append(f'<section class="gallery-group" aria-labelledby="{group}"><h2 id="{group}">{escape(title)}</h2><p>{escape(description)}</p><details{opened}><summary>Browse {len(files)} screenshots</summary>')
        subsets = [(None, files)]
        if group == 'digi-elf-2':
            subsets = [('Dialogue', [f for f in files if not f.stem.startswith('screen-')]), ('Stage-select menu', [f for f in files if f.stem.startswith('screen-')])]
        for heading, subset in subsets:
            if heading:
                markup.append(f'<h3>{heading}</h3>')
            markup.append('<div class="gallery-grid">')
            for file in subset:
                path = file.relative_to(ROOT).as_posix()
                caption = f'{title} · {file.stem}'
                label = file.name
                extra = 'Japanese game text with English annotations.'
                if group == 'digi-elf-2':
                    if file.stem.startswith('screen-'):
                        number = int(file.stem.split('-')[1])
                        caption = f'Digi-Elf 2 stage-select screen {number}'
                        label = f'Stage-select screen {number}'
                        extra = 'Stage IDs are shown in the same order as the stage reference.'
                    else:
                        label = 'Introduction' if file.stem == '02' else 'Warp or stay here'
                        caption = f'Digi-Elf 2: {label.lower()}'
                markup.append(f'<figure class="capture"><a href="{path}" aria-label="Open {escape(caption)} at full size"><img src="{path}" loading="lazy" decoding="async" alt="{escape(caption)}: {escape(description)}"></a><figcaption>{escape(label)}<span>{escape(extra)}</span></figcaption></figure>')
            markup.append('</div>')
        markup.append('</details></section>')
    return ''.join(markup)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
    # Preserve the original download URL while the canonical name follows the site title.
    shutil.copyfile(OUT / 'assets/tools/patch_dev_stage.py', OUT / 'assets/tools/patch_dev_world.py')
    pages = json.loads((ROOT / 'content/stages.json').read_text())
    assert [len(p['stages']) for p in pages] == [11] * 8 + [9]
    assert len({stage['id'] for page in pages for stage in page['stages']}) == 97
    (OUT / 'assets/data').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'content/stages.json', OUT / 'assets/data/stages.json')
    template = Template((ROOT / 'templates/page.html').read_text())
    for page_index, (slug, label, title, description) in enumerate(PAGES):
        body = make_renderer().render((ROOT / 'content' / f'{slug}.md').read_text())
        body = body.replace('<p>[[STAGES]]</p>', stage_markup(pages))
        body = body.replace('<p>[[GALLERY]]</p>', gallery_markup())
        body = body.replace('<table>', '<div class="table-scroll" role="region" aria-label="Reference table" tabindex="0"><table>').replace('</table>', '</table></div>')
        navigation = ''.join(f'<a href="{s}.html"' + (' aria-current="page"' if s == slug else '') + f'>{escape(l)}</a>' for s, l, _, _ in PAGES)
        header = f'<header class="page-header"><p class="page-eyebrow">Digimon World 4</p><h1>{escape(title)}</h1><p class="lede">{escape(description)}</p></header>'
        if slug == 'index':
            introduction, separator, following_sections = body.partition('<h2 ')
            assert separator, 'Overview needs a section after its introduction'
            body = separator + following_sections
            header = f'<header class="page-header home-header"><div><p class="page-eyebrow">Digimon World 4 / stag0000</p><h1>{escape(title)}</h1><div class="home-intro">{introduction}</div></div><figure class="overview-figure"><img src="assets/images/dev-world.png" width="640" height="478" alt="The developer stage uses the practice stage’s grid platform and background, with Digi-Elves, Leomon and debug objects."><figcaption>Developer Stage · stag0000</figcaption></figure></header>'
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
    gallery_count = len(list((ROOT / 'assets/images/translated').glob('*/*.png')))
    print(f'Built {len(PAGES)} pages, 97 stage entries and {gallery_count} gallery screenshots into dist/.')


if __name__ == '__main__':
    main()
