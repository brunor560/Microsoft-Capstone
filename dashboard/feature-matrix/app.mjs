// Documented capabilities page. Loads data/matrix.json independently of the benchmark data.
import { h, clear } from './dom.mjs';
import { buildIndex, classify, emptyFilters, parseParams, toParams, visibleRows } from './matrix-logic.mjs';
import { controls } from './controls.mjs';
import { cards, grid } from './grid.mjs';
import { detail, legend, profileGroups } from './views.mjs';
import { shortlist } from './shortlist.mjs';
import { readShortlist, writeShortlist } from './shortlist-logic.mjs';

const app = document.getElementById('app');

const banner = (kind, ...kids) => h('div', { class: 'banner ' + kind, role: kind === 'error' ? 'alert' : null }, kids);

// A draft preview loads only from a local server and only when asked for with ?preview=<file in data/>.
// Published pages always read data/matrix.json, and classify() refuses a preview payload without allowPreview.
const isLocal = ['localhost', '127.0.0.1', '[::1]', '::1'].includes(location.hostname);
function dataSource() {
  const want = new URLSearchParams(location.search).get('preview');
  return want && isLocal && /^[\w.-]+\.json$/.test(want)
    ? { url: 'data/' + want, allowPreview: true } : { url: 'data/matrix.json', allowPreview: false };
}

async function load() {
  const { url, allowPreview } = dataSource();
  let res;
  try { res = await fetch(url, { cache: 'no-store' }); } catch { return { kind: 'error', message: 'The data file could not be loaded (network error).' }; }
  if (!res.ok) return { kind: 'error', message: 'The data file could not be loaded (HTTP ' + res.status + ').' };
  let obj;
  try { obj = await res.json(); } catch { return { kind: 'error', message: 'The data file is not valid JSON.' }; }
  return { ...classify(obj, { allowPreview }), demo: allowPreview && obj?.release?.release_id === 'shortlist-demo' };
}

