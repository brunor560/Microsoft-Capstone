"""Per-cell validation: status, evidence, challenge flags and independent review."""
from . import model

SCORE_KEYS = ('score', 'rank', 'ranking', 'weight', 'points', 'rating')


def cell(ctx, cid, add):
    c = ctx.cells[cid]
    bad = [k for k in c if k.lower() in SCORE_KEYS]
    if bad:
        add('SCORE_FORBIDDEN', 'block', 'Score or rank fields are not allowed: %s' % bad, cid)
    if c.get('status') not in ctx.statuses:
        add('STATUS_INVALID', 'block', 'Unknown status %r' % c.get('status'), cid)
    if c.get('assessment_state') == 'pending':
        add('CELL_PENDING', 'block', 'Research pending; the NE status is a placeholder, not a finding', cid)
        return
    evidence(ctx, c, cid, add)
    for k in ('supported_scope', 'required_setup', 'activation_state', 'control_mechanism'):
        if c.get(k) in (None, ''):
            add('FIELD_MISSING', 'block', 'Missing %s' % k, cid)
    flags = (c.get('challenge') or {}).get('flags')
    if flags is None:
        add('CHALLENGE_MISSING', 'block', 'Evidence-challenge pass has not run on this cell', cid)
    else:
        for f in flags:
            if f['severity'] == 'block':
                add('CHALLENGE_' + f['type'].upper(), 'block', f['detail'], cid)
    independent_review(ctx, c, cid, add)


def evidence(ctx, c, cid, add):
    refs = c.get('evidence_refs', [])
    for r in refs:
        e = ctx.entries.get(r)
        if not e:
            add('EVIDENCE_DANGLING', 'block', 'Evidence %s is not in the source index' % r, cid)
        elif not (e.get('url') and e.get('access_date') and e.get('section')):
            add('EVIDENCE_INCOMPLETE', 'block', 'Evidence %s lacks URL, section or access date' % r, cid)
        elif e.get('check') != 'verified':
            add('EVIDENCE_UNVERIFIED', 'block', 'Evidence %s quote was not found in its section' % r, cid)
    if c['status'] != model.NE and not refs:
        add('EVIDENCE_MISSING', 'block', 'Affirmative or absence status needs an official source', cid)
    if c['status'] == model.NE:
        gr = (c.get('gap_reason') or '').strip()
        if not gr or gr.lower().startswith('assessment pending'):
            add('GAP_REASON_MISSING', 'block', 'Completed Not established needs a specific gap or conflict reason', cid)
        if c.get('evidence_basis') not in ('documentation_gap', 'documentation_conflict'):
            add('BASIS_INVALID', 'block', 'Not established must have a gap or conflict evidence basis', cid)


def independent_review(ctx, c, cid, add):
    if not c.get('author'):
        add('AUTHOR_MISSING', 'block', 'No named human author (agent drafts need a responsible team member)', cid)
    rv = ctx.reviews.get(cid)
    if not rv:
        add('REVIEW_MISSING', 'block', 'No independent team-member review', cid)
    elif rv['stale']:
        add('REVIEW_STALE', 'block', 'Cell changed after review by %s' % rv['reviewer'], cid)
    elif rv['reviewer'] == c.get('author'):
        add('REVIEW_MISSING', 'block', 'Self-review is not independent', cid)
    elif rv['reviewer'] not in ctx.people:
        add('REVIEW_INVALID', 'block', 'Reviewer is not on the roster', cid)
    elif rv['decision'] == 'disagree':
        if not rv.get('disposition') or rv['disposition'] == 'escalated':
            add('DISAGREEMENT_OPEN', 'block', 'Reviewer disagreement has no resolved disposition', cid)
        else:
            add('REVIEW_MISSING', 'block', 'Disagreement resolved (%s); the revised cell needs a new agree review'
                % rv['disposition'], cid)
