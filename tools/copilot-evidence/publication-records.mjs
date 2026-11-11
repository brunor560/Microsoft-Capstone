// Format preserved observations only. No model, grader, or candidate code execution.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import {packet, render, markdown, hashes, validate, read, json} from './packet.mjs';
const [dir, ...flags]=process.argv.slice(2);
assert(dir && flags.every(f=>['--readme-only','--copilot-inclusive-tokens'].includes(f)), 'Usage: node publication-records.mjs EVIDENCE_DIR [--readme-only | --copilot-inclusive-tokens]');
assert(!(flags.includes('--readme-only') && flags.includes('--copilot-inclusive-tokens')),'Presentation-only mode cannot generate token records');
const before=hashes(dir), staged=fs.mkdtempSync(path.join(os.tmpdir(),'copilot-packet-format-'));
try {
  fs.cpSync(dir,staged,{recursive:true});
  const outputs={};
  const write=(name,text)=>{outputs[name]=text;fs.writeFileSync(path.join(staged,name),text);};
  const add=(name,text)=>{if(fs.existsSync(path.join(staged,name)))assert(read(staged,name)===text,`Refusing to replace contradictory ${name}`);else write(name,text);};
  if(!fs.existsSync(path.join(staged,'token-usage.json'))) {
    assert(flags.includes('--copilot-inclusive-tokens'),'Verify installed usage schema, then explicitly select --copilot-inclusive-tokens; never guess cache semantics');
    const raw=json(staged,'copilot-usage.json'),metrics=Object.values(raw.modelMetrics || {});
    assert(metrics.length===1,'Mixed/missing model metrics');
    const u=metrics[0].usage;
    const fields={input_tokens:'inputTokens',output_tokens:'outputTokens',cached_input_tokens:'cacheReadTokens',cache_write_input_tokens:'cacheWriteTokens',reasoning_output_tokens:'reasoningTokens'};
    const usage=Object.fromEntries(Object.entries(fields).map(([k,v])=>[k,u[v] ?? null]));
    assert(Number.isSafeInteger(usage.input_tokens) && Number.isSafeInteger(usage.output_tokens),'Missing raw token totals');
    write('token-usage.json',JSON.stringify({source:'copilot-usage.json modelMetrics; one aggregate including subagents once',...usage,total_tokens:usage.input_tokens+usage.output_tokens,total_cost_usd:null,cost_reason:'Raw Copilot metrics expose request/AI-credit counters, not verified provider USD cost',accounting_notes:'Operator selected verified Copilot inclusive schema: cache read/write are subsets included in input; reasoning is a subset included in output; provider/agent summaries are not added again.'},null,2)+'\n');
  }
  let p=packet(staged);
  if(!flags.includes('--readme-only')) {
    if(!p.config.model)write('run-configuration.txt',read(staged,'run-configuration.txt').replace(/\n?$/,'\n')+`model=${p.model}\nmodel_verification_source=runtime-observation.json; corroborated by copilot-usage.json\n`);
    add('timing.txt',`start_utc=${p.timing.start_utc}\nend_utc=${p.timing.end_utc}\nelapsed_seconds=${p.timing.seconds}\nmethod=${p.timing.method}\napproval_wait_seconds=${p.timing.approval_wait_seconds ?? 'unavailable'}\nraw_record=timing.json\n`);
    add('original-test-exits.txt',p.results.map(s=>`${s.key}_exit=${s.exit}`).join('\n')+'\n');
  } else {
    assert(p.config.model===p.model,'Presentation-only update requires existing compatible model');
    assert(fs.existsSync(path.join(staged,'timing.txt')) && fs.existsSync(path.join(staged,'original-test-exits.txt')),'Presentation-only update needs compatible records');
  }
  p=packet(staged);
  write('publication-summary.json',JSON.stringify(p,null,2)+'\n');
  write('README.md',render(staged,p));
  write('publication-format-validation.json',JSON.stringify({version:2,status:'PASS (internal); unchanged importer gate still required',model:p.model,seconds:p.timing.seconds,method:p.timing.method,suites:p.results.map(s=>`${s.key}_exit=${s.exit}`),human_review:p.review.status},null,2)+'\n');
  markdown(staged,outputs['README.md']);
  write('publication-files.sha256',hashes(staged));
  validate(staged);
  assert(hashes(dir)===before,'Evidence changed while formatting');
  for(const [name,text] of Object.entries(outputs))fs.writeFileSync(path.join(dir,name),text);
  console.log(`Formatted and internally validated ${p.config.run_id}; unchanged importer gate still required.`);
} finally {fs.rmSync(staged,{recursive:true,force:true});}
