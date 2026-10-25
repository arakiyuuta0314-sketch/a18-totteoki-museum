const positions={west_sign:[4,61],east_sign:[503,61],west_sconce:[214,83],east_sconce:[334,83]};
const assets={};
const filenames=['QA_photos_sprites_none.png',...Object.keys(positions).map(k=>'entrance_'+k+'.png')];
Promise.all(filenames.map(n=>new Promise((res,rej)=>{let im=new Image();im.onload=()=>{assets[n]=im;res()};im.onerror=()=>rej(Error(n));im.src=n}))).then(()=>{
 const c=document.getElementById('preview'),ctx=c.getContext('2d');
 function render(){
  ctx.setTransform(2,0,0,2,0,0);ctx.clearRect(0,0,546,483);
  ctx.drawImage(assets['QA_photos_sprites_none.png'],0,0);
  for(const [name,pos] of Object.entries(positions))if(document.getElementById(name).checked)ctx.drawImage(assets['entrance_'+name+'.png'],...pos);
 }
 for(const k of Object.keys(positions))document.getElementById(k).addEventListener('change',render);
 document.getElementById('reset').addEventListener('click',()=>{for(const k of Object.keys(positions))document.getElementById(k).checked=true;render()});
 render();window.A18Fixtures={ready:true,state:()=>Object.fromEntries(Object.keys(positions).map(k=>[k,document.getElementById(k).checked]))};
}).catch(e=>{document.body.append('エラー:'+e.message);throw e});