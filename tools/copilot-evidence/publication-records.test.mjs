import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {hash,hashes,validate,markdown} from './packet.mjs';
import {gate} from './validate-publication.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)), formatter=path.join(here,'publication-records.mjs');
const tmp=()=>fs.mkdtempSync(path.join(os.tmpdir(),'copilot-format-test-'));
const put=(d,p,v)=>{fs.mkdirSync(path.dirname(path.join(d,p)),{recursive:true});fs.writeFileSync(path.join(d,p), typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
function fixture(d,{failure=false,pin='a'.repeat(40)}={}) {
 fs.mkdirSync(d,{recursive:true});
 put(d,'run-configuration.txt',`run_id=copilot-avoid-run99\ntask_id=006\ntool=Copilot CLI fixture\ninterface=headless\nmodel_requested=provider/claude-sonnet-4-6\nprovider=fixture BYOK\nsession_id=fixture-session\nsnapshot_commit=${pin}\nevaluator_commit=${pin}\nquality_commit=${pin}\n`);
 put(d,'source-commits.txt',`snapshot_commit=${pin}\nevaluator_commit=${pin}\nquality_commit=${pin}\n`);
 put(d,'runtime-observation.json',{source:'owned assistant.message events',models:['claude-sonnet-4-6'],session_id:'fixture-session'});
 const usage={inputTokens:100,outputTokens:20,cacheReadTokens:70,cacheWriteTokens:10,reasoningTokens:5};
 put(d,'copilot-usage.json',{modelMetrics:{'claude-sonnet-4-6':{usage}},agentMetrics:{main:{usage}},providerModelMetrics:[{usage}]});
 put(d,'token-usage.json',{input_tokens:100,output_tokens:20,cached_input_tokens:70,cache_write_input_tokens:10,reasoning_output_tokens:5,total_tokens:120,total_cost_usd:null,cost_reason:'Fixture provider exposes no USD cost',accounting_notes:'Verified cache and reasoning fields are subsets, included in aggregate.'});
 put(d,'timing.json',{start_utc:'2026-11-11T10:00:00Z',end_utc:'2026-11-11T10:00:03Z',final_report_event_utc:'2026-11-11T10:00:02Z',process_elapsed_seconds:3,session_id:'fixture-session'});
 const log=`ℹ tests 2\nℹ pass ${failure?1:2}\nℹ fail ${failure?1:0}\nℹ skipped 0\n`;
 put(d,'original-local-tests.txt',log);put(d,'original-api-tests.txt',log);put(d,'original-browser-tests.txt','Running 4 tests using 1 worker\n  4 passed (1.6s)\n');
 put(d,'original-security-scan.txt','A1=PASS production unchanged\nA2=PASS no purge audit\nA3=PASS policy unchanged\nsecurity=PASS\n');
 put(d,'original-test-exits.raw.json',{'local-tests':failure?1:0,'api-tests':failure?1:0,'browser-tests':0,'security-scan':0});
 put(d,'suite-applicability.json',{security_runtime:{applicable:false,reason:'No runtime suite in fixture protocol'}});
 put(d,'original-scope-diff.txt','app/server.js\n');put(d,'original/server.js','// fictional evidence only\n');
 put(d,'interventions.json',{run_id:'copilot-avoid-run99',interventions:[]});put(d,'operator.json',{operator_type:'ai',messages_to_agent:0});
 put(d,'review-status.json',{status:'UNREVIEWED',independent_human_review:'pending',configuration_limitations:['Fixture limitation.']});
 put(d,'publication-notes.json',{effort:'unavailable: fixture has no effort record',scope_findings:['Only app/server.js changed.'],source:'Fixture manifests.'});
 put(d,'quality.json',{checks:{lint:{pass:!failure},runtime:{applicable:false}}});
 put(d,'initial-prompt.txt','Fictional prompt\n');put(d,'initial-prompt.sha256',hash(Buffer.from('Fictional prompt\n'))+'\n');
 put(d,'before-files.csv',`Path,Hash SHA-256\napp/server.js,${hash(Buffer.from('baseline\n'))}\n`);
 put(d,'original-after-files.csv',`Path,Hash SHA-256\napp/server.js,${hash(Buffer.from('// fictional evidence only\n'))}\n`);
 for(const f of ['final-report.txt','conversation.md','scope-review.txt','approval-notes.txt','setup-notes.txt','quality-grading.txt'])put(d,f,'Fixture evidence\n');
}
const format=(d,...flags)=>spawnSync(process.execPath,[formatter,d,...flags],{encoding:'utf8'});
function withFixture(fn,opts) {const d=tmp();try {fixture(d,opts);fn(d);}finally {fs.rmSync(d,{recursive:true,force:true});}}
test('human-readable canonical README, exact fields, subsets counted once, idempotent',()=>withFixture(d=>{
 let r=format(d);assert.equal(r.status,0,r.stderr);const p=validate(d),md=fs.readFileSync(path.join(d,'README.md'),'utf8');
 assert.match(md,/\| Suite \| Passed \| Failed \| Skipped \| Exit \|/);assert.match(md,/A1: PASS/);assert.match(md,/Unavailable/);assert.match(md,/not applicable/);assert.doesNotMatch(md,/\{'|\['/);
 assert.equal(p.tokens.total_tokens,120);assert.equal(p.tokens.total_cost_usd,null);assert.match(fs.readFileSync(path.join(d,'original-test-exits.txt'),'utf8'),/^security_scan_exit=0$/m);assert(!fs.existsSync(path.join(d,'original-security-runtime.txt')));
 const before=hashes(d);r=format(d);assert.equal(r.status,0,r.stderr);assert.equal(hashes(d),before);
}));
test('genuine failing suite remains valid and readable',()=>withFixture(d=>{const r=format(d);assert.equal(r.status,0,r.stderr);assert.equal(validate(d).results[0].exit,1);}, {failure:true}));
for(const [name,mutate] of [
 ['placeholder suite',d=>put(d,'original-security-runtime.txt','Not applicable')],
 ['double-counted tokens',d=>{const p=path.join(d,'token-usage.json'),u=JSON.parse(fs.readFileSync(p));u.total_tokens=205;put(d,'token-usage.json',u);} ],
 ['observed model mismatch',d=>put(d,'runtime-observation.json',{source:'owned assistant.message events',models:['other-model'],session_id:'fixture-session'})],
 ['missing artifact',d=>fs.unlinkSync(path.join(d,'scope-review.txt'))],
 ['contradictory exit',d=>put(d,'original-local-tests.txt','ℹ pass 0\nℹ fail 2\n')],
 ['ambiguous repeated summary',d=>put(d,'original-local-tests.txt','ℹ pass 2\nℹ pass 4\nℹ fail 0\n')],
])test(`reject ${name} before writes`,()=>withFixture(d=>{mutate(d);const before=hashes(d),r=format(d);assert.notEqual(r.status,0);assert.equal(hashes(d),before);}));
test('Markdown sections, broken links, tables and contradictory README rejected',()=>withFixture(d=>{
 assert.equal(format(d).status,0);const good=fs.readFileSync(path.join(d,'README.md'),'utf8');
 for(const bad of [good.replace('## Timing','## Missing'),good+'\n[broken](missing.txt)\n',good.replace('| Exit |','| Exit | extra |'),good+'\n```js\n'])assert.throws(()=>markdown(d,bad));
 put(d,'README.md',good.replace('total: 120','total: 999'));put(d,'publication-files.sha256',hashes(d));assert.throws(()=>validate(d),/README contradicts/);
}));
test('freshness checks detect raw edit and incompatible machine fields',()=>withFixture(d=>{
 assert.equal(format(d).status,0);put(d,'original-test-exits.txt','local-tests=0\n');put(d,'publication-files.sha256',hashes(d));assert.throws(()=>validate(d),/suite exit/);
}));
test('committed-tree gate uses unchanged real importer, allows failures, blocks wrong scope/stale record',()=>{
 const root=tmp(),repo=path.join(root,'repo');fs.mkdirSync(repo);
 const git=(...a)=>execFileSync('git',['-C',repo,...a],{encoding:'utf8',stdio:['ignore','pipe','pipe']});
 try {
  // Uses a local Git object, never downloads or modifies the actual importer.
  const importer=execFileSync('git',['show','origin/master:dashboard/build-data.mjs'],{cwd:here});
  git('init','-q');git('config','user.name','Offline fixture');git('config','user.email','fixture@example.invalid');
  put(repo,'dashboard/build-data.mjs',importer.toString());put(repo,'app/server.js','baseline\n');git('add','.');git('commit','-qm','fixture baseline');const base=git('rev-parse','HEAD').trim();
  const d=path.join(repo,'benchmark-results/copilot/avoid-run99');fixture(d,{failure:true,pin:base});assert.equal(format(d).status,0);
  git('add','.');git('commit','-qm','fictional packet');
  const opts={repo,base,importerRef:base,runs:['copilot/avoid-run99'],report:path.join(root,'first.json'),writeRecords:true};
  const r=gate(opts);assert.equal(r.result,'PASS');assert.equal(r.runs[0].benchmark_outcome,'fail');assert.equal(r.importer_sha256,hash(importer));
  git('add','.');git('commit','-qm','validation proof');gate({...opts,report:path.join(root,'final.json'),writeRecords:false});
  const proof=fs.readFileSync(path.join(d,'publication-validation.json'),'utf8');
  const stale=JSON.parse(proof);stale.inputs['README.md']='wrong';put(d,'publication-validation.json',stale);put(d,'publication-files.sha256',hashes(d));git('add','.');git('commit','-qm','stale proof');
  assert.throws(()=>gate({...opts,report:path.join(root,'stale.json'),writeRecords:false}),/Stale publication validation/);
  put(d,'publication-validation.json',proof);put(d,'publication-files.sha256',hashes(d));git('add','.');git('commit','-qm','restore proof');
  put(repo,'unintended.txt','scope violation');git('add','.');git('commit','-qm','unintended');assert.throws(()=>gate({...opts,report:path.join(root,'bad.json')}),/unintended/);
 } finally {fs.rmSync(root,{recursive:true,force:true});}
});
test('generate compatible token record only with explicit inclusive-schema selection',()=>withFixture(d=>{
 fs.unlinkSync(path.join(d,'token-usage.json'));const before=hashes(d);
 assert.notEqual(format(d).status,0);assert.equal(hashes(d),before);
 const r=format(d,'--copilot-inclusive-tokens');assert.equal(r.status,0,r.stderr);
 const p=validate(d);assert.equal(p.tokens.total_tokens,120);assert.equal(p.tokens.cached_input_tokens,70);assert.equal(p.tokens.total_cost_usd,null);
}));
test('zero subsets and unavailable subsets remain distinct',()=>withFixture(d=>{
 const raw=JSON.parse(fs.readFileSync(path.join(d,'copilot-usage.json')));raw.modelMetrics['claude-sonnet-4-6'].usage.cacheReadTokens=0;delete raw.modelMetrics['claude-sonnet-4-6'].usage.reasoningTokens;put(d,'copilot-usage.json',raw);
 const u=JSON.parse(fs.readFileSync(path.join(d,'token-usage.json')));u.cached_input_tokens=0;delete u.reasoning_output_tokens;put(d,'token-usage.json',u);
 const r=format(d);assert.equal(r.status,0,r.stderr);const p=validate(d);assert.equal(p.tokens.cached_input_tokens,0);assert.equal(p.tokens.reasoning_output_tokens,null);
}));
test('all-failed browser summary is not rejected or given an invented pass count',()=>withFixture(d=>{
 put(d,'original-browser-tests.txt','Running 4 tests using 1 worker\n  4 failed\n');const exits=JSON.parse(fs.readFileSync(path.join(d,'original-test-exits.raw.json')));exits['browser-tests']=1;put(d,'original-test-exits.raw.json',exits);
 const r=format(d);assert.equal(r.status,0,r.stderr);const s=validate(d).results.find(s=>s.key==='browser');assert.equal(s.passed,null);assert.equal(s.failed,4);
}));
test('a measured zero approval wait stays zero',()=>withFixture(d=>{
 const t=JSON.parse(fs.readFileSync(path.join(d,'timing.json')));t.approval_wait_seconds=0;put(d,'timing.json',t);const r=format(d);assert.equal(r.status,0,r.stderr);assert.equal(validate(d).timing.approval_wait_seconds,0);
}));
