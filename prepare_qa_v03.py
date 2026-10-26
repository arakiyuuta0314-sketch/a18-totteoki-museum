from pathlib import Path
import shutil
root=Path(r'C:\Users\User\source\repos\a18-entrance-art-polish-v03-20261026')
p=root/'entrance-art-polish-v03-20261026'/'QA_browser_v03.cjs'
s=(root/'entrance-wood-onoff-v02-20261026'/'QA_browser_wood_onoff.cjs').read_text(encoding="utf8")
s=s.replace('const url=process.env.A18_WOOD_URL||"http://127.0.0.1:18852/";','const url=process.env.A18_WOOD_URL||"http://127.0.0.1:18854/";')
s=s.replace(' assert.deepEqual(errors,[]);',''' await p.click("#zoomDetails summary");
 assert.equal(await p.$eval("#zoomDetails",x=>x.open),true);
 await p.evaluate(async()=>{for(const im of document.querySelectorAll("#zoomDetails img"))await im.decode()});
 assert(await p.evaluate(()=>[...document.querySelectorAll("#zoomDetails img")].every(i=>i.naturalWidth>0)));
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
 await p.screenshot({path:path.join(__dirname,"QA_mobile_zoom_OPEN_390x844.png"),fullPage:true});
 assert.deepEqual(errors,[]);''')
p.write_text(s,encoding='utf8')
print('QA_READY',p)
