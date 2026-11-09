// Rendering safety tests with a minimal fake DOM (no dependencies): text in data must stay text.
import test from 'node:test';
import assert from 'node:assert/strict';

class Node_ { }
class Text extends Node_ { constructor(t) { super(); this.text = t; } get textContent() { return this.text; } }
class El extends Node_ {
  constructor(tag) { super(); this.tag = tag; this.attrs = {}; this.children = []; this.listeners = {}; this.className = ''; }
  setAttribute(k, v) { this.attrs[k] = v; }
  addEventListener(k, fn) { this.listeners[k] = fn; }
  append(...kids) { this.children.push(...kids); }
  get textContent() { return this.children.map((c) => c.textContent).join(''); }
  set textContent(value) { this.children = [new Text(value)]; }
  get firstChild() { return this.children[0]; }
  removeChild(child) { this.children.splice(this.children.indexOf(child), 1); }
  all() { return [this, ...this.children.flatMap((c) => (c instanceof El ? c.all() : []))]; }
}
globalThis.Node = Node_;
globalThis.document = { createElement: (t) => new El(t), createTextNode: (t) => new Text(t) };

const { h } = await import('../../../../dashboard/feature-matrix/dom.mjs');
const { detail, evidenceItem, profileCard } = await import('../../../../dashboard/feature-matrix/views.mjs');
const { buildIndex } = await import('../../../../dashboard/feature-matrix/matrix-logic.mjs');

const EVIL = '<img src=x onerror=alert(1)><script>alert(2)</script>';
const feature = { id: 'F08', area: 'A', name: 'Feat', capability: 'cap', examine: 'ex' };
const profile = { id: 'p', tool: 'Tool', surface_label: 'CLI', exclusions: [EVIL], version: { value: '1' }, modes: [], platforms: [], documentation_base: 'javascript:alert(1)' };
const cell = {
  feature_id: 'F08', profile_id: 'p', status: 'Built in', assessment_state: 'reviewed', supported_scope: EVIL, unsupported_scope: [EVIL],
  unestablished_scope: [], required_setup: EVIL, activation_state: 'default', control_mechanism: 'enforced', constraints: [EVIL],
  gap_reason: EVIL, evidence_refs: ['E01', 'E02'], limitations: 'lim', assessment_date: '2026-10-21', cell_sha256: 'h',
  author: { recorded: true }, review: { decision: 'agree', independent: true, stale: false, reviewed_at: '2026-11-01' },
};
const evidence = [
  { id: 'E01', url: 'javascript:alert(1)', quote: EVIL, quotation_matched: true, page_title: EVIL, section: EVIL },
  { id: 'E02', url: 'https://example.invalid/x', quote: 'ok', quotation_matched: false },
];
const ix = buildIndex({ catalog: { features: [feature], statuses: [{ name: 'Built in', meaning: 'm' }] }, profiles: [profile], cells: [cell], evidence });

test('markup in data is rendered as text, never as elements', () => {
  const tree = detail(ix, profile, feature, cell, false);
  assert.equal(tree.all().some((e) => ['img', 'script'].includes(e.tag)), false);
  assert.ok(tree.textContent.includes(EVIL));
  const card = profileCard(profile);
  assert.equal(card.all().some((e) => ['img', 'script'].includes(e.tag)), false);
});

test('unsafe URLs are not linked; https URLs are, with noopener', () => {
  const bad = evidenceItem(evidence[0]);
  assert.equal(bad.all().some((e) => e.tag === 'a'), false);
  assert.match(bad.textContent, /Link withheld/);
  const good = evidenceItem(evidence[1]).all().find((e) => e.tag === 'a');
  assert.equal(good.attrs.href, 'https://example.invalid/x');
  assert.match(good.attrs.rel, /noopener/);
  assert.equal(profileCard(profile).all().some((e) => e.tag === 'a'), false);
});

test('evidence shows MATRIX: id and the quotation-matched wording, not "verified"', () => {
  const text = detail(ix, profile, feature, cell, false).textContent;
  assert.match(text, /MATRIX:E01/);
  assert.match(text, /Quotation matched to source/);
  assert.match(text, /Quotation not matched to source/);
  assert.equal(/verified capability/i.test(text), false);
});

test('a pending cell shows a placeholder notice instead of a finding', () => {
  const pending = { ...cell, assessment_state: 'pending', status: 'Not established from documentation' };
  const text = detail(ix, profile, feature, pending, true).textContent;
  assert.match(text, /placeholder, not a finding/);
  assert.equal(text.includes('Documented support'), false);
});

test('h() skips null attributes and ignores falsy children', () => {
  const el = h('div', { class: 'x', id: null, hidden: false }, null, false, 'a', ['b', undefined]);
  assert.equal(el.className, 'x');
  assert.deepEqual(el.attrs, {});
  assert.equal(el.textContent, 'ab');
});

test('h() renders deeply nested child arrays (no "[object Object]")', () => {
  const el = h('div', {}, [[h('b', {}, 'x'), [h('i', {}, 'y')]], 'z']);
  assert.equal(el.textContent, 'xyz');
});

test('the detail panel renders evidence and review lines as elements', () => {
  const text = detail(ix, profile, feature, cell, false).textContent;
  assert.equal(text.includes('[object Object]'), false);
  assert.match(text, /Independently reviewed/);
  assert.match(text, /Documentation gap or conflict/);
});


test('shortlist preserves grouped controls, documentary reasons, safe text and exact cell links', async () => {
  const { shortlist } = await import('../../../../dashboard/feature-matrix/shortlist.mjs');
  const profileWithTier = { ...profile, account_and_tier: 'Recorded tier' };
  const data = { catalog: { features: [feature], statuses: [] }, profiles: [profileWithTier], cells: [{ ...cell, evidence_refs: ['E01'] }], evidence };
  const state = { tiers: new Set(['p']), features: new Set(['F08']), sort: 'group' };
  const tree = shortlist(buildIndex(data), () => {}, state, () => {},
    (p, f) => '?profile=' + p + '&feature=' + f);
  assert.equal(tree.all().some((e) => ['img', 'script'].includes(e.tag)), false);
  assert.ok(tree.textContent.includes(EVIL));
  assert.match(tree.textContent, /Documented gap/);
  const fieldsets = tree.all().filter((e) => e.tag === 'fieldset');
  assert.equal(fieldsets.length, 2);
  const checked = tree.all().filter((e) => e.tag === 'input' && 'checked' in e.attrs);
  assert.equal(checked.length, 2);
  const links = tree.all().filter((e) => e.tag === 'a');
  assert.equal(links.length, 1);
  assert.equal(links[0].attrs.href, '?profile=p&feature=F08');
});
