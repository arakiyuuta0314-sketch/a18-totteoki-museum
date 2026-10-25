const assert=require('node:assert/strict'),path=require('node:path');
const puppeteer=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
(async()=>{const browser=await puppeteer.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});const page=await browser.newPage(),errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});page.on('response',r=>{if(r.status()>=400)errors.push(r.url()+' '+r.status())});
try{await page.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
await page.goto('http://127.0.0.1:18823/entrance-picture-lights-final-20261025/',{waitUntil:'networkidle0',timeout:30000});
await page.waitForFunction(()=>window.A18PictureLights?.ready===true,{timeout:12000});
const s=()=>page.evaluate(()=>window.A18PictureLights.state());
assert.deepEqual(await s(),{west:true,east:true});
const pics=await page.evaluate(()=>[...document.images].map(i=>i.naturalWidth));assert(pics.every(x=>x>0));
const w=await page.$eval('#canvas',el=>el.getBoundingClientRect().width);assert(w>300&&w<=390);
await page.screenshot({path:path.resolve(__dirname,'QA_mobile_390x844.png'),fullPage:true});
await page.click('#west');assert.deepEqual(await s(),{west:false,east:true});
await page.click('#east');assert.deepEqual(await s(),{west:false,east:false});
await page.screenshot({path:path.resolve(__dirname,'QA_mobile_both_off_390x844.png'),fullPage:true});
await page.click('#reset');assert.deepEqual(await s(),{west:true,east:true});
assert.equal(errors.length,0,JSON.stringify(errors));
console.log('PASS PictureLights Mobile',{viewport:[390,844],cssCanvasWidth:w,states:['on','west-off','both-off','reset'],javascriptErrors:0});}
finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});