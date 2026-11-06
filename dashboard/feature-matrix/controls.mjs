// Filter controls. onChange(partial) merges into the filter state; onClear resets it.
import { h } from './dom.mjs';
import { filtersActive } from './matrix-logic.mjs';

function pick(id, label, options, value, onchange) {
  return h('label', {}, label, h('select', { id, onchange: (e) => onchange(e.target.value) },
    h('option', { value: '' }, 'All'), options.map((o) => h('option', { value: o, selected: o === value }, o))));
}

export function controls(ix, f, onChange, onClear) {
  const cat = ix.payload.catalog;
  return h('section', { class: 'card', 'aria-label': 'Filters' }, h('div', { class: 'filters' },
    pick('fArea', 'Feature area', ix.areas, f.area, (v) => onChange({ area: v })),
    pick('fStatus', 'Documentary status', cat.statuses.map((s) => s.name), f.status, (v) => onChange({ status: v })),
    pick('fAct', 'Activation', cat.activation_states, f.activation, (v) => onChange({ activation: v })),
    pick('fCtl', 'Control mechanism', cat.control_mechanisms, f.control, (v) => onChange({ control: v })),
    ix.profiles.length > 1
      ? pick('fProf', 'Profile', ix.profiles.map((p) => p.id), f.profiles[0] || '', (v) => onChange({ profiles: v ? [v] : [] }))
      : null,
    h('label', {}, 'Search', h('input', { id: 'fQ', type: 'search', value: f.q, placeholder: 'Feature, finding, setup…',
      oninput: (e) => onChange({ q: e.target.value }) })),
    h('button', { type: 'button', class: 'btn', disabled: filtersActive(f) ? null : true, onclick: onClear }, 'Clear filters')));
}
