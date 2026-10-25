# -*- coding:utf-8 -*-
"""A18 E05 original-source reversible gilded architectural trim.
Contains only extracted original pixels, no synthetic ornamentation.
"""
from pathlib import Path
from PIL import Image
import numpy as np,cv2,hashlib,json
R=Path(r"C:\Users\User\source\repos\a18-entrance-wall-trim-20261025")
O=Path(__file__).parent
S=R/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
P=R/"entrance-rear-frames-final-20261025"/"QA_photos_100pct.png"
assert S.is_file() and P.is_file()
original=Image.open(S).convert("RGB")
src=np.asarray(original);h,w=src.shape[:2]
# Intervals avoid wall pillars, framed photographs, the right-hand foreground balustrade.
# x1 and y1 are exclusive. Every pixel belongs to a real decorative cap of the source image.
spec={
 "ceiling_west":[65,11,205,20],
 "ceiling_east":[355,11,480,20],
 "wainscot_west":[68,164,203,172],
 "wainscot_east":[358,164,400,172]
}
target=src.copy()
def filled_wood(strip):
 x0,y0,x1,y1=strip
 # Sample matched architectural wood immediately above and below.
 # Distinct frame areas are kept entirely outside the repair region.
 donor_above=src[max(0,y0-7):max(0,y0-2),x0:x1,:].astype(np.float32)
 donor_below=src[y1+2:y1+7,x0:x1,:].astype(np.float32)
 assert len(donor_above)>0 and len(donor_below)>0
 top=np.median(donor_above,axis=0)
 bottom=np.median(donor_below,axis=0)
 top=cv2.GaussianBlur(top.reshape(1,x1-x0,3),(9,1),0)[0]
 bottom=cv2.GaussianBlur(bottom.reshape(1,x1-x0,3),(9,1),0)[0]
 for y in range(y0,y1):
  v=(y-y0+1)/(y1-y0+1)
  # existing wood textures under gold trim, no new complex geometry
  target[y,x0:x1]=np.uint8(np.clip(np.rint(top*(1-v)+bottom*v),0,255))
for k,rect in spec.items():
 x0,y0,x1,y1=rect
 fg=original.crop(rect).convert("RGBA")
 fg.save(O/f"entrance_wall_trim_{k}.png",optimize=True)
 Image.fromarray(np.full((y1-y0,x1-x0),255,dtype=np.uint8),"L").save(O/f"entrance_wall_trim_{k}_mask.png",optimize=True)
 filled_wood(rect)
background=Image.fromarray(target,"RGB")
background.save(O/"entrance_bg_without_wall_trims.png",optimize=True)
# Preserve 4-state source image and photo+official sprite montage.
p=np.asarray(Image.open(P).convert("RGB")).copy()
for rect in spec.values():
 x0,y0,x1,y1=rect
 p[y0:y1,x0:x1]=target[y0:y1,x0:x1]
photo_base=Image.fromarray(p,"RGB")
photo_base.save(O/"QA_with_photos_characters_trim_off.png",optimize=True)
def compose(layer,visible):
 c=layer.convert("RGBA")
 for k in spec:
  if k not in visible:continue
  x,y,_,_=spec[k]
  c.alpha_composite(Image.open(O/f"entrance_wall_trim_{k}.png").convert("RGBA"),(x,y))
 return c.convert("RGB")
allkeys=list(spec)
rebuild=compose(background,allkeys)
rebuild.save(O/"QA_source_reconstruction_all_on.png",optimize=True)
assert np.array_equal(np.asarray(rebuild),src),"Original reconstruction failed"
photo_on=compose(photo_base,allkeys)
photo_on.save(O/"QA_with_photos_characters_trim_on.png",optimize=True)
for n,shown in [("ceiling_only",["ceiling_west","ceiling_east"]),("lower_only",["wainscot_west","wainscot_east"]),("no_trim",[])]:
 compose(photo_base,shown).save(O/f"QA_{n}.png",optimize=True)
board=Image.new("RGB",(1092,483))
board.paste(photo_on,(0,0));board.paste(photo_base,(546,0))
board.save(O/"QA_all_trims_on_off.jpg",quality=95)
# Intermediate 3-level static previews for future data-free decoration phases.
groups={
 "stage0_empty":[],"stage1_lower":["wainscot_west","wainscot_east"],
 "stage2_both":allkeys
}
board3=Image.new("RGB",(546*3,483))
for i,(name,enabled) in enumerate(groups.items()):
 picture=compose(photo_base,enabled)
 picture.save(O/f"QA_{name}.png",optimize=True)
 board3.paste(picture,(546*i,0))
board3.save(O/"QA_trim_growth_3states.jpg",quality=95)
outside=np.ones((483,546),bool)
for x0,y0,x1,y1 in spec.values():outside[y0:y1,x0:x1]=False
assert np.array_equal(target[outside],src[outside])
# All photo windows and formal avatars are unchanged by trim reconstruction.
assert np.array_equal(np.asarray(photo_on)[outside],np.asarray(Image.open(P).convert("RGB"))[outside])
official=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\00_正式採用素材\characters")
for name in ["butler-front-00.png","curator-front-00.png"]:
 assert (official/name).read_bytes()==(R/"entrance-rear-frames-final-20261025"/name).read_bytes()
info={
 "source":str(S),"source_sha256":hashlib.sha256(S.read_bytes()).hexdigest(),
 "dimensions":[546,483],"rects_xyxy":spec,
 "separate_layers":len(spec),"background":"entrance_bg_without_wall_trims.png",
 "pixel_exact_source_reconstruction":True,
 "source_changed_outside_object_regions":False,
 "photo_and_official_characters_unchanged":True,
 "states_checked":list(groups.keys()),
 "game_implementation":False,
 "status":"completed visual candidate waiting user art approval",
 "limitations":"These are fixed-length original architectural mouldings, not nine-slice or free-moving furniture. Future length changes need new endpoint QA."
}
(O/"QA_manifest.json").write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUCCESS",len(spec),"wall/ceiling original golden mouldings, exact source reconstruction",len(list(O.iterdir())),"files")
