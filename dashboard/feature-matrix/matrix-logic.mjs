// Pure logic for the documented-capabilities page (no DOM access), so it can be tested under Node.
// Data contract: approach-a/publication/1 (see tools/approach_a/publish.py and pubcheck.py).
export const SCHEMA = 'approach-a/publication/1';
export const EMPTY_SCHEMA = 'approach-a/publication-empty/1';
export const EMPTY_MESSAGE = 'No reviewed assessment published yet.';

export function safeHref(url) {
  try {
    const u = new URL(url);
    return u.protocol === 'https:' && u.host ? u.href : null;
  } catch { return null; }
}

const fail = (message) => ({ kind: 'error', message });

// Decide what the page can show for a parsed data file: the deliberate empty state, data, or an error.
// A preview payload is only accepted when allowPreview is set (local use); it is never shown as published.
export function classify(obj, { allowPreview = false } = {}) {
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return fail('The data file is not a JSON object.');
  if (obj.schema === EMPTY_SCHEMA) return { kind: 'empty', message: EMPTY_MESSAGE };
  if (obj.schema !== SCHEMA) return fail('Unsupported data version: ' + String(obj.schema));
  const ok = obj.release && obj.catalog && Array.isArray(obj.catalog.features) && Array.isArray(obj.catalog.statuses)
    && Array.isArray(obj.profiles) && Array.isArray(obj.cells) && Array.isArray(obj.evidence);
  if (!ok) return fail('The data file is incomplete (release, catalog, profiles, cells or evidence is missing).');
  const mode = obj.release.publication_mode;
  if (mode !== 'accepted' && mode !== 'preview') return fail('Unknown publication mode: ' + String(mode));
  if (mode === 'preview' && !allowPreview) return fail('This file is a draft preview and cannot be shown as published.');
  if (!obj.profiles.length) return fail('The data file lists no profiles.');
  return { kind: 'data', payload: obj, preview: mode === 'preview' };
}

export function buildIndex(payload) {
  const cells = new Map(payload.cells.map((c) => [c.profile_id + '/' + c.feature_id, c]));
  const evidence = new Map(payload.evidence.map((e) => [e.id, e]));
  const areas = [...new Set(payload.catalog.features.map((f) => f.area))];
  const meaning = new Map(payload.catalog.statuses.map((s) => [s.name, s.meaning]));
  return { payload, cells, evidence, areas, meaning, features: payload.catalog.features, profiles: payload.profiles };
}

export const emptyFilters = () => ({ profiles: [], area: '', status: '', activation: '', control: '', q: '' });
export const filtersActive = (f) => !!(f.profiles.length || f.area || f.status || f.activation || f.control || f.q);

function haystack(cell, feature) {
  return [feature.name, feature.capability, cell.status, cell.supported_scope, cell.required_setup, cell.gap_reason,
    ...(cell.unsupported_scope || []), ...(cell.unestablished_scope || []), ...(cell.constraints || [])]
    .filter(Boolean).join(' \n ').toLowerCase();
}

export function cellMatches(cell, feature, f) {
  if (!cell) return !(f.status || f.activation || f.control || f.q);
  if (f.status && cell.status !== f.status) return false;
  if (f.activation && cell.activation_state !== f.activation) return false;
  if (f.control && cell.control_mechanism !== f.control) return false;
  if (f.q && !haystack(cell, feature).includes(f.q.trim().toLowerCase())) return false;
  return true;
}

// A feature row is shown when any selected profile matches. Other selected columns stay visible, marked
// as non-matching, so a comparison never hides individual cells and implies that research is missing.
export function visibleRows(ix, f) {
  const selected = ix.profiles.filter((p) => !f.profiles.length || f.profiles.includes(p.id));
  const rows = [];
  for (const feature of ix.features) {
    if (f.area && feature.area !== f.area) continue;
    const cells = selected.map((p) => {
      const cell = ix.cells.get(p.id + '/' + feature.id) || null;
      return { profile: p, cell, match: cellMatches(cell, feature, f) };
    });
    if (cells.some((c) => c.match)) rows.push({ feature, cells });
  }
  return { rows, columns: selected, total: ix.features.length };
}

const TONES = {
  'Built in': 'built-in', 'Configuration or extension required': 'config', 'Custom implementation required': 'custom',
  'Unavailable': 'unavailable', 'Not established from documentation': 'ne',
};
const WORKFLOW = {
  pending: 'Draft: research pending (placeholder, not a finding)', drafted: 'Draft: not reviewed',
  challenged: 'Draft: awaiting independent review', reviewed: 'Reviewed', missing: 'Draft: cell missing',
};

// The status shown for a cell. Pending research is never displayed as a "Not established" finding.
export function cellLabel(cell, preview) {
  if (!cell || cell.assessment_state === 'missing') return { text: 'Cell missing', tone: 'pending', workflow: WORKFLOW.missing };
  if (cell.assessment_state === 'pending') return { text: 'Research pending', tone: 'pending', workflow: WORKFLOW.pending };
  return { text: cell.status, tone: TONES[cell.status] || 'ne', workflow: preview ? (WORKFLOW[cell.assessment_state] || null) : null };
}

export function reviewLines(cell) {
  const lines = [cell.author && cell.author.recorded ? 'A named team member is responsible for this finding.' : 'No responsible author recorded yet.'];
  const r = cell.review;
  if (!r) lines.push('No independent review recorded.');
  else if (r.stale) lines.push('The cell changed after its review; the review is out of date.');
  else if (r.decision === 'agree' && r.independent) lines.push('Independently reviewed (agreed) on ' + String(r.reviewed_at).slice(0, 10) + '.');
  else lines.push('Review recorded (' + r.decision + (r.independent ? '' : ', not independent') + ') on ' + String(r.reviewed_at).slice(0, 10) + '.');
  return lines;
}

export const evidenceLabel = (id) => 'MATRIX:' + id;
export const matchLabel = (e) => (e.quotation_matched ? 'Quotation matched to source' : 'Quotation not matched to source');

export function parseParams(search) {
  const p = new URLSearchParams(search);
  const f = emptyFilters();
  f.profiles = (p.get('profiles') || '').split(',').filter(Boolean);
  for (const k of ['area', 'status', 'activation', 'control', 'q']) f[k] = p.get(k) || '';
  return { filters: f, profile: p.get('profile') || '', feature: p.get('feature') || '' };
}

export function toParams(f, sel) {
  const p = new URLSearchParams();
  if (f.profiles.length) p.set('profiles', f.profiles.join(','));
  for (const k of ['area', 'status', 'activation', 'control', 'q']) if (f[k]) p.set(k, f[k]);
  if (sel && sel.profile && sel.feature) { p.set('profile', sel.profile); p.set('feature', sel.feature); }
  const s = p.toString();
  return s ? '?' + s : '';
}

