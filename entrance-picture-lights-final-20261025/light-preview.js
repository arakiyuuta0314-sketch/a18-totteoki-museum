const file=['QA_photos_sprites_no_lights.png','entrance_picture_light_west_photo_safe.png','entrance_picture_light_east_photo_safe.png'],imgs={};
Promise.all(file.map(n=>new Promise((res,rej)=>{let im=new Image();im.onload=()=>{imgs[n]=im;res()};im.onerror=()=>rej(Error('missing '+n));im.src=n}))).then(()=>{
 const c=document.getElementById('canvas'),ctx=c.getContext('2d');
 function render(){
  ctx.setTransform(2,0,0,2,0,0);ctx.clearRect(0,0,546,483);
  ctx.drawImage(imgs[file[0]],0,0);
  if(document.getElementById('west').checked)ctx.drawImage(imgs[file[1]],116,30);
  if(document.getElementById('east').checked)ctx.drawImage(imgs[file[2]],391,30);
 }
 for(const side of ['west','east'])document.getElementById(side).addEventListener('change',render);
 document.getElementById('reset').addEventListener('click',()=>{document.getElementById('west').checked=true;document.getElementById('east').checked=true;render()});
 render();window.A18PictureLights={ready:true,state:()=>({west:document.getElementById('west').checked,east:document.getElementById('east').checked})};
}).catch(e=>{document.body.append('ERR '+e.message);throw e});