// Page sections. Every string from the data goes through h(), which creates text nodes only.
import { h } from './dom.mjs';
import { STATUSES, cellLabel, evidenceLabel, matchLabel, reviewLines, safeHref } from './matrix-logic.mjs';

import { profileScope, toolName } from './tool-brand.mjs';
import { accountScope, scopeWording } from './profile-scope.mjs';

const MARK = { 'built-in': '✓', config: '＋', custom: '</>', unavailable: '✕', ne: '?', pending: '…' };
const list = (items) => (items && items.length ? h('ul', {}, items.map((i) => h('li', {}, i))) : h('p', { class: 'muted' }, 'None recorded.'));

export function badge(label) {
  return h('span', { class: 'badge tone-' + label.tone }, MARK[label.tone] + ' ' + label.text);
}

export function profileCard(p, categories) {
  const v = p.version || {};
  const rows = [
    ['Version scope', v.value || v.documentation_note || 'Not stated'],
    ['Modes', (p.modes || []).join(', ')], ['Operating systems', (p.platforms || []).join(', ')],
    ['Account and tier scope', accountScope(p)], ['Documentation accessed', p.source_access_date],
  ];
  const href = safeHref(p.documentation_base);
  return h('div', { class: 'profile', 'data-profile': p.id },
    h('div', { class: 'profile-line' }, profileScope(p, categories), v.value ? h('span', { class: 'small' }, v.value) : null),
    h('details', {}, h('summary', {}, 'Profile details'),
      h('dl', { class: 'kv' }, rows.map(([k, val]) => [h('dt', {}, k), h('dd', {}, val || 'Not stated')])),
      h('h3', {}, 'Excluded from this profile'), list(p.exclusions),
      href ? h('p', { class: 'small' }, 'Documentation: ', h('a', { href, rel: 'noopener noreferrer', target: '_blank' }, href)) : null));
}

export function profileGroups(profiles, categories) {
  const families = new Map();
  for (const p of profiles) {
    const key = p.tool_key || p.tool;
    if (!families.has(key)) families.set(key, []);
    families.get(key).push(p);
  }
  return [...families].map(([key, group]) => h('section', { class: 'card tool-family', 'data-tool-key': key, 'data-tool-brand': group[0].tool_key },
    h('h2', {}, toolName(group[0])), group.map((profile) => profileCard(profile, categories))));
}

export function legend(ix) {
  return h('details', { class: 'status-legend', 'aria-label': 'Status meanings' },
    h('summary', {}, 'What the statuses mean'),
    h('ul', { class: 'legend' }, STATUSES.map((name) =>
      h('li', {}, badge(cellLabel({ status: name, assessment_state: 'reviewed' }, false)), h('div', { class: 'small' }, ix.meaning.get(name) || '')))),
    h('p', { class: 'small' }, 'Documented availability does not establish effectiveness. Statuses are not a ranking and are never added up.'));
}

export function evidenceItem(e) {
  const href = safeHref(e.url);
  return h('div', { class: 'evidence' },
    h('div', {}, h('strong', {}, evidenceLabel(e.id)), ' · ', e.page_title || 'Untitled page', e.section ? ' · section: ' + e.section : ''),
    h('blockquote', {}, e.quote || ''),
    h('div', { class: 'small' }, matchLabel(e), ' · accessed ', e.access_date || 'unknown', ' · scope: ', e.surface || 'unknown'),
    e.claim_summary ? h('div', { class: 'small' }, 'Supports: ', e.claim_summary) : null,
    href ? h('a', { href, rel: 'noopener noreferrer', target: '_blank' }, href) : h('span', { class: 'small' }, 'Link withheld: not a secure https address'),
    e.page_sha256 ? h('div', { class: 'small mono' }, 'Page SHA-256 ' + e.page_sha256) : null);
}

export function detail(ix, profile, feature, cell, preview) {
  const label = cellLabel(cell, preview);
  const body = [
    h('h2', {}, h('span', { class: 'fid mono' }, feature.id), feature.name),
    h('div', { class: 'detail-tool', 'data-tool-brand': profile.tool_key }, toolName(profile), profileScope(profile, ix.categories)),
    h('p', {}, badge(label), label.workflow ? h('span', { class: 'small' }, '  ' + label.workflow) : null)];
  if (!cell || cell.assessment_state === 'pending' || cell.assessment_state === 'missing') {
    body.push(h('p', {}, 'Research for this cell has not been completed. This is a placeholder, not a finding.'));
    return h('section', { class: 'card detail', id: 'detail', tabindex: '-1', 'aria-label': 'Cell details' }, body);
  }
  body.push(h('h3', {}, 'Finding'), h('p', {}, cell.supported_scope),
    h('h3', {}, 'Required setup and dependencies'), h('p', {}, scopeWording(profile, cell.required_setup) || 'None recorded.'),
    h('details', {}, h('summary', {}, 'Scope and constraints'),
    h('p', {}, feature.capability), h('p', { class: 'small' }, 'What was examined: ' + feature.examine),
    h('h3', {}, 'Explicitly unsupported'), list(cell.unsupported_scope),
    h('h3', {}, 'Not established'), list(cell.unestablished_scope),
    cell.gap_reason ? [h('h3', {}, 'Documentation gap or conflict'), h('p', {}, cell.gap_reason)] : null,
    h('p', { class: 'small' }, 'Profile exclusions: ' + ((profile.exclusions || []).join('; ') || 'none listed')),
    h('h3', {}, 'Activation and control'),
    h('p', {}, 'Activation: ' + cell.activation_state + ' · Control mechanism: ' + cell.control_mechanism),
    h('h3', {}, 'Constraints'), list(cell.constraints?.map((text) => scopeWording(profile, text)))),
    h('details', {}, h('summary', {}, 'Documentation evidence'), (cell.evidence_refs || []).map((r) => {
      const e = ix.evidence.get(r);
      return e ? evidenceItem(e) : h('p', { class: 'small' }, evidenceLabel(r) + ' is not in this data file.');
    })),
    h('details', {}, h('summary', {}, 'Authorship and review metadata'), reviewLines(cell).map((l) => h('p', {}, l)),
    h('p', { class: 'small' }, 'Assessed ' + (cell.assessment_date || 'date not recorded') + ' · ' + cell.limitations),
    h('p', { class: 'small mono' }, 'Cell SHA-256 ' + cell.cell_sha256)));
  return h('section', { class: 'card detail', id: 'detail', tabindex: '-1', 'aria-label': 'Cell details' }, body);
}
