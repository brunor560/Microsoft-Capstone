"""Structural validation of the Approach A dataset (SRS TC-5.1-1 to TC-5.4-1 scope).

Accepted only when no blocking finding remains. A pass shows the dataset is
structurally complete; it does not prove that sources support the claims, and
it is not by itself H-9 completion (TC-5.5-1 publication is out of scope here).
"""
from . import checks
from . import model
from . import store as st

LIMITS = [
    'Structural validation only: it does not prove that each source supports its claim.',
    'The automated evidence-challenge pass is not the independent team-member review (SRS Spec 5.3).',
    'TC-5.5-1 (separate publication) is not checked here; no publication is produced.',
    'A passing report is not by itself H-9 completion; the team confirms H-9.',
    'The CLI cannot authenticate people; reviewer and approver identity comes from the commit that records them.',
]


def run(store):
    issues = []

    def add(code, severity, msg, where=None):
        issues.append({'code': code, 'severity': severity, 'message': msg, 'where': where})

    ctx = checks.Context(store)
    checks.catalog(ctx, add)
    checks.manifest(ctx, add)
    expected = checks.coverage(ctx, add)
    for cid in sorted(expected & set(ctx.cells)):
        checks.cell(ctx, cid, add)

    blocking = [i for i in issues if i['severity'] == 'block']
    states = model.counts({k: v for k, v in ctx.cells.items() if k in expected})
    report = {
        'schema': 'approach-a/validation/1', 'generated_at': st.now(),
        'manifest_version': ctx.manifest.get('manifest_version'), 'profiles': ctx.ids,
        'P': len(ctx.ids), 'expected_cells': 18 * len(ctx.ids),
        'present_cells': len(expected & set(ctx.cells)), 'cell_states': states,
        'accepted': not blocking,
        'result': 'ACCEPTED (structurally complete)' if not blocking else 'NOT ACCEPTED',
        'blocking_count': len(blocking),
        'counts_by_code': {c: sum(i['code'] == c for i in issues) for c in sorted({i['code'] for i in issues})},
        'issues': issues, 'limits': LIMITS,
    }
    store.save('validation_report.json', report)
    store.log('validated', accepted=report['accepted'], blocking=len(blocking), P=len(ctx.ids))
    return report
