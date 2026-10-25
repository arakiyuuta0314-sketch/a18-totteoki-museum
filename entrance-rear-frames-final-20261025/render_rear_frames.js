"use strict";
const ART={
 left:{outer:[76,50,201,157],inner:[84,61,194,144],col:[0,20,48,77,105,125],row:[0,25,47,71,87,107]},
 right:{outer:[365,50,468,157],inner:[373,61,460,144],col:[0,17,40,65,86,103],row:[0,25,47,71,87,107]}
};
const files=["entrance_bg_without_rear_frames.png","frame_left_5x5.png","frame_right_5x5.png",
 "empty_left.png","empty_right.png","demo_photo_left.jpg","demo_photo_right.jpg","butler-front-00.png","curator-front-00.png"];
const loaded={};
const load=()=>Promise.all(files.map(name=>new Promise((resolve,reject)=>{
 const im=new Image();im.onload=()=>{loaded[name]=im;resolve()};im.onerror=()=>reject(Error("Missing image: "+name));im.src=name
})));
const dims=(edges,target)=>{
 const n=edges.slice(1).map((e,i)=>e-edges[i]);
 const d=target-edges[5];
 const out=[n[0],n[1]+Math.floor(d/2),n[2],n[3]+d-Math.floor(d/2),n[4]];
 if(out.some(v=>v<=0))throw Error("Frame too small");
 return out;
};
function drawFrame(ctx,name,geo,x,y,w,h){
 const orig=loaded["frame_"+name+"_5x5.png"];
 const dx=dims(geo.col,w),dy=dims(geo.row,h);
 let top=y;
 for(let j=0;j<5;j++){
  let left=x;
  for(let i=0;i<5;i++){
   const sw=geo.col[i+1]-geo.col[i],sh=geo.row[j+1]-geo.row[j];
   ctx.drawImage(orig,geo.col[i],geo.row[j],sw,sh,left,top,dx[i],dy[j]);
   left+=dx[i];
  }
  top+=dy[j];
 }
}
function drawPhoto(ctx,img,x,y,w,h){
 const scale=Math.max(w/img.width,h/img.height);
 const sw=w/scale,sh=h/scale;
 ctx.drawImage(img,(img.width-sw)/2,(img.height-sh)/2,sw,sh,x,y,w,h);
}
function drawSprite(ctx,key,x,foot,width){
 const im=loaded[key],height=Math.round(width*im.height/im.width);
 ctx.imageSmoothingEnabled=false;ctx.drawImage(im,Math.round(x-width/2),foot-height,width,height);ctx.imageSmoothingEnabled=true;
}
function render(leftScale=1,rightScale=1,photo=true){
 const c=document.querySelector("#viewer"),ctx=c.getContext("2d",{alpha:false});
 ctx.resetTransform();ctx.scale(2,2);ctx.imageSmoothingEnabled=true;
 ctx.drawImage(loaded["entrance_bg_without_rear_frames.png"],0,0);
 for(let name of ["left","right"]){
  const geo=ART[name],s=name==="left"?leftScale:rightScale;
  const [l,t,r,b]=geo.outer,[il,it,ir,ib]=geo.inner;
  const w=Math.round((r-l)*s),h=Math.round((b-t)*s);
  const x=l+Math.floor((r-l-w)/2),y=t+Math.floor((b-t-h)/2);
  const px=x+il-l,py=y+it-t,pw=w-(il-l)-(r-ir),ph=h-(it-t)-(b-ib);
  if(photo)drawPhoto(ctx,loaded["demo_photo_"+name+".jpg"],px,py,pw,ph);
  else ctx.drawImage(loaded["empty_"+name+".png"],px,py,pw,ph);
  drawFrame(ctx,name,geo,x,y,w,h);
 }
 drawSprite(ctx,"butler-front-00.png",140,371,43);
 drawSprite(ctx,"curator-front-00.png",287,366,35);
}
load().then(()=>{document.querySelector("#loading").hidden=true;document.querySelector("#viewer").hidden=false;
 const left=document.querySelector("#leftScale"),right=document.querySelector("#rightScale"),photos=document.querySelector("#showPhoto");
 const update=()=>{document.querySelector("#leftPct").textContent=left.value+"%";document.querySelector("#rightPct").textContent=right.value+"%";render(left.value/100,right.value/100,photos.checked)};
 [left,right,photos].forEach(el=>el.addEventListener("input",update));
 document.querySelector("#reset").addEventListener("click",()=>{left.value=right.value=100;photos.checked=true;update()});
 update();window.A18RearFrameQA={ready:true,render,state:()=>({left:Number(left.value),right:Number(right.value),photos:photos.checked})};
}).catch(e=>{document.querySelector("#loading").textContent="読み込みエラー："+e.message;throw e});
