"""Read-only network access to official documentation, with a local cache.

Only HTTP GET requests to documentation URLs are made. Cached page text lives
under <dataset>/.cache/pages/ (gitignored); the source index keeps metadata,
hashes and short quotes only.
"""
import gzip
import os
import urllib.error
import urllib.request

from . import pages
from . import store as st

UA = 'approach-a-workbench/0.1 (documentation review only; USF CIS4910 Team 3)'
TIMEOUT = 30


def fetch(url):
    """Return (status, effective_url, html). HTTP errors return their code."""
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'gzip'})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw, status, eff = r.read(), r.status, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, url, ''
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    return status, eff, raw.decode('utf-8', 'replace')


class PageCache:
    def __init__(self, store):
        self.dir = store.path('.cache', 'pages')

    def _read(self, name):
        p = os.path.join(self.dir, name)
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                return f.read()
        return None

    def get(self, page_id):
        return self._read(page_id + '.txt'), self._read(page_id + '.html')

    def put(self, page_id, text, page_html):
        os.makedirs(self.dir, exist_ok=True)
        for ext, data in (('.txt', text), ('.html', page_html)):
            with open(os.path.join(self.dir, page_id + ext), 'w', encoding='utf-8') as f:
                f.write(data)


def get_page(store, page_id, url, labels, offline=False, refresh=False):
    """Return (meta, text, html, from_cache). meta['status'] is ok, not_cached or http_<code>."""
    cache = PageCache(store)
    text = page_html = None
    if not refresh:
        text, page_html = cache.get(page_id)
    from_cache = text is not None
    meta = {'url': url}
    if text is None:
        if offline:
            return dict(meta, status='not_cached'), None, None, False
        try:
            status, eff, page_html = fetch(url)
        except (urllib.error.URLError, OSError) as e:
            return dict(meta, status='network_error', error=str(e)), None, None, False
        if status != 200 or not page_html:
            return dict(meta, status='http_%s' % status), None, None, False
        text = pages.to_text(page_html)
        cache.put(page_id, text, page_html)
        meta['fetched_at'] = st.now()
        meta['effective_url'] = eff
    meta.update({
        'status': 'ok',
        'title': pages.title_of(page_html or ''),
        'sha256': st.sha256(text.encode('utf-8')),
        'sections': len(pages.sections(text)),
        'available_on': pages.availability(page_html or '', labels),
    })
    return meta, text, page_html, from_cache
