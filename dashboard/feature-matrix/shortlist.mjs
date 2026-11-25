// Tier IDs are profile-scoped. Each outcome applies to a single profile, tier and feature.
import { h, clear } from './dom.mjs';

import { groups, groupOrder, recordedTier, shortlistRows } from './shortlist-logic.mjs';
export { shortlistRows } from './shortlist-logic.mjs';

function checklist(title, sections, selected, onChange, { searchable = false, defaultLabel = '' } = {}) {
  const summary = h('summary', { class: 'btn' });
  const choices = sections.map(({ label, items }) => ({
    label,
    options: items.map(({ id, name }) => ({
      name,
      el: h('label', {}, h('input', { type: 'checkbox', value: id, checked: selected.has(id), onchange: (event) => {
        if (event.target.checked) selected.add(id);
        else selected.delete(id);
        updateLabel();
        onChange();
      } }), ' ', name),
    })),
  }));
  const sectionsEl = choices.map(({ label, options }) =>
    h('fieldset', {}, h('legend', {}, label), options.map(({ el }) => el)));
  function updateLabel() {
    summary.textContent = title + (selected.size ? ' (' + selected.size + ')' : defaultLabel);
  }
  updateLabel();
  const picker = h('details', { class: 'shortlist-picker', onkeydown: (event) => {
    if (event.key === 'Escape') { picker.open = false; summary.focus(); }
  } }, summary,
    searchable ? h('input', { type: 'search', placeholder: 'Search features', 'aria-label': 'Search required features',
      oninput: (event) => {
        const query = event.target.value.trim().toLowerCase();
        choices.forEach(({ label, options }, index) => {
          options.forEach(({ name, el }) => { el.hidden = !(label + ' ' + name).toLowerCase().includes(query); });
          sectionsEl[index].hidden = options.every(({ el }) => el.hidden);
        });
      } }) : null,
    sectionsEl.length ? sectionsEl : h('p', { class: 'small' }, 'Tier eligibility has yet to be recorded in this dataset.'));
  return picker;
}

export function shortlist(ix, onEvidence, state, onChange, cellUrl) {
  const tierKeys = state.tiers;
  const featureIds = state.features;
  const changed = () => { state.sort = sort.value; onChange(); draw(); };
  const results = h('div');
  const selected = h('p', { class: 'small' });
  const count = h('p', { class: 'count', role: 'status' });
  const sort = h('select', { 'aria-label': 'Sort candidates', onchange: changed },
    h('option', { value: 'group' }, 'Match group'), h('option', { value: 'name' }, 'Tool name'));
  const tierSections = [...new Set(ix.profiles.map((p) => p.tool))].map((tool) => ({
    label: tool, items: ix.profiles.filter((p) => p.tool === tool).map((profile) => ({
      id: profile.id, name: (recordedTier(profile)?.label || 'Tier not established') + ' · ' + profile.surface_label + ' · ' + profile.id,
    })),
  }));
  const featureSections = ix.areas.map((area) => ({
    label: area, items: ix.features.filter((feature) => feature.area === area)
      .map((feature) => ({ id: feature.id, name: feature.id + ' ' + feature.name })),
  }));

  function resultCard(row) {
    const { profile, tier, requirements, state } = row;
    const ordered = requirements.slice().sort((a, b) => groupOrder.indexOf(b.state) - groupOrder.indexOf(a.state));
    const first = ordered[0];
    return h('details', { class: 'card shortlist-result' },
      h('summary', {}, h('strong', {}, profile.tool), ' · ', profile.surface_label, ' · ', tier?.label || 'Tier not established',
        ' · ', h('span', { class: 'shortlist-' + state }, groups[state]),
        h('span', { class: 'small shortlist-reason' }, first.feature.name + ' · ' + first.reason)),
      h('ul', {}, ordered.map(({ feature, state: outcome, reason }) =>
        h('li', {}, h('strong', {}, feature.name), ' · ', groups[outcome], '. ', reason, ' ',
          h('a', { class: 'btn', href: cellUrl(profile.id, feature.id), 'data-profile': profile.id, 'data-feature': feature.id, onclick: (event) => {
            if (event.button === 0 && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey) {
              event.preventDefault(); onEvidence(profile.id, feature.id);
            }
          } }, 'View matrix cell')))));
  }

  function draw() {
    const chosenFeatures = ix.features.filter((feature) => featureIds.has(feature.id));
    selected.textContent = chosenFeatures.length
      ? 'Required · ' + chosenFeatures.map((feature) => feature.name).join(' · ')
      : 'Select at least one required feature to compare profiles.';
    const rows = shortlistRows(ix, tierKeys, featureIds).sort((a, b) =>
      a.profile.tool.localeCompare(b.profile.tool) || (a.tier?.label || '').localeCompare(b.tier?.label || ''));
    count.textContent = chosenFeatures.length
      ? rows.filter((row) => row.state === 'match').length + ' of ' + rows.length + ' profile and tier options have documented coverage'
      : '';
    clear(results);
    if (chosenFeatures.length && !rows.length) results.append(h('p', {}, 'No profiles match the selected tier filter.'));
    if (state.sort === 'name') results.append(...rows.map(resultCard));
    else for (const state of groupOrder) {
      const matches = rows.filter((row) => row.state === state);
      if (matches.length) results.append(h('section', {}, h('h3', {}, groups[state]), matches.map(resultCard)));
    }
  }

  const panel = h('div', {},
    h('section', { class: 'card', 'aria-label': 'Client requirements' },
      h('h2', {}, 'Client requirements'),
      h('p', { class: 'small' }, 'A match needs documented coverage of every selected feature on the same profile and recorded tier. Unknown tiers stay visible for verification. Draft findings remain unreviewed; documented availability does not establish effectiveness.'),
      h('div', { class: 'shortlist-filters' },
        checklist('Tool tier', tierSections, tierKeys, changed, { defaultLabel: ' · Any tier' }),
        checklist('Required features', featureSections, featureIds, changed, { searchable: true }),
        h('label', {}, 'Sort ', sort)),
      selected),
    count, results);
  sort.value = state.sort;
  draw();
  return panel;
}
