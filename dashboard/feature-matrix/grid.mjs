// The feature x profile grid (wide screens) and the card list (small screens).
import { h } from './dom.mjs';
import { surfaceName } from './profile-scope.mjs';
import { cellLabel, STATUS_LABELS } from './matrix-logic.mjs';
import { badge } from './views.mjs';
import { profileScope, toolName } from './tool-brand.mjs';

function cellButton(ctx, profile, feature, cell, match) {
  const label = cellLabel(cell, ctx.preview);
  const active = ctx.sel.profile === profile.id && ctx.sel.feature === feature.id;
  const dims = cell && cell.assessment_state !== 'pending' && cell.activation_state
    ? h('span', { class: 'small' }, cell.activation_state + ' · ' + cell.control_mechanism) : null;
  return h('button', {
    type: 'button', class: 'cellbtn' + (match ? '' : ' nomatch'), 'aria-current': active ? 'true' : null,
    'aria-label': feature.id + ' ' + feature.name + ', ' + profile.tool + ': ' + label.text + (match ? '' : ' (does not match the current filters)'),
    onclick: () => ctx.select(profile.id, feature.id),
  }, badge({ ...label, text: STATUS_LABELS[label.text] || label.text }), dims);
}

const SURFACE_NAMES = new Map([['cli', 'CLI'], ['app', 'Desktop app']]);

export function grid(ctx, ix, rows, columns) {
  const body = ix.areas.flatMap((area) => {
    const inArea = rows.filter((r) => r.feature.area === area);
    if (!inArea.length) return [];
    return [h('tr', { class: 'area' }, h('th', { scope: 'colgroup', colspan: columns.length + 1 }, area)),
      ...inArea.map((r) => h('tr', {},
        h('th', { scope: 'row' }, h('span', { class: 'fid mono' }, r.feature.id), r.feature.name),
        r.cells.map((c) => h('td', {}, cellButton(ctx, c.profile, r.feature, c.cell, c.match)))))];
  });
  return h('div', { class: 'card tablewrap', tabindex: '0', role: 'region', 'aria-label': 'Feature comparison table' }, h('table', { class: 'matrix' },
    h('caption', { class: 'small' }, 'Feature by profile. Select a cell for its evidence.'),
    h('thead', {}, h('tr', {}, h('th', { scope: 'col' }, 'Feature'),
      columns.map((profile) => {
        const sharesSurface = columns.some((other) => other !== profile && other.surface === profile.surface
          && (other.tool_key || other.tool) === (profile.tool_key || profile.tool));
        const surfaceLabel = sharesSurface ? surfaceName(profile) : SURFACE_NAMES.get(profile.surface) || surfaceName(profile);
        return h('th', { scope: 'col', class: 'tool-column', 'data-tool-brand': profile.tool_key, title: surfaceName(profile) },
          toolName(profile), profileScope(profile, ix.categories, surfaceLabel));
      }))),
    h('tbody', {}, body)));
}

export function cards(ctx, rows, categories) {
  return h('div', { class: 'cards' }, rows.map((r) => h('div', { class: 'card' },
    h('strong', {}, r.feature.id + ' ' + r.feature.name), h('div', { class: 'small' }, r.feature.area),
    r.cells.map((c) => h('div', { class: 'mobile-tool', 'data-tool-brand': c.profile.tool_key },
      toolName(c.profile), profileScope(c.profile, categories),
      cellButton(ctx, c.profile, r.feature, c.cell, c.match))))));
}
