// Publication-only helpers: never execute candidate code, graders, or model requests.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
export const suites = {
  local: ['local-tests', 'original-local-tests.txt', 'Local'],
  api: ['api-tests', 'original-api-tests.txt', 'Independent API'],
  browser: ['browser-tests', 'original-browser-tests.txt', 'Independent browser'],
  acceptance: ['acceptance', 'original-acceptance.txt', 'Acceptance'],
  supplemental: ['supplemental', 'original-supplemental.txt', 'Supplemental'],
  security_runtime: ['security-runtime', 'original-security-runtime.txt', 'Runtime security'],
  security_scan: ['security-scan', 'original-security-scan.txt', 'Static security'],
};
export const sections = ['Configuration', 'Pinned inputs', 'Independent results', 'Changed files and scope', 'Timing', 'Tokens and cost', 'Approvals, interventions and review', 'Limitations', 'Evidence'];
export const read = (d, p) => fs.readFileSync(path.join(d, p), 'utf8');
export const json = (d, p) => JSON.parse(read(d, p));
export const hash = b => crypto.createHash('sha256').update(b).digest('hex');
export function kv(text) {
  const out = {};
  for (const line of text.trim().split(/\r?\n/)) {
    const m = line.match(/^([a-zA-Z_]+)=(.*)$/);
    if (m) { assert(!(m[1] in out), `Duplicate field ${m[1]}`); out[m[1]] = m[2]; }
  }
  return out;
}
const number = (n, field) => { assert(Number.isSafeInteger(n) && n >= 0, `Invalid ${field}`); return n; };
const display = n => n == null ? 'Unavailable' : typeof n === 'number' ? n.toLocaleString('en-US') : n;
const md = v => String(v).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('|', '&#124;').replaceAll('`', '&#96;').replace(/\r?\n/g, ' ');
export function outcomes(log) {
  const checks = [...log.matchAll(/^([A-Z]\d+)=(PASS|FAIL)\b[^\r\n]*/gm)].map(m => ({id:m[1], verdict:m[2], detail:m[0].replace(/^\S+\s*/, '')}));
  if (checks.length) {
    assert(new Set(checks.map(c => c.id)).size === checks.length, 'Duplicate static check');
    return {passed:checks.filter(c => c.verdict === 'PASS').length, failed:checks.filter(c => c.verdict === 'FAIL').length, skipped:null, checks};
  }
  const count = name => {
    const matches = [...log.matchAll(new RegExp(`^(?:ℹ|#) ${name} (\\d+)\\s*$`, 'gm'))];
    assert(matches.length <= 1, `Ambiguous repeated ${name} summary`);
    return matches.length ? +matches[0][1] : null;
  };
  let passed = count('pass'), failed = count('fail'), skipped = count('skipped');
  const browser = label => [...log.matchAll(new RegExp(`^\\s*(\\d+) ${label}(?: \\([^\\n]*\\))?\\s*$`, 'gm'))];
  if (passed == null && failed == null) {
    for (const name of ['passed','failed','skipped']) assert(browser(name).length <= 1, 'Ambiguous browser summary');
    const p=browser('passed'), f=browser('failed'), s=browser('skipped');
    if (p.length || f.length || s.length) { passed=p.length ? +p[0][1] : null; failed=f.length ? +f[0][1] : passed != null ? 0 : null; skipped=s.length ? +s[0][1] : null; }
  }
  if (passed == null && failed == null && skipped == null) {
    const verdict=log.match(/^(?:security|verdict)=(PASS|FAIL)$/m)?.[1];
    assert(verdict, 'Unrecognized/incomplete suite summary; preserve log and document blocker');
    return {passed:null, failed:null, skipped:null, verdict, checks:[]};
  }
  assert(passed != null || failed != null || skipped != null, 'Incomplete suite counts');
  return {passed, failed, skipped, checks:[]};
}
export function packet(d) {
  const config=kv(read(d,'run-configuration.txt')), pins=kv(read(d,'source-commits.txt'));
  for (const k of ['run_id','task_id','tool','interface','model_requested','provider','session_id']) assert(config[k], `Missing ${k}`);
  assert(/^copilot-/.test(config.run_id) && /^\d{3}$/.test(config.task_id), 'Invalid run/task identity');
  for (const k of ['snapshot_commit','evaluator_commit','quality_commit']) {
    assert(/^[a-f0-9]{40}$/.test(pins[k]), `Missing full ${k}`);
    assert(config[k] === pins[k], `Contradictory ${k}`);
  }
  const observed=json(d,'runtime-observation.json'), raw=json(d,'copilot-usage.json');
  assert(observed.source === 'owned assistant.message events', 'Unverified observed model source');
  const models=[...new Set(observed.models)];
  assert(models.length === 1 && typeof models[0] === 'string' && /[a-z]/i.test(models[0]) && !/unknown|auto/i.test(models[0]), 'Missing/mixed observed models');
  assert.deepEqual(Object.keys(raw.modelMetrics).sort(),models, 'Observed model and raw usage disagree');
  assert(observed.session_id === config.session_id, 'Observed session mismatch');
  if (config.model) assert(config.model === models[0], 'Recorded model contradicts verified observation');
  const t=json(d,'timing.json');
  if (t.session_id) assert(t.session_id === config.session_id, 'Timer session mismatch');
  const start=Date.parse(t.start_utc), end=Date.parse(t.final_report_event_utc || t.end_utc);
  assert(Number.isFinite(start) && Number.isFinite(end) && end>=start, 'Invalid actual UTC boundaries');
  if (t.final_report_event_utc) assert(end<=Date.parse(t.end_utc), 'Final report after process exit');
  const seconds=t.final_report_event_utc ? (end-start)/1000 : t.process_elapsed_seconds;
  assert(Number.isFinite(seconds) && seconds>=0, 'Missing measured elapsed time');
  if (!t.final_report_event_utc) assert(Math.abs(seconds-(end-start)/1000)<0.25, 'Monotonic/UTC timer mismatch');
  const method=t.final_report_event_utc
    ? 'launch-to-final-report proxy; process launch UTC to last owned final assistant.message event UTC; includes CLI startup, excludes setup/grading; not exact prompt-acceptance latency'
    : 'external monotonic process-lifetime proxy; before CLI launch to process exit; includes startup/shutdown/export overhead, excludes setup/grading';
  const wait=t.approval_wait_seconds ?? null;
  assert(wait == null || (Number.isFinite(wait) && wait>=0),'Invalid measured approval wait');
  const timing={start_utc:t.start_utc,end_utc:t.final_report_event_utc || t.end_utc,seconds,method,approval_wait_seconds:wait};
  const usage=json(d,'token-usage.json'), u=usage.usage || usage;
  assert(/subset|included/i.test(usage.accounting_notes || ''), 'Copilot inclusive token accounting must be verified and documented');
  const rawTokens=raw.modelMetrics[models[0]].usage;
  const fields={input_tokens:'inputTokens',output_tokens:'outputTokens',cached_input_tokens:'cacheReadTokens',cache_write_input_tokens:'cacheWriteTokens',reasoning_output_tokens:'reasoningTokens'};
  const tokens={};
  for (const [field,rawField] of Object.entries(fields)) {
    const expected=rawTokens[rawField];
    tokens[field]=expected == null ? null : number(expected, rawField);
    assert((u[field] ?? null) === tokens[field], `Token mismatch ${field}`);
  }
  assert(tokens.input_tokens != null && tokens.output_tokens != null, 'Input/output unavailable: document schema blocker rather than inventing totals');
  assert((tokens.cached_input_tokens ?? 0)+(tokens.cache_write_input_tokens ?? 0)<=tokens.input_tokens, 'Cache subsets exceed input');
  assert((tokens.reasoning_output_tokens ?? 0)<=tokens.output_tokens, 'Reasoning subset exceeds output');
  tokens.total_tokens=tokens.input_tokens+tokens.output_tokens;
  assert(u.total_tokens === tokens.total_tokens, 'Total must be input + output, without double-counted subsets');
  tokens.total_cost_usd=usage.total_cost_usd ?? null;
  assert(tokens.total_cost_usd == null || (Number.isFinite(tokens.total_cost_usd) && tokens.total_cost_usd>=0), 'Invalid USD cost');
  tokens.cost_reason=usage.cost_reason || usage.cost_note;
  assert(tokens.total_cost_usd != null || tokens.cost_reason, 'Explain unavailable cost');
  const exits=json(d,'original-test-exits.raw.json'), applicability=json(d,'suite-applicability.json'), results=[];
  const known=new Set(Object.values(suites).map(v=>v[0]));
  for (const k of Object.keys(exits)) assert(known.has(k) || k==='quality', `Unknown suite exit ${k}`);
  for (const [key,[rawKey,file,label]] of Object.entries(suites)) {
    const exists=fs.existsSync(path.join(d,file)), exit=exits[rawKey];
    if (exit == null) { assert(!exists, `Nonexistent suite ${key} has placeholder log`); continue; }
    assert(applicability[key]?.applicable !== false, `Exit for inapplicable suite ${key}`);
    assert(exists && Number.isInteger(exit) && exit>=0 && exit<=255, `Missing log/invalid actual exit ${key}`);
    const counts=outcomes(read(d,file));
    assert(!(exit===0 && (counts.failed>0 || counts.verdict==='FAIL')), `Failed suite ${key} claims exit 0`);
    results.push({key,file,label,exit,...counts});
  }
  assert(results.some(s=>s.key==='local'), 'Missing independent local suite');
  for (const [key,a] of Object.entries(applicability)) {
    assert(suites[key] && typeof a.applicable==='boolean' && a.reason, `Invalid applicability ${key}`);
    if (a.applicable) assert(results.some(s=>s.key===key), `Applicable suite ${key} not graded`);
  }
  const changed=read(d,'original-scope-diff.txt').trim().split(/\r?\n/).filter(Boolean);
  const manifest = file => Object.fromEntries(read(d,file).trim().split(/\r?\n/).slice(1).map(line=>{
    const m=line.match(/^"?(.+?)"?,"?([a-f0-9]{64})"?$/);assert(m,`Malformed source manifest ${file}`);return [m[1],m[2]];
  }));
  const before=manifest('before-files.csv'), after=manifest('original-after-files.csv');
  const actualChanges=[...new Set([...Object.keys(before),...Object.keys(after)])].filter(f=>before[f]!==after[f]);
  assert.deepEqual(changed.slice().sort(),actualChanges.sort(),'Scope list disagrees with source manifests');
  const preserved={'app/server.js':'server.js','app/test.js':'test.js','app/public/index.html':'index.html','app/legacy/billing-export.js':'billing-export.js'};
  for(const [source,file] of Object.entries(preserved))if(after[source])assert(hash(fs.readFileSync(path.join(d,'original',file)))===after[source],`Preserved code mismatch ${source}`);
  const interventions=json(d,'interventions.json'), operator=json(d,'operator.json'), review=json(d,'review-status.json');
  assert(interventions.run_id===config.run_id && Array.isArray(interventions.interventions), 'Wrong intervention run');
  assert(operator.messages_to_agent===interventions.interventions.length, 'Operator/intervention count mismatch');
  const reviewed=fs.existsSync(path.join(d,'h-review.json'));
  if (!reviewed) assert(review.status==='UNREVIEWED' && /pending/i.test(review.independent_human_review), 'Missing human review cannot claim reviewed');
  else assert(json(d,'h-review.json').reviewer, 'Missing real reviewer identity');
  const notes=json(d,'publication-notes.json');
  assert(Array.isArray(notes.scope_findings) && notes.scope_findings.length && notes.scope_findings.every(v=>typeof v==='string' && v.trim()),'Missing human-readable scope findings');
  assert(typeof notes.effort==='string' && notes.effort.trim(),'Record observed effort or explain unavailable effort');
  const quality=json(d,'quality.json');
  const quality_checks=Object.entries(quality.checks || {}).map(([name,c])=>({name,applicable:c.applicable !== false,pass:c.pass ?? null}));
  return {version:2,config,pins,notes,quality_checks,model:models[0],timing,tokens,results,applicability,changed,interventions:interventions.interventions.length,review,reviewed};
}
export function render(d,p) {
  const template=fs.readFileSync(new URL('./templates/run-readme.md', import.meta.url),'utf8');
  const list=items=>items.length ? items.map(v=>`- ${md(v)}`).join('\n') : 'None recorded.';
  const table=['| Suite | Passed | Failed | Skipped | Exit |','|---|---:|---:|---:|---:|',...p.results.map(s=>`| [${s.label}](${s.file}) | ${display(s.passed)} | ${display(s.failed)} | ${s.key==='security_scan' ? 'Not applicable' : display(s.skipped)} | ${s.exit} |`)].join('\n');
  const checks=p.results.flatMap(s=>s.checks.map(c=>`${c.id}: ${c.verdict} — ${c.detail}`));
  const absent=Object.entries(p.applicability).filter(([,v])=>!v.applicable).map(([k,v])=>`${suites[k][2]}: not applicable — ${v.reason}. No log or exit is created.`);
  const evidence=['run-configuration.txt','source-commits.txt','runtime-observation.json','copilot-usage.json','token-usage.json','timing.txt','timing.json','original-test-exits.txt','original-test-exits.raw.json','suite-applicability.json','original-scope-diff.txt','scope-review.txt','before-files.csv','original-after-files.csv','approval-notes.txt','interventions.json','operator.json','review-status.json','initial-prompt.txt','initial-prompt.sha256','final-report.txt','conversation.md','quality.json','quality-grading.txt', 'publication-summary.json','publication-notes.json'];
  const values={
    title:`Task ${p.config.task_id} — ${p.config.run_id} (${p.reviewed ? 'human review recorded' : 'UNREVIEWED'})`,
    configuration:list([`Run: ${p.config.run_id}; participant: ${p.config.participant || 'unavailable'}.`, `Tool: ${p.config.tool}; interface: ${p.config.interface}.`, `Verified observed model: ${p.model}; requested selector: ${p.config.model_requested}; provider: ${p.config.provider}.`, `Session: ${p.config.session_id}; effort: ${p.notes.effort}.`, `Approval mode: ${p.config.approval_mode || 'unavailable'}; fresh start: ${p.config.fresh_start || 'unavailable'}.`, `Isolation: ${p.config.isolation || 'unavailable'}.`]),
    pins:list([`Task snapshot: ${p.pins.snapshot_commit}`,`Evaluator: ${p.pins.evaluator_commit}`,`Quality grader: ${p.pins.quality_commit}`]),
    results:table+'\n\n'+(checks.length ? list(checks)+'\n\n' : '')+(absent.length ? list(absent)+'\n\n' : '')+'Skipped counts are unavailable where the log does not report them; static checks have no skipped-test counter. Nonzero exits and genuine benchmark failures are preserved. See [raw suite exits](original-test-exits.raw.json).',
    scope:list(p.changed.map(f=>`Changed: ${f}`))+'\n\n'+list(p.notes.scope_findings)+'\n\n'+ 'Scope and report-accuracy findings: [scope-review.txt](scope-review.txt). Full changes: [original-scope-diff.txt](original-scope-diff.txt); preserved code: [original/](original/).',
    timing:list([`Start UTC: ${p.timing.start_utc}`,`End UTC: ${p.timing.end_utc}`,`Elapsed seconds: ${p.timing.seconds}`,`Method: ${p.timing.method}`,`Approval waiting seconds: ${p.timing.approval_wait_seconds == null ? 'unavailable; not separately measured' : p.timing.approval_wait_seconds}. No zero wait is inferred from an empty intervention log.`])+'\n\nSupported elapsed uses UTC boundaries at millisecond precision when a final-message boundary is available. Raw submillisecond timestamps and the separate process-lifetime measurement remain in [timing.json](timing.json).',
    tokens:list([`Input: ${display(p.tokens.input_tokens)}; output: ${display(p.tokens.output_tokens)}; total: ${display(p.tokens.total_tokens)}.`,`Cache read: ${display(p.tokens.cached_input_tokens)}; cache write: ${display(p.tokens.cache_write_input_tokens)} (subsets of input).`,`Reasoning output: ${display(p.tokens.reasoning_output_tokens)} (subset of output).`,`Accounting: input plus output, using one modelMetrics aggregate per model/session. Provider and agent summaries are not added again; subagents are included once.`,`USD cost: ${p.tokens.total_cost_usd == null ? 'unavailable — '+p.tokens.cost_reason : p.tokens.total_cost_usd}.`]),
    review:`${md(read(d,'approval-notes.txt').trim())}\n\nPost-prompt interventions: ${p.interventions}. Human-review status: ${md(p.review.status)}; ${md(p.review.independent_human_review)}. ${p.reviewed ? 'See [human review](h-review.json).' : 'No h-review.json exists; no human collaboration score is claimed.'}`,
    limitations:list(p.review.configuration_limitations || [])+'\n\n'+list(p.quality_checks.map(c=>`Legacy quality diagnostic ${c.name}: ${!c.applicable ? 'not applicable' : c.pass == null ? 'unavailable' : c.pass ? 'PASS' : 'FAIL'}`))+'\n\nRaw measurements are retained. [quality.json](quality.json) contains pinned legacy diagnostics, including failures; it is not a native composite score. Missing information is unavailable, never zero. No general speed or isolation ranking is established.',
    evidence:evidence.map(f=>`- [${f}](${f})`).join('\n'),
  };
  return template.replace(/\{\{(\w+)\}\}/g,(_,k)=>{assert(k in values,`Unknown template field ${k}`);return values[k];});
}
export function markdown(d,text) {
  assert(!/\{\{\w+\}\}|\{'\w+':|\['[^']+'\]|\bNone\b/.test(text.replace(/None recorded\./g,'')), 'Placeholder or Python representation in README');
  assert(text.startsWith('# Task ') && text.endsWith('\n'), 'Invalid Markdown title/ending');
  for (const heading of sections) assert(text.split(`\n## ${heading}\n\n`).length===2, `Missing/duplicate section ${heading}`);
  assert((text.match(/^```/gm)||[]).length%2===0, 'Unclosed code fence');
  for (const m of text.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
    assert(!path.isAbsolute(m[1]) && !m[1].split('/').includes('..'), 'Unsafe evidence link');
    assert(fs.existsSync(path.join(d,m[1])), `Broken evidence link ${m[1]}`);
  }
  const lines=text.split('\n');
  for(let i=0;i<lines.length;i++) if(lines[i].startsWith('|')) {
    const cols=lines[i].split('|').length;
    while(i+1<lines.length && lines[i+1].startsWith('|')) assert(lines[++i].split('|').length===cols,'Malformed Markdown table');
  }
}
export function hashes(d) {
  const files=[];
  function walk(dir) { for(const name of fs.readdirSync(dir).sort()) {
    const full=path.join(dir,name),s=fs.lstatSync(full); assert(!s.isSymbolicLink(),'Publication symlink not allowed');
    if(s.isDirectory())walk(full);else {assert(s.isFile(),'Special publication file');if(name!=='publication-files.sha256')files.push(path.relative(d,full));}
  }}
  walk(d);
  return files.sort().map(f=>`${hash(fs.readFileSync(path.join(d,f)))}  ${f}`).join('\n')+'\n';
}
export function validate(d) {
  for(const f of ['README.md','publication-summary.json','initial-prompt.txt','initial-prompt.sha256','final-report.txt','conversation.md','scope-review.txt','approval-notes.txt','setup-notes.txt','operator.json','quality.json','quality-grading.txt','before-files.csv','original-after-files.csv']) assert(fs.existsSync(path.join(d,f)),`Missing required artifact ${f}`);
  const p=packet(d);
  assert(read(d,'initial-prompt.sha256').trim().split(/\s+/)[0]===hash(fs.readFileSync(path.join(d,'initial-prompt.txt'))),'Prompt hash mismatch');
  const timing=kv(read(d,'timing.txt'));
  assert(timing.approval_wait_seconds===String(p.timing.approval_wait_seconds ?? 'unavailable'),'Approval wait mismatch');
  assert.deepEqual([timing.start_utc,timing.end_utc,+timing.elapsed_seconds,timing.method],[p.timing.start_utc,p.timing.end_utc,p.timing.seconds,p.timing.method],'Compatible/raw timing mismatch');
  assert(kv(read(d,'run-configuration.txt')).model===p.model,'Missing supported verified model=');
  assert.deepEqual(kv(read(d,'original-test-exits.txt')),Object.fromEntries(p.results.map(s=>[s.key+'_exit',String(s.exit)])),'Wrong suite exit keys/values');
  assert.deepEqual(json(d,'publication-summary.json'),p,'Stale machine-readable summary');
  const text=read(d,'README.md');markdown(d,text);assert(text===render(d,p),'README contradicts evidence/template');
  const f=json(d,'publication-format-validation.json');
  assert(f.version===2 && f.status==='PASS (internal); unchanged importer gate still required' && f.model===p.model && f.seconds===p.timing.seconds && f.method===p.timing.method && f.human_review===p.review.status,'Stale format validation record');
  assert.deepEqual(f.suites,p.results.map(s=>`${s.key}_exit=${s.exit}`),'Format validation suites disagree');
  assert(read(d,'publication-files.sha256')===hashes(d),'Publication hashes stale');
  return p;
}
