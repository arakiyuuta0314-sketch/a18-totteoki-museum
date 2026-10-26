"""A18 isolated opening flow regression, never touches real browser save."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json, time, contextlib

ROOT=Path(__file__).resolve().parents[2]
QA=Path(__file__).parent
PORT=18781
results={"checks":[],"console_errors":[],"page_errors":[]}
def check(label,ok,info=None):
    results["checks"].append({"name":label,"pass":bool(ok),"info":info})
    if not ok:raise AssertionError(label+" "+str(info))
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
def take(page,name):
    page.screenshot(path=str(QA/name),animations="disabled",full_page=True)
def press_until(page,locator,limit=30):
    for n in range(limit):
        if page.locator(locator).count() and page.locator(locator).is_visible():return
        try:
            page.locator("#a18OpeningDialog").click(timeout=1500)
        except PlaywrightTimeoutError:
            if page.locator(locator).count() and page.locator(locator).is_visible():return
            raise
        page.wait_for_timeout(85)
    page.wait_for_selector(locator,timeout=10000)
def run():
    server=ThreadingHTTPServer(("127.0.0.1",PORT),partial(Quiet,directory=str(ROOT)))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
      with sync_playwright() as p:
        chrome=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        browser=p.chromium.launch(headless=True,executable_path=chrome,args=["--no-sandbox","--disable-gpu"])
        ctx=browser.new_context(viewport={"width":390,"height":844},is_mobile=True,device_scale_factor=2,has_touch=True)
        page=ctx.new_page()
        page.on("pageerror",lambda e:results["page_errors"].append(str(e)))
        page.on("console",lambda m:results["console_errors"].append(m.text) if m.type=="error" else None)
        url=f"http://127.0.0.1:{PORT}/layout-test/index.html"
        page.goto(url,wait_until="domcontentloaded",timeout=30000)
        page.locator("#a18OpeningStart").wait_for(timeout=45000)
        check("fresh title opens",page.locator("#a18OpeningStart").is_visible())
        img=page.evaluate("getComputedStyle(document.querySelector('.a18-opening-title')).backgroundImage")
        check("title separate image asset","title-background.webp" in img)
        check("title has only one functional button",page.locator("#a18OpeningStart").count()==1)
        take(page,"opening_v1_01_title_390.png")
        page.locator("#a18OpeningStart").click()
        page.wait_for_selector("#a18OpeningDialog")
        check("first protagonist line",page.locator("#a18OpeningSpeaker").inner_text()=="あなた")
        page.wait_for_timeout(140)
        take(page,"opening_v1_02_scene1_390.png")
        press_until(page,"#a18OpeningName")
        check("scene three name flow",page.locator("#a18OpeningImage").get_attribute("src").endswith("scene-03.webp"))
        take(page,"opening_v1_03_name_390.png")
        page.locator("#a18OpeningName").fill("花子")
        page.locator("#a18OpeningNameOk").click()
        press_until(page,"#a18OpeningFemale")
        check("gender choice after name",page.locator("#a18OpeningFemale").is_visible())
        take(page,"opening_v1_04_gender_390.png")
        page.locator("#a18OpeningFemale").click()
        # Advance through final light dialogue until the museum naming scene.
        press_until(page,"#a18OpeningMuseumTitle",limit=32)
        check("museum after white fade",page.locator("#a18OpeningRoot").is_hidden())
        check("butler addresses female honorific","花子お嬢様" in page.locator("#dialog").inner_text())
        take(page,"opening_v1_05_butler_museum_390.png")
        page.locator("#a18OpeningMuseumTitle").fill("星空の美術館")
        page.locator("#a18OpeningMuseumOk").click()
        page.locator("#startTour").wait_for(timeout=10000)
        check("name persisted after museum choice","星空の美術館" in page.locator("#museumName").inner_text())
        take(page,"opening_v1_06_tour_390.png")
        page.locator("#startTour").click()
        page.wait_for_timeout(400)
        check("normal museum interaction returns",page.locator("#a18OpeningRoot").is_hidden() and page.locator("#overlay").is_hidden())
        page.reload(wait_until="domcontentloaded")
        page.locator("#a18OpeningStart").wait_for(timeout=45000)
        page.locator("#a18OpeningStart").click()
        page.wait_for_timeout(450)
        check("saved profile skips replay",page.locator("#a18OpeningRoot").is_hidden() and page.locator("#a18OpeningName").count()==0)
        check("saved title persists","星空の美術館" in page.locator("#museumName").inner_text())
        page.locator("#settingsGear").click()
        page.locator("#p6StoryHistory").click()
        page.locator('[data-p6-replay="intro-v1"]').click()
        page.locator("#a18OpeningDialog").wait_for()
        check("intro replay opens sepia without changing save",page.locator("#a18OpeningRoot").is_visible())
        page.locator("#a18OpeningSkip").click()
        page.locator("#p6HistoryBack").wait_for()
        page.locator("#p6HistoryBack").click()
        page.locator("#closeSettings").click()
        check("replay leaves saved data unchanged","星空の美術館" in page.locator("#museumName").inner_text())
        ctx.close()
        # second clean browser checks skip -> mandatory default form
        ctx2=browser.new_context(viewport={"width":320,"height":700},is_mobile=True,has_touch=True)
        page2=ctx2.new_page()
        page2.on("pageerror",lambda e:results["page_errors"].append(str(e)))
        page2.goto(url,wait_until="domcontentloaded",timeout=30000)
        page2.locator("#a18OpeningStart").wait_for(timeout=45000)
        page2.locator("#a18OpeningStart").click()
        page2.locator("#a18OpeningSkip").click()
        page2.locator("#a18PlayerName").wait_for(timeout=10000)
        check("skip preserves mandatory profile input",page2.locator("#a18PlayerName").is_visible())
        take(page2,"opening_v1_07_skip_320.png")
        ctx2.close();browser.close()
      check("no page errors",not results["page_errors"],results["page_errors"])
    finally:server.shutdown()
    (QA/"opening_v1_qa.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__":
    try:
        run()
        print("PASS",len(results["checks"]),"/",len(results["checks"]))
    except Exception as e:
        results["failure"]=repr(e)
        (QA/"opening_v1_qa.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
        print("FAIL",repr(e))
        raise
