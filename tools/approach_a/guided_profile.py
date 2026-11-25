"""One editable profile proposal. No assessment writes until human confirmation."""
import copy
import datetime
import re
from types import SimpleNamespace

from . import cmd_blockers as prompts, cmd_misc, model, sources, store as st, ui, validate

SETUP_FIELDS = ('tool', 'tool_key', 'surface', 'surface_label', 'category_tags', 'modes',
                'platforms', 'account_and_tier', 'exclusions', 'included_components',
                'interface_and_execution_location', 'instructions_and_permissions', 'model_support',
                'documentation_base', 'documentation_entry_points')
EDIT_FIELDS = ('account_and_tier', 'surface', 'surface_label', 'platforms', 'modes', 'exclusions',
               'category_tags', 'included_components', 'interface_and_execution_location',
               'instructions_and_permissions', 'model_support', 'documentation_base',
               'documentation_entry_points', 'version', 'source_access_date')
LIST_FIELDS = ('platforms', 'modes', 'exclusions', 'category_tags', 'included_components', 'documentation_entry_points')
# Labels, source access dates and prose explaining unversioned docs do not make a
# second assessment boundary. A documented product version does.
SCOPE_FIELDS = ('tool_key', 'surface', 'account_and_tier', 'platforms', 'modes', 'exclusions',
                'included_components', 'interface_and_execution_location', 'instructions_and_permissions', 'model_support')
PLACEHOLDER = re.compile(r'\b(proposed|pending|tbd|todo|unknown|unspecified|not established|not yet|to confirm|operator to confirm)\b|<[^>]*>|^\.{3}$', re.I)


def normalized(value):
    if isinstance(value, list):
        return sorted(set(normalized(v) for v in value))
    return ' '.join(str(value or '').lower().split()).rstrip('.')


def boundary(profile):
    return {**{k: normalized(profile.get(k)) for k in SCOPE_FIELDS},
            'version': normalized((profile.get('version') or {}).get('value'))}


def duplicate(profile, profiles):
    return next((p for p in profiles if boundary(p) == boundary(profile)), None)


def candidate_for(store, profile):
    return next((c for c in store.candidates() if c['tool_key'] == profile.get('tool_key')), None)


def entry_points(candidate, surface):
    return [sources.doc_url(candidate['docs'], seed)
            for seed in candidate['surfaces'][surface].get('seed_pages', [])] or [candidate['docs']['base_url']]


def proposal(template, candidate, copied=False):
    p = {k: copy.deepcopy(template[k]) for k in SETUP_FIELDS if k in template}
    p['documentation_base'] = p.get('documentation_base') or candidate['docs']['base_url']
    p['documentation_entry_points'] = p.get('documentation_entry_points') or entry_points(candidate, p['surface'])
    p.update(account_and_tier='', version={'value': None, 'documentation_note': ''}, source_access_date=None)
    # New variants must research their own scope, never inherit another tier's
    # saved findings or candidate briefs. Saved drafts are already profile-keyed.
    p['use_prepared_briefs'] = not copied
    return p


def problems(p, candidate):
    required = [k for k in model.REQUIRED_PROFILE_FIELDS if k != 'id'] + ['documentation_base', 'documentation_entry_points']
    missing = []
    for field in required:
        value = p.get(field)
        if field == 'version':
            value = (value or {}).get('value') or (value or {}).get('documentation_note')
        values = value if isinstance(value, list) else [value]
        if not values or any(not v or PLACEHOLDER.search(str(v)) for v in values):
            missing.append(field)
    if p.get('surface') not in candidate['surfaces']:
        missing.append('surface (must resolve a candidate surface)')
    try:
        date = p.get('source_access_date') or ''
        parsed_date = datetime.date.fromisoformat(date)
        if parsed_date.isoformat() != date:
            raise ValueError('Use ISO date format')
        if parsed_date > datetime.date.today():
            missing.append('source_access_date (cannot be later than today)')
    except ValueError:
        missing.append('source_access_date (YYYY-MM-DD, actually reviewed)')
    urls = [p.get('documentation_base')] + (p.get('documentation_entry_points') or [])
    if any(not u or not u.startswith('https://') or not sources.official(u, candidate['docs']) for u in urls):
        missing.append('documentation URLs (must be inside the candidate official prefixes)')
    if any(tag not in ('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7') for tag in p.get('category_tags', [])):
        missing.append('category_tags (T1–T7)')
    return sorted(set(missing))


def stable_id(p, candidate, profiles):
    base = candidate['surfaces'][p['surface']]['profile_id']
    if not any(existing['id'] == base for existing in profiles):
        return base
    label = re.sub('[^a-z0-9]+', '-', p['account_and_tier'].lower()).strip('-')[:32] or 'variant'
    return '%s-%s-%s' % (base, label, st.sha256(boundary(p))[:10])


def edit(p, field, candidate):
    if field == 'version':
        value = prompts.ask('Documented version, or unversioned: <explanation> (no inherited version claim)')
        if value.lower() == 'unversioned':
            p[field] = {'value': None, 'documentation_note': ''}
        elif value.lower().startswith('unversioned:'):
            p[field] = {'value': None, 'kind': 'unversioned official documentation',
                        'documentation_note': value.split(':', 1)[1].strip()}
        else:
            p[field] = {'value': value, 'kind': 'operator-established documentation version',
                        'documentation_note': 'Version entered for this assessment; see documentation entry points'}
    elif field == 'surface':
        p[field] = prompts.ask('Surface', choices=sorted(candidate['surfaces']))
        p['surface_label'] = candidate['surfaces'][p[field]]['label']
        p['documentation_entry_points'] = entry_points(candidate, p[field])
    else:
        value = prompts.ask('%s%s (enter the replacement)' % (field, '; separate values with semicolons' if field in LIST_FIELDS else ''))
        p[field] = [s.strip() for s in value.split(';') if s.strip()] if field in LIST_FIELDS else value


