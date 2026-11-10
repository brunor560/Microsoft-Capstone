"""Shared official-source index (sources.json) and source discovery.

Pages are keyed by URL and shared by every profile and tool. Evidence entries
(MATRIX:E01, E02, ...) are immutable: reuse requires the same passage, source
snapshot and all recorded metadata. A later snapshot gets a new evidence ID.
"""
import re
import urllib.parse

from . import fetch
from . import pages
from . import store as st


def page_key(url):
    u = urllib.parse.urlparse(url)
    return re.sub(r'[^A-Za-z0-9]+', '_', u.netloc + u.path).strip('_') or 'root'


def doc_url(docs, page):
    if page.startswith('http'):
        return page
    return docs['base_url'].rstrip('/') + '/' + page.strip('/') + '/'


def official(url, docs):
    return any(url.startswith(p) for p in docs.get('allowed_prefixes', [docs['base_url']]))


class SourceIndex:
    def __init__(self, store, offline=False, refresh=False):
        self.store, self.offline, self.refresh = store, offline, refresh
        self.data = store.load('sources.json')
        self.text = {}
        self.html = {}

    def page(self, url, docs):
        """Fetch or reuse a page; returns (record, text) and updates the index."""
        if not official(url, docs):
            raise ValueError('NON_OFFICIAL_SOURCE: %s is outside %s' % (url, docs['allowed_prefixes']))
        labels = docs.get('surface_labels', {})
        meta, text, page_html, from_cache = fetch.get_page(
            self.store, page_key(url), url, labels, offline=self.offline, refresh=self.refresh)
        rec = self.data['pages'].get(url, {'url': url, 'publisher': docs.get('publisher')})
        if meta['status'] == 'ok':
            changed = rec.get('sha256') not in (None, meta['sha256'])
            if 'fetched_at' in meta or not rec.get('access_date'):
                rec['access_date'] = (meta.get('fetched_at') or st.now())[:10]
            if changed:
                rec.setdefault('previous_sha256', []).append(rec['sha256'])
            if meta.get('effective_url'):
                rec['effective_url'] = meta['effective_url']
            rec.update({'title': meta['title'], 'sha256': meta['sha256'],
                        'available_on': meta['available_on'], 'sections': meta['sections'],
                        'status': 'ok', 'version_or_update': 'unversioned page; identified by access date and SHA-256'})
            self.text[url], self.html[url] = text, page_html
        else:
            rec['status'] = meta['status']
        self.data['pages'][url] = rec
        return rec, text, from_cache

    def evidence(self, url, section_spec, quote, check, rec, claim):
        """Reuse an identical record; never rewrite evidence cited by other cells."""
        entry = {
            'publisher': rec.get('publisher'), 'page_title': rec.get('title'),
            'url': url, 'section_spec': section_spec,
            'section': ' > '.join(check['section_path'] or []),
            'surface': check['surface'], 'quote': quote, 'claim_summary': claim,
            'access_date': rec['access_date'], 'page_sha256': rec['sha256'],
            'version_or_update': rec.get('version_or_update'), 'check': check['status'],
        }
        for eid, existing in self.data['entries'].items():
            if {k: v for k, v in existing.items() if k != 'id'} == entry:
                return eid
        # Gaps or historical IDs must never cause an existing record to be replaced.
        last = max((int(eid[1:]) for eid in self.data['entries'] if re.fullmatch(r'E\d+', eid)), default=0)
        eid = 'E%02d' % (last + 1)
        self.data['entries'][eid] = dict(entry, id=eid)
        return eid

    def save(self):
        self.store.save('sources.json', self.data)


def discover(index, docs, seeds, crawl_limit, progress):
    """Fetch the prepared seed pages; with one seed or none, crawl same-prefix links.

    A prepared candidate lists its pages, so discovery stays within that list.
    A new candidate has only its base URL; discovery then follows links under
    the documentation prefix up to crawl_limit pages, in link order.
    """
    crawl = len(seeds) <= 1
    urls = [doc_url(docs, s) for s in seeds] if seeds else [docs['base_url']]
    limit = crawl_limit if crawl else len(urls)
    seen, ok, i = [], 0, 0
    while i < len(urls) and len(seen) < limit:
        url = urls[i]
        i += 1
        if url in seen:
            continue
        seen.append(url)
        rec, text, cached = index.page(url, docs)
        good = rec.get('status') == 'ok'
        eff = rec.get('effective_url')
        if good and eff and not official(eff, docs):
            # Redirected off the declared documentation prefix: record it, do not crawl it.
            rec['status'] = 'redirected_outside_prefix'
            rec['note'] = 'Redirected to %s; update the candidate documentation URL' % eff
            good = False
        ok += good
        progress('discovery', len(seen), min(limit, len(urls)) if crawl else limit,
                 '%s  %s' % (url.replace(docs['base_url'], '') or '(index)',
                             ('cached' if cached else 'fetched') if good else rec.get('status')))
        if crawl and good:
            for link in pages.doc_links(index.html[url], url, docs['base_url']):
                if link not in urls:
                    urls.append(link)
    return seen, ok
