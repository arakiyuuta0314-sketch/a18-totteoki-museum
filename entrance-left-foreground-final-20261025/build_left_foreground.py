# -*- coding: utf-8 -*-
"""Approved-source split of left entrance solid wall + walnut rail (art assets / no game mutation)."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import cv2,numpy as np,json,hashlib
ROOT=Path(r"C:\Users\User\source\repos\a18-entrance-left-foreground-20261025")
OUT=ROOT/"entrance-left-foreground-final-20261025"
SRC=ROOT/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
SPR=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\00_正式採用素材\characters")
ref=Image.open(SRC).convert("RGB");assert ref.size==(546,483)
src=np.asarray(ref)
H,W=483,546
# Original small west partition retaining marble front and walnut skirting.
# Its front plane is fixed; narrow hand rail is independently layered.
wall=[(0,215),(66,215),(70,221),(72,307),(78,316),(0,316)]
rail=[(83,198),(94,177),(101,180),(100,197),(94,204),(91,231),(89,250),(91,279),(87,308),(83,321),(72,318),(69,299),(72,231),(78,210)]
ms={}
for name,poly in (("wall",wall),("rail",rail)):
 m=Image.new("L",(W,H),0)
 ImageDraw.Draw(m).polygon(poly,fill=255)
 # Remove intentionally dynamic plant silhouette region: it needs its own future
 # asset and cannot be hidden or overwritten by this partition.
 # At (x<55, y>=267), retain original plant in source; wall is drawn behind it.
 if name=="wall":
  ImageDraw.Draw(m).rectangle((0,267,55,316),fill=0)
 arr=np.asarray(m)
 ms[name]=arr.copy()
 out=np.dstack([src,arr])
 Image.fromarray(out,"RGBA").save(OUT/f"entrance_left_foreground_{name}.png",optimize=True)
 Image.fromarray(arr,"L").save(OUT/f"entrance_left_{name}_mask.png",optimize=True)
mask_total=np.maximum(ms["wall"],ms["rail"])
# Underlay is hidden by both foreground pieces in normal display. Its role is
# to avoid baked architecture under an avatar, not a standalone room repaint.
# Crop donor from adjacent real marble floor and dark walnut wainscot.
blank=src.copy()
ma=mask_total>0
donor=src[212:332,105:205,:]
donor=cv2.resize(donor,(W,120),interpolation=cv2.INTER_CUBIC)
under=blank.copy()
under[170:290,:]=np.where(ma[170:290,:,None],donor[:120],under[170:290,:])
# upper wall in real source under lower part of the partition:
for y in range(290,322):
 for x in range(0,110):
  if ma[y,x]:
   under[y,x]=src[min(355,y+28),min(180,x+98)]
Image.fromarray(under,"RGB").save(OUT/"entrance_bg_without_left_foreground.png",optimize=True)
def over(base,*layers):
 im=base.convert("RGBA").copy()
 for item in layers:im.alpha_composite(item)
 return im.convert("RGB")
wallim=Image.open(OUT/"entrance_left_foreground_wall.png").convert("RGBA")
railim=Image.open(OUT/"entrance_left_foreground_rail.png").convert("RGBA")
rebuild=over(Image.fromarray(under,"RGB"),wallim,railim)
rebuild.save(OUT/"QA_left_partition_reassembled.png",optimize=True)
assert np.array_equal(np.asarray(rebuild),src),"original scene reconstruction must be exact"
# QA with user approved photo frames & actual official sprites.
photo=Image.open(ROOT/"entrance-rear-frames-final-20261025"/"QA_photos_100pct.png").convert("RGB")
def sprite(dest,name,cx,foot,w):
 f=SPR/name;assert f.is_file()
 raw=Image.open(f).convert("RGBA")
 h=round(w*raw.height/raw.width)
 obj=raw.resize((w,h),Image.Resampling.NEAREST)
 dest.alpha_composite(obj,(round(cx-w/2),foot-h))
 return hashlib.sha256(f.read_bytes()).hexdigest()
# sprite behind the front railing (testing occlusion)
b=Image.fromarray(under,"RGB").convert("RGBA")
# Keep photo and rest of scene source; replace only foreground in photo preview
pat=np.asarray(photo).copy()
pat[ma]=under[ma]
Image.fromarray(pat,"RGB").save(OUT/"QA_preview_underlay_photos.png",optimize=True)
back=Image.fromarray(pat,"RGB").convert("RGBA")
sh=sprite(back,"curator-front-00.png",94,273,35)
back.alpha_composite(wallim);back.alpha_composite(railim)
back.convert("RGB").save(OUT/"QA_character_behind_partition.png",optimize=True)
front=Image.fromarray(pat,"RGB").convert("RGBA")
front.alpha_composite(wallim);front.alpha_composite(railim)
sprite(front,"curator-front-00.png",94,273,35)
front.convert("RGB").save(OUT/"QA_character_in_front_partition.png",optimize=True)
# Other users can see untouched actors in unchanged room:
origpat=Image.fromarray(pat,"RGB").convert("RGBA")
origpat.alpha_composite(wallim);origpat.alpha_composite(railim)
sprite(origpat,"butler-front-00.png",140,371,43)
sprite(origpat,"curator-front-00.png",286,366,35)
origpat.convert("RGB").save(OUT/"QA_full_scene_formal_characters.png",optimize=True)
# Side by side comparison
compare=Image.new("RGB",(W*2,H));compare.paste(back.convert("RGB"),(0,0));compare.paste(front.convert("RGB"),(W,0))
compare.save(OUT/"QA_front_back_comparison.png",optimize=True)
mask_orig=np.zeros((H,W),np.uint8)
mask_orig[:]=mask_total
manifest={"source":str(SRC),"sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
"canvas":[W,H],"wall_polygon":wall,"rail_polygon":rail,
"mask_wall_pixels":int((ms["wall"]>0).sum()),"mask_rail_pixels":int((ms["rail"]>0).sum()),
"original_reconstruction_pixel_exact":True,"character_source_original_sha256":sh,
"visual_role":"occlusion foreground, fixed geometry","game_integrated":False,
"note":"Previous right display wall and photo frames unchanged. Fixed left-hand partition, not a free-standing movable furniture asset.",
"art_review_status":"candidate"}
(OUT/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("QA passed source exact:",len(list(OUT.iterdir())),"files")
