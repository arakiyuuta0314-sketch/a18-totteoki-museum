// Physical collision / connectivity regression suite (approved 546x483 art).
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx={window:{}};const folder=__dirname;
for(const f of ['entrance-collision.js','museum-navigation.js'])
 vm.runInNewContext(fs.readFileSync(folder+'/'+f,'utf8'),ctx,{filename:f});
const C=ctx.window.A18EntranceCollision,doors=ctx.window.A18Navigation.EDGES.entrance;
const cases=[
 ['floor center',326,425,true],['solid door above threshold',273,217,false],
 ['door floor threshold',273,218,true],['door wall',210,208,false],
 ['left railing',72,275,false],['reception',70,395,false],
 ['right partition',480,365,false],['butler',155,329,false],
 ['outside butler',185,329,true],['left frame approach',150,268,true],
 ['right frame approach',399,268,true],['right foreground approach',457,377,true],
 ['right frame base',432,347,false],['right planter',530,450,false]
];
for(const [label,x,y,expected] of cases){
 assert.equal(C.walkable(x,y),expected,label);console.log('PASS',label);
}
for(const x of [130,150,200,250,273,300,350,399,400]){
 assert(C.walkable(x,254),'continuous corridor at '+x);
}
console.log('PASS continuous corridor across central door');
for(const [label,x,y,open,allowed] of [
 ['locked door cannot enter',273,207,false,false],
 ['unlocked door permits narrow crossing',273,207,true,true],
 ['unlocked door cannot penetrate adjacent wall',247,207,true,false],
 ['unlocked door cannot go behind doorway',273,194,true,false]]){
 assert.equal(C.walkable(x,y,open),allowed,label);console.log('PASS',label);
}
const centers={north:[273,212],west:[136,297],east:[397,318]};
for(const [dir,[x,y]] of Object.entries(centers)){
 const r=doors[dir];assert(x>=r.x1&&x<=r.x2&&y>=r.y1&&y<=r.y2,'portal center '+dir);
 assert(C.walkable(x,y,dir==='north'),'portal traversable when unlocked '+dir);
}
const STEP=3,queue=[[326,425]],seen=new Set();const key=(x,y)=>x+','+y;
for(let head=0;head<queue.length;head++){
 const [x,y]=queue[head],k=key(x,y);if(seen.has(k))continue;seen.add(k);
 for(const [dx,dy] of [[STEP,0],[-STEP,0],[0,STEP],[0,-STEP]]){
  const nx=x+dx,ny=y+dy,nk=key(nx,ny);
  if(!seen.has(nk)&&C.walkable(nx,ny))queue.push([nx,ny]);
 }
}
for(const [name,[tx,ty]] of Object.entries({
 'north-door-approach':[273,218],west:centers.west,east:centers.east,'west-frame':[150,268],'east-frame':[399,268],
 'foreground-frame':[457,377],'butler-approach':[185,314],
 'left-crossing':[131,254],'right-crossing':[400,254]})){
 const reachable=[...seen].some(k=>{const [x,y]=k.split(',').map(Number);return Math.hypot(x-tx,y-ty)<=5});
 assert(reachable,'unreachable: '+name);console.log('PASS reachable',name);
}
console.log('ENTRANCE_GEOMETRY_QA_OK',seen.size,'grid nodes');
