// Documented capabilities page. Loads data/matrix.json independently of the benchmark data.
import { h, clear } from './dom.mjs';
import { buildIndex, classify, emptyFilters, parseParams, toParams, visibleRows } from './matrix-logic.mjs';
import { controls } from './controls.mjs';
import { cards, grid } from './grid.mjs';
import { detail, legend, profileCard } from './views.mjs';

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
  return classify(obj, { allowPreview });
}

function render(ix, preview) {
  const rel = ix.payload.release;
  const keepParams = () => (preview ? '&preview=' + encodeURIComponent(new URLSearchParams(location.search).get('preview')) : '');
  const init = parseParams(location.search);
  const ctx = { preview, f: init.filters, sel: { profile: init.profile, feature: init.feature }, select: null };
  const holder = h('div');
  clear(app).append(
    ...(preview ? [banner('draft', h('strong', {}, 'Draft — not accepted. '), 'Local preview of working research. Findings are unreviewed and must not be used as results.')] : []),
    h('div', { class: 'profiles' }, ix.profiles.map(profileCard)), legend(ix), holder,
    h('section', { class: 'card', 'aria-label': 'Method and limitations' }, h('h2', {}, 'Method and limitations'),
      h('ul', {}, ix.payload.limitations.map((l) => h('li', {}, l))),
      h('p', { class: 'small mono' }, 'Release ' + rel.release_id + ' · source commit ' + String(rel.source_commit || 'unknown') + ' · manifest v' + rel.manifest_version)));

  function url() {
    const q = toParams(ctx.f, ctx.sel);
    const extra = keepParams();
    return location.pathname + (q ? q + extra : extra ? '?' + extra.slice(1) : '');
  }
  function update(push) { history[push ? 'pushState' : 'replaceState'](null, '', url()); draw(); }
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
      rows.length ? [grid(ctx, ix, rows, columns), cards(ctx, rows)] : h('p', { class: 'muted' }, 'No features match these filters.'),
      p && f ? detail(ix, p, f, ix.cells.get(p.id + '/' + f.id) || null, preview) : null);
    if (typing) { const q = document.getElementById('fQ'); q.focus(); q.setSelectionRange(caret, caret); }
  }

  window.addEventListener('popstate', () => {
    const s = parseParams(location.search);
    ctx.f = s.filters; ctx.sel = { profile: s.profile, feature: s.feature }; draw();
  });
  draw();
}

(async function main() {
  const result = await load();
  if (result.kind === 'empty') {
    clear(app).append(banner('empty', h('strong', {}, result.message)),
      h('p', { class: 'muted' }, 'Documented-capability findings appear here once a profile has been assessed and independently reviewed. Benchmark results are on the ', h('a', { href: '../' }, 'dashboard'), '.'));
  } else if (result.kind === 'error') {
    clear(app).append(banner('error', h('strong', {}, 'The documented capabilities could not be shown. '), result.message));
  } else {
    render(buildIndex(result.payload), result.preview);
  }
})();
