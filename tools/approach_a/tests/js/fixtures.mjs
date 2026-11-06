// Synthetic payload for page tests. Test data, not findings. Kept outside dashboard/ because that directory is deployed.
export const STATUSES = ['Built in', 'Configuration or extension required', 'Custom implementation required', 'Unavailable', 'Not established from documentation'];

export function cell(profile, feature, over = {}) {
  return {
    feature_id: feature, profile_id: profile, status: 'Built in', assessment_state: 'reviewed', supported_scope: 'Supported thing',
    unsupported_scope: [], unestablished_scope: [], required_setup: 'None', activation_state: 'default', evidence_basis: 'documented_support',
    evidence_refs: ['E01'], gap_reason: null, control_mechanism: 'enforced', constraints: [], limitations: 'Documentation-only',
    assessment_date: '2026-10-21', cell_sha256: 'abc', author: { recorded: true },
    review: { decision: 'agree', disposition: null, reviewed_at: '2026-11-01T10:00:00+00:00', cell_sha256: 'abc', stale: false, independent: true },
    ...over,
  };
}

export function payload(mode = 'accepted') {
  const features = ['F01', 'F02', 'F03'].map((id, i) => ({ id, area: i < 2 ? 'Planning' : 'Development', name: 'Feature ' + id, capability: 'cap', examine: 'ex' }));
  const profiles = ['p-one', 'p-two'].map((id) => ({ id, tool: 'Tool ' + id, surface_label: 'CLI', exclusions: ['IDE'], version: { value: '1' } }));
  const cells = [];
  for (const p of profiles) for (const f of features) cells.push(cell(p.id, f.id));
  cells[1] = cell('p-one', 'F02', { status: 'Not established from documentation', evidence_basis: 'documentation_gap', gap_reason: 'Sources are silent', activation_state: 'not established' });
  cells[2] = cell('p-one', 'F03', { assessment_state: 'pending', status: 'Not established from documentation', review: null, author: null });
  cells[3] = cell('p-two', 'F01', { status: 'Configuration or extension required', activation_state: 'optional' });
  return {
    schema: 'approach-a/publication/1',
    release: { release_id: 'mx-test', publication_mode: mode, accepted: mode === 'accepted', source_commit: 'a'.repeat(40), manifest_version: 1 },
    catalog: { features, categories: [], statuses: STATUSES.map((name) => ({ name, meaning: name + ' meaning' })),
      activation_states: ['default', 'optional'], control_mechanisms: ['enforced'], evidence_bases: [], assessment_states: [] },
    profiles, cells, evidence: [{ id: 'E01', url: 'https://example.invalid/docs', quote: 'q', quotation_matched: true }], limitations: ['L1'],
  };
}
