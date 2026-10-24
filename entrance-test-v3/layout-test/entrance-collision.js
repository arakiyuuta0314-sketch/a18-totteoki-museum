/* Collision geometry for the approved 546x483 entrance image.
 * pos.x / pos.y are the avatar shadow/sole coordinates. The collision disc is
 * centred five pixels below that point, matching the pre-existing foot check.
 * Do not create unconditional "walkable strips": the railings and partition
 * occupy the same y coordinates as the corridor and MUST remain solid.
 */
(()=>{'use strict';
const FOOT_OFFSET=5,RADIUS=9;
const WALL_FOOT=218;
const NORTH_PASSAGE=Object.freeze({x1:257,x2:289,y1:195,y2:218});
const POLYGONS=Object.freeze([
 {id:'west-balustrade',points:[[0,211],[99,211],[117,257],[117,329],[0,335]]},
 {id:'reception',points:[[0,343],[146,343],[148,464],[0,464]]},
 {id:'east-partition',points:[[416,195],[546,237],[546,406],[422,347]]},
 {id:'east-planter',points:[[518,413],[546,405],[546,483],[516,483]]}
]);
function inside(x,y,p){let hit=false;for(let i=0,j=p.length-1;i<p.length;j=i++){
 const a=p[i],b=p[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])hit=!hit;
}return hit;}
function edgeDistanceSquared(x,y,a,b){
 const dx=b[0]-a[0],dy=b[1]-a[1],len=dx*dx+dy*dy;
 const t=len?Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/len)):0;
 const px=a[0]+t*dx,py=a[1]+t*dy;return (x-px)**2+(y-py)**2;
}
function hitsPolygon(x,y,p,r){
 if(inside(x,y,p))return true;
 for(let i=0;i<p.length;i++)if(edgeDistanceSquared(x,y,p[i],p[(i+1)%p.length])<r*r)return true;
 return false;
}
function walkable(x,y,northOpen=false){
 if(!Number.isFinite(x)||!Number.isFinite(y))return false;
 if(x<24||x>522||y>472)return false;
 if(y<WALL_FOOT){
  if(!northOpen||x<NORTH_PASSAGE.x1||x>NORTH_PASSAGE.x2||
     y<NORTH_PASSAGE.y1)return false;
 }
 const footY=y+FOOT_OFFSET;
 return !POLYGONS.some(o=>hitsPolygon(x,footY,o.points,RADIUS))
   && Math.hypot(x-155,footY-334)>=20;
}
window.A18EntranceCollision=Object.freeze({POLYGONS,FOOT_OFFSET,RADIUS,WALL_FOOT,NORTH_PASSAGE,walkable,hitsPolygon});
})();
