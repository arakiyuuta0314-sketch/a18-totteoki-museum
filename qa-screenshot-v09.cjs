const fs=require('fs'),assert=require('node:assert/strict');
async function run(){
 const target=(await (await fetch('http://127.0.0.1:18898/json')).json()).find(x=>x.type==='page');
 const ws=new WebSocket(target.webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 let n=0;const pending=new Map();
 ws.onmessage=e=>{const m=JSON.parse(e.data.toString());if(m.id&&pending.has(m.id)){const h=pending.get(m.id);pending.delete(m.id);m.error?h.reject(Error(JSON.stringify(m.error))):h.resolve(m.result);}};
 const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++n;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 await call('Page.enable');await call('Runtime.enable');
 const ready=await call('Runtime.evaluate',{expression:"({ready:window.__A18_SCENE_STUDY__.ready(),works:window.__A18_SCENE_STUDY__.state().works.length,scene:window.__A18_SCENE_STUDY__.state().scene})",returnByValue:true});
 console.log('GAME',ready.result.value);
 assert(ready.result.value.ready);
 const out=process.env.TEMP+'\\a18-v09-game-integrated-QA-20261026\\';
 const r=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
 fs.writeFileSync(out+'photo-migration-real-render.png',Buffer.from(r.data,'base64'));
 const check=await call('Runtime.evaluate',{expression:'('+function(){
  const f=window.__A18_SCENE_STUDY__.state().fixtures.filter(f=>f.roomId===0);
  const c=document.createElement('canvas');c.width=546;c.height=483;const ctx=c.getContext('2d',{willReadFrequently:true});
  const out=[];
  for(let index=0;index<3;index++){
   ctx.clearRect(0,0,546,483);
   window.A18Entrance.markSlot(ctx,f.find(v=>v.id==='frame-0-'+index));
   const d=ctx.getImageData(0,0,546,483).data;
   let x0=999,y0=999,x1=-1,y1=-1,count=0;
   for(let y=0;y<483;y++)for(let x=0;x<546;x++){
    const i=(y*546+x)*4;if(d[i+3]<15)continue;
    x0=Math.min(x0,x);y0=Math.min(y0,y);
    x1=Math.max(x1,x);y1=Math.max(y1,y);count++;
   }
   out.push({index,bounds:[x0,y0,x1,y1],pixels:count});
  }
  return out;
 }.toString()+')()',awaitPromise:true,returnByValue:true});
 console.log('MARKERS',check.result.value);
 const m=check.result.value;
 assert(m[0].bounds[0]>=38&&m[0].bounds[2]<=197);
 assert(m[1].bounds[0]>=369&&m[1].bounds[2]<=513);
 assert(m[2].bounds[0]>=416&&m[2].bounds[2]<=498);
 assert(m.every(v=>v.pixels>300));
 fs.writeFileSync(out+'markers-qa.json',JSON.stringify(m,null,2));
 ws.close();console.log('VISUAL_MARKER_QA_PASS');
}
run().catch(e=>{console.error(e);process.exitCode=1;});