function render(ix, preview, demo) {
  const rel = ix.payload.release;
  const initialParams = new URLSearchParams(location.search);
  const previewFile = preview ? initialParams.get('preview') : null;
  const init = parseParams(location.search);
  const ctx = { preview, f: init.filters, sel: { profile: init.profile, feature: init.feature }, select: null };
  const readView = () => {
    const requested = new URLSearchParams(location.search).get('view');
    if (requested === 'overview' || requested === 'profiles') return 'profiles';
    return requested === 'shortlist' ? 'shortlist' : 'compare';
  };
  let view = readView();
  const holder = h('div');
  const profilesPanel = h('div', { id: 'profiles-panel' },
    h('div', { class: 'profiles' }, profileGroups(ix.profiles, ix.categories)));
  const comparePanel = h('div', { id: 'compare-panel' }, holder);
  const statusLegend = legend(ix);
  let shortlistState = readShortlist(location.search);
  const shortlistPanel = h('div', { id: 'shortlist-panel' });
  function drawShortlist() {
    clear(shortlistPanel).append(shortlist(ix, (profile, feature) => {
      view = 'compare'; ctx.select(profile, feature);
    }, shortlistState, () => update(false), cellUrl));
  }
  const panels = { profiles: profilesPanel, compare: comparePanel, shortlist: shortlistPanel };
  const sectionHeader = h('h2', { class: 'matrix-section-title', tabindex: '-1' });
  const menuButton = document.getElementById('menuBtn');
  const sectionTemplate = document.getElementById('matrix-sections');
  const sectionButtons = [];
  for (const label of document.querySelectorAll('[data-sections]')) {
    const items = sectionTemplate.content.cloneNode(true);
    const inMenu = Boolean(label.closest('#menu'));
    for (const button of items.querySelectorAll('[data-view]')) {
      if (inMenu) button.setAttribute('role', 'menuitem');
      button.addEventListener('click', () => {
        if (view !== button.dataset.view) {
          view = button.dataset.view;
          update(true);
          window.scrollTo(0, 0);
        }
        if (inMenu) sectionHeader.focus({ preventScroll: true });
      });
      sectionButtons.push(button);
    }
    label.after(items);
    label.hidden = false;
  }
  menuButton.setAttribute('aria-label', 'Dashboards and sections');
  menuButton.title = 'Dashboards and sections';
  const notice = demo
    ? banner('draft', h('strong', {}, 'Illustrative demo. '), 'The tools, tiers and evidence shown here are fictional.')
    : preview ? banner('draft', h('strong', {}, 'Draft — not accepted. '), 'Local preview of working research. Findings are unreviewed and must not be used as results.') : null;
  clear(app).append(
    ...(notice ? [notice] : []),
    sectionHeader, profilesPanel, comparePanel, shortlistPanel,
    h('details', { class: 'card', 'aria-label': 'Method and limitations' }, h('summary', {}, 'Method and limitations'),
      h('ul', {}, ix.payload.limitations.map((l) => h('li', {}, l))),
      h('p', { class: 'small mono' }, 'Release ' + rel.release_id + ' · source commit ' + String(rel.source_commit || 'unknown') + ' · manifest v' + rel.manifest_version)));

  function showView() {
    for (const [name, panel] of Object.entries(panels)) panel.hidden = name !== view;
    const title = sectionButtons.find((button) => button.dataset.view === view).textContent.trim();
    if (sectionHeader.textContent !== title) sectionHeader.textContent = title;
    for (const button of sectionButtons) button.setAttribute('aria-current', String(button.dataset.view === view));
    if (view === 'shortlist') shortlistPanel.querySelectorAll('a[data-profile]').forEach((a) => {
      a.href = cellUrl(a.dataset.profile, a.dataset.feature);
    });
  }

  function cellUrl(profile, feature) {
    const params = new URLSearchParams(url().split('?')[1] || '');
    params.set('view', 'compare'); params.set('profile', profile); params.set('feature', feature);
    return location.pathname + '?' + params + '#detail';
  }

  function url() {
    const params = new URLSearchParams(toParams(ctx.f, ctx.sel));
    if (previewFile) params.set('preview', previewFile);
    writeShortlist(params, shortlistState);
    params.set('view', view);
    return location.pathname + (params.size ? '?' + params : '');
  }
  function update(push) {
    history[push ? 'pushState' : 'replaceState'](null, '', url());
    showView();
    if (view === 'compare') draw();
  }
  ctx.select = (profile, feature) => { view = 'compare'; ctx.sel = { profile, feature }; update(true); document.getElementById('detail')?.focus(); };

  function draw() {
    const typing = document.activeElement && document.activeElement.id === 'fQ';
    const caret = typing ? document.activeElement.selectionStart : 0;
    const { rows, columns, total } = visibleRows(ix, ctx.f);
    const p = ix.profiles.find((x) => x.id === ctx.sel.profile);
    const f = ix.features.find((x) => x.id === ctx.sel.feature);
    clear(holder).append(
      controls(ix, ctx.f, (part) => { ctx.f = { ...ctx.f, ...part }; update(false); }, () => { ctx.f = emptyFilters(); update(false); }),
      h('div', { class: 'compare-meta' },
        h('p', { class: 'count', role: 'status' }, 'Showing ' + rows.length + ' of ' + total + ' features'), statusLegend),
      ...(rows.length ? [grid(ctx, ix, rows, columns), cards(ctx, rows, ix.categories)]
        : [h('p', { class: 'muted' }, 'No features match these filters.')]));
    if (p && f) holder.append(detail(ix, p, f, ix.cells.get(p.id + '/' + f.id) || null, preview));
    if (typing) { const q = document.getElementById('fQ'); q.focus(); q.setSelectionRange(caret, caret); }
  }

  window.addEventListener('popstate', () => {
    const s = parseParams(location.search);
    ctx.f = s.filters;
    ctx.sel = { profile: s.profile, feature: s.feature };
    view = readView();
    shortlistState = readShortlist(location.search);
    drawShortlist();
    showView();
    if (view === 'compare') draw();
  });
  drawShortlist();
  showView();
  if (view === 'compare') {
    draw();
    if (location.hash === '#detail') document.getElementById('detail')?.scrollIntoView();
  }
}

(async function main() {
  const result = await load();
  if (result.kind === 'empty') {
    clear(app).append(h('section', { class: 'card empty' },
      h('h2', {}, result.message),
      h('p', { class: 'muted' }, 'Findings appear here once a tool profile has been assessed and independently reviewed.')));
  } else if (result.kind === 'error') {
    clear(app).append(banner('error', h('strong', {}, 'The documented capabilities could not be shown. '), result.message));
  } else {
    render(buildIndex(result.payload), result.preview, result.demo);
  }
})();
