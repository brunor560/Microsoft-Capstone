// Fictional local demo/test fixture. Never copy this into dashboard/ (Pages uploads it all).
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { cell, STATUSES } from './fixtures.mjs';

export function demoPayload() {
  const catalog = JSON.parse(readFileSync(new URL('../../../../assessment/catalog.json', import.meta.url), 'utf8'));
  const definitions = [
    ['alder-individual', 'Alder', 'Individual', 'MMG'], ['alder-enterprise', 'Alder', 'Enterprise', 'MMM'],
    ['birch-team', 'Birch', 'Team', 'MM?'], ['cedar-individual', 'Cedar', 'Individual', 'MMM'],
    ['dogwood-enterprise', 'Dogwood', 'Enterprise', 'MGM'], ['elm-undecided', 'Elm', null, 'MMM'],
  ];
  const profiles = definitions.map(([id, tool, tier]) => ({ id, tool, surface_label: 'Example CLI',
    account_and_tier: tier, version: { value: 'Illustrative' }, platforms: ['Example Linux workstation'],
    modes: ['Terminal'], exclusions: ['Other operating systems and product surfaces'] }));
  const evidence = [{ id: 'E01', page_title: 'Fictional documentation', url: 'https://example.invalid/docs',
    quote: 'Fictional fixture support and exclusions.', surface: 'Example CLI', quotation_matched: true }];
  const selected = ['F01', 'F07', 'F08'];
  const cells = definitions.flatMap(([id, , , coverage]) => catalog.features.map((feature) => {
    const marker = selected.includes(feature.id) ? coverage[selected.indexOf(feature.id)] : '?';
    return cell(id, feature.id, {
      assessment_state: marker === '?' ? 'pending' : 'challenged', author: null, review: null,
      status: marker === 'G' ? 'Unavailable' : marker === '?' ? 'Not established from documentation' : 'Built in',
      evidence_basis: marker === 'G' ? 'documented_absence' : marker === '?' ? 'documentation_gap' : 'documented_support',
      supported_scope: marker === 'M' ? 'The fictional CLI documents this whole capability within this recorded tier.' : 'Not established',
      unsupported_scope: marker === 'G' ? ['This capability is explicitly excluded by the fictional plan.'] : [],
      evidence_refs: marker === '?' ? [] : ['E01'],
      gap_reason: marker === '?' ? 'Fictional research pending.' : null,
    });
  }));
  return { schema: 'approach-a/publication/1', release: { release_id: 'shortlist-demo', publication_mode: 'preview', accepted: false, manifest_version: 1 },
    catalog: { ...catalog, activation_states: catalog.activation_state, control_mechanisms: catalog.control_mechanism, statuses: STATUSES.map((name) => ({ name, meaning: name })) }, profiles, cells, evidence,
    limitations: ['Illustrative demo: all tools, tiers and findings are fictional. Not accepted research.'] };
}

// Explicit local fixture generation only; imported by tests without writing any files.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.stdout.write(JSON.stringify(process.argv.includes('--presentation') ? presentationPayload() : demoPayload(), null, 2) + '\n');
}

// Presentation fixture: all five documentary findings plus a pending placeholder.
// Generated only into the ignored loopback preview directory.
export function presentationPayload() {
  const data = demoPayload();
  data.profiles = data.profiles.slice(0, 2).map((p, i) => ({ ...p, tool_key: 'alder',
    surface_label: i ? 'Example desktop app' : 'Example CLI',
    documentation_base: 'https://example.invalid/docs', source_access_date: '2026-11-09' }));
  data.cells = data.profiles.flatMap((p) => data.catalog.features.map((feature, i) => cell(p.id, feature.id, {
    status: STATUSES[i % STATUSES.length], assessment_state: i === 5 ? 'pending' : 'challenged',
    supported_scope: 'Fictional finding for ' + feature.id,
    required_setup: 'Fictional setup for ' + feature.id, evidence_refs: i === 5 ? [] : ['E01'],
    author: null, review: null,
  })));
  // A pending record deliberately carries the exporter placeholder status.
  for (const c of data.cells) if (c.assessment_state === 'pending') c.status = 'Not established from documentation';
  data.limitations = ['Presentation fixture — fictional data, not accepted research.'];
  return data;
}
