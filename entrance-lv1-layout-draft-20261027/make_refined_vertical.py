"""Geometry-conscious Lv1 desk mock. Review only: NO game code or official asset edits."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, math, json
D=Path(__file__).resolve().parent
R=D.parent
BG=R/"layout-test/assets/entrance/approved_initial_20261027/entrance_background_initial_approved.png"
BUTLER=R/"scenes-preview/assets/official/characters/butler-front-00.png"
PLAYER=R/"scenes-preview/assets/official/characters/curator-front-00.png"
FONT="C:/Windows/Fonts/meiryo.ttc"
IMAGE_W,IMAGE_H=1322,1190
# Legacy official canvas coordinate mapping, not hand-guessed background scaling.
LOGICAL_W,LOGICAL_H=546,483
S=IMAGE_W/LOGICAL_W
CROP=(IMAGE_H-LOGICAL_H*S)/2
assert BG.is_file() and BUTLER.is_file() and PLAYER.is_file()
assert hashlib.sha256(BG.read_bytes()).hexdigest()=="cc4bca9821242facbee3984d1df7034514845195205c2b30cc94ef4628a469cf"
background=Image.open(BG).convert("RGBA")
assert background.size==(IMAGE_W,IMAGE_H)
def ff(n): return ImageFont.truetype(FONT,n)
def world(x,y):return round(x*S),round(CROP+y*S)
def rect(d,coords,fill,outline=None,width=4):
    d.rectangle(coords,fill=fill,outline=outline,width=width)
def tag(d,x,y,label,color=(26,55,50,232),size=27):
    font=ff(size);bb=d.textbbox((0,0),label,font=font)
    d.rounded_rectangle((x-10,y-5,x+bb[2]+13,y+bb[3]+16),radius=9,fill=color)
    d.text((x,y),label,font=font,fill="#fff7e8")
def arrow(d,a,b,color="#419c7a"):
    d.line((*a,*b),fill=color,width=7)
    angle=math.atan2(b[1]-a[1],b[0]-a[0])
    for q in [-.58,.58]:
        d.line((b[0]-24*math.cos(angle+q),b[1]-24*math.sin(angle+q),*b),fill=color,width=7)
def sprite(layer,path,logicalX,logicalFootY,logicalSize=(43,55)):
    img=Image.open(path).convert("RGBA")
    # Official NPC draw: footBaselinePx=72 of sourceSize height 77.
    w,h=[round(z*S) for z in logicalSize]
    x,y=world(logicalX,logicalFootY)
    left=x-w//2
    top=round(y-h*72/77)
    img=img.resize((w,h),Image.Resampling.NEAREST)
    layer.alpha_composite(img,(left,top))
def frame_mock(draw):
    # Third artwork fixture as frontal wall, not a replacement for real 3rd mask.
    draw.polygon([(915,618),(1226,618),(1246,638),(933,638)],
                 fill=(222,177,107,231),outline="#573c25",width=7)
    draw.polygon([(933,638),(1246,638),(1246,912),(933,912)],
                 fill=(106,67,44,232),outline="#46301f",width=9)
    draw.rectangle((967,660,1210,874),fill=(31,97,82,229),
                   outline=(207,166,95,255),width=10)
    draw.rectangle((989,684,1188,850),fill=(232,217,188,229),
                   outline=(167,123,63,255),width=6)
def desk(draw,top,bottom):
    # x-range 420..526 source pixels, y-range top..bottom.
    # Customer approaches from right, Butler remains to its left.
    draw.polygon([(414,top),(506,top-13),(522,bottom-12),(428,bottom)],
                 fill=(240,196,117,242),outline="#553720",width=7)
    draw.polygon([(506,top-13),(522,bottom-12),(522,bottom+37),(506,top+38)],
                 fill=(124,78,42,236),outline="#4e311f",width=7)
    draw.polygon([(428,bottom),(522,bottom-12),(522,bottom+37),(428,bottom+48)],
                 fill=(104,65,39,240),outline="#4e311f",width=7)
    draw.polygon([(414,top),(428,bottom),(428,bottom+48),(414,top+46)],
                 fill=(111,75,46,219),outline="#4e311f",width=6)
    # Continuous inset panel on customer-facing side
    draw.line((510,top+78,520,bottom-45),fill=(225,173,98,238),width=5)
def make(kind,top,bottom):
    compact=kind=="compact"
    title="採用方向｜縦カウンター・短め" if compact else "比較｜縦カウンター・長め"
    result=Image.new("RGBA",(1322,1352),"#f7f0e7")
    result.paste(background,(0,100))
    lay=Image.new("RGBA",result.size,(0,0,0,0));d=ImageDraw.Draw(lay)
    for x0,x1 in [(105,453),(905,1224)]:
        # Record the existing unchanged rear frame zones.
        d.rounded_rectangle((x0,264,x1,455),radius=3,
                            outline=(244,208,131,210),width=5)
    # Overlay rectangles at offset +100
    offset=100
    def original_points(pts): return [(x,y+offset) for x,y in pts]
    # Overlay desk/furniture drawn into separate local RGBA at original source coords.
    furniture=Image.new("RGBA",(1322,1190),(0,0,0,0))
    fd=ImageDraw.Draw(furniture)
    frame_mock(fd);desk(fd,top,bottom)
    lay.alpha_composite(furniture,(0,offset))
    # Spawn genuine art sprites at *existing game coordinates*; not moving them.
    sprites=Image.new("RGBA",(1322,1190),(0,0,0,0))
    sprite(sprites,BUTLER,139,366)
    sprite(sprites,PLAYER,326,425)
    lay.alpha_composite(sprites,(0,offset))
    d=ImageDraw.Draw(lay)
    # Current butler feet are at x=139 y=366, on left of the proposed desk.
    bx,by=world(139,366)
    d.ellipse((bx-9,by+offset-9,bx+9,by+offset+9),fill="#5fe6ba",outline="#134b39",width=3)
    tag(d,45,932 if compact else 991,"爺や：現行座標のまま",size=23)
    # Source row where physical wall ends y=210 -> 518 original.
    wall_y=world(0,210)[1]+offset
    d.line((18,wall_y,1297,wall_y),fill=(249,213,145,150),width=3)
    # Gap arrow precisely measured from solid wall to proposed counter back end.
    gap=round((top-world(0,210)[1])/S,1)
    gx=562
    d.line((gx,wall_y,gx,top+offset),fill="#419c7a",width=4)
    for yy in [wall_y,top+offset]: d.line((gx-9,yy,gx+9,yy),fill="#419c7a",width=4)
    tag(d,582,wall_y+16,f"背面側の空き {gap:g}（ゲーム座標）",size=22)
    # On-site route arrows are only proposals, not existing unlocked doors.
    arrow(d,(641,704+offset),(641,565+offset))
    arrow(d,(636,565+offset),(30,565+offset))
    arrow(d,(646,565+offset),(1297,565+offset))
    tag(d,30,480+offset,"左上通路（今後開口）",size=25)
    tag(d,959,480+offset,"右上通路（今後開口）",size=25)
    tag(d,485,1110+offset,"中央の歩行スペース",size=25)
    tag(d,1001,938+offset,"額縁③：正面",size=25,color=(105,64,31,234))
    tag(d,520,783+offset,"← 受付面",size=25,color=(105,64,31,234))
    composed=Image.alpha_composite(result,lay)
    head=ImageDraw.Draw(composed)
    head.rectangle((0,0,1322,100),fill="#163a32")
    head.text((34,14),title,font=ff(46),fill="#fff6e8")
    head.text((36,68),"正式背景・正式キャラクター使用 ／ 家具形状のみ仮",font=ff(22),fill="#ecdbc0")
    head.rectangle((0,1291,1322,1352),fill="#faf1e1")
    head.text((32,1304),"左右の開口・接触判定・NPC会話範囲は未実装。表示は実装前比較図。",font=ff(22),fill="#624d33")
    fp=D/("lv1_vertical_"+kind+"_refined.png")
    composed.convert("RGB").save(fp,optimize=True)
    preview=composed.convert("RGB");preview.thumbnail((1020,1050))
    jpg=D/("lv1_vertical_"+kind+"_refined.jpg")
    preview.save(jpg,quality=83,optimize=True)
    return {"name":kind,"top":top,"bottom":bottom,"free_at_wall_logical":gap,
            "reception_width_logical":round((522-414)/S,1),
            "length_logical":round((bottom-top)/S,1),
            "image":fp.name,"jpeg":jpg.name}
variants=[make("compact",657,896),make("extended",569,910)]
(D/"VERTICAL_LAYOUT_GEOMETRY_20261027.json").write_text(json.dumps({
    "background_sha256":hashlib.sha256(BG.read_bytes()).hexdigest(),
    "actual_npc_game_position":{"butler_x":139,"butler_footY":366},
    "actual_player_game_position":{"x":326,"y":425},
    "entrance_wallFootY_game":210,
    "counter_third_wall":"illustrative only",
    "variants":variants},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(variants,ensure_ascii=False))
