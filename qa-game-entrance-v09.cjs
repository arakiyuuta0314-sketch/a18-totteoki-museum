const fs=require('fs'),assert=require('assert/strict');
const OUTPUT=process.env.TEMP+'\\a18-v09-game-integrated-QA-20261026';
const nap=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
 const targets=await (await fetch('http://127.0.0.1:18898/json')).json();
 const page=targets.find(x=>x.type==='page');
 assert(page?.webSocketDebuggerUrl,'page target missing');
 const ws=new WebSocket(page.webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 let seq=0;
 const pending=new Map(),errors=[],netErrors=[];
 ws.onmessage=e=>{
  const data=JSON.parse(e.data.toString());
  if(data.method==='Runtime.exceptionThrown')errors.push(data.params.exceptionDetails.text);
  if(data.method==='Network.loadingFailed'&&!data.params.canceled)netErrors.push(data.params.errorText);
  if(data.id){const p=pending.get(data.id);if(p){pending.delete(data.id);data.error?p.reject(Error(JSON.stringify(data.error))):p.resolve(data.result);}}
 };
 const send=(method,params={})=>new Promise((resolve,reject)=>{
  const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));
 });
 async function evaluate(expression){
  const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
  if(r.exceptionDetails)throw Error('JS exception: '+r.exceptionDetails.text);
  return r.result.value;
 }
 await send('Page.enable');await send('Runtime.enable');await send('Network.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:2,mobile:true});
 await send('Page.navigate',{url:'http://127.0.0.1:18899/layout-test/index.html?v=v09-regression-local'});
 let boot=null;
 for(let i=0;i<100;i++){
  await nap(450);
  boot=await evaluate("({ready:!!window.__A18_SCENE_STUDY__?.ready(), entrance:!!window.A18Entrance?.ready(), document:document.readyState})");
  if(boot.ready&&boot.entrance)break;
 }
 console.log('BOOT',JSON.stringify(boot));
 assert(boot.ready&&boot.entrance,'game never became ready');
 async function inspect(){
  const st=window.__A18_SCENE_STUDY__.state();
  const base=window.A18Entrance;
  const canvas=document.createElement('canvas');canvas.width=546;canvas.height=483;
  const ctx=canvas.getContext('2d',{willReadFrequently:true});
  base.background(ctx);
  const snapshot=ctx.getImageData(0,0,546,483).data.slice();
  const proof=[];
  const photo=new Image();photo.src='assets/sample0.png';await photo.decode();
  for(let index=0;index<3;index++){
   base.background(ctx);
   const f=st.fixtures.find(x=>x.id==='frame-0-'+index);
   if(!f)throw Error('E_QA_MISSING_FRAME_'+index);
   base.frame(ctx,f,photo);
   const actual=ctx.getImageData(0,0,546,483).data;
   const m=new Image();
   m.src=['assets/entrance/v09/rear_left_photo_mask_v09.png','assets/entrance/v09/rear_right_photo_mask_v09.png','assets/entrance/v09/front_photo_mask_v09.png'][index];
   await m.decode();const maskC=document.createElement('canvas');maskC.width=546;maskC.height=483;
   const mctx=maskC.getContext('2d',{willReadFrequently:true});mctx.drawImage(m,0,0);
   const mask=mctx.getImageData(0,0,546,483).data;
   let inside=0,outside=0;
   for(let i=0;i<546*483;i++){
    const off=4*i;
    if(actual[off]===snapshot[off]&&actual[off+1]===snapshot[off+1]&&actual[off+2]===snapshot[off+2])continue;
    if(mask[off]>0)inside++;else outside++;
   }
   proof.push({index,inside,outside,fixture:[f.x,f.y],mode:f.imageMode});
  }
  return {ready:base.ready(),assets:base.assetCount(),state:{scene:st.scene,room:st.galleryIndex,progression:st.unlockedRooms,frameRects:st.frameRects,interactions:st.interactionAnchors,obstacles:st.obstacles},placement:window.__A18_SCENE_STUDY__.validateLayout(0),proof,portals:st.links,css:{overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth}};
 }
 const res=await evaluate('('+inspect.toString()+')()');
 console.log('DEEP_QA',JSON.stringify(res));
 assert.equal(res.assets,4);
 for(const p of res.proof){assert(p.inside>1500,'photo not visible '+p.index);assert.equal(p.outside,0,'photo leaked outside mask '+p.index);}
 assert.equal(res.css.overflow,false,'horizontal overflow');
 assert.equal(res.placement.ok,true,'invalid entrance fixture placement');
 const movement=await evaluate('(()=>{const q=window.__A18_SCENE_STUDY__; return {rearLeft:q.canMove(150,227),rearRight:q.canMove(368,228),front:q.canMove(382,358),leftPortal:q.canMove(39,454),rightPortal:q.canMove(505,454),insidePartition:q.canMove(437,320),lockedNorth:q.canMove(284,190),butlerBody:q.canMove(139,341)};})()');
 console.log('COLLISION_QA',JSON.stringify(movement));
 for(const k of ['rearLeft','rearRight','front','leftPortal','rightPortal'])assert.equal(movement[k],true,'unreachable '+k);
 for(const k of ['insidePartition','lockedNorth','butlerBody'])assert.equal(movement[k],false,'collision leak '+k);
 const galleries=await evaluate('(async()=>{const canvas=document.createElement("canvas");canvas.width=589;canvas.height=482;const ctx=canvas.getContext("2d");const p={unlockedThroughLevel:6};const frames=window.A18Layout.defaults();const proof=[];for(let room=1;room<6;room++){await Promise.all([window.A18P3Gallery.prepare(room),window.A18P5Decorations.prepare(room,p)]);ctx.clearRect(0,0,589,482);window.A18P3Gallery.background(ctx,room,p);for(const f of frames.filter(x=>x.roomId===room))window.A18P3Gallery.frame(ctx,f,null,frames.filter(x=>x.roomId===room));const data=ctx.getImageData(0,0,589,482).data;let opaque=0;for(let i=3;i<data.length;i+=4){if(data[i])opaque++;}proof.push({room,opaque});}return proof;})()');
 console.log('GALLERY_02_TO_06_QA',JSON.stringify(galleries));
 assert.equal(galleries.length,5);
 for(const g of galleries)assert(g.opaque>100000,'gallery failed '+g.room);
 const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
 fs.writeFileSync(OUTPUT+'\\game-initial-390x844.png',Buffer.from(shot.data,'base64'));
 fs.writeFileSync(OUTPUT+'\\qa-results.json',JSON.stringify({boot,res,errors,netErrors},null,2));
 console.log('CHROME_EXCEPTIONS',JSON.stringify(errors),'NETWORK_ERRORS',JSON.stringify(netErrors));
 assert.equal(errors.length,0);assert.equal(netErrors.length,0);
 ws.close();console.log('A18_ENTRANCE_V09_GAME_QA_PASS');
}
main().catch(e=>{console.error('A18_ENTRANCE_V09_GAME_QA_FAIL',e);process.exitCode=1;});
