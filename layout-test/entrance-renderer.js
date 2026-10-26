/* A18 entrance v09 approved frame-OFF architecture.
   Photo masks: back-wall derived from v09 blank paper, front from canonical H v06.
   No baked actors, no old v0.3 fixtures/frames, no saved-data writes.
*/
(()=>{'use strict';
const ROOT='assets/entrance/v09/';
const SIZE=[546,483], PHOTO_W=220,PHOTO_H=166;
const FILES={
 background:'entrance_architecture_v09.png',
 rear_left:'rear_left_photo_mask_v09.png',
 rear_right:'rear_right_photo_mask_v09.png',
 front:'front_photo_mask_v09.png'
};
const PANELS=[
 {name:'rear_left',rect:[43,64,189,143]},
 {name:'rear_right',rect:[374,64,506,143]},
 {name:'front',rect:[421,195,494,326]}
];
// Inverse canonical homography from entrance-wall-plane-v07-20261026/single_H_geometry.json.
// Canonical source picture window: [84,61]..[194,144] maps to front trapezoid.
const FRONT_H_INV=[
 [2.2582576554692726,-0.02449889664425458,-854.9873467700153],
 [-0.2933780477833784,1.015847991558277,-7.050709650349285],
 [0.0032571841573975214,-0.000467047182836571,-0.18282765194690226]
];
const images=new Map(),masks=new Map();
const prepared=new WeakMap();
let ready=false;
function ensureReady(){if(!ready)throw Error('E_ENTRANCE_V09_NOT_READY');}
function blankCanvas(w,h){
 const c=document.createElement('canvas');c.width=w;c.height=h;return c;
}
async function load(filename){
 const im=new Image();
 await new Promise((resolve,reject)=>{
  im.onload=resolve;
  im.onerror=()=>reject(Error('E_ENTRANCE_V09_IMAGE '+filename));
  im.src=ROOT+filename;
 });
 if(im.naturalWidth!==SIZE[0]||im.naturalHeight!==SIZE[1])throw Error('E_ENTRANCE_V09_SIZE '+filename);
 return im;
}
async function init(){
 if(ready)return;
 for(const [key,file] of Object.entries(FILES)){
  const im=await load(file);images.set(key,im);
 }
 for(const p of PANELS){
  const c=blankCanvas(...SIZE),cx=c.getContext('2d',{willReadFrequently:true});
  cx.drawImage(images.get(p.name),0,0);
  // Source masks are grayscale RGB with opaque alpha. Pixel intensity is mask.
  const data=cx.getImageData(0,0,...SIZE).data,m=new Uint8Array(SIZE[0]*SIZE[1]);
  let count=0;
  for(let i=0;i<m.length;i++){m[i]=data[i*4];if(m[i])count++;}
  if(count<5000||count>20000)throw Error('E_ENTRANCE_V09_MASK '+p.name+' '+count);
  masks.set(p.name,m);
 }
 ready=true;
}
function background(ctx){
 ensureReady();
 ctx.save();ctx.imageSmoothingEnabled=false;
 ctx.drawImage(images.get('background'),0,0);ctx.restore();
}
function foreground(ctx){ensureReady(); /* partition foreground already in canonical v09 */ }
function panelFor(f){
 if(f?.roomId!==0)throw Error('E_ENTRANCE_V09_ROOM');
 const i=Number(f.id?.split('-')[2]);
 if(!Number.isInteger(i)||i<0||i>=PANELS.length||f.id!==`frame-0-${i}`)throw Error('E_ENTRANCE_V09_FRAME '+f.id);
 return PANELS[i];
}
function frameGeometry(f,img){
 const p=panelFor(f),r=p.rect;
 return {outer:{x:r[0],y:r[1],w:r[2]-r[0],h:r[3]-r[1]},
         inner:{x:r[0],y:r[1],w:r[2]-r[0],h:r[3]-r[1]},shape:'landscape'};
}
function photograph(img,f){
 const c=blankCanvas(PHOTO_W,PHOTO_H),ctx=c.getContext('2d',{willReadFrequently:true});
 ctx.fillStyle='#e7d0aa';ctx.fillRect(0,0,PHOTO_W,PHOTO_H);
 const w=img.naturalWidth,h=img.naturalHeight;
 if(!w||!h)throw Error('E_ENTRANCE_V09_BAD_PHOTO');
 const mode=f.imageMode||'cover';
 if(!['cover','contain','custom'].includes(mode))throw Error('E_ENTRANCE_V09_MODE');
 const fit=mode==='contain'?Math.min(PHOTO_W/w,PHOTO_H/h):Math.max(PHOTO_W/w,PHOTO_H/h);
 const scalar=mode==='custom'?(f.imageScale??1):1;
 const dw=w*fit*scalar,dh=h*fit*scalar;
 const ox=mode==='custom'?((PHOTO_W-dw)*(f.imageX??0)/2):0;
 const oy=mode==='custom'?((PHOTO_H-dh)*(f.imageY??0)/2):0;
 ctx.imageSmoothingEnabled=true;
 ctx.drawImage(img,(PHOTO_W-dw)/2+ox,(PHOTO_H-dh)/2+oy,dw,dh);
 return ctx.getImageData(0,0,PHOTO_W,PHOTO_H).data;
}
function photoOverlay(img,f,p){
 const key=[p.name,f.imageMode,f.imageScale,f.imageX,f.imageY].join('|');
 let entries=prepared.get(img);
 if(!entries){entries=new Map();prepared.set(img,entries);}
 if(entries.has(key))return entries.get(key);
 const photo=photograph(img,f),mask=masks.get(p.name),out=blankCanvas(...SIZE);
 const ctx=out.getContext('2d'),r=p.rect,output=ctx.createImageData(...SIZE);
 const source=output.data,W=SIZE[0];
 const isFront=p.name==='front';
 for(let y=r[1];y<r[3];y++){
  for(let x=r[0];x<r[2];x++){
   const i=y*W+x,a=mask[i];if(!a)continue;
   let u,v;
   if(isFront){
    const mat=FRONT_H_INV;
    const d=mat[2][0]*(x+.5)+mat[2][1]*(y+.5)+mat[2][2];
    if(Math.abs(d)<1e-10)continue;
    const sx=(mat[0][0]*(x+.5)+mat[0][1]*(y+.5)+mat[0][2])/d;
    const sy=(mat[1][0]*(x+.5)+mat[1][1]*(y+.5)+mat[1][2])/d;
    u=(sx-84)/110;v=(sy-61)/83;
   }else{
    u=(x+.5-r[0])/(r[2]-r[0]);
    v=(y+.5-r[1])/(r[3]-r[1]);
   }
   if(u<0||u>=1||v<0||v>=1)continue;
   const sx=Math.min(PHOTO_W-1,Math.max(0,Math.floor(u*PHOTO_W)));
   const sy=Math.min(PHOTO_H-1,Math.max(0,Math.floor(v*PHOTO_H)));
   const from=(sy*PHOTO_W+sx)*4,to=i*4;
   source[to]=photo[from];source[to+1]=photo[from+1];
   source[to+2]=photo[from+2];source[to+3]=a;
  }
 }
 ctx.putImageData(output,0,0);
 entries.set(key,out);
 return out;
}
function frame(ctx,f,img,preferredShape=null){
 ensureReady();
 const panel=panelFor(f);
 if(!img||!img.naturalWidth)return; // Canonical matte already shows a blank slot.
 const overlay=photoOverlay(img,f,panel);
 ctx.drawImage(overlay,0,0);
}
window.A18Entrance={init,background,foreground,frame,frameGeometry,assetCount:()=>images.size,ready:()=>ready};
})();