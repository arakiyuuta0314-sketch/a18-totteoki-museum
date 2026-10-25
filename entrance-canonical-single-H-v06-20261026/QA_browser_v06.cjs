const assert=require('node:assert/strict'),path=require('node:path'),puppeteer=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
const URL=process.env.A18_SINGLE_H_URL||'http://127.0.0.1:18841/entrance-canonical-single-H-v06-20261026/';
(async()=>{const browser=await puppeteer.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
try{
 const page=await browser.newPage(),errors=[];
 page.on('pageerror',e=>errors.push('JS '+e.message));
 page.on('console',msg=>{if(msg.type()==='error')errors.push('CONSOLE '+msg.text())});
 page.on('response',r=>{if(r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url())});
 await page.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const res=await page.goto(URL,{waitUntil:'networkidle0',timeout:30000});assert.equal(res.status(),200);
 await page.waitForFunction(()=>window.A18SingleH?.ready,{timeout:20000});
 assert(await page.evaluate(()=>[...document.images].every(i=>i.naturalWidth>0)),'unloaded images');
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'overflow');
 await page.screenshot({path:path.join(__dirname,'QA_mobile_wood_empty_390x844.png'),fullPage:true});
 let n=0;
 for(const style of ['wood','gold','gold_body','none']){
  await page.click('[data-style="'+style+'"]');
  for(const mode of ['empty','photos','registration']){
   await page.click('[data-mode="'+mode+'"]');
   for(const scale of [90,100,110]){
    await page.click('[data-scale="'+scale+'"]');
    await page.waitForFunction(()=>window.A18SingleH.ready,{timeout:10000});
    assert.deepEqual(await page.evaluate(()=>A18SingleH.state()),{style,mode,scale});
    assert(await page.$eval('#scene',e=>e.naturalWidth===546&&e.naturalHeight===483));
    if(style==='gold'&&mode==='photos'&&scale===100)await page.screenshot({path:path.join(__dirname,'QA_mobile_gold_photos_390x844.png'),fullPage:true});
    if(style==='wood'&&mode==='registration'&&scale===100)await page.screenshot({path:path.join(__dirname,'QA_mobile_registration_390x844.png'),fullPage:true});
    n++;
   }
  }
 }
 assert.equal(n,36);assert.deepEqual(errors,[]);
 console.log('V06_BROWSER_PASS viewport390x844 DPR2, 36 states, 0 console/js/http errors, no overflow. '+URL);
}finally{await browser.close()}})().catch(e=>{console.error(e.stack||e);process.exit(1)});
