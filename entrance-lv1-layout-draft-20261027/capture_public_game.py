"""Capture actual PUBLIC A18 in isolated Chrome after real first-art tutorial.
No user profile or user IndexedDB accessed. Test sample artwork only.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
from io import BytesIO
import json

DEST=Path(__file__).resolve().parent
URL="https://arakiyuuta0314-sketch.github.io/a18-totteoki-museum/layout-test/index.html"
def sample_art():
    im=Image.new("RGB",(600,450),"#647d7d")
    d=ImageDraw.Draw(im)
    d.rectangle((0,295,600,450),fill="#49604e")
    d.ellipse((250,87,350,187),fill="#eac38b")
    d.polygon([(0,297),(170,155),(325,300)],fill="#778794")
    d.polygon([(176,297),(410,120),(600,301)],fill="#a7aeae")
    output=BytesIO();im.save(output,format="PNG");return output.getvalue()

with sync_playwright() as p:
    browser=p.chromium.launch(channel="chrome",headless=True)
    context=browser.new_context(viewport={"width":390,"height":844},
                                device_scale_factor=2,is_mobile=True,has_touch=True)
    page=context.new_page()
    errors=[];http_fail=[]
    page.on("pageerror", lambda ex:errors.append(str(ex)))
    page.on("response",lambda r:http_fail.append(f"{r.status} {r.url}") if r.status>=400 else None)
    response=page.goto(URL+"?qa=entrance-capture-20261027",
                       wait_until="domcontentloaded",timeout=45000)
    assert response.status==200,response.status
    page.locator("#a18OpeningStart").wait_for(timeout=60000)
    page.locator("#a18OpeningStart").click()
    page.locator("#a18OpeningSkip").click()
    page.locator("#a18PlayerName").fill("てすと")
    page.locator("#a18PlayerGender").select_option("male")
    page.locator("#a18MuseumTitle").fill("配置確認用の美術館")
    page.locator("#confirmName").click()
    page.locator("#overlay").wait_for(state="hidden",timeout=30000)

    # Walk to Butler in the actual game; do not bypass the tutorial.
    for _ in range(15):page.evaluate("window.__A18_SCENE_STUDY__.move('left')")
    for _ in range(5):page.evaluate("window.__A18_SCENE_STUDY__.move('up')")
    st=page.evaluate("window.__A18_SCENE_STUDY__.state()")
    assert st["interaction"] and st["interaction"]["type"]=="butler",st["pos"]
    page.locator("#act").click()
    page.locator("#tutorialButlerAction").click()
    page.locator("#name").fill("配置確認用の写真")
    page.locator("#photo").set_input_files({"name":"sample.png",
        "mimeType":"image/png","buffer":sample_art()})
    page.locator("#save").click()
    page.locator("#offerNo").wait_for(timeout=20000)
    page.locator("#offerNo").click()
    page.locator("#receiveWork").wait_for(timeout=20000)
    page.locator("#receiveWork").click()
    page.locator("#overlay").wait_for(state="hidden")
    for _ in range(4):page.evaluate("window.__A18_SCENE_STUDY__.move('left')")
    for _ in range(9):page.evaluate("window.__A18_SCENE_STUDY__.move('up')")
    page.evaluate("window.__A18_SCENE_STUDY__.move('right')")
    page.locator("#act").click()
    page.locator("#tutorialNext").wait_for(timeout=15000)
    for _ in range(3):
        page.locator("#tutorialNext").click()
    page.locator("#tutorialFreeRoam").wait_for(timeout=10000)
    page.locator("#tutorialFreeRoam").click()
    page.locator("#overlay").wait_for(state="hidden")
    # Return player to the default open space via real movement, preserving real NPC.
    for _ in range(13):page.evaluate("window.__A18_SCENE_STUDY__.move('right')")
    for _ in range(12):page.evaluate("window.__A18_SCENE_STUDY__.move('down')")
    page.wait_for_timeout(1100)
    st=page.evaluate("window.__A18_SCENE_STUDY__.state()")
    assert st["scene"]=="entrance" and st["galleryIndex"]==0,st
    page.screenshot(path=str(DEST/"live_public_game_original_390.png"),full_page=True,animations="disabled")
    page.locator("#world").screenshot(path=str(DEST/"live_public_game_world_390.png"),animations="disabled")
    # Only in this disposable isolated browser: test Butler moved together with desk.
    # The actual sprite is redrawn by the running game; no repo/user data is changed.
    for key,point in [("left_30",111),("left_48",93)]:
        page.evaluate("(x) => {window.A18Layout.BUTLER.x=x}",point)
        # Entrance renderer skips repaint unless movement/state signature changes.
        # A reversible real D-pad step invalidates its cache without save edits.
        page.evaluate("window.__A18_SCENE_STUDY__.move('up')")
        page.evaluate("window.__A18_SCENE_STUDY__.move('down')")
        page.wait_for_timeout(440)
        page.locator("#world").screenshot(
            path=str(DEST/("live_public_game_butler_"+key+"_390.png")),
            animations="disabled")
        page.screenshot(path=str(DEST/("live_public_full_butler_"+key+"_390.png")),
                        full_page=True,animations="disabled")
    report={"url":URL,"browser":"isolated Chrome Chromium channel=chrome",
       "viewport_css":{"width":390,"height":844,"dpr":2},
       "visible_work_count":len(st["works"]),
       "game_state":{k:st[k] for k in ["scene","galleryIndex","roomCapacity","pos","viewport","interaction","museumLevel"]},
       "page_errors":errors,"http_errors":http_fail,
       "page_title":page.title(),
       "world_box":page.locator("#world").bounding_box(),
       "canvas_box":page.locator("#game").bounding_box() if page.locator("#game").count() else None}
    (DEST/"live_public_game_capture.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("LIVE CAPTURE",json.dumps(report,ensure_ascii=False))
    assert not errors,errors
    assert not http_fail,http_fail
    context.close();browser.close()