def open_existing(store, p):
    cells = [c for c in store.load('cells.json')['cells'].values() if c['profile_id'] == p['id']]
    counts = model.counts({str(i): c for i, c in enumerate(cells)})
    reviews = {i['where'] for i in validate.inspect(store)['issues']
               if i['code'] in prompts.REVIEW_CODES and (i.get('where') or '').startswith(p['id'] + '/')}
    print('Existing profile %s: research pending/drafted=%d; remaining reviews=%d' % (
        p['id'], counts['pending'] + counts['drafted'], len(reviews)))
    print('Next: ./matrix research --profile %s or ./matrix review --profile %s' % (p['id'], p['id']))
    if prompts.ask('Open this existing profile (read-only)?', default='n', choices=['y', 'n']) == 'y':
        cmd_misc.show(store, SimpleNamespace(feature='F01', profile=[p['id']]))


def run(store, args):
    """Return the new profile ID, or None on cancellation/existing-profile open."""
    library = store if store.exists('catalog.json') else st.Store(st.DEFAULT_ROOT)
    manifest_before = store.load('manifest.json')
    cells_before = store.load('cells.json')
    options = [('prepared', 'Use a prepared candidate'), ('copy', 'Copy an existing profile'),
               ('new', 'New tool (existing ./matrix new command)')]
    path = prompts.choose('Create one profile', options)
    if path == 'new':
        print('Use ./matrix new to enter official documentation for a new tool, then ./matrix start and choose prepared.')
        return None
    profiles = manifest_before['profiles']
    if path == 'copy':
        if not profiles:
            print('No existing profiles to copy. Choose prepared on the next start.')
            return None
        selected = prompts.choose('Copy setup inputs from', [(p['id'], '%s / %s / %s' % (
            p['tool'], p['surface'], p['account_and_tier'])) for p in profiles])
        template = next(p for p in profiles if p['id'] == selected)
        candidate = candidate_for(library, template)
        if not candidate or template['surface'] not in candidate['surfaces']:
            raise ValueError('No candidate research inputs for this tool/surface. Use ./matrix new to prepare them first.')
    else:
        from . import cmd_start
        candidate = cmd_start.choose_tool(library, args)
        surface = prompts.ask('Surface', default=args.surface or candidate.get('default_surface'), choices=sorted(candidate['surfaces']))
        template = model.profile_from_candidate(candidate, surface)
    p = proposal(template, candidate, copied=path == 'copy')
    inherited = copy.deepcopy(p)
    p['account_and_tier'] = prompts.ask('Intended account and exact tier (required; no inherited tier)')
    while True:
        errors = problems(p, candidate)
        ui.heading('Editable boundary summary — setup proposal, not a finding')
        print('Tool: %s; candidate research key: %s' % (p['tool'], p['tool_key']))
        for field in EDIT_FIELDS:
            state = 'NEEDS INPUT' if any(e == field or e.startswith(field + ' ') for e in errors) else (
                'EDITED' if p.get(field) != inherited.get(field) else 'INHERITED setup')
            ui.wrap('%s [%s]' % (field, state), p.get(field))
        if errors:
            print('Confirmation blocked: ' + ', '.join(errors))
        print('Enter a field name to jump directly to it; confirm to add; q to cancel.')
        action = prompts.ask('Field or confirm', default='q', choices=[*EDIT_FIELDS, 'confirm', 'q'])
        if action != 'confirm':
            edit(p, action, candidate)
            continue
        # Detect matching boundaries even when the new version/date input is
        # unfinished. Opening an existing record never creates a proposal.
        match = duplicate(p, profiles)
        if match:
            open_existing(store, match)
            return None
        if errors:
            continue
        p['id'] = stable_id(p, candidate, profiles)
        if any(existing['id'] == p['id'] for existing in profiles) or any(
                cid.startswith(p['id'] + '/') for cid in cells_before['cells']):
            raise ValueError('Profile ID already in use; no records changed: %s' % p['id'])
        if boundary(p) != boundary(model.profile_from_candidate(candidate, p['surface'])):
            p['use_prepared_briefs'] = False
        print('New stable profile ID: %s (18 fresh pending cells; manifest approval will be required).' % p['id'])
        who = prompts.ask('Your roster ID', choices=list(library.people()))
        if prompts.ask('Confirm this boundary and add %s as %s?' % (p['id'], who), default='n', choices=['y', 'n']) != 'y':
            return None
        if store.load('manifest.json') != manifest_before or store.load('cells.json') != cells_before:
            raise ValueError('Dataset changed during setup; restart before confirming. Nothing added.')
        if not store.exists('manifest.json'):
            store.init_from()
        p.update(confirmed_by=who, confirmed_at=st.now(), boundary_state='confirmed')
        result = model.add_profile(store, p, who)
        print('Added %s. Manifest version %s requires approval; no findings, authors or reviews copied.' % (
            p['id'], result['manifest_version']))
        return p['id']
