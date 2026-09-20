import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {validateConfig,requestBody,prepare,submit,get,read,loadPlan,resultOf} from '../examples/node/atlas-media.mjs';
const config={kind:'image',model:'test-provider/fake-model',params:{prompt:'Offline test only'}};
const setup=async()=>{const root=await fs.mkdtemp(path.join(os.tmpdir(),'atlas-node-test-'));const dir=path.join(root,'run');await prepare(config,dir);return {root,dir};};
const cleanup=x=>fs.rm(x.root,{recursive:true,force:true});
const reply=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json'}});

test('REST body is flattened and the selected model stays fixed',()=>assert.deepEqual(requestBody(config),{prompt:'Offline test only',model:config.model}));
test('placeholders and reserved params rejected',()=>{
 assert.throws(()=>validateConfig({...config,model:'REPLACE_MODEL'}));
 assert.throws(()=>validateConfig({...config,params:{model:'evil'}}));
 assert.throws(()=>validateConfig({...config,params:{image:'@local.png'}}));
});
test('pure preview does not need API credentials',async()=>{const x=await setup();try{assert.deepEqual((await loadPlan(x.dir)).config,config);}finally{await cleanup(x);}});
test('submit requires approval before network or marker',async()=>{const x=await setup();let calls=0;try{await assert.rejects(()=>submit(x.dir,{key:'test-not-a-real-key',fetchFn:async()=>{calls++;}}));assert.equal(calls,0);await assert.rejects(()=>fs.stat(path.join(x.dir,'attempt.json')));}finally{await cleanup(x);}});
test('one POST stores ID and never follows redirect; repeat is blocked',async()=>{
 const x=await setup();let calls=0;try{
 const fake=async(url,options)=>{calls++;assert.equal(url,'https://api.atlascloud.ai/api/v1/model/generateImage');assert.equal(options.method,'POST');assert.equal(options.redirect,'error');return reply({data:{id:'p1',status:'processing'}});};
 assert.equal((await submit(x.dir,{approve:true,key:'test-not-a-real-key',fetchFn:fake})).prediction_id,'p1');
 await assert.rejects(()=>submit(x.dir,{approve:true,key:'test-not-a-real-key',fetchFn:fake}));assert.equal(calls,1);
 }finally{await cleanup(x);}
});
test('network POST error remains unknown and is not retried',async()=>{const x=await setup();let calls=0;try{const r=await submit(x.dir,{approve:true,key:'test-not-a-real-key',fetchFn:async()=>{calls++;throw Error('offline');}});assert.equal(r.state,'unknown');assert.equal(calls,1);assert.ok(await fs.stat(path.join(x.dir,'attempt.json')));}finally{await cleanup(x);}});
test('HTTP 500 with a terminal failed task stays terminal',async()=>{const x=await setup();try{await submit(x.dir,{approve:true,key:'test',fetchFn:async()=>reply({data:{id:'p1',status:'starting'}})});const r=await get(x.dir,{key:'test',fetchFn:async()=>reply({data:{id:'p1',status:'failed'}},500)});assert.equal(r.state,'remote_failed');assert.equal(r.http_status,500);}finally{await cleanup(x);}});
test('successful GET for the wrong task is not accepted',async()=>{const x=await setup();try{await submit(x.dir,{approve:true,key:'test',fetchFn:async()=>reply({data:{id:'p1',status:'starting'}})});assert.equal((await get(x.dir,{key:'test',fetchFn:async()=>reply({data:{id:'p2',status:'completed'}})})).state,'unknown');}finally{await cleanup(x);}});
test('missing ID blocks GET before fake fetch is called',async()=>{const x=await setup();let calls=0;try{await submit(x.dir,{approve:true,key:'test',fetchFn:async()=>reply({message:'unexpected'})});await assert.rejects(()=>get(x.dir,{key:'test',fetchFn:async()=>{calls++;}}));assert.equal(calls,0);}finally{await cleanup(x);}});
test('receipt HTTP success is not generation success',()=>{assert.equal(resultOf({data:{id:'p1',status:'queued'}}).state,'pending');assert.equal(resultOf({data:{id:'p1',status:'unrecognized'}}).state,'unknown');});
test('tampered plan blocked',async()=>{const x=await setup();try{const p=await read(path.join(x.dir,'plan.json'));p.config.params.prompt='changed';await fs.writeFile(path.join(x.dir,'plan.json'),JSON.stringify(p));await assert.rejects(()=>loadPlan(x.dir));}finally{await cleanup(x);}});
test('non-JSON receipt preserves unknown outcome',async()=>{const x=await setup();try{const r=await submit(x.dir,{approve:true,key:'test',fetchFn:async()=>new Response('<html>bad</html>',{status:502})});assert.equal(r.state,'unknown');assert.equal((await read(path.join(x.dir,'submit-response.json'))).raw,'<html>bad</html>');}finally{await cleanup(x);}});
