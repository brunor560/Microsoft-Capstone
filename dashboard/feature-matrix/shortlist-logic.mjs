// Documentary eligibility, not a capability score. Uses only publication/1 fields.
export const groups = { match: 'Documented match', unknown: 'Needs verification', gap: 'Documented gap' };
export const groupOrder = Object.keys(groups);

export function recordedTier(profile) {
  const label = profile.account_and_tier?.trim();
  // Do not turn an inventory of possible plans or an undecided boundary into eligible tiers.
  return label && !/not (?:stated|established|selected|recorded)|unknown|unverified|team choice|pending|to be (?:confirmed|selected|decided)|\btbd\b/i.test(label)
    ? { id: profile.id, label } : null;
}

export function requirementFinding(ix, profile, feature) {
  const cell = ix.cells.get(profile.id + '/' + feature.id);
  if (!cell || !['drafted', 'challenged', 'reviewed'].includes(cell.assessment_state)) {
    return { feature, state: 'unknown', reason: 'Research is pending or the cell is missing; no finding is established.' };
  }
  const notes = [cell.supported_scope, ...(cell.unsupported_scope || []).map((s) => 'Unsupported: ' + s),
    ...(cell.unestablished_scope || []).map((s) => 'Not established: ' + s), cell.gap_reason,
    cell.required_setup && 'Required setup: ' + cell.required_setup,
    ...(cell.constraints || []).map((s) => 'Constraint: ' + s)].filter(Boolean).join(' ');
  const result = (state, reason) => ({ feature, state, reason: reason + (notes ? ' ' + notes : '') });
  const refs = cell.evidence_refs || [];
  const documented = refs.length && refs.every((id) => ix.evidence.get(id)?.quotation_matched === true);
  if (!documented) return result('unknown', 'Supporting quotations are missing or not matched to their sources.');
  if (cell.review?.stale || (cell.review && (cell.review.decision !== 'agree' || !cell.review.independent))) {
    return result('unknown', 'The review is stale, disputed or not independent.');
  }
  // An explicit unsupported subcapability defeats whole-feature coverage, even alongside support.
  if ((cell.unsupported_scope || []).length || (cell.status === 'Unavailable' && cell.evidence_basis === 'documented_absence')) {
    return result('gap', 'The cell explicitly documents an unsupported requirement or subcapability.');
  }
  if (!recordedTier(profile)) return result('unknown', 'The assessment tier has not been established.');
  const supportedStatus = ['Built in', 'Configuration or extension required', 'Custom implementation required'].includes(cell.status);
  const setupKnown = cell.required_setup?.trim() && !/^(?:none|not established|unknown|not stated)[.!]?$/i.test(cell.required_setup.trim());
  if (!supportedStatus || cell.evidence_basis !== 'documented_support'
      || (cell.status !== 'Built in' && !setupKnown)
      || !cell.supported_scope?.trim() || /^(?:not established|unknown|none)[.!]?$/i.test(cell.supported_scope.trim())
      || cell.unestablished_scope?.length || cell.gap_reason?.trim()) {
    return result('unknown', 'Whole-feature coverage within this profile is not established; inspect scope and dependencies.');
  }
  return result('match', cell.status + ': documented coverage within the recorded profile and tier; setup and constraints still apply.');
}

export function shortlistRows(ix, tierKeys, featureIds) {
  const features = ix.features.filter((feature) => featureIds.has(feature.id));
  if (!features.length) return [];
  return ix.profiles.filter((profile) => !tierKeys.size || tierKeys.has(profile.id)).map((profile) => {
    const requirements = features.map((feature) => requirementFinding(ix, profile, feature));
    const state = requirements.some((item) => item.state === 'gap') ? 'gap'
      : requirements.some((item) => item.state === 'unknown') ? 'unknown' : 'match';
    return { profile, tier: recordedTier(profile), requirements, state };
  });
}

export function readShortlist(search) {
  const params = new URLSearchParams(search);
  return { tiers: new Set(params.getAll('tier')), features: new Set(params.getAll('required')),
    sort: params.get('sort') === 'name' ? 'name' : 'group' };
}

export function writeShortlist(params, state) {
  params.delete('tier'); params.delete('required'); params.delete('sort');
  for (const id of state.tiers) params.append('tier', id);
  for (const id of state.features) params.append('required', id);
  if (state.sort === 'name') params.set('sort', 'name');
  return params;
}
