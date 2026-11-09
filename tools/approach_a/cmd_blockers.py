"""Interactive, local-only walkthrough of current validation blockers.

Browsing never writes. Only explicit human decisions use the existing review and
boundary functions. Revalidation refreshes saved reports after each decision.
"""
import copy
from collections import Counter, OrderedDict
from types import SimpleNamespace

from . import cmd_misc, model, render, review, store as st, ui, validate

GLOBAL = ':manifest'
REVIEW_CODES = {'REVIEW_MISSING', 'REVIEW_STALE', 'REVIEW_INVALID', 'DISAGREEMENT_OPEN'}
APPROVAL_CODES = {'APPROVAL_MISSING', 'APPROVAL_STALE', 'APPROVAL_INVALID'}


class Quit(Exception):
    pass


class Back(Exception):
    pass


def ask(prompt, default='', choices=None):
    """EOF exits instead of looping at a required prompt. No implicit decisions."""
    while True:
        try:
            value = input(prompt + (' [%s]' % default if default else '') + ' (q=quit): ').strip()
        except EOFError:
            raise Quit
        value = value or default
        if value.lower() == 'q':
            raise Quit
        if choices is None or value in choices:
            return value
        print('Choose: ' + ', '.join(choices))


def blockers(store):
    return [i for i in validate.inspect(store)['issues'] if i['severity'] == 'block']


def profile_for(issue, profiles):
    where = issue.get('where') or ''
    for pid in profiles:
        if where == 'manifest:' + pid or where.startswith(pid + '/'):
            return pid
    return GLOBAL


def inventory(store):
    issues = blockers(store)
    counts = Counter(i['code'] for i in issues)
    ui.heading('Blocking items — dataset: %s' % store.root)
    ui.table(sorted(counts.items()), ['blocking key', 'items'])
    print('  %d blocking finding(s). These are current checks, not the last saved report.' % len(issues))
    return issues


def choose(title, options):
    ui.heading(title)
    ui.table([(n, key, label) for n, (key, label) in enumerate(options, 1)], ['#', 'key', 'description'])
    while True:
        value = ask('Choose a number or key', default='q')
        if value in dict(options):
            return value
        if value.isdecimal() and 1 <= int(value) <= len(options):
            return options[int(value) - 1][0]
        print('Choose one of the listed numbers or keys.')


