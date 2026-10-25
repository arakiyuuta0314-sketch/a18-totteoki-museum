const assert=require('node:assert/strict');
const path=require('node:path');
const puppeteer=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
 const page=await browser.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url())});
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 try{
 await page.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 await page.goto('http://127.0.0.1:18836/entrance-frames-independent-20261026/',{waitUntil:'networkidle0',timeout:30000});
 await page.waitForFunction(()=>window.A18Frames?.ready,{timeout:15000});
 const state=()=>page.evaluate(()=>window.A18Frames.state());
 assert.deepEqual(await state(),{style:'none',pic:'empty',size:100});
 assert(await page.evaluate(()=>[...document.images].every(i=>i.naturalWidth>0)));
 assert((await page.$eval('#scene',e=>e.getBoundingClientRect().width))>=330);
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'Horizontal overflow');
 await page.screenshot({path:path.join(__dirname,'QA_mobile_no_gold_390x844.png'),fullPage:true});
 let states=0;
 for(const sty of ['none','wood','gold_full']) {
   await page.click('#'+sty);
   for(const photo of ['empty','photos']){
    await page.click('#'+photo);
    for(const size of [90,100,110]){
     await page.click('#s'+size);
     await page.waitForFunction(()=>document.querySelector('#scene').complete&&document.querySelector('#scene').naturalWidth===546);
     const s=await state();assert.equal(s.style,sty);assert.equal(s.pic,photo);assert.equal(s.size,size);
     assert.equal(await page.$eval('#scene',e=>e.naturalHeight),483);
     states++;
     if(sty==='wood'&&photo==='photos'&&size===110)await page.screenshot({path:path.join(__dirname,'QA_mobile_wood_photo110_390x844.png'),fullPage:true});
     if(sty==='gold_full'&&photo==='empty'&&size===100)await page.screenshot({path:path.join(__dirname,'QA_mobile_gold_recovered_390x844.png'),fullPage:true});
    }
   }
 }
 assert.equal(states,18);
 assert.deepEqual(errors,[]);
 console.log('PASS MOBILE 390x844 DPR2 18 states; 3 styles x photos x 3 scales, no horizontal overflow, JS/HTTP errors=0');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
