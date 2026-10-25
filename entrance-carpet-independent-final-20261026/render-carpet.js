const sources=['entrance_marble_floor_without_carpet.png','entrance_red_carpet_body.png','entrance_red_carpet_plain_body.png','entrance_red_carpet_contact_shadow.png','entrance_red_carpet_gold_trim.png','characters/butler-front-00.png','characters/curator-front-00.png'];const assets={};
Promise.all(sources.map(n=>new Promise((ok,fail)=>{let im=new Image();im.onload=()=>{assets[n]=im;ok()};im.onerror=()=>fail(Error(n));im.src=n}))).then(()=>{
const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d');
const carpet=document.getElementById('carpet'),gold=document.getElementById('gold'),scale=document.getElementById('scale'),offset=document.getElementById('offset');
const state=()=>({carpet:carpet.checked,gold:gold.checked,scale:Number(scale.value),offset:Number(offset.value)});
function sprite(name,cx,foot,w){let i=assets[name];let h=Math.round(i.height*w/i.width);ctx.imageSmoothingEnabled=false;ctx.drawImage(i,Math.round(cx-w/2),foot-h,w,h);ctx.imageSmoothingEnabled=true}
function draw(){let s=state();ctx.setTransform(2,0,0,2,0,0);ctx.clearRect(0,0,546,483);ctx.drawImage(assets[sources[0]],0,0);
document.getElementById('scaleValue').textContent=s.scale+'%';document.getElementById('offsetValue').textContent=s.offset===0?'標準':s.offset+'px';
gold.disabled=!s.carpet;gold.parentElement.classList.toggle('disabled',!s.carpet);
if(s.carpet){let z=s.scale/100,ax=281,ay=438;
let x=Math.round(ax+s.offset+(164-ax)*z),y=Math.round(ay+(226-ay)*z),w=Math.round(235*z),h=Math.round(223*z);
ctx.drawImage(assets[sources[3]],x,y,w,h);
ctx.drawImage(assets[s.gold?sources[1]:sources[2]],x,y,w,h);
if(s.gold)ctx.drawImage(assets[sources[4]],Math.round(ax+s.offset+(173-ax)*z),Math.round(ay+(235-ay)*z),Math.round(220*z),Math.round(203*z))}
sprite(sources[5],140,371,43);sprite(sources[6],287,366,35)}
[carpet,gold,scale,offset].forEach(e=>e.addEventListener('input',draw));
document.getElementById('reset').addEventListener('click',()=>{carpet.checked=true;gold.checked=true;scale.value=100;offset.value=0;draw()});draw();
window.A18CarpetIndependent={ready:true,state};
}).catch(e=>{document.body.append('画像の読み込みに失敗: '+e.message);throw e});