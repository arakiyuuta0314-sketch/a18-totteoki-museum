const assert=require('node:assert/strict'),path=require('node:path'),puppeteer=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
const URL=process.env.A18_CANONICAL_URL||'http://127.0.0.1:18840/entrance-canonical-front-v05-20261026/';
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
 try{
  const p=await browser.newPage(),err=[];
  p.on('pageerror',x=>err.push('JS '+x.message));p.on('response',r=>{if(r.status()>=400)err.push('HTTP '+r.status()+' '+r.url())});
  p.on('console',m=>{if(m.type()==='error')err.push('console '+m.text())});
  await p.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
  const res=await p.goto(URL,{waitUntil:'networkidle0',timeout:30000});
  assert.equal(res.status(),200);await p.waitForFunction(()=>window.A18Canonical?.ready,{timeout:15000});
  assert(await p.evaluate(()=>Array.from(document.images).every(im=>im.naturalWidth>0)));
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await p.screenshot({path:path.join(__dirname,'QA_mobile_wood_empty_390x844.png'),fullPage:true});
  let states=0;
  for(const style of ['wood','gold','gold_sans_ornament','none']){
   await p.click('[data-style="'+style+'"]');
   for(const content of ['empty','photos','registration']){
    await p.click('[data-content="'+content+'"]');
    for(const size of [90,100,110]){
     await p.click('[data-size="'+size+'"]');
     await p.waitForFunction(()=>A18Canonical.ready);
     assert.deepEqual(await p.evaluate(()=>A18Canonical.state()),{style,content,size});
     assert(await p.$eval('#scene',el=>el.naturalWidth===546&&el.naturalHeight===483));
     if(style==='gold'&&content==='photos'&&size===100)await p.screenshot({path:path.join(__dirname,'QA_mobile_gold_photo_390x844.png'),fullPage:true});
     if(style==='wood'&&content==='registration'&&size===100)await p.screenshot({path:path.join(__dirname,'QA_mobile_register_390x844.png'),fullPage:true});
     states++;
    }
   }
  }
  assert.equal(states,36);assert.deepEqual(err,[]);
  console.log('A18_V05_BROWSER_PASS 390x844 DPR2 36 states, JS/HTTP 0, no overflow: '+URL);
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
