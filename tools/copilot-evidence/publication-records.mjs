// Format observed evidence for the existing dashboard reader. Not a benchmark runner/grader.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const [dir] = process.argv.slice(2);
assert(dir, 'Usage: node publication-records.mjs EVIDENCE_DIR');
const read = n => JSON.parse(fs.readFileSync(path.join(dir, n), 'utf8'));
const write = (n, t) => { const p=path.join(dir,n); assert(!fs.existsSync(p), `Refusing overwrite: ${n}`); fs.writeFileSync(p,t); };
const observed = read('runtime-observation.json');
assert(observed.source === 'owned assistant.message events', 'Runtime identity must come from owned session events');
const models = [...new Set(observed.models)];
assert(models.length === 1 && models[0] && !/unknown|auto/i.test(models[0]), 'Missing/mixed models: preserve raw evidence, exclude from single-model cohort');
const usage = read('copilot-usage.json');
assert.deepEqual(Object.keys(usage.modelMetrics).sort(), models.slice().sort(), 'Runtime messages and usage disagree');
const configPath=path.join(dir,'run-configuration.txt');
const config=fs.readFileSync(configPath,'utf8');
assert(!/^model=/m.test(config), 'Never replace a recorded model identity');
fs.appendFileSync(configPath, `model=${models[0]}\nmodel_verification_source=runtime-observation.json; corroborated by copilot-usage.json\n`);
const t=read('timing.json');
const final=t.final_report_event_utc;
const seconds=final ? (Date.parse(final)-Date.parse(t.start_utc))/1000 : t.process_elapsed_seconds;
assert(Number.isFinite(seconds) && seconds>=0, 'Missing actual timer boundaries');
const method=final ? 'launch-to-final-report proxy; process launch UTC to last owned final assistant.message event UTC; includes CLI startup, excludes setup/grading; not exact prompt-acceptance latency' : 'external monotonic process-lifetime proxy; before CLI launch to process exit; includes startup/shutdown/export overhead, excludes setup/grading';
write('timing.txt',`start_utc=${t.start_utc}\nend_utc=${final || t.end_utc}\nelapsed_seconds=${seconds}\nmethod=${method}\napproval_wait_seconds=unavailable\nraw_record=timing.json\n`);
const exits=read('original-test-exits.raw.json');
const mapping={'local-tests':'local','api-tests':'api','browser-tests':'browser','security-scan':'security_scan','security-runtime':'security_runtime','acceptance':'acceptance','supplemental':'supplemental'};
const logs={local:'original-local-tests.txt',api:'original-api-tests.txt',browser:'original-browser-tests.txt',security_scan:'original-security-scan.txt',security_runtime:'original-security-runtime.txt',acceptance:'original-acceptance.txt',supplemental:'original-supplemental.txt'};
const lines=[];
for(const [raw,key] of Object.entries(mapping)) {
  if(exits[raw]!==undefined) { assert(Number.isInteger(exits[raw]), 'Suite exit must be actual integer'); assert(fs.existsSync(path.join(dir,logs[key])),`Missing performed suite ${key}`); lines.push(`${key}_exit=${exits[raw]}`); }
  else assert(!fs.existsSync(path.join(dir,logs[key])),`Absent suite ${key} must not have a placeholder log`);
}
assert(lines.some(l=>l.startsWith('local_exit=')),'Missing independent local outcome');
write('original-test-exits.txt',lines.join('\n')+'\n');
write('publication-format-validation.json',JSON.stringify({status:'record-format validated; unchanged importer validation still required before pushing',model:models[0],seconds,method,suites:lines,raw:['runtime-observation.json','copilot-usage.json','timing.json','original-test-exits.raw.json'],human_review:'pending; no h-review.json generated'},null,2)+'\n');
