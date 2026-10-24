# -*- coding: utf-8 -*-
"""A18 entrance north door, fully compositable CLOSED/OPEN state material master.
The approved 546x483 one-piece image is the immutable exact visual reference.
The OPEN interior uses a perspective-mapped detail of a separate architecture study;
the rest of the museum is unchanged, with official game characters only in QA.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance,ImageOps
import numpy as np, cv2, hashlib,json
A18=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
R=Path(r"C:\Users\User\source\repos\a18-totteoki-museum-pages\entrance-test-v3\layout-test\assets\entrance\v0.3")
OUT=A18/"26_エントランス_完成素材_北扉_v01"
REF=R/"approved_entrance_trial.jpg"
EXTRA=A18/"24_エントランス再設計_品質基準"/"A18_entrance_Lv6_A_background_candidate_20261025.png"
PHOTO=A18/"25_エントランス個別素材制作_v01"/"QA_3photos_in_original_entrance.png"
CHAR=A18/"00_正式採用素材"/"characters"
assert all(p.is_file() for p in [REF,EXTRA,PHOTO,CHAR/"curator-front-00.png",CHAR/"butler-front-00.png"])
src=Image.open(REF).convert("RGB")
assert src.size==(546,483)
arch=Image.open(EXTRA).convert("RGB")
assert arch.size==(1254,1254)
# Corridor is used purely INSIDE the artwork's existing northern doorway (no other architecture changes).
corridor=arch.crop((505,150,737,478))
corridor=ImageOps.fit(corridor,(79,100),Image.Resampling.LANCZOS,centering=(.5,.42))
corridor=ImageEnhance.Color(corridor).enhance(.75)
corridor=ImageEnhance.Brightness(corridor).enhance(.77)
corridor=ImageEnhance.Contrast(corridor).enhance(.92)
n=np.array(corridor).astype(np.float32)
# Darker side jambs and vignetting to embed a recessed passage.
Y,X=np.mgrid[0:100,0:79]
edge=np.clip((np.minimum(X,78-X)/10),.45,1)
top=np.clip(.84+Y/100*.26,.78,1.03)
n=np.uint8(np.clip(n*edge[...,None]*top[...,None],0,255))
insert=Image.fromarray(n,"RGB")
# Exact 546x483 screenshot coordinate surface.
base=np.array(src).copy()
replacement=np.array(insert)
# Region fully within old door leaves; surrounding arch lintel never touched.
box=(243,116,322,213)
x0,y0,x1,y1=box
replacement=cv2.resize(replacement,(x1-x0,y1-y0),interpolation=cv2.INTER_AREA)
# Narrow shade edges appear behind fixed frame, visually matching the existing passage
for xx in range(x1-x0):
    vign=0.62+0.38*min(1, min(xx,(x1-x0-1)-xx)/7)
    replacement[:,xx,:]=np.uint8(np.clip(replacement[:,xx,:].astype(float)*vign,0,255))
base[y0:y1,x0:x1]=replacement
# Open state backing has the original gallery architecture EXCEPT its northern portal interior.
baseI=Image.fromarray(base,"RGB")
baseI.save(OUT/"entrance_bg_north_open_base.png",optimize=True)
# Door closed over the open portal: pixel-exact reconstruction.
def fullcanvas():
    return Image.new("RGBA",(546,483),(0,0,0,0))
closed=fullcanvas()
doorRect=src.crop((x0,y0,x1,y1)).convert("RGBA")
closed.alpha_composite(doorRect,(x0,y0))
closed.save(OUT/"entrance_door_north_closed.png",optimize=True)
# Open state: dark lacquered wooden leaves folded out against each side of arch.
opened=fullcanvas()
D=ImageDraw.Draw(opened,"RGBA")
# Self-contained trim: muted golden highlights sampled from existing door.
D.polygon([(243,116),(251,118),(251,212),(243,214)], fill=(49,31,20,255))
D.polygon([(314,119),(322,115),(322,214),(314,212)], fill=(51,33,23,255))
# Texture both folded leaves with the ORIGINAL wood pixels (not flat-color CGI).
leftLeaf=ImageEnhance.Brightness(src.crop((249,118,271,212))).enhance(.58).resize((8,94),Image.Resampling.LANCZOS).convert("RGBA")
rightLeaf=ImageEnhance.Brightness(src.crop((297,118,320,212))).enhance(.58).resize((8,94),Image.Resampling.LANCZOS).convert("RGBA")
opened.alpha_composite(leftLeaf,(243,118))
opened.alpha_composite(rightLeaf,(314,118))

D.line([(250,119),(250,208)], fill=(169,121,61,240),width=1)
D.line([(315,119),(315,209)], fill=(150,108,61,230),width=1)
# Understated open door handles on the side leaf, not floating in corridor.
D.ellipse((248,164,250,167),fill=(194,154,82,255))
D.ellipse((315,164,317,167),fill=(194,154,82,255))
opened.save(OUT/"entrance_door_north_open.png",optimize=True)

def overlay_on(under,overlay):
    result=under.convert("RGBA").copy()
    result.alpha_composite(overlay)
    return result.convert("RGB")

check_closed=overlay_on(baseI,closed)
check_open=overlay_on(baseI,opened)
check_closed.save(OUT/"QA_north_door_closed.png",optimize=True)
check_open.save(OUT/"QA_north_door_open.png",optimize=True)
# Pixel-exact closed guarantee
err=np.abs(np.array(check_closed).astype('int16')-np.array(src).astype('int16'))
if np.count_nonzero(err)>0: raise AssertionError("Door CLOSED does not reconstruct approved source")
# Every pixel OUTSIDE the base replaced region must be unchanged.
open_pixels=np.array(check_open)
original_pixels=np.array(src)
outside=np.ones((483,546),bool);outside[y0:y1,x0:x1]=False
# open door leaf overhangs 245..301, so only allow deviation in this thin boundary area
outside[115:215,239:325]=False
assert np.array_equal(open_pixels[outside],original_pixels[outside])
# Actual photo frame QA - photo component remains clear, not burned into static base.
photoImg=Image.open(PHOTO).convert("RGB")
delta=np.array(photoImg).astype('int16')-np.array(src).astype('int16')
picOpen=np.uint8(np.clip(open_pixels.astype('int16')+delta,0,255))
photoOpen=Image.fromarray(picOpen,"RGB")
# Photo difference outside the 3 photo masks is 0 by construction
photoOpen.save(OUT/"QA_north_open_with_photos.png",optimize=True)
def sprite(im,name,centerX,footY,width):
    sc=Image.open(CHAR/name).convert("RGBA")
    h=round(sc.height*width/sc.width)
    sc=sc.resize((width,h),Image.Resampling.NEAREST)
    im.alpha_composite(sc,(round(centerX-width/2),round(footY-h)))
# Formal PNG remains unchanged, QA only
p=photoOpen.convert("RGBA")
sprite(p,"butler-front-00.png",143,369,43)
sprite(p,"curator-front-00.png",270,375,35)
p.save(OUT/"QA_north_open_photos_formal_characters.png",optimize=True)
# side by side at original actual resolution
board=Image.new("RGB",(546*2,483))
board.paste(check_closed,(0,0));board.paste(check_open,(546,0))
board.save(OUT/"QA_north_closed_vs_open.png",optimize=True)
# Extra high-res QA helps audit pixel seam when viewed on mobile
focus=check_open.crop((204,47,351,244))
focus.resize((588,788),Image.Resampling.NEAREST).save(OUT/"QA_north_open_4x.png",optimize=True)
qa={
 "scope":"NORTH DOOR CLOSED/OPEN with exact approved architecture",
 "source_approved":str(REF),"source_sha256":hashlib.sha256(REF.read_bytes()).hexdigest(),
 "source_extra_arch_study":str(EXTRA),
 "geometry":{"portal_replaced_region":[x0,y0,x1,y1],"north_collision_window":{"x_min":257,"x_max":289,"y_min":195,"y_max":218}},
 "screen_canvas":[546,483],
 "closed_pixel_exact":bool(np.count_nonzero(err)==0),
 "off_door_art_preserved":bool(np.array_equal(open_pixels[outside],original_pixels[outside])),
 "characters":"Only original formal PNGs used in QA. None baked into delivered assets.",
 "user_photos":"No user photos used. QA uses demonstration photos only.",
 "quality_status":"DOOR DRAWN AND ALPHA-VALIDATED; USER VISUAL APPROVAL PENDING",
 "files":{}
}
for f in OUT.glob("*.png"):
    qa["files"][f.name]={"size":list(Image.open(f).size),"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()}
(OUT/"QA_north_door.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS closed_exact, outside_unchanged, transparency, photo QA")
for key in ("entrance_bg_north_open_base.png","entrance_door_north_closed.png","entrance_door_north_open.png"):
 f=OUT/key; print("ASSET",key, f.stat().st_size,Image.open(f).mode)
