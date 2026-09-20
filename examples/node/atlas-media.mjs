#!/usr/bin/env node
/** Teaching REST client. Local receipts, fixed credential origin, no POST retries.
 * Live model schema/price checks belong to the caller. Node >=22 recommended.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const BASE = 'https://api.atlascloud.ai/api/v1';
const ENDPOINTS = {image:'generateImage',video:'generateVideo',audio:'generateAudio','3d':'generateImage'};
const SUCCESS = new Set(['completed','succeeded']);
const FAILED = new Set(['failed','error','timeout','cancelled','canceled']);
const PENDING = new Set(['starting','queued','processing','running','pending']);
const plain = x => x !== null && typeof x === 'object' && !Array.isArray(x);
export function validateConfig(c) {
  if (!plain(c) || Object.keys(c).some(k=>!['kind','model','params'].includes(k))) throw Error('Only kind/model/params are supported');
  if (!Object.hasOwn(ENDPOINTS,c.kind)) throw Error('Unsupported kind');
  if (typeof c.model!=='string' || !c.model || /\s|[\u0000-\u001f]|replace_|placeholder|替换|填入/i.test(c.model) || c.model.startsWith('-')) throw Error('Use an actual discovered model ID');
  if (!plain(c.params) || !Object.keys(c.params).length) throw Error('Model params must be a nonempty object');
  for (const k of Object.keys(c.params)) if (['model','authorization','api_key','token','access_token'].includes(k.toLowerCase())) throw Error('Reserved field or credential in params');
  const walk = x => {
    if (typeof x==='string' && x.startsWith('@')) throw Error('This REST example needs pre-authorized URLs, not local @file paths');
    if (typeof x==='number' && !Number.isFinite(x)) throw Error('Non-finite value');
    if (x && typeof x==='object') Object.values(x).forEach(walk);
  }; walk(c);
  return c;
}
export function requestBody(c) { validateConfig(c); return {...c.params,model:c.model}; }
function stable(x) {
  if (Array.isArray(x)) return x.map(stable);
  if (plain(x)) return Object.fromEntries(Object.keys(x).sort().map(k=>[k,stable(x[k])]));
  return x;
}
const hash = x => createHash('sha256').update(JSON.stringify(stable(x))).digest('hex');
export async function save(file,data,exclusive=false) {
  const text=JSON.stringify(data,null,2)+'\n';
  if (exclusive) { const h=await fs.open(file,'wx',0o600); try {await h.writeFile(text);await h.sync();} finally {await h.close();} return; }
  const tmp=file+`.tmp-${process.pid}-${Date.now()}`;
  await save(tmp,data,true); await fs.rename(tmp,file);
}
export async function read(file) {
  if ((await fs.stat(file)).size > 4*1024*1024) throw Error('Input exceeds 4 MiB');
  return JSON.parse(await fs.readFile(file,'utf8'));
}
export async function prepare(config,dir) {
  validateConfig(config);await fs.mkdir(path.dirname(dir),{recursive:true});await fs.mkdir(dir,{mode:0o700});
  const plan={format:1,config,config_sha256:hash(config)};
  await save(path.join(dir,'plan.json'),plan,true);return plan;
}
export async function loadPlan(dir) {
  const p=await read(path.join(dir,'plan.json'));validateConfig(p.config);
  if(hash(p.config)!==p.config_sha256)throw Error('Plan modified; do not change an existing operation');return p;
}
export function resultOf(envelope) {
  const task=plain(envelope?.data)?envelope.data:envelope;
  const id=typeof task?.id==='string' && task.id.trim()===task.id && task.id.length>0 && !/[\s\u0000-\u001f]/.test(task.id) ? task.id : null;
  const s=typeof task?.status==='string'?task.status.toLowerCase():'';
  const state=SUCCESS.has(s)?'remote_succeeded':FAILED.has(s)?'remote_failed':PENDING.has(s)?'pending':'unknown';
  return {prediction_id:id,state};
}
async function request(method,endpoint,body,key,fetchFn,timeoutMs) {
  if (!key || typeof key!=='string') throw Error('ATLASCLOUD_API_KEY is required');
  const headers={'Accept':'application/json','Authorization':`Bearer ${key}`};
  if (body)headers['Content-Type']='application/json';
  // Reject redirects: never forward credentials to a downloaded output host.
  const response=await fetchFn(BASE+endpoint,{method,headers,body:body?JSON.stringify(body):undefined,
    redirect:'error',signal:AbortSignal.timeout(timeoutMs)});
  const text=await response.text();
  if(text.length>4*1024*1024)throw Error('Response exceeds local receipt limit; preserve unknown acceptance');
  let payload=null;try{payload=JSON.parse(text);}catch{}
  const retry=Number(response.headers.get('retry-after'));
  return {http_status:response.status,body:payload,raw:payload===null?text:null,
    retry_after_seconds:Number.isFinite(retry)&&retry>0?Math.min(retry,60):null};
}
export async function submit(dir,{approve=false,key,fetchFn=fetch,timeoutMs=30000}={}) {
  const plan=await loadPlan(dir);
  if(!approve)throw Error('Explicit --approve is required for a billable POST');
  if(!key)throw Error('Missing API key');
  await save(path.join(dir,'attempt.json'),{started_at:new Date().toISOString(),config_sha256:plan.config_sha256},true);
  let record;
  try { record=await request('POST','/model/'+ENDPOINTS[plan.config.kind],requestBody(plan.config),key,fetchFn,timeoutMs); }
  catch {record={http_status:null,body:null,error:'Request or receipt failed; acceptance is unknown. Do not repeat POST.'};}
  await save(path.join(dir,'submit-response.json'),record);
  const state={...resultOf(record.body),http_status:record.http_status};
  if(!state.prediction_id)state.state='unknown';
  await save(path.join(dir,'state.json'),state);return state;
}
export async function get(dir,{key,fetchFn=fetch,timeoutMs=30000}={}) {
  await loadPlan(dir);const known=await read(path.join(dir,'state.json'));
  const id=known.prediction_id;
  if(typeof id!=='string'||!id||/[\s\u0000-\u001f]/.test(id))throw Error('No reliable ID; reconcile without submitting');
  let record;
  try {record=await request('GET','/model/prediction/'+encodeURIComponent(id),undefined,key,fetchFn,timeoutMs);}
  catch {record={http_status:null,body:null,error:'GET failed; retain the original task ID'};}
  const parsed=resultOf(record.body);
  let state=parsed.state;
  if(parsed.prediction_id && parsed.prediction_id!==id)state='unknown';
  // Authentication failures are not an opportunity to switch accounts.
  if([401,403].includes(record.http_status))state='unknown';
  const obs={...record,prediction_id:id,state};
  await fs.mkdir(path.join(dir,'observations'),{recursive:true});
  await save(path.join(dir,'observations',`${Date.now()}-${process.hrtime.bigint()}.json`),obs,true);
  return obs;
}
export async function wait(dir,{key,fetchFn=fetch,maxSeconds=120,intervalSeconds=3}={}) {
  if(!Number.isFinite(maxSeconds)||maxSeconds<1||maxSeconds>3600)throw Error('wait seconds must be 1..3600');
  const deadline=Date.now()+maxSeconds*1000;let delay=Math.max(1,intervalSeconds);let last;
  while(Date.now()<deadline){
    const left=deadline-Date.now();
    last=await get(dir,{key,fetchFn,timeoutMs:Math.max(1,Math.min(30000,left))});
    if(['remote_succeeded','remote_failed'].includes(last.state))return last;
    if([401,403,404].includes(last.http_status))return last;
    if(last.state==='unknown' && last.http_status>=200 && last.http_status<300)return last;
    const ms=Math.min((last.retry_after_seconds??delay)*1000,Math.max(0,deadline-Date.now()));
    if(ms>0)await new Promise(r=>setTimeout(r,ms));delay=Math.min(15,delay*1.5);
  }
  return {...last,local_wait_timed_out:true};
}
async function main(){
  const [action,...args]=process.argv.slice(2);let dir,config,approve=false,seconds=120;
  for(let i=0;i<args.length;i++){
    if(args[i]==='--run-dir')dir=args[++i];else if(args[i]==='--config')config=args[++i];
    else if(args[i]==='--approve')approve=true;else if(args[i]==='--seconds')seconds=Number(args[++i]);
    else throw Error('Unknown argument: '+args[i]);
  }
  if(!dir)throw Error('--run-dir is required');dir=path.resolve(dir);let out;
  const key=process.env.ATLASCLOUD_API_KEY;
  if(action==='prepare'){if(!config)throw Error('--config is required');out=await prepare(await read(config),dir);}
  else if(action==='preview'){const p=await loadPlan(dir);out={body:requestBody(p.config),note:'Local request-shape preview only. No live schema validation, quotation or API call.'};}
  else if(action==='submit')out=await submit(dir,{approve,key});
  else if(action==='get')out=await get(dir,{key});
  else if(action==='wait')out=await wait(dir,{key,maxSeconds:seconds});
  else throw Error('Use prepare/preview/submit/get/wait');
  console.log(JSON.stringify(out,null,2));
  process.exitCode=out.state==='pending'?3:out.state==='remote_failed'?4:out.state==='unknown'?2:0;
}
if(process.argv[1] && import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
  main().catch(e=>{console.error(`Error: ${e.message}. Preserve existing records; never delete attempt.json to repeat a submission.`);process.exitCode=2;});
}
