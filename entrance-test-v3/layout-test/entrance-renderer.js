/* A18 entrance v0.3: isolated visual layers; gameplay coordinates and stores are unchanged. */
(()=>{'use strict';
const ROOT='assets/entrance/v0.3/';
const ITEMS={
 floor:['entrance_floor_base_v03.png',546,483],
 wall:['entrance_wall_base_v03.png',546,483],
 carpet:['entrance_carpet_v03.png',546,483],
 sidewalls:['entrance_sidewalls_v03.png',546,483],
 north:['entrance_door_north_v03.png',76,170],
 west:['entrance_door_west_v03.png',64,112],
 east:['entrance_door_east_v03.png',64,112],
 frame:['entrance_frame_horizontal_v03.png',100,77],
 portraitDemo:['entrance_frame_portrait_demo_v03.png',62,122],
 squareDemo:['entrance_frame_square_demo_v03.png',90,90],
 atlas:['entrance_frame_9slice_atlas_v03.png',42,42],
 plant:['entrance_plant_v03.png',65,98],
 light:['entrance_wall_light_v03.png',26,38],
 glow:['entrance_wall_glow_v03.png',546,483],
 plaque:['entrance_plaque_blank_v03.png',101,23],
 approved:['approved_entrance_trial.jpg',546,483]
};
const images=new Map();
let ready=false;
async function init(){
 if(ready)return;
 // A missing asset is a fatal, visible boot error, never a silent placeholder.
 await Promise.all(Object.entries(ITEMS).map(async ([key,[filename,width,height]])=>{
  const im=await new Promise((resolve,reject)=>{
   const image=new Image();
   image.onload=()=>resolve(image);
   image.onerror=()=>reject(Error('エントランスv0.3素材を読み込めません：'+ROOT+filename));
   image.src=ROOT+filename;
  });
  if(im.naturalWidth!==width||im.naturalHeight!==height)
   throw Error('エントランスv0.3素材の寸法が不正：'+filename);
  images.set(key,im);
 }));
 ready=true;
}
function requireReady(){
 if(!ready)throw Error('エントランスv0.3画像の読み込みが未完了');
}
function place(ctx,key,x,y){
 const im=images.get(key);
 if(!im)throw Error('未定義のエントランス素材：'+key);
 ctx.drawImage(im,x,y);
}
function background(ctx){
 requireReady();
 ctx.save();
 ctx.imageSmoothingEnabled=false;
 ctx.fillStyle='#d4c6ad';ctx.fillRect(0,0,546,483);
 if(new URLSearchParams(location.search).get('entranceArt')!=='legacy'){place(ctx,'approved',0,0);ctx.restore();return;}
 place(ctx,'floor',0,0);
 place(ctx,'wall',0,0);
 place(ctx,'carpet',0,0);
 place(ctx,'sidewalls',0,0);
 place(ctx,'north',328,69);
 place(ctx,'west',0,326);
 place(ctx,'east',482,326);
 place(ctx,'glow',0,0);
 place(ctx,'light',168,90);
 ctx.restore();
}
function foreground(ctx){
 requireReady();
 ctx.save();ctx.imageSmoothingEnabled=false;
 place(ctx,'plant',422,205);
 ctx.restore();
}
// The atlas is 3 x 3 patches, each exactly 14 px.
// Nine-slice destinations are 9 px on each side, so the transparent central
// window is precisely aligned to the photographed rectangle.
function nineSlice(ctx,outer){
 const atlas=images.get('atlas');
 if(!atlas)throw Error('9-sliceの額縁素材がありません');
 const b=9,s=14;
 const dx=[outer.x,outer.x+b,outer.x+outer.w-b];
 const dy=[outer.y,outer.y+b,outer.y+outer.h-b];
 const dw=[b,outer.w-2*b,b],dh=[b,outer.h-2*b,b];
 if(dw[1]<0||dh[1]<0)throw Error('額縁の表示寸法が小さすぎます');
 ctx.save();ctx.imageSmoothingEnabled=false;
 for(let iy=0;iy<3;iy++)for(let ix=0;ix<3;ix++){
  if(ix===1&&iy===1)continue; // full transparency for the work
  ctx.drawImage(atlas,ix*s,iy*s,s,s,dx[ix],dy[iy],dw[ix],dh[iy]);
 }
 ctx.restore();
}
function frameGeometry(f,img,preferredShape=null){
 // Coordinates remain anchored to the three existing frames, without
 // changing fixture geometry or persisted IDs.
 const shape=(preferredShape==='portrait'||preferredShape==='square')?preferredShape:window.A18Art.displayShape(f,img,preferredShape);
 // Enlarge only entrance wall displays by about 25%; gallery rooms stay unchanged.
 let maxW=102,maxH=74;
 if(shape==='portrait'){maxW=102;maxH=130;}
 if(shape==='square'){maxW=90;maxH=90;}
 let innerW=maxW,innerH=maxH;
 const hasPhoto=img&&img.naturalWidth>0&&img.naturalHeight>0;
 if(hasPhoto){
  const ratio=img.naturalWidth/img.naturalHeight;
  // Size the photo window to the actual original aspect ratio for every shape.
  // This avoids off-ratio matting and unnecessary cropping, even in cover mode.
  const size=Math.min(maxW/ratio,maxH);
  innerW=size*ratio;innerH=size;
 }
 // Protect the 40 x 40 minimum frame without inserting white padding.
 const outerW=Math.max(40,innerW+18),outerH=Math.max(40,innerH+18);
 // The left/right frame windows can be tall, but must remain within the wall.
 const x=f.x-outerW/2;
 const y=Math.max(34,Math.min(199-outerH,f.y-outerH/2));
 const outer={x,y,w:outerW,h:outerH};
 return {outer,inner:{x:x+(outerW-innerW)/2,y:y+(outerH-innerH)/2,w:innerW,h:innerH},shape};
}
// Exact photo windows measured against the approved 1536x1024 source,
// projected into the existing 546x483 logical entrance canvas.
// Slot IDs and interaction coordinates are intentionally unchanged.
const APPROVED_WINDOWS=[
 {x:82,y:67,w:111,h:77},
 {x:376,y:67,w:81,h:77},
 {x:432,y:204,w:56,h:107}
];
// The foreground-right exhibit is on an angled partition.
// Texture-map two triangles into its trapezoidal inner opening.
const RIGHT_PANEL=[[408,201],[481,225],[463,314],[409,284]];
// A continuous column-wise perspective warp avoids the diagonal seam caused
// by the earlier two-triangle affine mapping.
const RIGHT_PANEL_CACHE=new WeakMap();
const RIGHT_WARP_CACHE=new WeakMap();
let RIGHT_EMPTY_WARP=null;
function rightPanel(ctx,f,img){
 const cached=img?RIGHT_WARP_CACHE.get(img):RIGHT_EMPTY_WARP;
 if(cached){ctx.drawImage(cached,408,201);return;}
 // Pre-warp to a raster once, with inverse bilinear sampling. No independent
 // canvas strips: Safari otherwise exposes seams on each transformed column.
 let source=img&&RIGHT_PANEL_CACHE.get(img);
 if(!source){
  source=document.createElement('canvas');source.width=256;source.height=256;
  const c=source.getContext('2d');
  if(img&&img.naturalWidth>0&&img.naturalHeight>0){
   const scale=Math.max(256/img.naturalWidth,256/img.naturalHeight);
   const w=img.naturalWidth*scale,h=img.naturalHeight*scale;
   c.drawImage(img,(256-w)/2,(256-h)/2,w,h);
   RIGHT_PANEL_CACHE.set(img,source);
  }else{
   c.fillStyle=f.workId?'#4b4034':'#bba986';c.fillRect(0,0,256,256);
   if(!f.workId){c.fillStyle='#776143';c.font='bold 72px serif';c.textAlign='center';c.textBaseline='middle';c.fillText('+',128,128);}
  }
 }
 const [tl,tr,br,bl]=RIGHT_PANEL;
 const left=Math.floor(Math.min(tl[0],bl[0])),top=Math.floor(Math.min(tl[1],tr[1]));
 const right=Math.ceil(Math.max(tr[0],br[0])),bottom=Math.ceil(Math.max(bl[1],br[1]));
 const w=right-left,h=bottom-top;
 const input=source.getContext('2d',{willReadFrequently:true}).getImageData(0,0,256,256).data;
 const out=ctx.createImageData(w,h),dst=out.data;
 // Solve the inverse bilinear quad per destination pixel. Both side edges
 // lean with depth, unlike the old fixed-x column approximation.
 for(let py=0;py<h;py++)for(let px=0;px<w;px++){
  const x=left+px+.5,y=top+py+.5;
  let u=.5,v=.5;
  for(let k=0;k<9;k++){
   const xx=(1-u)*(1-v)*tl[0]+u*(1-v)*tr[0]+u*v*br[0]+(1-u)*v*bl[0];
   const yy=(1-u)*(1-v)*tl[1]+u*(1-v)*tr[1]+u*v*br[1]+(1-u)*v*bl[1];
   const dxdu=(1-v)*(tr[0]-tl[0])+v*(br[0]-bl[0]);
   const dydu=(1-v)*(tr[1]-tl[1])+v*(br[1]-bl[1]);
   const dxdv=(1-u)*(bl[0]-tl[0])+u*(br[0]-tr[0]);
   const dydv=(1-u)*(bl[1]-tl[1])+u*(br[1]-tr[1]);
   const det=dxdu*dydv-dxdv*dydu;
   if(Math.abs(det)<1e-7)break;
   const ex=x-xx,ey=y-yy;
   u+=(ex*dydv-ey*dxdv)/det;
   v+=(ey*dxdu-ex*dydu)/det;
  }
  if(u<0||u>1||v<0||v>1)continue;
  const sx=Math.min(255,Math.max(0,Math.floor(u*256)));
  const sy=Math.min(255,Math.max(0,Math.floor(v*256)));
  const si=(sy*256+sx)*4,di=(py*w+px)*4;
  dst[di]=input[si];dst[di+1]=input[si+1];dst[di+2]=input[si+2];dst[di+3]=255;
 }
 const warped=document.createElement('canvas');warped.width=w;warped.height=h;
 warped.getContext('2d').putImageData(out,0,0);
 if(img)RIGHT_WARP_CACHE.set(img,warped);else RIGHT_EMPTY_WARP=warped;
 ctx.drawImage(warped,left,top);
}
// Shared geometric source of truth for the visual openings and interaction.
function approvedAnchor(index){
 if(index===2)return {x:390,y:338}; // stand on the accessible side of the angled partition
 const rect=APPROVED_WINDOWS[index];
 if(!rect)throw Error('Unknown approved frame index '+index);
 return {x:rect.x+rect.w/2,y:226};
}
function approvedGeometry(index){
 if(index===2)return {polygon:RIGHT_PANEL.map(p=>p.slice()),anchor:approvedAnchor(index)};
 const r=APPROVED_WINDOWS[index];
 if(!r)throw Error('Unknown approved frame index '+index);
 return {window:{...r},anchor:approvedAnchor(index)};
}
function approvedFrame(ctx,f,img,index){
 if(index<0||index>=APPROVED_WINDOWS.length)throw Error('Unknown entrance photo slot '+f.id);
 if(index===2){rightPanel(ctx,f,img);return;}
 const rect=APPROVED_WINDOWS[index];
 ctx.save();
 ctx.beginPath();ctx.rect(rect.x,rect.y,rect.w,rect.h);ctx.clip();
 if(img&&img.naturalWidth>0&&img.naturalHeight>0){
  const scale=Math.max(rect.w/img.naturalWidth,rect.h/img.naturalHeight);
  const dw=img.naturalWidth*scale,dh=img.naturalHeight*scale;
  ctx.imageSmoothingEnabled=true;
  ctx.drawImage(img,rect.x+(rect.w-dw)/2,rect.y+(rect.h-dh)/2,dw,dh);
 }else if(!f.workId){
  ctx.fillStyle='#bba986';ctx.fillRect(rect.x,rect.y,rect.w,rect.h);
  ctx.fillStyle='#776143';ctx.font='bold 20px serif';ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillText('+',rect.x+rect.w/2,rect.y+rect.h/2);
 }else{
  ctx.fillStyle='#4b4034';ctx.fillRect(rect.x,rect.y,rect.w,rect.h);
 }
 ctx.restore();
}
function frame(ctx,f,img,preferredShape=null,index=-1){
 requireReady();
 if(new URLSearchParams(location.search).get('entranceArt')!=='legacy'){approvedFrame(ctx,f,img,index);return;}
 const {outer,inner}=frameGeometry(f,img,preferredShape);
 // The shadow is BEHIND the art. Never darken the photograph with a mat overlay.
 ctx.save();
 ctx.fillStyle='#271f17a0';
 ctx.fillRect(outer.x+2,outer.y+3,outer.w,outer.h);
 ctx.fillStyle='#b9a783';
 ctx.fillRect(outer.x+9,outer.y+9,outer.w-18,outer.h-18);
 if(img&&img.naturalWidth>0){
  const sw=img.naturalWidth,sh=img.naturalHeight,mode=f.imageMode||'cover';
  const fit=mode==='contain'?Math.min(inner.w/sw,inner.h/sh):Math.max(inner.w/sw,inner.h/sh);
  const scale=fit*(mode==='custom'?(f.imageScale||1):1);
  const dw=sw*scale,dh=sh*scale;
  const ox=mode==='custom'?(inner.w-dw)*(f.imageX||0)/2:0;
  const oy=mode==='custom'?(inner.h-dh)*(f.imageY||0)/2:0;
  ctx.beginPath();ctx.rect(inner.x,inner.y,inner.w,inner.h);ctx.clip();
  ctx.imageSmoothingEnabled=true;
  ctx.drawImage(img,inner.x+(inner.w-dw)/2+ox,inner.y+(inner.h-dh)/2+oy,dw,dh);
 }else if(!f.workId){
  ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillStyle='#826e4c';ctx.font='bold 22px serif';
  ctx.fillText('+',inner.x+inner.w/2,inner.y+inner.h/2);
 }else{
  ctx.fillStyle='#45372c';ctx.fillRect(inner.x,inner.y,inner.w,inner.h);
 }
 ctx.restore();
 nineSlice(ctx,outer);
}
window.A18Entrance={init,background,foreground,frame,frameGeometry,approvedAnchor,approvedGeometry,assetCount:()=>images.size,ready:()=>ready};
})();