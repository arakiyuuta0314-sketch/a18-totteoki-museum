const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ctx={window:{}};vm.runInNewContext(fs.readFileSync(__dirname+'/entrance-collision.js','utf8'),ctx);
const m=ctx.window.A18EntranceCollision;
const cases=[
 ['floor center',326,425,true],['door wall',273,210,false],
 ['door approach',273,260,true],['left railing',72,275,false],
 ['reception',70,395,false],['right partition',480,365,false],
 ['butler center',155,329,false],['butler outside',185,329,true],['right frame upper approach',405,284,true],['right frame base',432,347,false],['frame front walk',399,365,true],['frame center blocked',465,300,false],['carpet side',380,365,true],['right planter',530,450,false]
];
for(const [label,x,y,expected] of cases){const actual=m.walkable(x,y);assert.strictEqual(actual,expected,label);console.log('PASS',label);}
const targets={north:[273,260],west:[142,325],east:[399,365]};
const step=3,queue=[[326,425]],seen=new Set(),key=(x,y)=>x+','+y;
while(queue.length){const [x,y]=queue.shift();if(seen.has(key(x,y)))continue;seen.add(key(x,y));
for(const [dx,dy] of [[step,0],[-step,0],[0,step],[0,-step]]){const nx=x+dx,ny=y+dy;if(m.walkable(nx,ny)&&!seen.has(key(nx,ny)))queue.push([nx,ny]);}}
for(const [name,[tx,ty]] of Object.entries(targets)){
 const reachable=[...seen].some(s=>{const [x,y]=s.split(',').map(Number);return Math.hypot(x-tx,y-ty)<8});
 console.log(name,reachable?'REACHABLE':'BLOCKED');assert(reachable,name+' unreachable');
}
console.log('QA OK reachable cells',seen.size);

