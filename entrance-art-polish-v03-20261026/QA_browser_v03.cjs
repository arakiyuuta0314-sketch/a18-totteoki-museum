const assert=require("node:assert/strict"),path=require("node:path");
const puppeteer=require("C:/Users/User/AppData/Local/npm-cache/_npx/4b4c857f6efdfb61/node_modules/puppeteer");
const url=process.env.A18_WOOD_URL||"http://127.0.0.1:18854/";
(async()=>{const browser=await puppeteer.launch({headless:true,executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe",args:["--no-sandbox"]});
try{
 const p=await browser.newPage(),errors=[];
 p.on("pageerror",e=>errors.push("JS:"+e.message));
 p.on("console",m=>{if(m.type()==="error")errors.push("CONSOLE:"+m.text())});
 p.on("response",r=>{if(r.status()>=400)errors.push("HTTP:"+r.status()+" "+r.url())});
 await p.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const response=await p.goto(url,{waitUntil:"networkidle0",timeout:30000});
 assert.equal(response.status(),200);
 await p.waitForFunction(()=>window.A18WoodToggle52?.ready===true,{timeout:12000});
 assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
 assert.equal(await p.evaluate(()=>[...document.querySelectorAll('#compareGrid img')].every(i=>i.naturalWidth===546&&i.naturalHeight===483)),true);
 const check=()=>p.evaluate(()=>({state:A18WoodToggle52.state(),canvas:[mainScene.width,mainScene.height],
    pressed:[btnOff.getAttribute("aria-pressed"),btnOn.getAttribute("aria-pressed")],
    pixel:[...mainScene.getContext("2d").getImageData(438,205,1,1).data],
    compare:!compareGrid.hidden}));
 let x=await check();assert.deepEqual(x.canvas,[546,483]);assert.equal(x.state.wood,false);assert.deepEqual(x.pressed,["true","false"]);
 await p.screenshot({path:path.join(__dirname,"QA_mobile_OFF_390x844.png"),fullPage:true});
 await p.click("#btnOn");x=await check();assert.equal(x.state.wood,true);assert.deepEqual(x.pressed,["false","true"]);
 await p.screenshot({path:path.join(__dirname,"QA_mobile_ON_390x844.png"),fullPage:true});
 await p.click("#btnOff");assert.equal((await check()).state.wood,false);
 await p.click("#compareToggle");assert.equal((await check()).compare,false);
 await p.click("#compareToggle");assert.equal((await check()).compare,true);
 await p.click("#zoomDetails summary");
 assert.equal(await p.$eval("#zoomDetails",x=>x.open),true);
 await p.evaluate(async()=>{for(const im of document.querySelectorAll("#zoomDetails img"))await im.decode()});
 assert(await p.evaluate(()=>[...document.querySelectorAll("#zoomDetails img")].every(i=>i.naturalWidth>0)));
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
 await p.screenshot({path:path.join(__dirname,"QA_mobile_zoom_OPEN_390x844.png"),fullPage:true});
 assert.deepEqual(errors,[]);
 console.log("QA_WOOD_ONOFF_BROWSER_PASS",JSON.stringify({url,width:390,height:844,DPR:2,buttonTransitions:3,comparisonSwitches:2,canvas:[546,483],errors}));
} finally {await browser.close();}
})().catch(e=>{console.error("QA_WOOD_ONOFF_FAIL",e.stack||e);process.exit(1);});
