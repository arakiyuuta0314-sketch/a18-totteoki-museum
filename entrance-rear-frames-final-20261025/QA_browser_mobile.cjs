const assert=require('node:assert/strict');
const pp=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
const path=require('node:path');
(async()=>{
 const browser=await pp.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
 const page=await browser.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 page.on('response',r=>{if(r.status()>=400)errors.push(r.url()+' HTTP '+r.status())});
 try{
  await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:2});
  await page.goto('http://127.0.0.1:18821/entrance-rear-frames-final-20261025/',{waitUntil:'networkidle0',timeout:30000});
  await page.waitForFunction(()=>window.A18RearFrameQA?.ready===true,{timeout:15000});
  const first=await page.evaluate(()=>({state:window.A18RearFrameQA.state(),canvas:document.querySelector('#viewer').getBoundingClientRect().toJSON(),images:[...document.images].map(x=>[x.currentSrc.split('/').pop(),x.naturalWidth,x.naturalHeight])}));
  assert(first.canvas.width>300&&first.canvas.width<=390,JSON.stringify(first.canvas));
  assert(first.images.every(x=>x[1]>0));
  await page.screenshot({path:path.resolve(__dirname,'QA_browser_390x844.png'),fullPage:true});
  await page.$eval('#leftScale',e=>{e.value=90;e.dispatchEvent(new Event('input',{bubbles:true}))});
  await page.$eval('#rightScale',e=>{e.value=108;e.dispatchEvent(new Event('input',{bubbles:true}))});
  await page.click('#showPhoto');
  const second=await page.evaluate(()=>window.A18RearFrameQA.state());
  assert.deepEqual(second,{left:90,right:108,photos:false});
  await page.screenshot({path:path.resolve(__dirname,'QA_browser_controls_390x844.png'),fullPage:true});
  await page.click('#reset');
  assert.deepEqual(await page.evaluate(()=>window.A18RearFrameQA.state()),{left:100,right:100,photos:true});
  assert.equal(errors.length,0,JSON.stringify(errors));
  console.log('BROWSER PASS',JSON.stringify({viewport:[390,844],imageCount:first.images.length,canvas:first.canvas,stateChange:second,errorCount:0}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
