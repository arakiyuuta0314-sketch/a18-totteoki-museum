"""E2E: first butler meeting -> real photo registration -> wall display -> wooden frame gift.
Isolated Chrome + IndexedDB; never accesses user profile or public-site save.
"""
from pathlib import Path
from io import BytesIO
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
from PIL import Image
import json, time

ROOT=Path(__file__).resolve().parents[2]
QA=Path(__file__).parent
PORT=18787
report={"checks":[],"page_errors":[],"messages":[]}
def assert_pass(name,ok,detail=None):
    report["checks"].append({"name":name,"pass":bool(ok),"detail":detail})
    if not ok:raise AssertionError(f"{name}: {detail}")
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
def picture():
    img=Image.new('RGB',(640,480),(132,75,39))
    for x in range(640):
        for y in range(480):
            if (x//32+y//32)%2==0:img.putpixel((x,y),(230,195,112))
    b=BytesIO();img.save(b,format="PNG");return b.getvalue()
def game(page):
    return page.evaluate("window.__A18_SCENE_STUDY__.state()")
def save(page):
    return page.evaluate("async()=>await window.A18P2Store.load()")
def intro(page):
    return next(x for x in save(page)["progression"]["events"] if x["id"]=="intro-v1")
def boot_skip(page):
    page.goto(f"http://127.0.0.1:{PORT}/layout-test/index.html",wait_until="domcontentloaded",timeout=30000)
    page.locator("#a18OpeningStart").wait_for(timeout=40000)
    page.locator("#a18OpeningStart").click()
    page.locator("#a18OpeningSkip").click()
    page.locator("#a18PlayerName").fill("花子")
    page.locator("#a18PlayerGender").select_option("female")
    page.locator("#a18MuseumTitle").fill("最初の美術館")
    page.locator("#confirmName").click()
    page.locator("#overlay").wait_for(state="hidden",timeout=15000)
    assert_pass("profile title stored",save(page)["museumTitle"]=="最初の美術館")
    assert_pass("intro stays queued after profile",intro(page)["status"]=="queued")
    hint=page.locator("#hint")
    assert_pass("initial obsolete walk-up message absent",
                "館長を歩かせて" not in hint.inner_text())
    assert_pass("tutorial hint placed near bottom",
                page.evaluate("""() => {
                    const h=document.querySelector('#hint'),s=document.querySelector('#stage');
                    const hb=h.getBoundingClientRect(),sb=s.getBoundingClientRect();
                    return hb.top>sb.top+sb.height*.5 &&
                           hb.bottom<sb.bottom-164+5;
                }"""))
    assert_pass("no intro auto-finish button",page.locator("#startTour").count()==0)
def walk_to_butler(page):
    for _ in range(15):page.evaluate("window.__A18_SCENE_STUDY__.move('left')")
    for _ in range(5):page.evaluate("window.__A18_SCENE_STUDY__.move('up')")
    state=game(page)
    report["messages"].append({"walkedButler":state["pos"],"interaction":state["interaction"]})
    assert_pass("physical D-pad walk reaches butler",state["interaction"] is not None and state["interaction"]["type"]=="butler",state["pos"])
    page.locator("#act").click()
def register(page,via_walk=True):
    if via_walk:walk_to_butler(page)
    else:page.evaluate("window.__A18_SCENE_STUDY__.butlerDialog()")
    page.locator("#tutorialButlerAction").wait_for()
    assert_pass("butler starts guided registration","最初の作品を預ける" in page.locator("#tutorialButlerAction").inner_text())
    page.locator("#tutorialButlerAction").click()
    assert_pass("obsolete completion and pieces inputs removed",
                page.locator("#date, #pieces, #dateToday, #dateClear").count()==0)
    assert_pass("only title memory and photo are requested",
                page.locator("#name, #notes, #photo").count()==3)
    page.screenshot(path=str(QA/"first_art_registration_simple_390.png"),full_page=True)
    page.locator("#name").fill("大切な景色")
    page.locator("#photo").set_input_files({"name":"my-memory.png","mimeType":"image/png","buffer":picture()})
    page.locator("#save").click()
    page.locator("#offerNo").wait_for(timeout=16000)
    # Make the first completion line deterministic: it previously said 「館長」.
    page.evaluate("Math.random = () => 0")
    page.locator("#offerNo").click()
    page.locator("#receiveWork").wait_for(timeout=30000)
    handover=page.locator("#dialog").inner_text()
    assert_pass("handover addresses player by name",
                "花子お嬢様" in handover and "館長" not in handover,handover)
    assert_pass("saved photo is real local blob",len(save(page)["works"])==1 and
        page.evaluate("async()=> (await window.A18P2Store.load()).works[0].originalBlob.size")>1000)
    assert_pass("photo saved before handing over",game(page)["carrying"]==save(page)["works"][0]["id"])
    assert_pass("gift not issued by registration",intro(page)["status"]=="queued")
    assert_pass("legacy metadata not populated in new registration",
                save(page)["works"][0]["complete"] is None and save(page)["works"][0]["pieces"] is None)
    hint=page.locator("#hint").inner_text()
    assert_pass("hint uses visible green placement outline",
        "緑の枠" in hint and "ここに飾る" in hint and "奥の額縁" not in hint,hint)
    page.locator("#receiveWork").click()
    page.locator("#overlay").wait_for(state="hidden")
def placement_gift(page):
    # Physically walk from the butler to the rear-left frame and use the visible action button.
    # Step around the butler's collision rectangle before approaching the wall.
    for _ in range(4):page.evaluate("window.__A18_SCENE_STUDY__.move('left')")
    for _ in range(9):page.evaluate("window.__A18_SCENE_STUDY__.move('up')")
    page.evaluate("window.__A18_SCENE_STUDY__.move('right')")
    status=game(page)
    report["messages"].append({"walkedFrame":status["pos"],"interaction":status["interaction"]})
    assert_pass("physical walk reaches first empty frame",status["interaction"] is not None and
        status["interaction"]["type"]=="art" and status["interaction"]["i"]==0,status)
    assert_pass("physical action offers place",page.locator("#act").inner_text()=="ここに飾る")
    page.screenshot(path=str(QA/"first_art_tutorial_green_outline_390.png"),full_page=True)
    page.locator("#act").click()
    page.locator("#tutorialNext").wait_for(timeout=15000)
    assert_pass("first wall fixture assigned",save(page)["works"][0]["fixtureId"]=="frame-0-0")
    assert_pass("frame remains pending until gift",intro(page)["status"]=="queued")
    page.wait_for_timeout(350)
    before=page.locator("#world").screenshot(animations="disabled")
    page.screenshot(path=str(QA/"first_art_tutorial_before_gift_390.png"),full_page=True)
    assert_pass("butler says first photo displayed","最初の一枚" in page.locator("#dialog").inner_text())
    page.locator("#tutorialNext").click()
    page.locator("#tutorialNext").click()
    assert_pass("butler presents wood frame","木製のフレーム" in page.locator("#dialog").inner_text())
    page.locator("#tutorialNext").click()
    page.locator("#tutorialFreeRoam").wait_for(timeout=13000)
    assert_pass("gift persists in intro-v1 status",intro(page)["status"]=="seen")
    final_lines=page.locator("#dialog").inner_text()
    assert_pass("free-roam blessing addresses player by name",
        "花子お嬢様" in final_lines and "館長" not in final_lines,final_lines)
    assert_pass("tutorial hint disappears on completion",page.locator("#hint").is_hidden())
    page.wait_for_timeout(350)
    after=page.locator("#world").screenshot(animations="disabled")
    assert_pass("wooden border visually appears after gift",before!=after)
    page.screenshot(path=str(QA/"first_art_tutorial_after_gift_390.png"),full_page=True)
    page.locator("#tutorialFreeRoam").click()
    page.locator("#overlay").wait_for(state="hidden")
    assert_pass("free roam after gift",not page.locator("#overlay").is_visible())
    page.evaluate("window.__A18_SCENE_STUDY__.list()")
    assert_pass("artwork list omits obsolete metadata",
                "完成日" not in page.locator("#dialog").inner_text() and
                "ピース" not in page.locator("#dialog").inner_text())
    page.locator('[data-work]').first.click()
    assert_pass("photo viewer omits obsolete metadata",
                "完成日" not in page.locator("#photoDetails").inner_text() and
                "ピース" not in page.locator("#photoDetails").inner_text())
    page.evaluate("window.A18Viewer.close()")
    page.evaluate("window.__A18_SCENE_STUDY__.inspect(0)")
    assert_pass("artwork detail omits obsolete metadata",
                "完成日" not in page.locator("#dialog").inner_text() and
                "ピース" not in page.locator("#dialog").inner_text())
    page.reload(wait_until="domcontentloaded")
    page.locator("#a18OpeningStart").click()
    page.wait_for_timeout(650)
    assert_pass("photo and frame survive restart",len(save(page)["works"])==1 and
      save(page)["works"][0]["fixtureId"]=="frame-0-0" and intro(page)["status"]=="seen")
    page.evaluate("window.__A18_SCENE_STUDY__.butlerDialog()")
    assert_pass("normal butler restored",page.locator("#rpgAdvance").count()==1 and
        page.locator("#tutorialNext").count()==0)
    page.screenshot(path=str(QA/"first_art_tutorial_free_390.png"),full_page=True)
def interruption(page):
    boot_skip(page)
    register(page)
    page.reload(wait_until="domcontentloaded")
    page.locator("#a18OpeningStart").click()
    page.wait_for_timeout(400)
    assert_pass("reopen keeps photo without completing intro",
        intro(page)["status"]=="queued" and len(save(page)["works"])==1)
    page.evaluate("window.__A18_SCENE_STUDY__.butlerDialog()")
    page.locator("#tutorialButlerAction").wait_for()
    assert_pass("butler resumes carried art guidance",
                "飾りに行く" in page.locator("#tutorialButlerAction").inner_text())
    assert_pass("butler identifies green frame",
                "緑の枠" in page.locator("#dialog").inner_text())
    page.locator("#tutorialButlerAction").click()
    page.evaluate("window.__A18_SCENE_STUDY__.inspect(0)")
    page.locator("#tutorialNext").wait_for()
    assert_pass("first placement after reload triggers gift",intro(page)["status"]=="queued")
    page.reload(wait_until="domcontentloaded")
    page.locator("#a18OpeningStart").click()
    page.wait_for_timeout(450)
    assert_pass("reload during gift never skips it",intro(page)["status"]=="queued" and
                save(page)["works"][0]["fixtureId"]=="frame-0-0")
    page.evaluate("window.__A18_SCENE_STUDY__.butlerDialog()")
    page.locator("#tutorialNext").wait_for()
    assert_pass("gift can resume from butler after interrupted dialogue",
                "最初の一枚" in page.locator("#dialog").inner_text())
def main():
    server=ThreadingHTTPServer(("127.0.0.1",PORT),partial(Quiet,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox","--disable-gpu"])
        ctx=browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
        page=ctx.new_page()
        page.on("pageerror",lambda err:report["page_errors"].append(str(err)))
        boot_skip(page)
        anchors=game(page)["interactionAnchors"]
        report["messages"].append({"entranceAnchors":anchors,"pos":game(page)["pos"]})
        register(page)
        placement_gift(page)
        ctx.close()
        ctx2=browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
        page2=ctx2.new_page()
        page2.on("pageerror",lambda err:report["page_errors"].append(str(err)))
        interruption(page2)
        ctx2.close()
        browser.close()
      assert_pass("no page errors",not report["page_errors"],report["page_errors"])
    finally:
      server.shutdown()
      (QA/"first_art_tutorial_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
if __name__=="__main__":
    try:
        main()
        print(f"PASS {sum(x['pass'] for x in report['checks'])}/{len(report['checks'])}")
    except Exception as exc:
        report["failure"]=repr(exc)
        (QA/"first_art_tutorial_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
        print("FAIL",repr(exc))
        raise
