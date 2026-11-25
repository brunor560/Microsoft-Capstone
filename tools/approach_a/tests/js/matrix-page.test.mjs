// Page logic tests (Node built-in runner, no dependencies):  node --test tools/approach_a/tests/js/
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildIndex, cellLabel, classify, emptyFilters, parseParams, reviewLines, safeHref, toParams, visibleRows,
} from '../../../../dashboard/feature-matrix/matrix-logic.mjs';
import { cell, payload } from './fixtures.mjs';

test('empty marker is a deliberate empty state', () => {
  const r = classify({ schema: 'approach-a/publication-empty/1', message: 'ignored' });
  assert.equal(r.kind, 'empty');
  assert.equal(r.message, 'No reviewed assessment published yet.');
});

test('missing or malformed data is an error, never the empty state', () => {
  for (const bad of [null, [], 'x', {}, { schema: 'other/1' }, { schema: 'approach-a/publication/1' }]) {
    assert.equal(classify(bad).kind, 'error', JSON.stringify(bad));
  }
  const noProfiles = payload(); noProfiles.profiles = [];
  assert.equal(classify(noProfiles).kind, 'error');
  const badMode = payload(); badMode.release.publication_mode = 'weird';
  assert.equal(classify(badMode).kind, 'error');
});

test('a preview payload is refused unless explicitly allowed', () => {
  assert.equal(classify(payload('preview')).kind, 'error');
  const r = classify(payload('preview'), { allowPreview: true });
  assert.equal(r.kind, 'data'); assert.equal(r.preview, true);
  assert.equal(classify(payload()).preview, false);
});

test('pending research is never labeled as a Not established finding', () => {
  const ix = buildIndex(payload());
  const pending = cellLabel(ix.cells.get('p-one/F03'), false);
  assert.equal(pending.text, 'Research pending'); assert.equal(pending.tone, 'pending');
  const ne = cellLabel(ix.cells.get('p-one/F02'), false);
  assert.equal(ne.text, 'Not established from documentation'); assert.equal(ne.tone, 'ne');
  assert.equal(cellLabel(null, false).text, 'Cell missing');
});

test('preview cells carry visible workflow labels; published cells do not', () => {
  const c = cell('p', 'F01', { assessment_state: 'challenged' });
  assert.match(cellLabel(c, true).workflow, /awaiting independent review/);
  assert.equal(cellLabel(c, false).workflow, null);
});

test('a row shows when any selected profile matches and keeps the other columns', () => {
  const ix = buildIndex(payload());
  const { rows, columns } = visibleRows(ix, { ...emptyFilters(), status: 'Configuration or extension required' });
  assert.deepEqual(rows.map((r) => r.feature.id), ['F01']);
  assert.equal(columns.length, 2);
  assert.deepEqual(rows[0].cells.map((c) => c.match), [false, true]);
});

test('filters: area, activation, search, profile selection and clearing', () => {
  const ix = buildIndex(payload());
  const ids = (f) => visibleRows(ix, { ...emptyFilters(), ...f }).rows.map((r) => r.feature.id);
  assert.deepEqual(ids({ area: 'Development' }), ['F03']);
  assert.deepEqual(ids({ activation: 'optional' }), ['F01']);
  assert.deepEqual(ids({ q: 'sources are silent' }), ['F02']);
  const one = visibleRows(ix, { ...emptyFilters(), profiles: ['p-two'] });
  assert.equal(one.columns.length, 1); assert.equal(one.rows.length, 3);
  assert.equal(ids({}).length, 3);
});

test('URL parameters round-trip and support stable cell links', () => {
  const f = { ...emptyFilters(), area: 'Planning', q: 'a b', profiles: ['p-one'] };
  const back = parseParams(toParams(f, { profile: 'p-one', feature: 'F08' }));
  assert.deepEqual(back.filters, f);
  assert.equal(back.profile, 'p-one'); assert.equal(back.feature, 'F08');
  assert.equal(toParams(emptyFilters(), null), '');
  assert.equal(parseParams('?profile=antigravity-cli&feature=F08').feature, 'F08');
});

test('only https links are ever linked', () => {
  assert.equal(safeHref('https://example.com/a'), 'https://example.com/a');
  for (const bad of ['javascript:alert(1)', 'http://example.com', 'data:text/html,x', '', null, 'not a url']) assert.equal(safeHref(bad), null, String(bad));
});

test('review lines show provenance without identities', () => {
  const lines = reviewLines(cell('p', 'F01')).join(' ');
  assert.match(lines, /Independently reviewed/); assert.match(lines, /2026-11-01/);
  assert.match(reviewLines(cell('p', 'F01', { review: null })).join(' '), /No independent review/);
  const stale = { decision: 'agree', stale: true, independent: true, reviewed_at: '2026-11-01' };
  assert.match(reviewLines(cell('p', 'F01', { review: stale })).join(' '), /out of date/);
});

test('rows follow catalog order and no score is computed', () => {
  const ix = buildIndex(payload());
  const out = visibleRows(ix, emptyFilters());
  assert.deepEqual(out.rows.map((r) => r.feature.id), ['F01', 'F02', 'F03']);
  assert.equal(JSON.stringify(out).toLowerCase().includes('"score"'), false);
});
