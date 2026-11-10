"""Documentation-only comparison and explicit, baseline-checked reopening.

Comparison artifacts live in a temporary directory, never in the live index or
URL cache. No model calls. Context preservation is deliberately conservative:
all same-surface and unscoped prose is compared, not merely a matching quote.
"""
import copy
import json
import os
from pathlib import Path
import re
import shlex
import tempfile

from . import cmd_blockers, fetch, model, pages, publish, research, review, sources, store as st, ui, validate

SCHEMA = 'approach-a/refresh/1'
UNCHANGED = 'unchanged'
CHANGED = 'needs re-review'
UNKNOWN = 'could not verify'


def historical(store, entry):
    raw_hash = entry.get('page_html_sha256')
    archive = Path(store.path('.cache', 'refresh-history', str(raw_hash) + '.json'))
    try:
        if raw_hash and re.fullmatch(r'[0-9a-f]{64}', raw_hash) and archive.is_file():
            snapshot = json.loads(archive.read_text(encoding='utf-8'))
            text, html = snapshot['text'], snapshot['html']
        else:
            text, html = fetch.PageCache(store).get(sources.page_key(entry['url']))
    except (OSError, ValueError, KeyError):
        return None
    if (text is None or html is None or st.sha256(text.encode()) != entry.get('page_sha256') or
            pages.to_text(html) != text or (raw_hash and st.sha256(html.encode()) != raw_hash)):
        return None
    if pages.title_of(html) != entry.get('page_title'):
        return None
    return {'text': text, 'html': html}


def context(text, section_path, labels, surface, scope_terms=()):
    """Include citation subtree, ancestor lead-ins and all unscoped prose.

    The only omitted prose is inside explicitly different product-surface
    sections with no mention of the assessed scope or qualification clauses. Unknown relevance is
    included. Headings/structure are always compared, including other surfaces.
    Thus ordinary edits to other same-surface features conservatively reopen.
    """
    sections = pages.sections(text)
    if sum(s['path'] == section_path for s in sections) != 1:
        return None
    heads = list(pages.HEADING.finditer(text))
    target_names = [surface] + [name for name, key in labels.items() if key == surface] + [s for s in scope_terms if s]
    mentions = re.compile('|'.join(r'(?<!\w)%s(?!\w)' % re.escape(name) for name in target_names), re.I)
    qualifiers = re.compile(r'\b(only|not|except|unless|require\w*|availab\w*|support\w*|limit\w*|'
                            r'account\w*|tier\w*|plan\w*|platform\w*|subscription\w*|enterprise|'
                            r'premium|paid|free|linux|windows|macos|version\w*|release\w*|default|must|cannot|'
                            r'all|every|globally|unlike|whereas|compared|also|both|other|same)\b', re.I)
    out = [('preamble', text[:heads[0].start()] if heads else text)]
    for i, s in enumerate(sections):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[s['body_start']:end]
        declared = None
        for title in reversed(s['path']):
            named = {key for name, key in labels.items()
                     if re.search(r'(?<!\w)%s(?!\w)' % re.escape(name), title, re.I)}
            if named:
                declared = next(iter(named)) if len(named) == 1 else None
                break
        in_citation = s['path'][:len(section_path)] == section_path
        # Keep all headings even when a distinct surface's prose is omitted.
        out.append(('heading', s['level'], s['path']))
        if in_citation or declared in (None, surface) or mentions.search(body) or qualifiers.search(body):
            out.append(('body', body.strip()))
    return out


