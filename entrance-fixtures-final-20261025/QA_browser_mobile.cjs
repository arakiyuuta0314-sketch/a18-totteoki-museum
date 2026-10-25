const assert=require('node:assert/strict'),path=require('node:path');
const pp=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
(async()=>{
const browser=await pp.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
const page=await browser.newPage();const errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
page.on('response',r=>{if(r.status()>=400)errors.push(r.url()+' HTTP '+r.status())});
try{
await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:2});
await page.goto('http://127.0.0.1:18822/entrance-fixtures-final-20261025/',{waitUntil:'networkidle0',timeout:30000});
await page.waitForFunction(()=>window.A18Fixtures?.ready===true,{timeout:12000});
const init=await page.evaluate(()=>window.A18Fixtures.state());
assert(Object.values(init).every(Boolean));
const images=await page.evaluate(()=>[...document.images].map(i=>({name:i.src.split('/').pop(),w:i.naturalWidth})));
assert(images.every(i=>i.w>0),JSON.stringify(images));
assert((await page.$eval('#preview',el=>el.getBoundingClientRect().width))>=300);
await page.screenshot({path:path.resolve(__dirname,'QA_browser_mobile_390x844.png'),fullPage:true});
await page.click('#west_sign');await page.click('#east_sconce');
const mixed=await page.evaluate(()=>window.A18Fixtures.state());
assert(mixed.west_sign===false&&mixed.east_sign===true&&mixed.west_sconce===true&&mixed.east_sconce===false);
await page.screenshot({path:path.resolve(__dirname,'QA_browser_mixed_390x844.png'),fullPage:true});
await page.click('#reset');
assert(Object.values(await page.evaluate(()=>window.A18Fixtures.state())).every(Boolean));
assert.equal(errors.length,0,JSON.stringify(errors));
console.log('PASS_BROWSER_MOBILE',{width:390,devicePixelRatio:2,images:images.length,states:['all','mixed','reset'],errors:0});
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
