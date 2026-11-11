// Read a committed Git tree, run the unchanged importer in temporary storage, compare evidence.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {validate, hash, hashes, read, json} from './packet.mjs';
export function gate({repo,ref='HEAD',base,importerRef='origin/master',runs,report,writeRecords=false}) {
  assert(repo && base && report && runs?.length,'repo, base, report, and explicit runs required');
  assert(new Set(runs).size===runs.length && runs.every(r=>/^copilot\/(?:run|[a-z]+(?:-[a-z]+)*-run)\d+$/.test(r)),'Invalid/repeated run directory');
  const git=(...args)=>execFileSync('git',['-C',repo,...args],{maxBuffer:128<<20});
  const head=git('rev-parse',`${ref}^{commit}`).toString().trim(), baseSHA=git('rev-parse',`${base}^{commit}`).toString().trim();
  const allowed=runs.map(r=>'benchmark-results/'+r);
  const changes=git('diff','--name-only','-z',baseSHA,head).toString().split('\0').filter(Boolean);
  assert(changes.length && changes.every(p=>allowed.some(d=>p.startsWith(d+'/'))),'Results-only diff contains unintended paths');
  for(const dir of allowed)assert(changes.some(p=>p.startsWith(dir+'/')),`Selected run ${dir} has no changes`);
  const importerCommit=git('rev-parse',`${importerRef}^{commit}`).toString().trim();
  const importer=git('show',`${importerCommit}:dashboard/build-data.mjs`);
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'copilot-publication-gate-'));
  try {
    const records=[];
    for(const dir of allowed) {
      const folder=path.join(tmp,dir);fs.mkdirSync(folder,{recursive:true});
      const entries=git('ls-tree','-r','-z',head,'--',dir).toString().split('\0').filter(Boolean);
      const inputs={};
      for(const entry of entries) {
        const m=entry.match(/^(\d+) blob ([a-f0-9]+)\t(.+)$/s);assert(m && /^100(644|755)$/.test(m[1]),'Symlink/special packet artifact');
        const rel=m[3].slice(dir.length+1),target=path.join(folder,rel),bytes=git('cat-file','blob',m[2]);
        fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,bytes);
        if(!['publication-files.sha256','publication-validation.json'].includes(rel))inputs[rel]=hash(bytes);
      }
      const p=validate(folder);
      assert(p.config.run_id==='copilot-'+dir.split('/').at(-1),'Run ID/path mismatch');
      if(!writeRecords && fs.existsSync(path.join(folder,'publication-validation.json'))) {
        const proof=json(folder,'publication-validation.json');
        assert(proof.version===2 && proof.result==='PASS' && proof.run===p.config.run_id && proof.importer_sha256===hash(importer),'Contradictory publication validation record');
        assert.deepEqual(proof.inputs,inputs,'Stale publication validation record');
      }
      records.push({dir,p,inputs});
    }
    const script=path.join(tmp,'build-data.mjs');fs.writeFileSync(script,importer);
    execFileSync(process.execPath,[script,head],{cwd:repo,maxBuffer:32<<20});
    assert(fs.readFileSync(script).equals(importer),'Importer modified');
    const data=JSON.parse(fs.readFileSync(path.join(tmp,'data.js'),'utf8').replace(/^window.BENCH_DATA = /,'').trim().replace(/;$/,''));
    const checked=[];
    for(const {dir,p,inputs} of records) {
      const row=data.runs.find(r=>r.path===dir);assert(row,`Importer missing ${dir}`);
      const pretty={'claude-sonnet-4-6':'Claude Sonnet 4.6','gpt-6.1-sol':'GPT-6.1 Sol','gpt-6-luna':'GPT-6 Luna'};
      assert(row.model===(pretty[p.model] || p.model),'Imported observed model mismatch');
      assert.deepEqual(row.timing,{seconds:+p.timing.seconds.toFixed(1),method:p.timing.method},'Imported timing mismatch');
      assert.deepEqual(row.suites.map(s=>s.key).sort(),p.results.map(s=>s.key).sort(),'Spurious/missing imported suite');
      for(const s of p.results) {
        const imported=row.suites.find(x=>x.key===s.key);
        assert(imported.exit===String(s.exit) && imported.ok===(s.exit===0),'Imported suite exit/outcome mismatch');
        for(const [a,b] of [['pass','passed'],['fail','failed']])assert((imported[a] ?? null)===s[b],`Imported ${s.key} ${a} mismatch`);
        if(s.verdict)assert(imported.verdict===s.verdict,'Imported verdict mismatch');
      }
      for(const [a,b] of [['input','input_tokens'],['cached','cached_input_tokens'],['output','output_tokens'],['total','total_tokens'],['cost','total_cost_usd']])assert((row.tokens?.[a] ?? null)===p.tokens[b],`Imported tokens ${a} mismatch`);
      for(const c of p.quality_checks)assert((row.quality?.checks?.[c.name]?.pass ?? null)===c.pass,'Imported quality diagnostic mismatch');
      assert(Boolean(row.hReview)===p.reviewed,'Imported human review status mismatch');
      // Importer tracks only its four app paths; other changes stay visible in scope evidence.
      assert(row.changed.every(c=>p.changed.includes(c.path)),'Imported changed file absent from scope report');
      checked.push({run:p.config.run_id,directory:dir,result:'PASS',benchmark_outcome:row.status,inputs});
    }
    const result={version:2,result:'PASS',checked_commit:head,base_commit:baseSHA,importer_commit:importerCommit,importer_sha256:hash(importer),generated_dashboard_data:'temporary only; not committed',markdown:'generated-template subset: sections, tables, fences, local evidence links; canonical README equality',runs:checked};
    if(writeRecords) {
      assert(git('rev-parse','HEAD').toString().trim()===head,'Write records only for checked HEAD');
      for(const r of checked)for(const [file,expected] of Object.entries(r.inputs))assert(hash(fs.readFileSync(path.join(repo,r.directory,file)))===expected,`Worktree changed since check: ${file}`);
    }
    assert(!fs.existsSync(report),'Refusing to overwrite validation report');
    fs.writeFileSync(report,JSON.stringify(result,null,2)+'\n');
    if(writeRecords) {
      assert(git('rev-parse','HEAD').toString().trim()===head,'Write records only for checked HEAD');
      for(const r of checked) {
        const dest=path.join(repo,r.directory);
        for(const [file,expected] of Object.entries(r.inputs))assert(hash(fs.readFileSync(path.join(dest,file)))===expected,`Worktree changed since check: ${file}`);
        fs.writeFileSync(path.join(dest,'publication-validation.json'),JSON.stringify({version:2,result:'PASS',checked_commit:head,importer_commit:importerCommit,importer_sha256:hash(importer),run:r.run,benchmark_outcome:r.benchmark_outcome,inputs:r.inputs},null,2)+'\n');
        fs.writeFileSync(path.join(dest,'publication-files.sha256'),hashes(dest));
        validate(dest);
      }
    }
    return result;
  } finally { fs.rmSync(tmp,{recursive:true,force:true}); }
}
if(process.argv[1]===fileURLToPath(import.meta.url)) {
  const args=process.argv.slice(2),opts={runs:[]};
  for(let i=0;i<args.length;i++) {
    const k=args[i];
    if(k==='--write-records')opts.writeRecords=true;
    else { assert(['--repo','--ref','--base','--importer-ref','--run','--report'].includes(k),`Unknown option ${k}`); const v=args[++i];assert(v,'Missing option value');if(k==='--run')opts.runs.push(v);else opts[{'--importer-ref':'importerRef'}[k] || k.slice(2)]=v; }
  }
  const r=gate(opts);console.log(`PASS: ${r.runs.length} packets; genuine benchmark failures retained; report ${opts.report}`);
}
