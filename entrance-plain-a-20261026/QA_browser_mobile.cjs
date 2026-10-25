const assert=require('node:assert/strict'),path=require('node:path');const pp=require('C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
(async()=>{const browser=await pp.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});const page=await browser.newPage(),errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url())});
try{await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:2});
await page.goto('http://127.0.0.1:18834/entrance-plain-a-20261026/',{waitUntil:'networkidle0',timeout:30000});
await page.waitForFunction(()=>window.A18Plain?.ready===true&&document.getElementById('main').naturalWidth===546);
assert.equal(await page.evaluate(()=>window.A18Plain.state()),'A18_entrance_A_plain_no_decor_preview.png');
assert(await page.evaluate(()=>[...document.images].every(i=>i.naturalWidth===546&&i.naturalHeight===483)));
assert((await page.$eval('#main',e=>e.getBoundingClientRect().width))>=300);
await page.screenshot({path:path.join(__dirname,'QA_mobile_A_plain_390x844.png'),fullPage:true});
await page.click('#viewBefore');await page.waitForFunction(()=>window.A18Plain.state()==='QA_prior_decorated_reference.png');
await page.screenshot({path:path.join(__dirname,'QA_mobile_decorated_390x844.png'),fullPage:true});
await page.click('#viewA');assert.equal(await page.evaluate(()=>window.A18Plain.state()),'A18_entrance_A_plain_no_decor_preview.png');
assert.equal(errors.length,0,JSON.stringify(errors));
console.log('PASS A FULL MOBILE QA',{viewport:[390,844],dpr:2,states:['A','decorated','A'],httpOrJsErrors:errors.length});}
finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});