class Walker:
    def __init__(self, store, operator=None):
        self.store, self.operator = store, operator
        if operator and operator not in store.people():
            raise ValueError('operator %r is not on this dataset roster' % operator)

    def actor(self, role=None):
        people = self.store.people()
        eligible = {pid: p for pid, p in people.items() if not role or role in p.get('roles', [])}
        if not eligible:
            raise ValueError('No roster member has the required role: %s' % role)
        if not self.operator:
            self.operator = choose('Who is recording this decision? Select your own roster ID.',
                                   [(pid, p['name']) for pid, p in eligible.items()])
        if self.operator not in eligible:
            raise ValueError('%s lacks the %s role; use u to change the recording person' % (self.operator, role))
        print('  Recording as %s (%s).' % (people[self.operator]['name'], self.operator))
        return self.operator

    def context(self, where):
        manifest = self.store.load('manifest.json')
        profile = next((p for p in manifest['profiles'] if where == 'manifest:' + p['id']), None)
        if profile:
            for field in ('id', 'surface_label', 'version', 'modes', 'platforms', 'account_and_tier', 'exclusions'):
                value = profile.get(field)
                ui.wrap(field, str(value) if isinstance(value, dict) else value)
            print('  Confirmation clears this profile’s authorship and manifest approval; check findings against the agreed boundary.')
        elif where in self.store.load('cells.json')['cells']:
            cell = self.store.load('cells.json')['cells'][where]
            cmd_misc.show(self.store, SimpleNamespace(feature=cell['feature_id'], profile=[cell['profile_id']]))
        else:
            print('  Manifest version:', manifest['manifest_version'])
            ui.table([(p['id'], p.get('account_and_tier'), p.get('confirmed_by') or 'unconfirmed')
                      for p in manifest['profiles']], ['profile', 'account/tier', 'boundary confirmed by'])

    def fingerprint(self, where):
        cells = self.store.load('cells.json')['cells']
        if where in cells:
            # Includes automated/challenge state as well as substantive data.
            entries = self.store.load('sources.json')['entries']
            evidence = {ref: entries.get(ref) for ref in cells[where].get('evidence_refs', [])}
            reviews = [r for r in self.store.load('reviews.json')['reviews'] if r['cell_id'] == where]
            return (st.sha256(cells[where]), st.manifest_hash(self.store.load('manifest.json')),
                    st.sha256(evidence), st.sha256(reviews))
        return st.sha256(self.store.load('manifest.json'))

    def unchanged(self, where, before):
        if self.fingerprint(where) != before:
            raise ValueError('The cell, evidence, review or manifest changed while it was displayed. Recheck (r) before recording a decision.')

    def confirm_boundary(self, where, before):
        who = self.actor()
        current = self.store.load('manifest.json')
        profile = copy.deepcopy(next(p for p in current['profiles'] if where == 'manifest:' + p['id']))
        tier = ask('Agreed account/tier (Enter keeps displayed value)', default=profile['account_and_tier'])
        if tier.lower().startswith('proposed:') or 'pending team confirmation' in tier.lower():
            raise ValueError('Enter the actual agreed tier instead of confirming the proposal placeholder.')
        platforms = ask('Platforms, separated by semicolons (Enter keeps current)', default='; '.join(profile['platforms']))
        extra = ask('Additional exclusions, separated by semicolons (Enter for none)')
        profile['account_and_tier'] = tier
        profile['platforms'] = [p.strip() for p in platforms.split(';') if p.strip()]
        profile['exclusions'] += [p.strip() for p in extra.split(';') if p.strip()]
        ui.wrap('Agreed tier', tier)
        ui.wrap('Agreed platforms', profile['platforms'])
        ui.wrap('Exclusions', profile['exclusions'])
        if ask('Confirm this boundary as %s?' % who, default='n', choices=['y', 'n']) != 'y':
            return False
        self.unchanged(where, before)
        profile.update(confirmed_by=who, confirmed_at=st.now(), boundary_state='confirmed')
        model.confirm_profile(self.store, profile, who)
        return True

    def decide(self, code, where, action, before):
        if code == 'BOUNDARY_UNCONFIRMED':
            return self.confirm_boundary(where, before)
        if code == 'AUTHOR_MISSING':
            who = self.actor()
            self.unchanged(where, before)
            review.set_author(self.store, where, who)
        elif code in REVIEW_CODES:
            who = self.actor('reviewer')
            cell = self.store.load('cells.json')['cells'][where]
            if not cell.get('author'):
                raise ValueError('Record the responsible author first (AUTHOR_MISSING).')
            if who == cell['author']:
                raise ValueError('Self-review is not independent. Use s to skip or u to change to the actual reviewer.')
            note = ask('Your review note (required)')
            if not note:
                raise ValueError('A review note is required; nothing recorded.')
            disposition = None
            if action == 'd':
                disposition = ask('Disagreement disposition', default='unresolved',
                                  choices=['unresolved', *review.DISPOSITIONS])
                disposition = None if disposition == 'unresolved' else disposition
            self.unchanged(where, before)
            review.record(self.store, where, who, 'disagree' if action == 'd' else 'agree', note, disposition)
        elif code in APPROVAL_CODES:
            who = self.actor('approver')
            self.unchanged(where, before)
            review.approve(self.store, who)
        else:
            return False
        return True

    def apply_profile(self, profile, code):
        """Apply one person's explicit decision to eligible unresolved cells."""
        is_review = code in REVIEW_CODES
        who = self.actor('reviewer' if is_review else None)
        cells = self.store.load('cells.json')['cells']
        ids = [model.cell_id(f['id'], profile) for f in self.store.catalog()['features']
               if model.cell_id(f['id'], profile) in cells]
        live = {}
        for issue in blockers(self.store):
            live.setdefault(issue.get('where'), set()).add(issue['code'])
        before = {cid: self.fingerprint(cid) for cid in ids}
        eligible, skipped = [], []
        for cid in ids:
            cell = cells[cid]
            if cell['assessment_state'] == 'pending':
                skipped.append((cid, 'Research pending'))
            elif not is_review and cell.get('author'):
                skipped.append((cid, 'Author already recorded'))
            elif is_review and not cell.get('author'):
                skipped.append((cid, 'Needs an author first'))
            elif is_review and cell['author'] == who:
                skipped.append((cid, 'Self-review is not independent'))
            elif is_review and not (live.get(cid, set()) & REVIEW_CODES):
                skipped.append((cid, 'Current review already recorded'))
            elif not is_review and 'AUTHOR_MISSING' not in live.get(cid, set()):
                skipped.append((cid, 'No missing-author blocker'))
            else:
                eligible.append(cid)
        ui.heading('Profile-wide %s — %s' % ('review' if is_review else 'authorship', profile))
        ui.table([(cid, cells[cid]['status'], cells[cid].get('author') or 'none') for cid in eligible],
                 ['affected cell', 'finding', 'current author'])
        if skipped:
            ui.table(skipped, ['unchanged cell', 'reason'])
        if not eligible:
            ui.warn('No eligible cells; nothing recorded.')
            return False
        decision, note, disposition = None, None, None
        if is_review:
            print('  This records a review of every listed cell, not a future reviewer assignment.')
            decision = ask('Decision for all listed cells', choices=['agree', 'disagree'])
            note = ask('Shared review note for all listed cells (required)')
            if not note:
                raise ValueError('A review note is required; nothing recorded.')
            if decision == 'disagree':
                disposition = ask('Disagreement disposition', default='unresolved',
                                  choices=['unresolved', *review.DISPOSITIONS])
                disposition = None if disposition == 'unresolved' else disposition
        if ask('Record %s as %s for all %d listed cells in %s?' %
               (who, 'reviewer (%s)' % decision if is_review else 'author', len(eligible), profile),
               default='n', choices=['y', 'n']) != 'y':
            return False
        # Reject a changed selection or unseen edits before making any batch writes.
        now = self.store.load('cells.json')['cells']
        if {cid for cid, c in now.items() if c['profile_id'] == profile} != set(ids):
            raise ValueError('Profile cells changed while displayed. Recheck before applying profile-wide.')
        for cid in ids:
            self.unchanged(cid, before[cid])
        saved = 0
        for cid in eligible:
            try:
                self.unchanged(cid, before[cid])
                if is_review:
                    review.record(self.store, cid, who, decision, note, disposition)
                else:
                    review.set_author(self.store, cid, who)
                saved += 1
            except ValueError as error:
                if not saved:
                    raise
                ui.warn('Stopped after %d saved decisions: %s' % (saved, error))
                break
        ui.ok('%d profile-wide decision(s) recorded; %d cell(s) left unchanged.' % (saved, len(ids) - saved))
        return bool(saved)

    def walk(self, profile, code):
        profiles = model.profile_ids(self.store.load('manifest.json'))
        pending = OrderedDict()
        for issue in blockers(self.store):
            if issue['code'] == code and profile_for(issue, profiles) == profile:
                pending.setdefault(issue.get('where') or '', []).append(issue)
        for n, where in enumerate(pending, 1):
            while True:
                current = [i for i in blockers(self.store) if i['code'] == code and (i.get('where') or '') == where]
                if not current:
                    break
                ui.heading('%s — %d/%d — %s' % (code, n, len(pending), where or 'manifest-wide'))
                for issue in current:
                    print('  ' + issue['message'])
                before = self.fingerprint(where)
                self.context(where)
                if code == 'BOUNDARY_UNCONFIRMED':
                    actions = {'c': 'confirm/update boundary'}
                elif code == 'AUTHOR_MISSING':
                    actions = {'a': 'take responsibility as author', 'p': 'apply one author profile-wide'}
                elif code in REVIEW_CODES:
                    actions = {'a': 'agree after checking sources', 'd': 'record disagreement',
                               'p': 'apply one reviewer profile-wide'}
                elif code in APPROVAL_CODES:
                    actions = {'a': 'approve this manifest version (not cell findings)'}
                else:
                    actions = {}
                    print('  Correct the finding/source data in %s, then recheck. This walker does not invent research or remove validation rules.' % self.store.root)
                actions.update(s='skip', r='recheck', u='change recording person', b='back to menus', q='quit')
                try:
                    action = ask(' / '.join('%s=%s' % pair for pair in actions.items()), default='s', choices=list(actions))
                    if action == 's':
                        break
                    if action == 'b':
                        raise Back
                    if action == 'u':
                        self.operator = None
                        continue
                    if action == 'r':
                        continue
                    if action == 'p':
                        self.unchanged(where, before)
                        saved = self.apply_profile(profile, code)
                    else:
                        saved = self.decide(code, where, action, before)
                    if saved:
                        report = validate.run(self.store)
                        ui.ok('Decision saved. %d blocking finding(s) remain.' % report['blocking_count'])
                        try:
                            render.run(self.store)
                        except (KeyError, TypeError, ValueError) as error:
                            ui.warn('Decision is saved, but generated views need a data correction: %s' % error)
                        break
                except ValueError as error:
                    ui.warn(str(error))


