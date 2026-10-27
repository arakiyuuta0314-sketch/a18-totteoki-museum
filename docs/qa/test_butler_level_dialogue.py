"""Isolated Chrome QA for level-specific butler greetings and non-repeating menu salutation."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = Path(__file__).with_name("butler_level_dialogue_qa.json")
checks = []

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def check(label, condition, value=None):
    checks.append({"name": label, "pass": bool(condition), "actual": value})
    if not condition:
        raise AssertionError(f"{label}: {value}")

JS_DIALOG = """({level, random, gender='male', role='butler'}) => {
  const root=document.querySelector('#dialog');
  Math.random=()=>random;
  window.A18Registration.staffDialog({
    open:(_title, html)=>{root.innerHTML=html},
    close:()=>{root.innerHTML=''},
    list:()=>{},form:()=>{},carrying:null,role,
    playerName:'ゆた',gender,works:[],museumLevel:level
  });
  return root.querySelector('.rpg-message')?.textContent||'';
}"""

def main():
    handler = partial(Quiet, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(channel="chrome", headless=True)
            context=browser.new_context(viewport={"width":390,"height":844}, device_scale_factor=1)
            page=context.new_page()
            errors=[]
            page.on("pageerror", lambda err:errors.append(str(err)))
            page.goto(f"http://127.0.0.1:{server.server_port}/layout-test/index.html",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_function("!!window.A18Registration",timeout=30000)
            # Each Lv.1 entry should be independently reachable.
            lv1=set()
            for k in range(8):
                greeting=page.evaluate(JS_DIALOG, {"level":1,"random":k/8})
                lv1.add(greeting)
                check(f"level 1 greeting {k+1} addresses player",greeting.startswith("ゆた様、"),greeting)
                page.evaluate("document.getElementById('rpgAdvance').click()")
                menu=page.locator("#dialog .rpg-message").text_content()
                check(f"level 1 menu {k+1} does not repeat name",
                      "ゆた様" not in menu and "お呼びでございますか" in menu, menu)
                check(f"level 1 menu actions {k+1}",
                      page.locator("#staffRegister, #all, #staffChat, #close").count()==4)
            check("eight distinct level 1 greetings",len(lv1)==8, sorted(lv1))
            starts={
                2:"ゆた様、新しい展示室の扉が開きましたな。",
                3:"ゆた様、また一つ展示室が増えましたな。",
                4:"ゆた様、展示室を巡るたび",
                5:"ゆた様、館内もずいぶんと広く",
                6:"ゆた様、この館も大きく育ちましたな。"
            }
            for level,begin in starts.items():
                greeting=page.evaluate(JS_DIALOG, {"level":level,"random":0})
                check(f"level {level} uses its own line",greeting.startswith(begin),greeting)
                page.evaluate("document.getElementById('rpgAdvance').click()")
                menu=page.locator("#dialog .rpg-message").text_content()
                check(f"level {level} menu has no name","ゆた様" not in menu, menu)
                page.evaluate("document.getElementById('staffChat').click()")
                check(f"level {level} chat is available",page.locator("#staffChatAgain").count()==1)
                page.evaluate("document.getElementById('returnMenu').click()")
                check(f"level {level} return menu has no name",
                      "ゆた様" not in page.locator("#dialog .rpg-message").text_content())
            female=page.evaluate(JS_DIALOG,{"level":1,"random":0,"gender":"female"})
            check("female honorific is preserved",female.startswith("ゆたお嬢様、"),female)
            page.evaluate("document.getElementById('rpgAdvance').click()")
            check("female menu has no repeated honorific",
                  "ゆたお嬢様" not in page.locator("#dialog .rpg-message").text_content())
            staff=page.evaluate(JS_DIALOG,{"level":1,"random":0,"gender":"female","role":"staff"})
            check("staff greeting remains unchanged",staff.startswith("ゆたさん、"),staff)
            invalid=page.evaluate("""() => {
                try {
                  window.A18Registration.staffDialog({
                    open:()=>{},close:()=>{},list:()=>{},form:()=>{},
                    carrying:null,role:'butler',playerName:'ゆた',
                    gender:'male',works:[],museumLevel:7
                  });
                  return null;
                } catch(e) {return e.message;}
            }""")
            check("unsupported level fails explicitly",invalid=="E_BUTLER_GREETING_LEVEL: 7",invalid)
            check("no browser errors",not errors,errors)
            context.close()
            browser.close()
    finally:
        server.shutdown()
    REPORT.write_text(json.dumps({"checks":checks, "passed":len(checks)},
                                 ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"PASS {len(checks)}/{len(checks)} browser checks; {REPORT}")

if __name__=="__main__":
    main()
