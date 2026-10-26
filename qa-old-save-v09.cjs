const assert=require('node:assert/strict'),fs=require('fs');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
 const targets=await (await fetch('http://127.0.0.1:18898/json')).json();
 const ws=new WebSocket(targets.find(x=>x.type==='page').webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 const pending=new Map(),errors=[];let id=0;
 ws.onmessage=e=>{const x=JSON.parse(e.data.toString());if(x.method==='Runtime.exceptionThrown')errors.push(x.params.exceptionDetails.text);if(x.id&&pending.has(x.id)){const p=pending.get(x.id);pending.delete(x.id);x.error?p.reject(Error(JSON.stringify(x.error))):p.resolve(x.result)}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}))});
 const ev=async expression=>{
  const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
  if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails).slice(0,650));
  return r.result.value;
 };
 await send('Page.enable');await send('Runtime.enable');
 const url='http://127.0.0.1:18899/layout-test/index.html?v=old-save-qa-20261026';
 const boot=async()=>{
  await send('Page.navigate',{url});
  for(let i=0;i<80;i++){await wait(250);const ok=await ev('!!window.__A18_SCENE_STUDY__?.ready()');if(ok)return;}
  throw Error('BOOT_TIMEOUT');
 };
 await boot();
 const before=await ev('('+async function(){
  const P2=window.A18P2Store;
  const old=await P2.load(),next=P2.copy(old);
  next.revision=old.revision+1;next.galleryIndex=0;next.pos={x:326,y:425,dir:'up',stride:0};
  const oldGeom=[[40,58,140,135],[184,58,284,135],[430,58,530,135]];
  for(let i=0;i<3;i++){
   const f=next.fixtures.find(v=>v.id==='frame-0-'+i);
   if(!f)throw Error('E_FIXTURE_MISSING');
   const [x1,y1,x2,y2]=oldGeom[i];
   Object.assign(f,{x:(x1+x2)/2,y:(y1+y2)/2,width:x2-x1,height:y2-y1,installation:'wall'});
   f.workId=null;
  }
  next.carrying=null;next.works=[];
  const id='old-photo-'+Date.now();
  const originalBlob=await (await fetch('assets/sample0.png')).blob();
  const art={id,title:'保存済みQA作品',notes:'old content must survive',complete:null,
   registered:'2026-10-26',pieces:100,preferredShape:'landscape',
   thumbnail:null,displaySrc:null,fixtureId:'frame-0-0',
   originalBlob};
  next.works.push(art);
  next.fixtures.find(v=>v.id===art.fixtureId).workId=id;
  P2.validate(next);await P2.commit(old.revision,next);
  return {revision:next.revision,id,blobSize:art.originalBlob.size,storedLeftX:next.fixtures.find(f=>f.id==='frame-0-0').x,works:next.works.length};
 }.toString()+')()');
 console.log('SYNTHETIC_OLD_V3',before);
 await boot();
 const after=await ev('('+async function(){
  const P2=window.A18P2Store,s=await P2.load();
  P2.validate(s);
  const old=s.works.find(w=>w.id&&w.id.startsWith('old-photo-'));
  return {revision:s.revision,left:s.fixtures.find(x=>x.id==='frame-0-0').x,
   right:s.fixtures.find(x=>x.id==='frame-0-1').x,
   front:s.fixtures.find(x=>x.id==='frame-0-2').x,
   firstWorkId:s.fixtures.find(x=>x.id==='frame-0-0').workId,
   workId:old?.id,notes:old?.notes,blobSize:old?.originalBlob.size,
   workCount:s.works.length,
   roomRects:window.__A18_SCENE_STUDY__.state().frameRects,
   status:window.__A18_SCENE_STUDY__.ready()};
 }.toString()+')()');
 console.log('UPGRADED_WITHOUT_DATA_LOSS',after);
 assert(after.status);
 assert.equal(after.revision,before.revision+1);
 assert.equal(after.left,116);assert.equal(after.right,440);assert.equal(after.front,459.5);
 assert.equal(after.firstWorkId,before.id);assert.equal(after.workId,before.id);
 assert.equal(after.notes,'old content must survive');
 assert.equal(after.blobSize,before.blobSize);assert.equal(after.workCount,1);
 assert.equal(after.roomRects[0][0],43);
 assert.equal(after.roomRects[1][0],374);
 assert.equal(after.roomRects[2][0],421);
 assert.equal(errors.length,0);
 fs.writeFileSync(process.env.TEMP+'\\a18-v09-game-integrated-QA-20261026\\old-save-qa.json',JSON.stringify({before,after,errors},null,2));
 ws.close();console.log('QA_OLD_SAVE_PHOTO_PRESERVED_PASS');
}
main().catch(e=>{console.error('QA_OLD_SAVE_PHOTO_PRESERVED_FAIL',e);process.exitCode=1;});
