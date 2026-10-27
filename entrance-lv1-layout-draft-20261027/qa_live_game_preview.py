"""QA: artifacts are actual browser captures with furniture-only mock overlay."""
from pathlib import Path
from PIL import Image,ImageChops
import json
P=Path(__file__).resolve().parent
capture=json.loads((P/"live_public_game_capture.json").read_text(encoding="utf-8"))
mock=json.loads((P/"LIVE_PUBLIC_SCREEN_MOCK_20261027.json").read_text(encoding="utf-8"))
assert capture["page_errors"]==capture["http_errors"]==[]
assert capture["viewport_css"]=={"width":390,"height":844,"dpr":2}
assert capture["game_state"]["scene"]=="entrance"
assert capture["visible_work_count"]==1
assert len(mock["variants"])==2
world=Image.open(P/"live_public_game_world_390.png").convert("RGB")
full=Image.open(P/"live_public_game_original_390.png").convert("RGB")
assert world.size==(780,1258) and full.size==(780,1688)
for x in mock["variants"]:
 name=x["name"]
 w=Image.open(P/("live_public_game_butler_"+name+"_390.png")).convert("RGB")
 preview=Image.open(P/x["display_full"]).convert("RGB")
 assert w.size==world.size and preview.size==full.size
 assert ImageChops.difference(w,world).getbbox() is not None
 # HUD and D-pad remain actual screenshot pixels (JPEG tolerance).
 for spot in [(90,35),(320,1514),(340,1632)]:
  a=Image.open(P/("live_public_full_butler_"+name+"_390.png")).convert("RGB").getpixel(spot)
  b=preview.getpixel(spot)
  assert max(abs(a[j]-b[j]) for j in range(3))<30,(name,spot,a,b)
assert mock["variants"][1]["butler_x_game"]==93
assert mock["variants"][1]["desk_shift_game"]==-48
print("PASS | actual public Chrome game captures, world/camera, Butler moved, UI untouched, 2 furniture overlays")
