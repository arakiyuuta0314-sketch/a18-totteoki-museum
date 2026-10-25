const assert=require("node:assert/strict"),path=require("node:path");
const puppeteer=require("C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer");
const URL=process.env.A18_LIGHTS_URL||"http://127.0.0.1:18843/lighting-additional-sconces-v01/";
(async()=>{
const browser=await puppeteer.launch({headless:true,executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe",args:["--no-sandbox"]});
try{
 const page=await browser.newPage();const errors=[];
 page.on("pageerror",e=>errors.push("JS "+e.message));
 page.on("console",m=>{if(m.type()==="error")errors.push("Console "+m.text())});
 page.on("response",r=>{if(r.status()>=400)errors.push("HTTP "+r.status()+" "+r.url())});
 await page.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const res=await page.goto(URL,{waitUntil:"networkidle0",timeout:30000});
 assert.equal(res.status(),200);
 await page.waitForFunction(()=>window.A18Lighting?.ready,{timeout:15000});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),"page overflow");
 assert(await page.evaluate(()=>Array.from(document.images).every(x=>x.naturalWidth>0)),"comparison image missing");
 const ids=["outer_left","outer_right","foreground_left","foreground_right"];
 for(let bits=0;bits<16;bits++){
   for(let i=0;i<ids.length;i++){
    const desired=!!(bits&(1<<i)),sel='[data-lamp="'+ids[i]+'"]';
    if(await page.$eval(sel,x=>x.checked)!==desired)await page.click(sel);
   }
   for(const glow of [true,false]){
     const cur=await page.$eval("#glow",x=>x.checked);
     if(cur!==glow)await page.click("#glow");
     const state=await page.evaluate(()=>A18Lighting.state());
     assert.deepEqual(state.lit,ids.filter((_,i)=>!!(bits&(1<<i))));
     assert.equal(state.glow,glow);
     const hasContent=await page.evaluate(()=>{
       const el=document.querySelector("#scene"),data=el.getContext("2d").getImageData(100,100,1,1).data;
       return data[3]===255});
     assert(hasContent);
     if(bits===0&&glow)await page.screenshot({path:path.join(__dirname,"QA_mobile_all_off_390x844.png"),fullPage:true});
     if(bits===15&&glow)await page.screenshot({path:path.join(__dirname,"QA_mobile_all_on_390x844.png"),fullPage:true});
     if(bits===15&&!glow)await page.screenshot({path:path.join(__dirname,"QA_mobile_body_only_390x844.png"),fullPage:true});
   }
 }
 await page.click("#allOff");
 assert.equal((await page.evaluate(()=>A18Lighting.state())).lit.length,0);
 await page.click("#allOn");
 assert.equal((await page.evaluate(()=>A18Lighting.state())).lit.length,4);
 await page.click("#bodyOnly");
 assert.equal((await page.evaluate(()=>A18Lighting.state())).glow,false);
 assert.deepEqual(errors,[]);
 console.log("QA_BROWSER_PASS 390x844 DPR2 32 toggle combinations; all-off/all-on/body-only controls; JS/HTTP errors=0; overflow=0 URL="+URL);
} finally {await browser.close()}
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