def run(store, args):
    print('Browsing/skipping is read-only. Decisions record the named person; this CLI does not authenticate identity.')
    issues = inventory(store)
    if args.list:
        return 0
    walker = Walker(store, args.operator)
    selected, code = args.profile, args.code
    if code and not selected:
        raise ValueError('--code requires --profile; select manifest-wide blockers interactively')
    if selected and selected not in model.profile_ids(store.load('manifest.json')):
        raise ValueError('Unknown profile: %s' % selected)
    try:
        while issues:
            profiles = model.profile_ids(store.load('manifest.json'))
            counts = Counter(profile_for(i, profiles) for i in issues)
            options = [(pid, '%d blocker(s)' % counts[pid]) for pid in profiles if counts[pid]]
            if counts[GLOBAL]:
                options.append((GLOBAL, 'Manifest-wide — %d blocker(s), including approval' % counts[GLOBAL]))
            selected = selected or choose('Choose a profile (or manifest-wide items)', options)
            codes = Counter(i['code'] for i in issues if profile_for(i, profiles) == selected)
            if not codes:
                ui.ok('No blockers for that profile.')
            else:
                if code and code not in codes:
                    raise ValueError('No current %s blockers for %s' % (code, selected))
                code = code or choose('Choose a blocking key for %s' % selected,
                                      [(key, '%d item(s)' % count) for key, count in sorted(codes.items())])
                try:
                    walker.walk(selected, code)
                except Back:
                    pass
            selected, code = None, None
            issues = inventory(store)
        ui.ok('No blocking findings remain (structural validation only). Nothing published.')
    except KeyboardInterrupt:
        print('\nInterrupted. Recorded decisions are saved; no additional changes made.')
        return 130
    except Quit:
        print('\nStopped. %d blocking finding(s) remain. Recorded decisions are saved; skipped items remain open.' % len(blockers(store)))
    return 0
