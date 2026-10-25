const assert=require('node:assert/strict'),path=require('node:path');
const puppeteer=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
const URL=process.env.A18_FRONT_URL || 'http://127.0.0.1:18838/entrance-front-wood-aligned-v03-20261026/';
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
 const page=await browser.newPage(); const errors=[];
 page.on('pageerror',x=>errors.push('JS '+x.message));page.on('console',x=>{if(x.type()==='error')errors.push('Console '+x.text())});
 page.on('response',r=>{if(r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url())});
 try {
 await page.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const res=await page.goto(URL,{waitUntil:'networkidle0',timeout:30000});
 assert.equal(res.status(),200);
 await page.waitForFunction(()=>window.A18Front?.ready,{timeout:15000});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'horizontal overflow');
 assert(await page.evaluate(()=>[...document.images].every(i=>i.naturalWidth>0)));
 assert.deepEqual(await page.evaluate(()=>A18Front.state()),{style:'new',photo:'empty',size:100});
 await page.screenshot({path:path.join(__dirname,'QA_mobile_front_corrected_390x844.png'),fullPage:true});
 let n=0;
 for(const s of ['new','old','none','gold']){
  await page.click('#'+s);
  for(const p of ['empty','photos']){
   await page.click('#'+p);
   for(const z of [90,100,110]){
    await page.click('#sz'+z);
    await page.waitForFunction(()=>A18Front.ready);
    assert.deepEqual(await page.evaluate(()=>A18Front.state()),{style:s,photo:p,size:z});
    assert(await page.$eval('#scene',e=>e.naturalWidth===546&&e.naturalHeight===483));
    if(s==='new'&&p==='photos'&&z===110)await page.screenshot({path:path.join(__dirname,'QA_mobile_front_photo110_390x844.png'),fullPage:true});
    n++;
   }
  }
 }
 assert.equal(n,24);
 assert.deepEqual(errors,[]);
 console.log('QA_BROWSER_PASS mobile390x844 DPR2 states='+n+' js/http=0 horizontal_overflow=0 '+URL);
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
