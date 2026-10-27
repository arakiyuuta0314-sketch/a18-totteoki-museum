"use strict";
(()=>{
 const SW=780,SH=1688,STORE="a18-placement-editor-v3";
 const presets={
  counter:{x:90,y:795,w:185,h:338,a:0,visible:true},
  wall:{x:574,y:736,w:315,h:310,a:0,visible:true},
  picture:{x:658,y:801,w:156,h:133,a:0,visible:true}
 };
 const labels={counter:"カウンター",wall:"右の仕切り壁",picture:"作品の表示サイズ"};
 const keys=Object.keys(presets),$=s=>document.querySelector(s);
 const scene=$("#scene"),pieces=Object.fromEntries(keys.map(k=>[k,$("#piece-"+k)]));
 const fields=Object.fromEntries(["x","y","w","h"].map(k=>[k,$("#"+k)]));
 const sliders={w:$("#widthRange"),h:$("#heightRange"),a:$("#angleRange")};
 let state=clone(presets),selected="wall",busy=null,assetUrls={};
 function clone(x){return JSON.parse(JSON.stringify(x))}
 function finite(v){return typeof v==="number"&&Number.isFinite(v)}
 function valid(data){
  return data&&typeof data==="object"&&keys.every(k=>{
   const z=data[k];return z&&["x","y","w","h","a"].every(s=>finite(z[s]))&&
    z.w>=24&&z.w<=600&&z.h>=24&&z.h<=900&&Math.abs(z.x)<1500&&Math.abs(z.y)<2500&&
    Math.abs(z.a)<=90&&typeof z.visible==="boolean";
  });
 }
 function cap(v,lo,hi){return Math.min(hi,Math.max(lo,v))}
 function load(){
  try{
   const params=new URLSearchParams(location.search);
   if(params.has("layout")){
    const candidate=JSON.parse(params.get("layout"));
    if(valid(candidate))return candidate;
   }
   const raw=localStorage.getItem(STORE);
   if(raw){const candidate=JSON.parse(raw);if(valid(candidate))return candidate}
  }catch(err){console.warn("Saved positions unavailable",err)}
  return clone(presets);
 }
 state=load();
 function persist(){try{localStorage.setItem(STORE,JSON.stringify(state))}catch(e){status("端末への自動保存に失敗しました")}}
 function status(msg){$("#status").textContent=msg}
 function apply(){
  for(const k of keys){
   const z=state[k],el=pieces[k];
   el.style.left=(100*z.x/SW)+"%";el.style.top=(100*z.y/SH)+"%";
   el.style.width=(100*z.w/SW)+"%";el.style.height=(100*z.h/SH)+"%";
   el.style.transform="rotate("+z.a+"deg)";
   el.style.display=z.visible?"block":"none";
   el.classList.toggle("selected",k===selected);
   el.setAttribute("aria-pressed",String(k===selected));
  }
  for(const b of document.querySelectorAll("[data-select]")){
   b.setAttribute("aria-pressed",String(b.dataset.select===selected))
  }
  const z=state[selected];
  $("#selectedName").textContent=labels[selected];
  $("#visibility").textContent=z.visible?"非表示にする":"表示する";
  for(const k of Object.keys(fields)){
   if(document.activeElement!==fields[k])fields[k].value=Math.round(z[k]);
  }
  sliders.w.value=cap(z.w,Number(sliders.w.min),Number(sliders.w.max));
  sliders.h.value=cap(z.h,Number(sliders.h.min),Number(sliders.h.max));
  sliders.a.value=z.a;
  $("#widthValue").textContent=Math.round(z.w)+"px";
  $("#heightValue").textContent=Math.round(z.h)+"px";
  $("#angleValue").textContent=Math.round(z.a)+"°";
 }
 function update(patch){Object.assign(state[selected],patch);apply();persist()}
 function select(k){if(!keys.includes(k))return;selected=k;apply();status(labels[k]+"を選択中")}
 function adjust(k,value){
  if(!finite(value))return;
  if(k==="x"||k==="y"){update({[k]:Math.round(cap(value,k==="x"?-state[selected].w/2:0,k==="x"?SW-state[selected].w/2:SH-state[selected].h/2))})}
  else if(k==="w"||k==="h"){update({[k]:Math.round(cap(value,24,k==="w"?600:900))})}
  else if(k==="a")update({a:cap(value,-25,25)});
 }
 // Wall drag carries its photo along; changing the wall size never resizes the photo.
 // Photo can independently be moved and resized as a separate layer.
 function move(k,x,y){
  const z=state[k],nextX=cap(Math.round(x),-z.w/2,SW-z.w/2),
        nextY=cap(Math.round(y),0,SH-z.h/2);
  const dx=nextX-z.x,dy=nextY-z.y;
  z.x=nextX;z.y=nextY;
  if(k==="wall"){state.picture.x=cap(Math.round(state.picture.x+dx),-state.picture.w/2,SW-state.picture.w/2);
    state.picture.y=cap(Math.round(state.picture.y+dy),0,SH-state.picture.h/2)}
  apply();persist();
 }
 for(const k of keys){
  const el=pieces[k];
  el.addEventListener("pointerdown",e=>{
   if(e.button!==undefined&&e.button!==0)return;
   e.preventDefault();
   e.stopPropagation();
   select(k);
   const sceneRect=scene.getBoundingClientRect(),o=state[k];
   busy={id:e.pointerId,k,mode:e.target.classList.contains("handle")?"resize":"move",
         atX:e.clientX,atY:e.clientY,orig:clone(o),origPhoto:clone(state.picture),
         scale:SW/sceneRect.width};
   el.setPointerCapture(e.pointerId);el.classList.add("dragging");
  });
  el.addEventListener("pointermove",e=>{
   if(!busy||busy.id!==e.pointerId||busy.k!==k)return;
   e.preventDefault();
   const dx=(e.clientX-busy.atX)*busy.scale,dy=(e.clientY-busy.atY)*busy.scale;
   if(busy.mode==="resize"){
    const z=state[k];z.w=Math.round(cap(busy.orig.w+dx,24,600));
    z.h=Math.round(cap(busy.orig.h+dy,24,900));
    apply();persist();
   }else{
    // Relative to pointer origin, not the last event: smooth even after selection changes.
    const z=busy.orig;
    const x=cap(Math.round(z.x+dx),-z.w/2,SW-z.w/2);
    const y=cap(Math.round(z.y+dy),0,SH-z.h/2);
    state[k].x=x;state[k].y=y;
    if(k==="wall"){
      state.picture.x=cap(Math.round(busy.origPhoto.x+x-z.x),-state.picture.w/2,SW-state.picture.w/2);
      state.picture.y=cap(Math.round(busy.origPhoto.y+y-z.y),0,SH-state.picture.h/2)
    }
    apply();persist();
   }
  });
  const end=e=>{if(busy&&busy.id===e.pointerId){busy=null;el.classList.remove("dragging");status("位置を端末内に保存しました")}};
  el.addEventListener("pointerup",end);el.addEventListener("pointercancel",end);
  el.addEventListener("keydown",e=>{
   const delta={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[e.key];
   if(!delta)return;
   e.preventDefault();select(k);
   move(k,state[k].x+delta[0]*(e.shiftKey?10:1),state[k].y+delta[1]*(e.shiftKey?10:1))
  });
 }
 for(const b of document.querySelectorAll("[data-select]"))b.addEventListener("click",()=>select(b.dataset.select));
 for(const k of Object.keys(fields)){
  fields[k].addEventListener("change",()=>{const v=Number(fields[k].value);
   if(Number.isFinite(v))adjust(k,v);else apply()});
 }
 for(const k of Object.keys(sliders))sliders[k].addEventListener("input",e=>adjust(k,Number(e.target.value)));
 for(const b of document.querySelectorAll("[data-nudge]"))b.addEventListener("click",()=>{
  const [dx,dy]=b.dataset.nudge.split(",").map(Number),z=state[selected];
  move(selected,z.x+dx,z.y+dy);
 });
 $("#visibility").addEventListener("click",()=>update({visible:!state[selected].visible}));
 $("#assetUpload").addEventListener("change",e=>{
  const file=e.target.files?.[0];
  if(!file)return;
  if(!/^image\/(png|jpeg|webp)$/.test(file.type)||file.size>8*1024*1024){
    status("PNG/JPEG/WebP、8MB以下の画像を選んでください");return;
  }
  if(assetUrls[selected])URL.revokeObjectURL(assetUrls[selected]);
  assetUrls[selected]=URL.createObjectURL(file);
  pieces[selected].querySelector("img").src=assetUrls[selected];
  status(labels[selected]+"の画像を仮に差し替えました（この画面のみ）");
  e.target.value="";
 });
 function infoUrl(){
  const url=new URL(location.href);
  url.search="";url.hash="";
  url.searchParams.set("layout",JSON.stringify(state));
  return url.toString();
 }
 async function copy(text,label){
  $("#shareText").value=text;
  try{await navigator.clipboard.writeText(text);status(label+"をコピーしました。チャットに貼り付けてね")}
  catch(e){$("#shareText").focus();$("#shareText").select();status("下の欄を長押ししてコピーしてください")}
 }
 $("#share").addEventListener("click",()=>copy(infoUrl(),"配置リンク"));
 $("#shareTop").addEventListener("click",()=>copy(infoUrl(),"配置リンク"));
 $("#copyJson").addEventListener("click",()=>copy(JSON.stringify(state,null,2),"配置データ"));
 $("#download").addEventListener("click",()=>{
  const blob=new Blob([JSON.stringify({version:1,canvas:{w:SW,h:SH},objects:state},null,2)],
                     {type:"application/json"});
  const url=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=url;a.download="a18-entrance-position.json";document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  status("座標JSONをダウンロードしました");
 });
 $("#reset").addEventListener("click",()=>{
  if(!confirm("3つの設備の位置・サイズをすべて初期配置へ戻しますか？"))return;
  state=clone(presets);persist();apply();status("初期配置に戻しました");
 });
 // Diagnostic readonly handle for automated acceptance tests.
 Object.defineProperty(window,"__A18_PLACEMENT_TEST__",{value:Object.freeze({
  getState:()=>clone(state),select,move:(k,x,y)=>{select(k);move(k,x,y)},getShareUrl:infoUrl
 })});
 apply();
})();
