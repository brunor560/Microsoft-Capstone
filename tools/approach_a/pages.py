"""Pure text functions for documentation pages (no network).

HTML is converted to text where real headings become '#' lines, so that an
evidence quote can be checked against the exact section it cites.
"""
import html
import re
import urllib.parse

HEADING = re.compile(r'^(#{1,6}) (.+?)\s*$', re.M)


def title_of(page_html):
    m = re.search(r'<title>([^<]*)</title>', page_html)
    return html.unescape(m.group(1)).strip() if m else ''


def to_text(page_html):
    m = re.search(r'<main[^>]*>(.*)</main>', page_html, flags=re.S)
    body = m.group(1) if m else page_html
    body = re.sub(r'<(script|style|nav|aside|svg)[^>]*>.*?</\1>', ' ', body, flags=re.S)
    body = re.sub(r'<h([1-6])[^>]*>', lambda x: '\n\n\x01H%s\x01' % x.group(1), body)
    body = re.sub(r'</h[1-6]>', '\n', body)
    body = re.sub(r'<(p|li|tr|pre|div|br)[^>]*>', '\n', body)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = html.unescape(body).split('Your download has started')[0]
    body = re.sub(r'Section titled “[^”]*”', ' ', body)
    body = re.sub(r'[ \t\u00a0]+', ' ', body)
    lines = []
    for line in body.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            line = '\\' + line  # code samples that start with '#' are not headings
        hm = re.match(r'\x01H(\d)\x01\s*(.*)', line)
        if hm:
            line = '#' * int(hm.group(1)) + ' ' + hm.group(2).strip()
        lines.append(line)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip() + '\n'


def norm(s):
    s = s.lower()
    for a, b in (('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'), ('\u201d', '"'),
                 ('\u2014', '-'), ('\u2013', '-'), ('\\', '')):
        s = s.replace(a, b)
    return re.sub(r'\s+', '', s)


def sections(text):
    hs = [(len(m.group(1)), m.group(2).strip(), m.start(), m.end()) for m in HEADING.finditer(text)]
    out, stack = [], []
    for i, (lvl, title, start, body_start) in enumerate(hs):
        while stack and stack[-1][0] >= lvl:
            stack.pop()
        stack.append((lvl, title))
        end = len(text)
        for lvl2, _, start2, _ in hs[i + 1:]:
            if lvl2 <= lvl:
                end = start2
                break
        out.append({'level': lvl, 'title': title, 'path': [t for _, t in stack],
                    'body_start': body_start, 'end': end})
    return out


def surface_key(heading, labels):
    h = heading.lower()
    for label, key in sorted(labels.items(), key=lambda kv: -len(kv[0])):
        if label.lower() in h:
            return key
    return None


def availability(page_html, labels):
    """Surfaces in the page's 'Available on:' badge list (page header, outside <main>).

    Returns [] when the page shows no badge list; the caller then treats the
    page's surface as unspecified rather than guessing.
    """
    found = []
    i = page_html.find('Available on:')
    if i >= 0:
        m = re.search(r'surface-chips-list[^>]*>(.*?)</div>', page_html[i:i + 6000], flags=re.S)
        for chip in re.findall(r'<span class="[^"]*">([^<]+)</span>', m.group(1) if m else ''):
            key = surface_key(html.unescape(chip).strip(), labels)
            if key and key not in found:
                found.append(key)
    if not found:
        # Pages without badges carry the surface in the title suffix,
        # for example "CLI commands - Antigravity CLI | Google Antigravity Docs".
        m = re.match(r'.* - ([^|]+?)\s*\|', title_of(page_html))
        key = surface_key(m.group(1), labels) if m else None
        if key:
            found.append(key)
    return found


def locate(text, section_spec, quote, labels, page_surfaces):
    """Check that `quote` appears inside the section named by `section_spec`.

    section_spec is a heading, or 'Ancestor > Heading' to disambiguate.
    Status: verified | quote_outside_section | section_not_found | quote_not_found.
    The surface comes from the nearest surface-named heading in the section
    path, else from the page's 'Available on' list.
    """
    parts = [p.strip() for p in section_spec.split('>')]
    target, ancestors = norm(parts[-1]), [norm(p) for p in parts[:-1]]
    secs = [s for s in sections(text) if norm(s['title']) == target and
            all(any(norm(t) == a for t in s['path'][:-1]) for a in ancestors)]
    q = norm(quote)
    in_page = q in norm(text)
    if not secs:
        return {'status': 'section_not_found' if in_page else 'quote_not_found',
                'section_path': None, 'surface': None}
    for s in secs:
        if q in norm(text[s['body_start']:s['end']]):
            surface = None
            for title in reversed(s['path']):
                surface = surface_key(title, labels)
                if surface:
                    break
            if not surface:
                surface = ('page:' + '+'.join(page_surfaces)) if page_surfaces else 'unspecified'
            return {'status': 'verified', 'section_path': s['path'], 'surface': surface}
    return {'status': 'quote_outside_section' if in_page else 'quote_not_found',
            'section_path': secs[0]['path'], 'surface': None}


def doc_links(page_html, base_url, prefix):
    links = set()
    for href in re.findall(r'href="([^"#?]+)', page_html):
        absolute = urllib.parse.urljoin(base_url, href)
        if absolute.startswith(prefix):
            links.add(absolute if absolute.endswith('/') else absolute + '/')
    return sorted(links)
