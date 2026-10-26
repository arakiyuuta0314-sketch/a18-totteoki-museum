# -*- coding: utf-8 -*-
"""A18 original-PNG-only OFF/ON wood frame composite; preserve 546x483 architecture."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,cv2,json,hashlib,shutil,zipfile
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
HERE=Path(__file__).resolve().parent
OUT=HERE/"entrance-wood-onoff-v01-20261026";OUT.mkdir(parents=True,exist_ok=True)
def folder(prefix):
 hits=[p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith(prefix+"_")]
 assert len(hits)==1,(prefix,hits)
 return hits[0]
D29,D30,D42,D43,D44,D49,D50,D51=[folder(str(i)) for i in (29,30,42,43,44,49,50,51)]
CH=ROOT/"00_正式採用素材"/"characters"
W,H=546,483
def img(p,mode="RGB"):
 assert p.exists(),p
 v=Image.open(p).convert(mode);assert v.size==(W,H),(p,v.size)
 return v
def rgb(p):return np.asarray(img(p),dtype=np.uint8).copy()
def png(v,name):
 f=OUT/name
 (v if isinstance(v,Image.Image) else Image.fromarray(v)).save(f,optimize=True)
 return f
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=rgb(D43/"entrance_bare_three_frame_backing.png")
# Fixture 29 four registered rectangles: apply source-based repaired source ONLY there.
fixture29={"west_sign":(4,61,43,116),"east_sign":(503,61,543,116),
 "west_sconce":(214,83,233,129),"east_sconce":(334,83,354,129)}
s29=rgb(D29/"entrance_bg_without_signs_sconces.png")
for l,t,r,b in fixture29.values():base[t:b,l:r]=s29[t:b,l:r]
# The picture lights (30) are still baked in at this stage. Reapply 30's
# existing horizontal donor inpainting to frame-free 43, NOT old decorated pixels.
picture30={"west":(116,30,161,69),"east":(391,30,438,69)}
for l,t,r,b in picture30.values():
 src=base.copy();left=np.median(src[t:b,l-9:l-3],axis=1)
 right=np.median(src[t:b,r+3:r+9],axis=1)
 for y in range(t,b):
  for x in range(l,r):
   f=(x-l)/(r-l-1);v=left[y-t]*(1-f)+right[y-t]*f
   a=np.clip(min((x-l+.1)/3,(r-x-.1)/3,(y-t+.1)/3,(b-y-.1)/3),0,1)
   base[y,x]=np.uint8(np.clip(np.rint(src[y,x]*(1-a)+v*a),0,255))
# 50: registered four-lamp removal *diff only*. Wood-frame pixels in the
# 49 reference must NEVER be copied into the frame-free base.
s49=rgb(D50/"QA_source_v49.png")
off50=rgb(D50/"QA_all_four_sconces_off.png")
rect50={"outer_left":(38,68,66,150),"outer_right":(473,68,501,150),
 "foreground_left":(392,203,419,274),"foreground_right":(497,253,530,327)}
fifty=np.zeros((H,W),bool)
for l,t,r,b in rect50.values():
 m=np.any(off50[t:b,l:r]!=s49[t:b,l:r],axis=2)
 roi=base[t:b,l:r];roi[m]=off50[t:b,l:r][m]
 fifty[t:b,l:r]=m
# 51: ceiling and desk removal diff-only; these are the only legal
# replacement pixels. All original building / floor / people remain untouched.
s51=rgb(D51/"QA_source_v50.png")
off51=rgb(D51/"QA_all_off.png")
allowed51=np.zeros((H,W),bool)
allowed51[:15,:]=True;allowed51[303:399,8:47]=True
assert not np.any(np.any(off51!=s51,axis=2)&~allowed51),"51 edits outside contract"
mask51=np.any(off51!=s51,axis=2)&allowed51
base[mask51]=off51[mask51]
# The tiny countertop guide placard is not building architecture and must
# not remain in a "no signs" OFF state. The surrounding existing countertop
# supplies source pixels for a strictly localized estimated repair.
signmask=np.zeros((H,W),dtype=np.uint8)
cv2.fillPoly(signmask,[np.array([(49,339),(65,339),(73,350),(74,378),(71,391),(42,391),(42,356)],np.int32)],255)
signmask=cv2.dilate(signmask,np.ones((3,3),np.uint8),iterations=1)
original_sign=base.copy()
repaired=base.copy()
# Same-row countertop donors preserve the horizontal stone/green/wood bands.
# The 8px perimeter feather joins the original intact tabletop.
for y in range(334,398):
 left=np.median(original_sign[y,26:40],axis=0).astype(float)
 right=np.median(original_sign[y,80:91],axis=0).astype(float)
 for x in range(38,78):
  u=np.clip((x-38)/39,0,1)
  repaired[y,x]=np.uint8(np.clip(np.rint(left*(1-u)+right*u),0,255))
dist=cv2.distanceTransform(signmask,cv2.DIST_L2,3)
soft=np.clip(dist/6,0,1)
base=np.uint8(np.clip(np.rint(base*(1-soft[:,:,None])+repaired*soft[:,:,None]),0,255))
png(signmask,"QA_counter_nameplate_removal_mask.png")
png(base,"entrance_clean_base_no_mats_no_characters.png")
canvas=Image.fromarray(base,"RGB").convert("RGBA")
mats={"left":img(D43/"exhibition_left_empty_mat.png","RGBA"),
      "right":img(D43/"exhibition_right_empty_mat.png","RGBA"),
      "front":img(D49/"right_front_content_empty.png","RGBA")}
for v in mats.values():canvas.alpha_composite(v)
png(canvas,"entrance_OFF_no_characters.png")
# Full 48 original characters preserved; two existing front idle sprites are
# placed at the agreed v07 registered positions, with nearest-neighbor resizing.
characters=[("butler-front-00.png",140,371,43),("curator-front-00.png",287,366,35)]
hashes={}
for name,cx,foot,w in characters:
 p=CH/name;hashes[name]=sha(p)
 sprite=Image.open(p).convert("RGBA");h=round(sprite.height*w/sprite.width)
 canvas.alpha_composite(sprite.resize((w,h),Image.Resampling.NEAREST),(round(cx-w/2),foot-h))
off=canvas.convert("RGB");png(off,"entrance_OFF.png")
frames={"rear_left":img(D44/"frame_left_wood_grain_v02.png","RGBA"),
        "rear_right":img(D44/"frame_right_wood_grain_v02.png","RGBA"),
        "right_front_v07":img(D49/"right_front_frame_wood.png","RGBA")}
on=canvas.copy()
for f in frames.values():on.alpha_composite(f)
on=on.convert("RGB");png(on,"entrance_ON.png")
# Store independent composed 3-frame overlay; NO emission, no signs/plants.
overlay=Image.new("RGBA",(W,H))
for f in frames.values():overlay.alpha_composite(f)
png(overlay,"wood_frame_three_only.png")
for key,f in frames.items():png(f,"layer_"+key+".png")
# Strong byte/pixel invariant: ON differs from OFF ONLY where some wood-frame alpha exists.
a=np.asarray(overlay.getchannel("A"))>0
o=np.asarray(off);n=np.asarray(on)
diff=np.any(o!=n,axis=2)
assert not np.any(diff&~a), "Non-frame difference"
assert int(np.count_nonzero(diff))>1000, "Wood not rendered"
assert np.array_equal(np.asarray(Image.open(OUT/"entrance_OFF.png")),o)
assert np.array_equal(np.asarray(Image.open(OUT/"entrance_ON.png")),n)
# No material pixel of either official sprite file changed. Stage byte-identical copies.
for name in hashes:
 shutil.copy2(CH/name,OUT/name)
 assert sha(OUT/name)==hashes[name]
# Validate photo-mat masks: common in OFF and ON and no wood alpha inside true aperture.
for k in ("left","right"):
 win=np.asarray(Image.open(D43/f"exhibition_{k}_window_mask.png").convert("L"))>0
 assert not np.any(win & (np.asarray(frames["rear_"+k].getchannel("A"))>0))
win=np.asarray(Image.open(D49/"right_front_shared_window_mask.png").convert("L"))>0
assert not np.any(win & (np.asarray(frames["right_front_v07"].getchannel("A"))>0))
# Contact sheet for side-by-side comparison, native resolution halves.
board=Image.new("RGB",(W*2,H));board.paste(off,(0,0));board.paste(on,(W,0))
png(board,"QA_OFF_ON_side_by_side.png")
png(np.uint8(a)*255,"QA_allowed_frame_mask.png")
png(np.uint8(diff)*255,"QA_actual_pixel_diff_mask.png")
for nm,rect in {"rear_left":(70,41,208,165),"rear_right":(354,41,474,168),
                "right_front":(394,153,533,369),"desk":(0,295,98,420),
                "ceiling":(0,0,546,35)}.items():
 l,t,r,b=rect
 duo=Image.new("RGB",((r-l)*6,(b-t)*3))
 for i,src in enumerate((off,on)):
  duo.paste(src.crop(rect).resize(((r-l)*3,(b-t)*3),Image.Resampling.NEAREST),(i*(r-l)*3,0))
 png(duo,"QA_zoom_"+nm+".png")
report={"status":"technical_candidate_pending_art_review",
 "canvas":[W,H],"OFF_ON_wood_only":True,
 "base":"43/entrance_bare_three_frame_backing.png",
 "components":["29 signs+inner wall sconces off","30 picture lights off adapted to 43 clean base",
 "50 four other sconces off (only removed diff pixels)","51 ceiling lamps and reception lamp off (only removed diff pixels)",
 "43 rear empty mats","49 v07 right-front empty matte","44 rear two wood","49 right-front v07 wood"],
 "formal_characters_sha256":hashes,
 "source_sha256":{k:sha(p) for k,p in {
  "D43_base":D43/"entrance_bare_three_frame_backing.png",
  "D44_left":D44/"frame_left_wood_grain_v02.png",
  "D44_right":D44/"frame_right_wood_grain_v02.png",
  "D49_front":D49/"right_front_frame_wood.png",
  "D50_off":D50/"QA_all_four_sconces_off.png",
  "D51_off":D51/"QA_all_off.png"}.items()},
 "wood_pixels_affected":int(diff.sum()),"wood_alpha_area":int(a.sum()),
 "non_wood_changed_pixels":int((diff&~a).sum()),
 "fifty_changed_pixels":int(fifty.sum()),"fifty_allowed_rects":rect50,
 "fifty_one_changed_pixels":int(mask51.sum()),
 "counter_nameplate_removed":True,"counter_nameplate_repair_pixels":int(np.count_nonzero(signmask)),
 "picture_light_repairs":picture30,"sign_wall_light_repairs":fixture29,
 "estimated_repairs":["29 sign/sconce backgrounds","30 rear picture lights","50 sconces","51 ceiling lamps and reception desk lamp","43 wall behind old gold frames","countertop guide placard"],
 "approval_level1":False,"user_art_approval":False,"game_integrated":False,
 "main_game_modified":False}
(OUT/"QA_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("BUILD_PASS",json.dumps({k:report[k] for k in ("wood_pixels_affected","wood_alpha_area","non_wood_changed_pixels","fifty_changed_pixels","fifty_one_changed_pixels")}),"OUTPUT",OUT,flush=True)
