from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/layout-test/placement-editor/"
checks=[]
def check(msg,ok):
 checks.append([msg,bool(ok)])
 if not ok:raise AssertionError(msg)
with sync_playwright() as p:
 browser=p.chromium.launch(channel="chrome",headless=True)
 for label,kwargs in [
  ("desktop",{"viewport":{"width":1180,"height":980}}),
  ("iphone",{"viewport":{"width":390,"height":844},"device_scale_factor":2,"is_mobile":True,"has_touch":True})]:
  context=browser.new_context(**kwargs,permissions=["clipboard-read","clipboard-write"])
  page=context.new_page();errors=[];bad=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  page.on("response",lambda r:bad.append(str(r.status)+" "+r.url) if r.status>=400 else None)
  response=page.goto(url,wait_until="networkidle")
  check(label+" responds",response.status==200)
  page.locator("#reference").wait_for(state="visible")
  check(label+" actual original game screenshot loaded",page.evaluate("document.querySelector('#reference').naturalWidth===780"))
  check(label+" actual counter asset loaded",page.evaluate("document.querySelector('#piece-counter img').naturalWidth>=300"))
  check(label+" frameless wall asset loaded",page.evaluate("document.querySelector('#piece-wall img').naturalWidth>=500"))
  state=page.evaluate("window.__A18_PLACEMENT_TEST__.getState()")
  check(label+" 3 distinct elements",set(state)=={"counter","wall","picture"})
  check(label+" all initially visible",all(x["visible"] for x in state.values()))
  # Drag wall with browser pointer: photo must follow, same photo dimensions.
  piece=page.locator("#piece-wall")
  bb=piece.bounding_box()
  page.mouse.move(bb["x"]+bb["width"]*.08,bb["y"]+bb["height"]*.13)
  page.mouse.down();page.mouse.move(bb["x"]+bb["width"]*.08+20,bb["y"]+bb["height"]*.13+15,steps=8);page.mouse.up()
  moved=page.evaluate("window.__A18_PLACEMENT_TEST__.getState()")
  check(label+" drag moves wall",moved["wall"]["x"]!=state["wall"]["x"] and moved["wall"]["y"]!=state["wall"]["y"])
  check(label+" drag carries photo",moved["picture"]["x"]!=state["picture"]["x"] and moved["picture"]["y"]!=state["picture"]["y"])
  check(label+" photo dimensions unchanged on wall drag",moved["picture"]["w"]==state["picture"]["w"])
  # Resize wall through slider; independent picture size remains.
  page.locator('[data-select="wall"]').click()
  page.locator("#widthRange").fill("190")
  after=page.evaluate("window.__A18_PLACEMENT_TEST__.getState()")
  check(label+" wall width independently resizable",after["wall"]["w"]==190)
  check(label+" photo width stays original",after["picture"]["w"]==state["picture"]["w"])
  # Manual numeric placement exact.
  page.locator('[data-select="picture"]').click()
  page.locator("#w").fill("210");page.locator("#w").press("Tab")
  photo=page.evaluate("window.__A18_PLACEMENT_TEST__.getState()")["picture"]
  check(label+" photo dimensions manually editable",photo["w"]==210)
  # Copy shareable URL to visible text even if clipboard permissions differ.
  page.locator("#shareTop").click()
  share=page.locator("#shareText").input_value()
  check(label+" URL conveys geometry",'layout=' in share and 'picture' in share)
  check(label+" URL selection restore",page.goto(share,wait_until="networkidle").status==200 and
        page.evaluate("window.__A18_PLACEMENT_TEST__.getState()")["picture"]["w"]==210)
  check(label+" localStorage autosaved",page.evaluate("!!localStorage.getItem('a18-placement-editor-v3')"))
  page.screenshot(path=str(OUT/f"placement_editor_{label}.png"),full_page=True,animations="disabled")
  # screenshot is QA evidence only
  check(label+" no page errors",not errors)
  check(label+" no network errors",not bad)
  context.close()
 browser.close()
server.shutdown()
(OUT/"placement_editor_qa.json").write_text(json.dumps({"passed":len(checks),"checks":checks},ensure_ascii=False,indent=2),encoding="utf-8")
print(f"PASS {len(checks)}/{len(checks)}; "+str(OUT/"placement_editor_qa.json"))