def compare(store, entry, page, docs, profile):
    if page.get('error'):
        return UNKNOWN, page['error']
    if not sources.official(entry['url'], docs) or not sources.official(page['effective_url'], docs):
        return UNKNOWN, 'official_scope: URL or redirect is outside the candidate official prefixes'
    labels = docs.get('surface_labels', {})
    spec = entry.get('section_spec') or entry.get('section', '')
    check = pages.locate(page['text'], spec, entry['quote'], labels, pages.availability(page['html'], labels))
    if check['status'] != 'verified':
        return CHANGED, 'passage_changed: %s at the cited section' % check['status']
    if entry.get('check') != 'verified':
        return UNKNOWN, 'historical_context: original quotation was not verified'
    if check['surface'] != entry.get('surface'):
        return CHANGED, 'scope_changed: documented product surface changed'
    if page['sha256'] == entry.get('page_sha256'):
        # Badge metadata can change outside the converted main text.
        old_meta = store.load('sources.json')['pages'].get(entry['url'], {})
        if old_meta.get('sha256') == entry.get('page_sha256') and 'available_on' in old_meta:
            if sorted(old_meta['available_on']) != sorted(pages.availability(page['html'], labels)):
                return CHANGED, 'scope_changed: page availability badges changed'
        if pages.title_of(page['html']) != entry.get('page_title'):
            return CHANGED, 'scope_changed: page title changed'
        return UNCHANGED, 'same_source_hash: cited source snapshot still matches'
    old = historical(store, entry)
    if old is None:
        return UNKNOWN, 'historical_context: no hash-verified historical text/HTML pair; quote matching alone is insufficient'
    old_check = pages.locate(old['text'], spec, entry['quote'], labels, pages.availability(old['html'], labels))
    if old_check['status'] != 'verified' or old_check['surface'] != entry.get('surface'):
        return UNKNOWN, 'historical_context: cited section/surface cannot be established in historical snapshot'
    scope_terms = [profile.get('account_and_tier', ''), *profile.get('platforms', []), *profile.get('modes', [])]
    before = context(old['text'], old_check['section_path'], labels, profile['surface'], scope_terms)
    after = context(page['text'], check['section_path'], labels, profile['surface'], scope_terms)
    if before is None or after is None:
        return UNKNOWN, 'historical_context: section path is missing or ambiguous'
    if (before != after or pages.title_of(old['html']) != pages.title_of(page['html']) or
            pages.availability(old['html'], labels) != pages.availability(page['html'], labels)):
        return CHANGED, 'context_changed: cited context or scope qualifications changed, even if the quote survives'
    return UNCHANGED, 'verified_context: historical citation and all same-surface/unscoped context unchanged; only separate-surface prose changed'


def checked_baseline(store, baseline):
    if {name: st.sha256(raw) for name, raw in publish.snapshot(store).items()} != baseline:
        raise ValueError('Dataset changed since refresh check (manifest, cells, evidence, reviews, catalog or roster). Check again; nothing applied.')


