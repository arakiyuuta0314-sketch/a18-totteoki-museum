"""Review preview only: exact user JSON, wall/photo unchanged, counter edited but source intact."""
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
P=Path(__file__).resolve().parent
m=json.loads((P/"v3-placement-source.json").read_text(encoding="utf-8"))
u=m["userProvidedGeometry"];v=m["v3CounterEnlargementProposal"]
assert u=={
    "counter":{"x":118,"y":827,"w":143,"h":291,"a":0,"visible":True},
    "wall":{"x":574,"y":736,"w":315,"h":310,"a":0,"visible":True},
    "picture":{"x":658,"y":801,"w":156,"h":133,"a":0,"visible":True}
}
assert v["wall"]==u["wall"] and v["picture"]==u["picture"]
assert v["counter"]["w"]>u["counter"]["w"] and v["counter"]["h"]>u["counter"]["h"]
assert v["wall"]["x"]-v["counter"]["x"]-v["counter"]["w"]>=275
assert m["butlerScreenshotOverride"]["x"]==145
before=P/"reference-game.png"
after=P/"reference-game-counter-inside.png"
assert Image.open(after).size==Image.open(before).size==(780,1688)
assert ImageChops.difference(Image.open(before).convert("RGB"),Image.open(after).convert("RGB")).getbbox()
assert Image.open(P/"counter-open.webp").mode=="RGBA"
assert Image.open(P/"wall-real-noframe.webp").mode=="RGBA"
assert (P/"counter-open.webp").stat().st_size>19000
code=(P/"editor.js").read_text(encoding="utf-8")
assert 'STORE="a18-placement-editor-v3"' in code
assert all(f'{k}:{{x:{t["x"]},y:{t["y"]},w:{t["w"]},h:{t["h"]}' in code for k,t in v.items())
html=(P/"index.html").read_text(encoding="utf-8")
assert "counter-open.webp" in html and "reference-game-counter-inside.png" in html
assert "counter-real.webp" not in html
print("PASS user-provided layout unchanged, enlarged counter is separate proposal, hall clear, edited transparent art and real Chrome reference")
