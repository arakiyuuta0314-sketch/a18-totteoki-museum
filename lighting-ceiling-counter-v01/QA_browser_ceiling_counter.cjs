const assert=require("node:assert/strict"),path=require("node:path");
const puppeteer=require("C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer");
const URL=process.env.A18_CEILING_DESK_URL||"http://127.0.0.1:18844/lighting-ceiling-counter-v01/";
(async()=>{const browser=await puppeteer.launch({headless:true,executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe",args:["--no-sandbox"]});
try{
 const p=await browser.newPage(),err=[];
 p.on("pageerror",e=>err.push("JS: "+e.message));
 p.on("console",msg=>{if(msg.type()==="error")err.push("CONSOLE "+msg.text())});
 p.on("response",r=>{if(r.status()>=400)err.push("HTTP "+r.status()+" "+r.url())});
 await p.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const response=await p.goto(URL,{waitUntil:"networkidle0",timeout:30000});
 assert.equal(response.status(),200);
 await p.waitForFunction(()=>window.A18Lighting51?.ready,{timeout:12000});
 assert(await p.evaluate(()=>[...document.images].every(x=>x.naturalWidth>0)));
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 let count=0;
 for(let mask=0;mask<8;mask++){
  const desired={ceiling:!!(mask&1),desk:!!(mask&2),emission:!!(mask&4)};
  for(const [id,v] of Object.entries(desired)){
   if(await p.$eval("#"+id,el=>el.checked)!==v)await p.click("#"+id);
  }
  assert.deepEqual(await p.evaluate(()=>A18Lighting51.state()),desired);
  assert(await p.$eval("#scene",el=>el.getContext("2d").getImageData(100,100,1,1).data[3]===255));
  if(mask===0)await p.screenshot({path:path.join(__dirname,"QA_mobile_all_off_390x844.png"),fullPage:true});
  if(mask===3)await p.screenshot({path:path.join(__dirname,"QA_mobile_body_only_390x844.png"),fullPage:true});
  if(mask===7)await p.screenshot({path:path.join(__dirname,"QA_mobile_all_on_390x844.png"),fullPage:true});
  count++;
 }
 await p.click("#allOn");assert.deepEqual(await p.evaluate(()=>A18Lighting51.state()),{ceiling:true,desk:true,emission:true});
 await p.click("#bodyOnly");assert.deepEqual(await p.evaluate(()=>A18Lighting51.state()),{ceiling:true,desk:true,emission:false});
 await p.click("#allOff");assert.equal((await p.evaluate(()=>A18Lighting51.state())).ceiling,false);
 assert.equal((await p.evaluate(()=>A18Lighting51.state())).desk,false);
 assert.deepEqual(err,[]);
 console.log("QA_CEILING_COUNTER_BROWSER_PASS: 390x844 DPR2, 8 combinations, all 3 buttons, JS/HTTP errors=0, no horizontal overflow, url="+URL);
}finally{await browser.close()}
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
