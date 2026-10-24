const assert=require('node:assert/strict');
const puppeteer=require(process.env.A18_PUPPETEER_PATH||'C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
const target=process.env.A18_TEST_URL||'http://127.0.0.1:18087/entrance-test-v3/layout-test/index.html?collisionDebug=1';
(async()=>{
 const b=await puppeteer.launch({headless:true,executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
 const p=await b.newPage();await p.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const state=()=>p.evaluate(()=>window.__A18_SCENE_STUDY__.state());
 const move=async(dir,n=1)=>p.evaluate(({dir,n})=>{const api=window.__A18_SCENE_STUDY__;for(let i=0;i<n;i++)api.move(dir);return api.state().pos;},{dir,n});
 const check=(name,condition,detail='')=>{assert(condition,name+' '+detail);console.log('PASS',name,detail)};
 try{
  await p.goto(target,{waitUntil:'domcontentloaded',timeout:30000});
  await p.waitForFunction('window.__A18_SCENE_STUDY__?.ready()', {timeout:30000});
  const first=await state();check('initial entrance',first.scene==='entrance');
  if(first.playerName===''){
   await p.click('#introSkipOpening');await p.type('#a18PlayerName','QA');await p.click('#confirmName');
   await p.waitForSelector('#skipTour');await p.click('#skipTour');
  }
  await sleep(350);
  check('onboarding closed',await p.$eval('#overlay',e=>e.hidden));
  check('approved room image',await p.evaluate(()=>window.A18Entrance.ready()));
  const geometry=await p.evaluate(()=>{
   const api=window.__A18_SCENE_STUDY__,nav=window.A18Navigation.EDGES.entrance;
   return {doorBlocked:!api.canMove(273,217),doorFloor:api.canMove(273,218),
    railing:!api.canMove(72,275),partition:!api.canMove(465,300),
    wall:!api.canMove(210,208),leftPortal:api.canMove(139,296),rightPortal:api.canMove(397,318),
    anchors:api.state().interactionAnchors,nav};
  });console.log('GEOMETRY',JSON.stringify(geometry));
  for(const [key,val] of Object.entries(geometry))if(typeof val==='boolean')check(key,val);
  let a=await move('up',17);check('approach wall vertically',a.y<=222,JSON.stringify(a));
  a=await move('left',4);check('aligned north door',a.x>=257&&a.x<=289,JSON.stringify(a));
  a=await move('up',2);check('closed door stops at foot line',a.y>=218&&a.y<=220,JSON.stringify(a));
  check('closed door becomes inspectable',(await state()).interaction?.type==='door');
  await p.screenshot({path:'C:/Users/User/AppData/Local/Temp/a18_collision_door_fixed.png'});
  await p.click('#act');check('closed door inspect dialog',await p.$eval('#dialog',e=>e.innerText.includes('閉ざされています')));await p.click('#closeDoor');
  a=await move('down',3);check('corridor floor',a.y>=250&&a.y<=260,JSON.stringify(a));
  a=await move('left',16);check('left corridor reached',a.x<=150,JSON.stringify(a));
  const leftX=a.x,leftY=a.y;
  check('left rear painting reachable',(await state()).interaction?.i===0,JSON.stringify((await state()).interaction));
  a=await move('right',27);check('left-to-right across door',a.x>=390,JSON.stringify(a));
  check('right rear painting reachable',(await state()).interaction?.i===1,JSON.stringify((await state()).interaction));
  a=await move('left',27);check('right-to-left across door',a.x<=150,JSON.stringify(a));
  console.log('CORRIDOR',JSON.stringify({leftX,leftY,rightmost:leftX+27*12,back:a}));
  a=await move('right',1);a=await move('down',4);
  check('west passage physical arrival',a.x>=128&&a.x<=144&&a.y>=288&&a.y<=306,JSON.stringify(a));
  check('west locked without accidental transition',(await state()).scene==='entrance');
  a=await move('up',4);a=await move('right',22);a=await move('down',5);
  check('east passage physical arrival',a.x>=389&&a.x<=405&&a.y>=306&&a.y<=330,JSON.stringify(a));
  check('east locked without accidental transition',(await state()).scene==='entrance');
  a=await move('left',17);check('butler conversation radius',(await state()).interaction?.type==='butler',JSON.stringify(a));
  a=await move('right',16);a=await move('down',5);a=await move('right',6);
  check('foreground right picture reachable',(await state()).interaction?.i===2,JSON.stringify(a));
  check('butler and front right artwork remain solid',await p.evaluate(()=>!window.__A18_SCENE_STUDY__.canMove(155,329)&&!window.__A18_SCENE_STUDY__.canMove(465,300)));
  await p.screenshot({path:'C:/Users/User/AppData/Local/Temp/a18_collision_right_fixed.png'});
  // The debug grid's green pixels are produced by the same canMove predicate
  // that each 3px swept movement step uses; check all 5 probes for each cell.
  const sample=await p.evaluate(()=>{
   const a=window.__A18_SCENE_STUDY__;let green=0,border=0,red=0,fullMismatch=0;
   for(let y=0;y<483;y+=6)for(let x=0;x<546;x+=6){
     const points=[[1,1],[5,1],[1,5],[5,5],[3,3]].map(([dx,dy])=>a.canMove(x+dx,y+dy));
     const count=points.filter(Boolean).length;
     if(count===5){green++;if(!points.every(Boolean))fullMismatch++;}
     else if(count===0)red++;else border++;
   }return {green,red,border,fullMismatch};
  });check('debug full-green classification exact',sample.fullMismatch===0,JSON.stringify(sample));
  check('no browser exceptions',errors.length===0,JSON.stringify(errors));
  console.log('BROWSER_QA_OK',target);
 }finally{await b.close()}
})().catch(e=>{console.error('BROWSER_QA_FAILED',e.stack||e);process.exit(1)});
