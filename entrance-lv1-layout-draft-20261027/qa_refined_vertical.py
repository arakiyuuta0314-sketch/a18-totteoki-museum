"""Static mock QA. Fail-fast on source drift, non-comparable variants or dimensions."""
from pathlib import Path
from PIL import Image,ImageChops,ImageOps,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parent
repo=R.parent
base=repo/"layout-test/assets/entrance/approved_initial_20261027/entrance_background_initial_approved.png"
guide=json.loads((R/"VERTICAL_LAYOUT_GEOMETRY_20261027.json").read_text(encoding="utf-8"))
original=Image.open(base).convert("RGB")
assert original.size==(1322,1190)
sha=hashlib.sha256(base.read_bytes()).hexdigest()
assert sha==guide["background_sha256"]=="cc4bca9821242facbee3984d1df7034514845195205c2b30cc94ef4628a469cf"
assert guide["actual_npc_game_position"]=={"butler_x":139,"butler_footY":366}
assert guide["entrance_wallFootY_game"]==210
items={x["name"]:x for x in guide["variants"]}
assert set(items)=={"compact","extended"}
assert items["compact"]["free_at_wall_logical"]>=50
assert items["extended"]["free_at_wall_logical"]<25
assert items["compact"]["length_logical"]<items["extended"]["length_logical"]
images=[]
for k in ["compact","extended"]:
    x=items[k]
    im=Image.open(R/x["image"]).convert("RGB")
    assert im.size==(1322,1352)
    assert (R/x["jpeg"]).exists()
    images.append(im)
# The right fixture artwork is identical; comparison labels elsewhere may differ.
assert ImageChops.difference(images[0].crop((940,770,1250,995)),
                             images[1].crop((940,770,1250,995))).getbbox() is None
# Check background-only witness pixels survive exactly on both variations.
for im in images:
    for x,y in [(580,392),(703,463),(806,1090),(1054,1030)]:
        assert im.getpixel((x,y+100))==original.getpixel((x,y)),(x,y)
assert ImageChops.difference(*images).getbbox() is not None
canvas=Image.new("RGB",(1518,846),"#f6f0e7")
for i,im in enumerate(images):
    fit=ImageOps.contain(im,(735,752),Image.Resampling.LANCZOS)
    canvas.paste(fit,(14+i*755,58))
draw=ImageDraw.Draw(canvas)
draw.rectangle((0,0,1518,50),fill="#193c32")
font=ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc",29)
draw.text((24,6),"Lv.1｜縦カウンターの長さ比較（左：短め／右：長め）",font=font,fill="#fff6e7")
draw.text((36,806),"正式背景・キャラ実寸ベース。左奥の動線を優先するなら短め。",font=ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc",22),fill="#5c4a36")
out=R/"lv1_refined_vertical_length_comparison.jpg"
canvas.save(out,quality=89,optimize=True)
assert Image.open(out).size==(1518,846)
print("PASS | SHA & untouched base | real NPC position | relative fixture spans | common right wall | two PNG/JPG | comparison")
print("COMPARISON",out)
