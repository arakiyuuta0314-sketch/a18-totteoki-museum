"""Review mock on top of screenshots captured from running PUBLIC A18 in isolated Chrome.
Actual backgrounds, NPCs, artwork and UI come from the browser; desk/wall are temporary polygons.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json,math
R=Path(__file__).resolve().parent
report=json.loads((R/"live_public_game_capture.json").read_text(encoding="utf-8"))
v=report["game_state"]["viewport"]
assert report["url"]=="https://arakiyuuta0314-sketch.github.io/a18-totteoki-museum/layout-test/index.html"
assert report["page_errors"]==[] and report["http_errors"]==[]
assert v["portrait"] and (v["backingWidth"],v["backingHeight"])==(780,1258)
S=v["backingWidth"]/v["logicalW"]
cx,cy=v["cameraX"],v["cameraY"]
def loc(x,y):
    return (round((x-cx)*S),round((y-cy)*S))
def lt(p):return [loc(x,y) for x,y in p]
def shade(d,poly,fill,outline="#5c3c24",width=4):
    d.polygon(lt(poly),fill=fill)
    d.line(lt(poly+[poly[0]]),fill=outline,width=width,joint="curve")
def txt(d,xy,msg,size=29,color="#203e34"):
    font=ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc",size)
    x,y=xy;bb=d.textbbox((0,0),msg,font=font)
    d.rounded_rectangle((x-9,y-6,x+bb[2]+12,y+bb[3]+14),fill=color,radius=9)
    d.text(xy,msg,font=font,fill="#fff5e3")
def desk(d,xshift):
    # Reuse last approved compact mock but move horizontally in logical game units.
    # Original baseline polys from make_refined_vertical.py converted to game world:
    # source (1322 x 1190), world (546 x 483), centered crop.
    k=1322/546
    ypad=(1190-483*k)/2
    def src(pt):
        x,y=pt
        return (x/k+xshift,(y-ypad)/k)
    def draw(points,fill):shade(d,[src(z) for z in points],fill)
    draw([(414,657),(506,644),(522,884),(428,896)],"#ebc27e")
    draw([(506,644),(522,884),(522,921),(506,682)],"#9d6339")
    draw([(428,896),(522,884),(522,921),(428,944)],"#774b30")
    draw([(414,657),(428,896),(428,944),(414,702)],"#6d452f")
    # small wood inlay on service-facing vertical plane
    p0=loc(*src((510,730)));p1=loc(*src((517,866)))
    d.line((*p0,*p1),fill="#f1cf8f",width=4)
def right_display(d):
    # Deliberately compact front-facing partition inside current phone viewport.
    # NOT the existing 3rd fixture mask, which still requires implemention.
    shade(d,[(365,260),(460,260),(468,270),(374,270)],"#cda168")
    shade(d,[(374,270),(468,270),(468,363),(374,363)],"#805235")
    shade(d,[(386,283),(457,283),(457,354),(386,354)],"#b59362",width=5)
    shade(d,[(392,290),(451,290),(451,348),(392,348)],"#254d40",width=3)
    shade(d,[(399,296),(443,296),(443,342),(399,342)],"#daccb2",width=3)
def render(key,shift,npc):
    base=Image.open(R/("live_public_full_butler_"+key+"_390.png")).convert("RGB")
    world=Image.open(R/("live_public_game_butler_"+key+"_390.png")).convert("RGB")
    original=Image.open(R/"live_public_game_original_390.png").convert("RGB")
    assert base.size==original.size and world.size==(780,1258)
    # Full screenshot world begins at CSS y 51 and DPR2 => 102 source px.
    dy=round(report["world_box"]["y"]*report["viewport_css"]["dpr"])
    assert dy==102 and base.crop((0,dy,780,dy+1258)).size==world.size
    layer=Image.new("RGBA",world.size,(0,0,0,0))
    dr=ImageDraw.Draw(layer)
    # Furniture is the only illustrative layer in these screenshots.
    right_display(dr)
    desk(dr,shift)
    # Short unobtrusive note within the space below the world floor.
    txt(dr,(345,1160),f"仮配置｜カウンター左へ {abs(shift)}",size=21)
    merged=Image.alpha_composite(world.convert("RGBA"),layer).convert("RGB")
    # Compose back into real mobile screenshot, retaining its genuine D-pad and HUD.
    final=base.copy();final.paste(merged,(0,dy))
    dst=R/("live_public_entrance_counter_"+key+"_390.jpg")
    final.save(dst,quality=88,optimize=True)
    small=R/("live_public_world_counter_"+key+"_390.jpg")
    merged.save(small,quality=90,optimize=True)
    assert Image.open(dst).size==base.size
    return {"name":key,"desk_shift_game":shift,"butler_x_game":npc,
            "display_full":dst.name,"display_world":small.name}

variants=[render("left_30",-30,111),render("left_48",-48,93)]
(R/"LIVE_PUBLIC_SCREEN_MOCK_20261027.json").write_text(
 json.dumps({"source":"Captured public GitHub Pages via isolated Chrome, not reconstructed background",
 "viewport":report["viewport_css"],"game_world":v,"tested_sample_photo":True,
 "desk_and_right_frame_are_overlays_not_live_game_assets":True,
 "butler_x_temporarily_changed_in_disposable_browser":True,"variants":variants},
 ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS live Chrome pixel screenshot overlays",json.dumps(variants,ensure_ascii=False))
