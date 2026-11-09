// Documented capabilities page. Loads data/matrix.json independently of the benchmark data.
import { h, clear } from './dom.mjs';
import { buildIndex, classify, emptyFilters, parseParams, toParams, visibleRows } from './matrix-logic.mjs';
import { controls } from './controls.mjs';
import { cards, grid } from './grid.mjs';
import { detail, legend, profileCard } from './views.mjs';
import { shortlist } from './shortlist.mjs';
import { readShortlist, writeShortlist } from './shortlist-logic.mjs';

const app = document.getElementById('app');

// Theme: same preference key and attribute as the benchmark dashboard.
try { const t = localStorage.getItem('bench-theme'); if (t) document.documentElement.dataset.theme = t; } catch {}
document.getElementById('themeBtn').addEventListener('click', () => {
  const cur = document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  document.documentElement.dataset.theme = cur === 'light' ? 'dark' : 'light';
  try { localStorage.setItem('bench-theme', document.documentElement.dataset.theme); } catch {}
});

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
  let view = initialParams.get('view') === 'shortlist' ? 'shortlist' : 'overview';
  const holder = h('div');
  const overview = h('div', { id: 'overview-panel' },
    h('div', { class: 'profiles' }, ix.profiles.map(profileCard)), legend(ix), holder);
  let shortlistState = readShortlist(location.search);
  const shortlistPanel = h('div', { id: 'shortlist-panel' });
  function drawShortlist() {
    clear(shortlistPanel).append(shortlist(ix, (profile, feature) => {
      view = 'overview'; ctx.select(profile, feature);
    }, shortlistState, () => update(false), cellUrl));
  }
  const overviewButton = viewButton('Overview', 'overview', overview);
  const shortlistButton = viewButton('Shortlist', 'shortlist', shortlistPanel);
  const notice = demo
    ? banner('draft', h('strong', {}, 'Illustrative demo. '), 'The tools, tiers and evidence shown here are fictional.')
    : preview ? banner('draft', h('strong', {}, 'Draft — not accepted. '), 'Local preview of working research. Findings are unreviewed and must not be used as results.') : null;
  clear(app).append(
    ...(notice ? [notice] : []),
    h('nav', { class: 'matrix-tabs', 'aria-label': 'Feature matrix views' }, overviewButton, shortlistButton),
    overview, shortlistPanel,
    h('section', { class: 'card', 'aria-label': 'Method and limitations' }, h('h2', {}, 'Method and limitations'),
      h('ul', {}, ix.payload.limitations.map((l) => h('li', {}, l))),
      h('p', { class: 'small mono' }, 'Release ' + rel.release_id + ' · source commit ' + String(rel.source_commit || 'unknown') + ' · manifest v' + rel.manifest_version)));

  function viewButton(label, target, panel) {
    return h('button', { type: 'button', class: 'btn', 'aria-controls': panel.id, onclick: () => {
      if (view === target) return;
      view = target;
      update(true);
    } }, label);
  }

  function showView() {
    overview.hidden = view !== 'overview';
    shortlistPanel.hidden = view !== 'shortlist';
    overviewButton.setAttribute('aria-pressed', String(!overview.hidden));
    shortlistButton.setAttribute('aria-pressed', String(!shortlistPanel.hidden));
    if (!shortlistPanel.hidden) shortlistPanel.querySelectorAll('a[data-profile]').forEach((a) => {
      a.href = cellUrl(a.dataset.profile, a.dataset.feature);
    });
  }

  function cellUrl(profile, feature) {
    const params = new URLSearchParams(url().split('?')[1] || '');
    params.delete('view'); params.set('profile', profile); params.set('feature', feature);
    return location.pathname + '?' + params + '#detail';
  }

  function url() {
    const params = new URLSearchParams(toParams(ctx.f, ctx.sel));
    if (previewFile) params.set('preview', previewFile);
    writeShortlist(params, shortlistState);
    if (view === 'shortlist') params.set('view', view);
    return location.pathname + (params.size ? '?' + params : '');
  }
  function update(push) {
    history[push ? 'pushState' : 'replaceState'](null, '', url());
    showView();
    if (view === 'overview') draw();
  }
  ctx.select = (profile, feature) => { ctx.sel = { profile, feature }; update(true); document.getElementById('detail')?.focus(); };

  function draw() {
    const typing = document.activeElement && document.activeElement.id === 'fQ';
    const caret = typing ? document.activeElement.selectionStart : 0;
    const { rows, columns, total } = visibleRows(ix, ctx.f);
    const p = ix.profiles.find((x) => x.id === ctx.sel.profile);
    const f = ix.features.find((x) => x.id === ctx.sel.feature);
    clear(holder).append(
      controls(ix, ctx.f, (part) => { ctx.f = { ...ctx.f, ...part }; update(false); }, () => { ctx.f = emptyFilters(); update(false); }),
      h('p', { class: 'count', role: 'status' }, 'Showing ' + rows.length + ' of ' + total + ' features'),
      ...(rows.length ? [grid(ctx, ix, rows, columns), cards(ctx, rows)]
        : [h('p', { class: 'muted' }, 'No features match these filters.')]));
    if (p && f) holder.append(detail(ix, p, f, ix.cells.get(p.id + '/' + f.id) || null, preview));
    if (typing) { const q = document.getElementById('fQ'); q.focus(); q.setSelectionRange(caret, caret); }
  }

  window.addEventListener('popstate', () => {
    const s = parseParams(location.search);
    ctx.f = s.filters;
    ctx.sel = { profile: s.profile, feature: s.feature };
    view = new URLSearchParams(location.search).get('view') === 'shortlist' ? 'shortlist' : 'overview';
    shortlistState = readShortlist(location.search);
    drawShortlist();
    showView();
    if (view === 'overview') draw();
  });
  drawShortlist();
  showView();
  if (view === 'overview') draw();
}

(async function main() {
  const result = await load();
  if (result.kind === 'empty') {
    clear(app).append(banner('empty', h('strong', {}, result.message)),
      h('p', { class: 'muted' }, 'Documented-capability findings appear here once a profile has been assessed and independently reviewed. Benchmark results are on the ', h('a', { href: '../' }, 'dashboard'), '.'));
  } else if (result.kind === 'error') {
    clear(app).append(banner('error', h('strong', {}, 'The documented capabilities could not be shown. '), result.message));
  } else {
    render(buildIndex(result.payload), result.preview, result.demo);
  }
})();
