import assert from 'node:assert/strict';
import test from 'node:test';
import { buildIndex, classify } from '../../../../dashboard/feature-matrix/matrix-logic.mjs';
import { recordedTier, shortlistRows, readShortlist, writeShortlist } from '../../../../dashboard/feature-matrix/shortlist-logic.mjs';
import { demoPayload } from './shortlist-fixture.mjs';

const rows = (data, tiers = [], features = ['F01', 'F07', 'F08']) =>
  shortlistRows(buildIndex(data), new Set(tiers), new Set(features));

test('all requirements must match within one eligible profile and recorded tier', () => {
  assert.deepEqual(rows(demoPayload(), ['alder-individual', 'alder-enterprise']).map((r) => [r.tier.label, r.state]),
    [['Individual', 'gap'], ['Enterprise', 'match']]);
  const split = demoPayload();
  Object.assign(split.cells.find((c) => c.profile_id === 'alder-enterprise' && c.feature_id === 'F01'),
    { status: 'Unavailable', evidence_basis: 'documented_absence', unsupported_scope: ['Excluded'] });
  assert.ok(rows(split, ['alder-individual', 'alder-enterprise']).every((r) => r.state === 'gap'));
  assert.deepEqual(rows(split, [], []), []);
  assert.deepEqual(rows(split, ['absent']), []);
});

test('explicit gap wins over missing tier or inconclusive other requirements', () => {
  const data = demoPayload();
  data.profiles.find((p) => p.id === 'alder-individual').account_and_tier = null;
  data.cells.find((c) => c.profile_id === 'alder-individual' && c.feature_id === 'F01').assessment_state = 'pending';
  assert.equal(rows(data, ['alder-individual'])[0].state, 'gap');
});

test('missing tier stays visible, cannot match, and is excluded by another tier filter', () => {
  assert.equal(rows(demoPayload()).find((r) => r.profile.id === 'elm-undecided').state, 'unknown');
  assert.equal(rows(demoPayload(), ['cedar-individual']).length, 1);
  for (const value of [null, '', 'Not established', 'Tier for the assessment is a team choice.']) {
    assert.equal(recordedTier({ id: 'p', account_and_tier: value }), null);
  }
  assert.equal(recordedTier({ id: 'p', account_and_tier: 'Recorded custom plan' }).label, 'Recorded custom plan');
});

test('pending, partial, conflicting, unmatched or disputed evidence cannot be a match', () => {
  assert.equal(rows(demoPayload(), ['birch-team'])[0].state, 'unknown');
  for (const change of [
    { assessment_state: 'pending' }, { evidence_refs: [] }, { evidence_refs: ['absent'] },
    { status: 'Not established from documentation' }, { unestablished_scope: ['Network isolation'] },
    { gap_reason: 'Conflicting versions' }, { evidence_basis: 'documentation_conflict' },
    { status: 'Configuration or extension required' }, { status: 'Custom implementation required' },
    { review: { stale: true } }, { review: { decision: 'disagree', independent: true } },
  ]) {
    const data = demoPayload();
    Object.assign(data.cells.find((c) => c.profile_id === 'cedar-individual' && c.feature_id === 'F08'), change);
    assert.equal(rows(data, ['cedar-individual'])[0].state, 'unknown', JSON.stringify(change));
  }
  const data = demoPayload(); data.evidence[0].quotation_matched = false;
  assert.equal(rows(data, ['cedar-individual'])[0].state, 'unknown');
});

test('mixed support explicitly retains unsupported and unestablished scope in reasons', () => {
  const data = demoPayload();
  Object.assign(data.cells.find((c) => c.profile_id === 'cedar-individual' && c.feature_id === 'F08'),
    { unsupported_scope: ['Network not isolated'], unestablished_scope: ['Windows'], required_setup: 'Enable sandbox' });
  const result = rows(data, ['cedar-individual'])[0];
  assert.equal(result.state, 'gap');
  assert.match(result.requirements.find((r) => r.feature.id === 'F08').reason, /Network not isolated.*Windows.*Enable sandbox/);
});

test('shortlist URL state round-trips without removing overview filters or preview', () => {
  const params = new URLSearchParams('q=existing&preview=matrix.demo.json&profile=p&feature=F01');
  const state = { tiers: new Set(['a', 'b']), features: new Set(['F01', 'F08']), sort: 'name' };
  assert.deepEqual(readShortlist(writeShortlist(params, state).toString()), state);
  assert.equal(params.get('q'), 'existing'); assert.equal(params.get('preview'), 'matrix.demo.json');
  writeShortlist(params, { tiers: new Set(), features: new Set(), sort: 'group' });
  assert.equal(params.has('required'), false); assert.equal(params.has('tier'), false);
});

test('fictional demo uses the existing contract and all 18 catalog features, never published mode', () => {
  const data = demoPayload();
  assert.equal(data.catalog.features.length, 18); assert.equal(data.cells.length, 18 * data.profiles.length);
  assert.equal(classify(data).kind, 'error'); assert.equal(classify(data, { allowPreview: true }).preview, true);
  assert.equal(JSON.stringify(data).includes('shortlist_tiers'), false);
});


test('documented delivery mechanisms are not ranked; complete setup and scope can establish coverage', () => {
  for (const status of ['Configuration or extension required', 'Custom implementation required']) {
    const data = demoPayload();
    Object.assign(data.cells.find((c) => c.profile_id === 'cedar-individual' && c.feature_id === 'F08'),
      { status, required_setup: 'Documented setup within the recorded profile boundary' });
    const result = rows(data, ['cedar-individual'])[0];
    assert.equal(result.state, 'match');
    assert.ok(result.requirements.find((r) => r.feature.id === 'F08').reason.includes(status));
  }
});