def check(store, profile_ids=None):
    raw = publish.snapshot(store)
    baseline = {name: st.sha256(data) for name, data in raw.items()}
    manifest = json.loads(raw['manifest.json'])
    cells = json.loads(raw['cells.json'])['cells']
    entries = json.loads(raw['sources.json'])['entries']
    profiles = {p['id']: p for p in manifest['profiles']}
    selected = list(profile_ids or profiles)
    if set(selected) - profiles.keys():
        raise ValueError('Unknown profile(s): ' + ', '.join(sorted(set(selected) - profiles.keys())))
    candidates = {c['tool_key']: c for c in store.candidates()}
    docs = {}
    for pid in selected:
        try:
            candidate = research.candidate_for_profile(candidates, profiles[pid])
        except ValueError:
            candidate = None
        docs[pid] = candidate['docs'] if candidate else None
    directory = Path(tempfile.mkdtemp(prefix='approach-a-refresh-'))
    fetched = {}
    results = []
    current = review.current(store, cells)
    for cid, cell in sorted(cells.items()):
        pid = cell['profile_id']
        if pid not in selected:
            continue
        reasons, refs, states = [], {}, []
        if (cell.get('evidence_basis') == 'documentation_gap' or cell.get('unestablished_scope') or
                not cell.get('evidence_refs')):
            states.append(UNKNOWN)
            reasons.append('documentation_gap: cited-page checks cannot establish continued documentation absence; broader human coverage review required')
        if cell['assessment_state'] == 'pending':
            states.append(UNKNOWN)
            reasons.append('research_pending: this cell has no completed finding')
        if cid in current and current[cid]['stale']:
            states.append(CHANGED)
            reasons.append('review_stale: finding, evidence or profile differs from the recorded review')
        for ref in cell.get('evidence_refs', []):
            e = entries.get(ref)
            if not e:
                states.append(UNKNOWN)
                reasons.append('%s: missing evidence entry' % ref)
                continue
            url = e['url']
            config = docs[pid]
            if not config or not url.startswith('https://') or not sources.official(url, config):
                states.append(UNKNOWN)
                reasons.append('%s: official_scope: missing official candidate configuration or URL outside its prefixes' % ref)
                continue
            if url not in fetched:
                print('Checking official documentation: %s' % url, flush=True)
                try:
                    status, effective, html = fetch.fetch(url)
                    if status != 200 or not html:
                        fetched[url] = {'error': 'fetch_failed: HTTP %s or empty response' % status}
                    else:
                        text = pages.to_text(html)
                        fetched[url] = {'url': url, 'effective_url': effective, 'html': html, 'text': text,
                                        'sha256': st.sha256(text.encode()), 'html_sha256': st.sha256(html.encode()),
                                        'access_date': st.today(), 'title': pages.title_of(html)}
                except OSError as error:
                    fetched[url] = {'error': 'fetch_failed: %s' % error}
                filename = st.sha256(url.encode()) + '.json'
                (directory / filename).write_text(json.dumps(fetched[url], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            state, reason = compare(store, e, fetched[url], config, profiles[pid])
            states.append(state)
            reasons.append('%s: %s' % (ref, reason))
            refs[ref] = {'url': url, 'classification': state}
        classification = UNKNOWN if UNKNOWN in states else CHANGED if CHANGED in states else UNCHANGED
        results.append({'cell_id': cid, 'classification': classification, 'reasons': reasons, 'references': refs})
    checked_baseline(store, baseline)
    report = {'schema': SCHEMA, 'dataset': os.path.realpath(store.root), 'checked_at': st.now(),
              'baseline': baseline, 'profiles': selected, 'docs': docs, 'cells': results,
              'pages': {url: {'file': st.sha256(url.encode()) + '.json', 'sha256': st.sha256(page)} for url, page in fetched.items()}}
    path = directory / 'report.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path, report


def show(report):
    print('Refresh check: %s — %s' % (report['dataset'], report['checked_at']))
    ui.table([(row['cell_id'], row['classification'], '; '.join(row['reasons'])) for row in report['cells']],
             ['cell', 'result', 'reason'])
    print('No assessment records, source index or current URL cache changed. No model calls.')


def apply(store, report_path, cell_ids):
    path = Path(report_path)
    report = json.loads(path.read_text(encoding='utf-8'))
    if report.get('schema') != SCHEMA or report['dataset'] != os.path.realpath(store.root):
        raise ValueError('Refresh report belongs to another dataset or schema')
    checked_baseline(store, report['baseline'])
    affected = {r['cell_id']: r for r in report['cells'] if r['classification'] != UNCHANGED}
    selected = list(dict.fromkeys(cell_ids))
    if not selected or set(selected) - affected.keys():
        raise ValueError('Select only affected cells from this check')
    snapshots = {}
    for url, meta in report['pages'].items():
        expected = st.sha256(url.encode()) + '.json'
        if meta['file'] != expected:
            raise ValueError('Invalid comparison snapshot path')
        page = json.loads((path.parent / expected).read_text(encoding='utf-8'))
        if st.sha256(page) != meta['sha256']:
            raise ValueError('Comparison snapshot changed; run a new refresh check')
        snapshots[url] = page
    index = sources.SourceIndex(store)
    original_index = copy.deepcopy(index.data)
    data = store.load('cells.json')
    archive_pages = {}
    for cid in selected:
        cell, result = data['cells'][cid], affected[cid]
        previous_author = cell.get('author')
        previous_refs = copy.deepcopy(cell.get('evidence_refs', []))
        refs = []
        for ref in cell.get('evidence_refs', []):
            e = index.data['entries'].get(ref)
            if not e:
                refs.append(ref)
                continue
            observed = result['references'].get(ref)
            page = snapshots.get(e['url'])
            # Only selected affected cells receive new snapshot references.
            # Failed/out-of-prefix checks have no new evidence to assert.
            config = report['docs'][cell['profile_id']]
            if (observed and page and not page.get('error') and
                    config and sources.official(page['effective_url'], config)):
                spec = e.get('section_spec') or e['section']
                located = pages.locate(page['text'], spec, e['quote'], config.get('surface_labels', {}),
                                       pages.availability(page['html'], config.get('surface_labels', {})))
                rec = {'publisher': e.get('publisher'), 'title': page['title'], 'access_date': page['access_date'],
                       'sha256': page['sha256'], 'html_sha256': page['html_sha256'],
                       'effective_url': page['effective_url'],
                       'version_or_update': 'Refresh snapshot; version requires human verification; identified by hashes and access date'}
                ref = index.evidence(e['url'], spec, e['quote'], located, rec, e.get('claim_summary', ''))
                archive_pages[page['html_sha256']] = page
                index.data['pages'][e['url']] = dict(
                    index.data['pages'].get(e['url'], {}), url=e['url'], title=page['title'],
                    publisher=e.get('publisher'), sha256=page['sha256'], access_date=page['access_date'],
                    available_on=pages.availability(page['html'], config.get('surface_labels', {})),
                    status='ok', effective_url=page['effective_url'], version_or_update=rec['version_or_update'])
            refs.append(ref)
        cell['evidence_refs'] = refs
        cell['documentation_refresh'] = {'checked_at': report['checked_at'], 'classification': result['classification'],
                                         'reasons': result['reasons'], 'prior_author': previous_author,
                                         'prior_evidence_refs': previous_refs}
        cell['author'] = None
        cell['challenge'] = None
        if cell['assessment_state'] != 'pending':
            cell['assessment_state'] = 'drafted'
        model.touch(cell, 'documentation_refresh_reopened', reasons=result['reasons'])
    # Recheck every bound file immediately before the first authoritative write.
    checked_baseline(store, report['baseline'])
    for page in archive_pages.values():
        archive = Path(store.path('.cache', 'refresh-history', page['html_sha256'] + '.json'))
        archive.parent.mkdir(parents=True, exist_ok=True)
        if not archive.exists():
            archive.write_text(json.dumps(page, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    checked_baseline(store, report['baseline'])
    if index.data != original_index:
        index.save()
    store.save('cells.json', data)
    store.log('documentation_refresh_applied', cells=selected, checked_at=report['checked_at'])
    return validate.inspect(store)


def run(store, args):
    if not args.apply:
        path, report = check(store, args.profile)
        show(report)
        print('Comparison report: %s' % path)
        print('Explicit apply (review the listed cells first): ./matrix --data %s refresh --apply %s' % (
            shlex.quote(store.root), shlex.quote(str(path))))
        return 0
    report = json.loads(Path(args.apply).read_text(encoding='utf-8'))
    show(report)
    affected = [r for r in report['cells'] if r['classification'] != UNCHANGED and
                (not args.profile or r['cell_id'].rsplit('/', 1)[0] in args.profile)]
    if not affected:
        print('No selected affected cells; nothing to apply.')
        return 0
    ui.table([(r['cell_id'], r['classification'], '; '.join(r['reasons'])) for r in affected], ['affected cell', 'result', 'reason'])
    try:
        choice = cmd_blockers.ask('Cells to reopen (space-separated full IDs, all, or Enter to cancel)')
        if not choice:
            return 0
        selected = [r['cell_id'] for r in affected] if choice == 'all' else list(dict.fromkeys(choice.split()))
        if set(selected) - {r['cell_id'] for r in affected}:
            raise ValueError('Choose only the displayed selected affected cells')
        if cmd_blockers.ask('Reopen these %d cells? Existing authorship and reviews will need re-verification' % len(selected),
                            default='n', choices=['y', 'n']) != 'y':
            return 0
        result = apply(store, args.apply, selected)
        print('%d cells reopened; %d validation blockers remain. Use research --no-draft, author and review/blockers after correcting evidence.' % (
            len(selected), result['blocking_count']))
    except cmd_blockers.Quit:
        print('Canceled; nothing applied.')
    return 0
