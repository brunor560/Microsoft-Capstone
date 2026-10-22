"""Create a candidate for a tool with no prepared profile (live demo path).

The operator supplies only what they know: the tool name, the official
documentation URL and the surface. Fields the operator does not enter are
recorded as 'Not established; operator to confirm' instead of being guessed.
No research brief exists, so every cell stays pending: an honest partial result.
"""
import json
import os
import re

from . import store as st
from . import ui

UNKNOWN = 'Not established; operator to confirm from official documentation'


def run(store, args):
    if not store.exists('manifest.json'):
        store.init_from()
    ui.heading('New tool candidate (no prepared research)')
    tool = ui.ask('Tool name (as the vendor writes it)', default=args.tool_name,
                  assume=args.tool_name if args.yes else None)
    url = ui.ask('Official documentation base URL', default=args.docs_url,
                 assume=args.docs_url if args.yes else None)
    if not tool or not re.match(r'^https://[^ ]+/$', url or ''):
        raise ValueError('INPUT_INCOMPLETE: a tool name and an https documentation URL ending in / are required')
    surface = ui.ask('Surface key (for example cli, ide, cloud)', default=args.surface or 'cli',
                     assume=(args.surface or 'cli') if args.yes else None)
    key = re.sub(r'[^a-z0-9]+', '-', tool.lower()).strip('-')
    cand = {
        'schema': 'approach-a/candidate/1', 'tool_key': key, 'tool': tool, 'vendor': UNKNOWN,
        'default_surface': surface,
        'note': 'Created live with `assess new` on %s. Only the tool name, documentation URL and surface were '
                'entered; other fields are unconfirmed. No research brief: every cell stays pending.' % st.today(),
        'docs': {'base_url': url, 'allowed_prefixes': [url], 'publisher': UNKNOWN,
                 'surface_labels': {}},
        'surfaces': {surface: {
            'label': '%s (%s)' % (tool, surface), 'profile_id': '%s-%s' % (key, surface),
            'category_tags': [args.category] if args.category else ['T1'] if surface == 'ide' else ['T2'],
            'interface_and_execution_location': UNKNOWN,
            'version': {'value': None, 'kind': 'not yet identified',
                        'documentation_note': 'Version not yet established from documentation; record the access date'},
            'modes': [UNKNOWN], 'platforms': [UNKNOWN], 'account_and_tier': UNKNOWN,
            'model_support': UNKNOWN, 'included_components': [UNKNOWN],
            'exclusions': ['Other product surfaces of %s' % tool, 'Add-ons and third-party integrations'],
            'instructions_and_permissions': UNKNOWN, 'seed_pages': [url]}},
    }
    d = store.path('candidates', key)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'candidate.json'), 'w', encoding='utf-8') as f:
        json.dump(cand, f, indent=2, ensure_ascii=False)
        f.write('\n')
    store.log('candidate_created', actor=args.operator or 'cli', tool_key=key, docs=url, surface=surface)
    ui.ok('Candidate %s created. Next: start --tool %s (confirm the boundary), then research.' % (key, key))
    ui.warn('Category tag %s is a placeholder for the operator to confirm.' % cand['surfaces'][surface]['category_tags'][0])
    return 0
