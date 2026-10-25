const assert=require('node:assert/strict'),path=require('node:path'),puppeteer=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
const URL=process.env.A18_PROJECTIVE_URL||'http://127.0.0.1:18839/entrance-front-homography-v04-20261026/';
(async()=>{
 const browser=await puppeteer.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
 try{
  const page=await browser.newPage(),err=[];
  page.on('pageerror',e=>err.push('JS '+e.message));
  page.on('response',r=>{if(r.status()>=400)err.push('HTTP '+r.status()+' '+r.url())});
  page.on('console',m=>{if(m.type()==='error')err.push('console '+m.text())});
  await page.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
  const res=await page.goto(URL,{waitUntil:'networkidle0',timeout:30000});
  assert.equal(res.status(),200);
  await page.waitForFunction(()=>window.A18Projective?.ready,{timeout:15000});
  assert(await page.evaluate(()=>[...document.images].every(i=>i.naturalWidth>0)));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'Horizontal overflow');
  await page.screenshot({path:path.join(__dirname,'QA_mobile_new_frame_390x844.png'),fullPage:true});
  let states=0;
  for(const mode of ['new','v03','old','gold','none']){
    await page.click('[data-mode="'+mode+'"]');
    for(const photo of ['empty','photos']){
      await page.click('[data-photo="'+photo+'"]');
      for(const scale of [90,100,110]){
        await page.click('[data-scale="'+scale+'"]');
        await page.waitForFunction(()=>window.A18Projective.ready);
        assert.deepEqual(await page.evaluate(()=>A18Projective.state()),{mode,photo,scale});
        assert(await page.$eval('#scene',im=>im.naturalWidth===546&&im.naturalHeight===483));
        if(mode==='new'&&photo==='photos'&&scale===110)
          await page.screenshot({path:path.join(__dirname,'QA_mobile_photo_110_390x844.png'),fullPage:true});
        states++;
      }
    }
  }
  assert.equal(states,30);assert.deepEqual(err,[]);
  console.log('PASS 390x844 DPR2 30 states; no JS/HTTP errors, no horizontal overflow',URL);
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
