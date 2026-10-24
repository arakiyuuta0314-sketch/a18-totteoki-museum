# -*- coding: utf-8 -*-
"""A18 still image only. Actual approved character PNGs, no generated characters.
Background image remains a visual candidate. Never edits the game or its save.
"""
from pathlib import Path
from PIL import Image,ImageEnhance,ImageFilter,ImageDraw
import numpy as np, cv2,hashlib,json

ASSETS=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
SRC=ASSETS/"24_エントランス再設計_品質基準"
CHAR=ASSETS/"00_正式採用素材"/"characters"
OUT=Path(__file__).parent
BG=SRC/"A18_entrance_Lv6_A_background_candidate_20261025.png"
must=[BG,CHAR/"curator-back-00.png",CHAR/"female-back-00.png",CHAR/"butler-front-00.png",
      SRC/"memory_dog_demo.jpg",SRC/"memory_holiday_demo.jpg",SRC/"memory_cat_demo.jpg"]
for p in must:
    if not p.exists():raise FileNotFoundError(str(p))
bg=Image.open(BG).convert("RGB")
if bg.size!=(1254,1254):raise AssertionError("Background dimensions changed")
# Gently remove the glare and excessive gold saturation while retaining artwork details.
bg=ImageEnhance.Color(bg).enhance(0.72)
bg=ImageEnhance.Contrast(bg).enhance(0.89)
bg=ImageEnhance.Brightness(bg).enhance(0.96)
B=np.array(bg,dtype=np.float32)
H,W=B.shape[:2]
# Soften showpiece chandelier and over-bright floor without changing geometry.
YY,XX=np.mgrid[0:H,0:W]
heat=np.exp(-(((XX-630)/215)**2+((YY-16)/145)**2)/2)
B[:]=B*(1-heat[...,None]*0.11)
B=np.uint8(np.clip(B,0,255))
bg=Image.fromarray(B).convert("RGBA")

def apply_photo(base,path,quad):
    """Perspective-fit only inside existing empty mat. Art is a temporary demo."""
    img=Image.open(path).convert("RGB")
    targetw=180;targeth=188
    from PIL import ImageOps
    img=ImageOps.fit(img,(targetw,targeth),method=Image.Resampling.LANCZOS)
    pts=np.array(quad,dtype=np.float32)
    src=np.array([[0,0],[targetw-1,0],[targetw-1,targeth-1],[0,targeth-1]],dtype=np.float32)
    M=cv2.getPerspectiveTransform(src,pts)
    dst=cv2.warpPerspective(np.array(img),M,(W,H),flags=cv2.INTER_CUBIC)
    mask=np.zeros((H,W),dtype=np.uint8)
    cv2.fillConvexPoly(mask,pts.astype(np.int32),255)
    # 1px feather for natural edge against fixed frame
    mask=cv2.GaussianBlur(mask,(3,3),0.4)
    arr=np.array(base.convert("RGB"))
    k=mask.astype(np.float32)[...,None]/255.
    out=np.uint8(np.clip(arr*(1-k)+dst*k,0,255))
    return Image.fromarray(out).convert("RGBA")

# Three interior mats, no accidental covering of ornate gold molding.
FRAMES=[
  {"name":"dog","photo":SRC/"memory_dog_demo.jpg","quad":[[323,197],[430,196],[431,324],[322,326]]},
  {"name":"holiday","photo":SRC/"memory_holiday_demo.jpg","quad":[[827,195],[930,196],[930,326],[826,326]]},
  {"name":"cat","photo":SRC/"memory_cat_demo.jpg","quad":[[1050,546],[1198,575],[1200,748],[1050,716]]}
]

def add_sprite(base,name,x,foot,w):
    src=Image.open(CHAR/name).convert("RGBA")
    h=round(src.height*w/src.width)
    sprite=src.resize((w,h),resample=Image.Resampling.NEAREST)
    # Grounded shadow drawn on separate transparent overlay, keeping sprite original.
    layer=Image.new("RGBA",base.size,(0,0,0,0))
    draw=ImageDraw.Draw(layer)
    shadow=(x-w//2-13,foot-7,x+w//2+13,foot+11)
    draw.ellipse(shadow,fill=(24,19,15,50))
    layer=layer.filter(ImageFilter.GaussianBlur(3))
    base.alpha_composite(layer)
    base.alpha_composite(sprite,(round(x-w/2),round(foot-h)))

crop=(0,72,1254,1182)
resolution=(1092,967)
bg_only=bg.crop(crop).resize(resolution,Image.Resampling.LANCZOS).convert("RGB")
bg_only.save(OUT/"A18_entrance_A_Lv6_background_no_people.png",optimize=True)
for item in FRAMES:
    bg=apply_photo(bg,item["photo"],item["quad"])
# Transparent false characters are never generated. Use exact source PNG sprites.
for key,avname in [("male","curator-back-00.png"),("female","female-back-00.png")]:
    composite=bg.copy()
    add_sprite(composite,"butler-front-00.png",372,814,98)
    add_sprite(composite,avname,635,1018,82)
    img=composite.crop(crop).resize(resolution,Image.Resampling.LANCZOS).convert("RGB")
    path=OUT/f"A18_entrance_A_Lv6_photo_first_OFFICIAL_{key}.png"
    img.save(path,optimize=True)
    print("FINISHED",str(path),img.size,path.stat().st_size)
out={}
out["source_sha256"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in must}
out["character_sprite_handling"]="Loaded original approved PNG, nearest-neighbor resize only. No AI redraw."
out["frame_demo"]="3 sample photos cropped from generated reference; NOT user content."
out["background_is_candidate"]=True
out["art_approval"]="Not yet approved; static one-sheet mock only; layered game integration not done"
out["cropping_in_source_px"]=crop
out["output_resolution"]=resolution
out["composite_count"]=2
(OUT/"A18_entrance_A_Lv6_still_QA.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
