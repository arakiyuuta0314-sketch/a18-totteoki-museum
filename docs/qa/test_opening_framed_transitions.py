"""A18 scene-only transitions: isolated-browser visual bounds and safe replay."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json

ROOT=Path(__file__).resolve().parents[2]
QA=Path(__file__).parent
PORT=18782
report={"checks":[],"errors":[]}
def require(name,ok,detail=None):
    report["checks"].append({"name":name,"pass":bool(ok),"detail":detail})
    if not ok:raise AssertionError(name+" "+str(detail))
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
def advance_until(page,select,limit=55):
    for i in range(limit):
        if page.locator(select).count() and page.locator(select).is_visible():return
        page.locator("#a18OpeningDialog").click()
        page.wait_for_timeout(80)
    page.locator(select).wait_for(timeout=10000)
def rect(el):
    b=el.bounding_box()
    if b is None:raise AssertionError("missing visible bounds")
    return {key:round(b[key],1) for key in ("x","y","width","height")}
def same_rect(a,b):
    return all(abs(a[k]-b[k])<.2 for k in ("x","y","width","height"))
def anchored_dialog(a,b):
    # Input forms may grow the dialogue upward; the lower edge and width stay fixed.
    return (abs(a["x"]-b["x"])<.2 and abs(a["width"]-b["width"])<.2 and
            abs((a["y"]+a["height"])-(b["y"]+b["height"]))<.2)
def main():
    server=ThreadingHTTPServer(("127.0.0.1",PORT),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                                      args=["--no-sandbox","--disable-gpu"])
            for width,height in [(390,844),(320,700)]:
                ctx=browser.new_context(viewport={"width":width,"height":height},is_mobile=True,has_touch=True,device_scale_factor=2)
                page=ctx.new_page()
                page.on("pageerror",lambda error:report["errors"].append(str(error)))
                page.goto(f"http://127.0.0.1:{PORT}/layout-test/index.html",wait_until="domcontentloaded",timeout=30000)
                page.locator("#a18OpeningStart").wait_for(timeout=45000)
                page.locator("#a18OpeningStart").click()
                page.locator("#a18OpeningVisual").wait_for()
                visual=page.locator("#a18OpeningVisual")
                dialog=page.locator("#a18OpeningDialog")
                fixed_visual=rect(visual)
                fixed_dialog=rect(dialog)
                frame=rect(page.locator(".a18-opening-frame"))
                require("image frame narrower than overall scene "+str(width),
                        fixed_visual["height"]<frame["height"]*.4,{"visual":fixed_visual,"frame":frame})
                require("white/dim curtain nested in image frame "+str(width),
                        page.locator("#a18OpeningVisual > #a18OpeningVisualCurtain").count()==1)
                require("no whole-scene black curtain "+str(width),
                        page.locator("#a18OpeningCurtain").count()==0)
                page.evaluate("""() => {
                    window.__openingFx=[];
                    const visual=document.querySelector('#a18OpeningVisual');
                    const observe=()=>{
                        const f=visual.getBoundingClientRect();
                        const curtain=document.querySelector('#a18OpeningVisualCurtain');
                        const c=curtain.getBoundingClientRect();
                        window.__openingFx.push({
                            incoming:visual.querySelectorAll('.a18-opening-incoming').length,
                            dim:curtain.classList.contains('dim'),
                            white:curtain.classList.contains('white'),
                            visible:curtain.classList.contains('visible'),
                            bounded: c.left>=f.left-1 && c.top>=f.top-1 &&
                                    c.right<=f.right+1 && c.bottom<=f.bottom+1
                        });
                    };
                    new MutationObserver(observe).observe(visual,{
                        childList:true,subtree:true,attributes:true,attributeFilter:['class']
                    });
                    observe();
                }""")
                advance_until(page,"#a18OpeningName")
                require("scene 3 reached "+str(width),page.locator("#a18OpeningImage").get_attribute("src").endswith("scene-03.webp"))
                require("fixed black-band image rectangle "+str(width),same_rect(fixed_visual,rect(visual)))
                require("fixed dialogue rectangle "+str(width),anchored_dialog(fixed_dialog,rect(dialog)))
                page.screenshot(path=str(QA/("framed_transition_scene3_"+str(width)+".png")),full_page=True)
                page.locator("#a18OpeningName").fill("てすと")
                page.locator("#a18OpeningNameOk").click()
                advance_until(page,"#a18OpeningFemale")
                page.locator("#a18OpeningFemale").click()
                advance_until(page,'#a18OpeningImage[src$="scene-04.webp"]')
                page.wait_for_timeout(160)
                events=page.evaluate("window.__openingFx")
                require("all transition overlays stay bounded "+str(width),all(x["bounded"] for x in events))
                require("uses overlapping image fades "+str(width),sum(x["incoming"]>0 for x in events)>0)
                require("only scene 1->2 uses partial dim "+str(width),any(x["dim"] for x in events))
                require("dialogue stays fixed at scene 4 "+str(width),anchored_dialog(fixed_dialog,rect(dialog)))
                page.screenshot(path=str(QA/("framed_transition_scene4_"+str(width)+".png")),full_page=True)
                advance_until(page,"#a18OpeningMuseumTitle",limit=28)
                events=page.evaluate("window.__openingFx")
                require("end uses image-only white "+str(width),any(x["white"] and x["visible"] for x in events))
                require("end white remains bounded "+str(width),all(x["bounded"] for x in events))
                require("butler loads after ending "+str(width),page.locator("#a18OpeningRoot").is_hidden())
                ctx.close()
            browser.close()
        require("no page errors",not report["errors"],report["errors"])
    finally:
        server.shutdown()
        (QA/"framed_transitions_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":
    try:
        main()
        print("PASS",len(report["checks"]),"/",len(report["checks"]))
    except Exception as exc:
        report["failure"]=repr(exc)
        (QA/"framed_transitions_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        raise
