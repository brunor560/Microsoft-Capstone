// Filter controls. onChange(partial) merges into the filter state; onClear resets it.
import { h } from './dom.mjs';
import { STATUSES, filtersActive } from './matrix-logic.mjs';
import { recordedTier } from './shortlist-logic.mjs';

function pick(id, label, options, value, onchange) {
  return h('label', {}, label, h('select', { id, onchange: (e) => onchange(e.target.value) },
    h('option', { value: '' }, 'All'), options.map((o) => h('option', { value: o.value ?? o, selected: (o.value ?? o) === value }, o.label ?? o))));
}

export function controls(ix, f, onChange, onClear) {
  const cat = ix.payload.catalog;
  return h('section', { class: 'card', 'aria-label': 'Filters' }, h('div', { class: 'filters' },
    pick('fArea', 'Feature group', ix.areas, f.area, (v) => onChange({ area: v })),
    pick('fStatus', 'Status', STATUSES, f.status, (v) => onChange({ status: v })),
    pick('fProf', 'Tool tier', ix.profiles.map((p) => ({ value: p.id, label: p.tool + ' · ' + p.surface_label + ' · ' + (recordedTier(p)?.label || 'Tier not established') })), f.profiles[0] || '', (v) => onChange({ profiles: v ? [v] : [] })),
    h('label', {}, 'Search', h('input', { id: 'fQ', type: 'search', value: f.q, placeholder: 'Feature, finding, setup…',
      oninput: (e) => onChange({ q: e.target.value }) })),
    h('button', { type: 'button', class: 'btn', disabled: filtersActive(f) ? null : true, onclick: onClear }, 'Clear filters')),
    h('details', { open: f.activation || f.control ? true : null }, h('summary', {}, 'More filters'), h('div', { class: 'filters' },
      pick('fAct', 'Activation', cat.activation_states || [], f.activation, (v) => onChange({ activation: v })),
      pick('fCtl', 'Control mechanism', cat.control_mechanisms || [], f.control, (v) => onChange({ control: v })))));
}
