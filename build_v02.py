# -*- coding: utf-8 -*-
"""A18 entrance scene v02: remove remaining baked lamps and sign ghosts from existing real PNGs.
No generation, no redraw, no global grading, no changes to game/main.
All repairs are localized source-pixel donor synthesis, subject to visual approval.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import cv2,numpy as np,hashlib,json,shutil
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"entrance-wood-onoff-v02-20261026"
OUT.mkdir(parents=True,exist_ok=True)
OLD=Path(r"C:\Users\User\source\repos\a18-art-wood-onoff-v02-publish-20261026\entrance-wood-onoff-v01-20261026")
D52=Path(r"C:\Users\User\source\repos\a18-entrance-wood-onoff-v02-20261026\entrance-wood-onoff-v01-20261026")
for name in ("entrance_OFF.png","entrance_ON.png"):
 assert (OLD/name).exists()
 shutil.copy2(OLD/name,OUT/("reference_9ceeca4_"+name))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def im(p):return Image.open(p).convert("RGBA")
base=np.asarray(Image.open(OLD/"entrance_OFF.png").convert("RGB")).copy()
on_prior=np.asarray(Image.open(OLD/"entrance_ON.png").convert("RGB")).copy()
assert base.shape==(483,546,3)
W,H=546,483
def save(image,name):
 p=OUT/name
 (image if isinstance(image,Image.Image) else Image.fromarray(image)).save(p,optimize=True)
 return p
wood=im(D52/"wood_frame_three_only.png")
wood_alpha=np.asarray(wood.getchannel("A"))>0
prior_recomp=np.asarray(Image.alpha_composite(Image.fromarray(base).convert("RGBA"),wood).convert("RGB"))
assert np.array_equal(prior_recomp,on_prior),("published ON does not match wood overlay",int(np.any(prior_recomp!=on_prior,axis=2).sum()))
# 1) small sign-mount shadows still visible after 29 removal.
# Thin local source-donor substitution; surrounding warm plaster unchanged.
sign_mask=np.zeros((H,W),np.uint8)
sign_img=base.copy()
# Same-row beige plaster from adjacent original image pixels. Protect all carved
# columns and picture walls. Shadows from previous fixture separation are removed.
sign_specs=[
 (0,24,22,32,70,124,True,False),
 (503,520,522,532,70,124,False,False),
 (532,546,520,530,70,124,False,True),
]
for x0,x1,dl,dr,y0,y1,openleft,openright in sign_specs:
 top=np.median(base[56:67,x0:x1],axis=0)
 top_center=np.median(base[56:67,dl:dr],axis=(0,1))
 grad=np.asarray([top[max(0,j-4):min(x1-x0,j+5)].mean(axis=0)-top_center
                  for j in range(x1-x0)])
 for y in range(y0,y1):
  donor=np.median(base[y,dl:dr],axis=0)
  for x in range(x0,x1):
   f=min(1,(y-y0+1)/8,(y1-y)/8)
   if not openleft:f=min(f,(x-x0+1)/4)
   if not openright:f=min(f,(x1-x)/4)
   f=max(0,f)
   # Preserve each wall's horizontal shading from clean top source pixels
   # while replacing the old fixture's narrow vertical residuals.
   strength=.75 if x0==0 else .8
   value=np.clip(donor+grad[x-x0]*strength,0,255)
   sign_img[y,x]=np.uint8(np.clip(np.rint(base[y,x]*(1-f)+value*f),0,255))
   if f>0:sign_mask[y,x]=255
changed_sign=np.any(sign_img!=base,axis=2)
base=sign_img
# 2) rear exhibition lights: x=138 and 414 gold fixtures and colored bloom
# reside above empty-paper windows. Rear frame display wall horizontal:
# line-wise left/right surrounding pixel donors preserve wood ceiling and green
# wall color at each y with no change below y=61.
rear_mask=np.zeros((H,W),np.uint8)
for cx in (138,414):
 # bloom ellipse y29..59 + protruding bracket around y24..38
 cv2.ellipse(rear_mask,(cx,43),(24,19),0,0,360,255,-1)
 cv2.ellipse(rear_mask,(cx,30),(8,9),0,0,360,255,-1)
rear_mask[61:,:]=0
assert not rear_mask[61:].any()
rear=base.copy()
for cx in (138,414):
 lx,rx=(106,170) if cx==138 else (380,450)
 ly,uy=23,61
 ys,xs=np.where((rear_mask>0)&(np.indices(rear_mask.shape)[1]>cx-27)&(np.indices(rear_mask.shape)[1]<cx+27))
 for y,x in zip(ys,xs):
  L=np.median(base[y,lx:lx+7],axis=0);R=np.median(base[y,rx-7:rx],axis=0)
  t=np.clip((x-lx)/(rx-lx),0,1)
  rear[y,x]=np.uint8(np.clip(np.rint(L*(1-t)+R*t),0,255))
changed_rear=np.any(rear!=base,axis=2)
base=rear
# 3) right-front top exhibited picture light. Restore the wood handrail/green
# wall as a continuous 0.42-perspective plane by donor interpolation along the
# architectural slope, x=427 and x=480 reference columns only.
fixture_mask=np.zeros((H,W),np.uint8)
points=np.asarray([(431,189),(439,187),(447,186),(452,183),(462,186),
                  (466,190),(470,196),(470,203),(462,205),
                  (456,201),(447,199),(436,197),(431,195)],np.int32)
cv2.fillPoly(fixture_mask,[points],255)
fixture_mask=cv2.dilate(fixture_mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)),iterations=1)
front=base.copy()
for y,x in zip(*np.where(fixture_mask>0)):
 lx,rx,slope=427,480,.42
 yl=int(round(y-slope*(x-lx)))
 yr=int(round(y+slope*(rx-x)))
 L=base[yl,lx].astype(np.float32);R=base[yr,rx].astype(np.float32)
 t=np.clip((x-lx)/(rx-lx),0,1)
 front[y,x]=np.uint8(np.clip(np.rint(L*(1-t)+R*t),0,255))
changed_front=np.any(front!=base,axis=2)
base=front
# Keep ceiling, floor, doorway, characters and photo mats identical outside
# the explicit masks: no global color adjustment.
all_mask=(sign_mask>0)|(rear_mask>0)|(fixture_mask>0)
raw=np.asarray(Image.open(OLD/"entrance_OFF.png").convert("RGB"))
assert not np.any(np.any(raw!=base,axis=2)&~all_mask)
assert not np.any(all_mask[230:,:] & (np.indices(all_mask.shape)[0][230:,:]>230)), "unexpected lower artifact edit"
save(base,"entrance_OFF.png")
on=np.asarray(Image.alpha_composite(Image.fromarray(base,"RGB").convert("RGBA"),wood).convert("RGB"))
save(on,"entrance_ON.png")
save(wood,"wood_frame_three_only.png")
for file in ("layer_rear_left.png","layer_rear_right.png","layer_right_front_v07.png","butler-front-00.png","curator-front-00.png"):
 shutil.copy2(D52/file,OUT/file)
# For ON/OFF binary contract no RGB pixel may change outside frame sprites.
diff=np.any(on!=base,axis=2)
assert not np.any(diff&~wood_alpha)
# Verify every image is 546x483. Mat and character locations are unaffected.
for n in ("entrance_OFF.png","entrance_ON.png","wood_frame_three_only.png"):
 assert Image.open(OUT/n).size==(W,H)
# Compare previous vs current floor, doorway, staff unmodified.
for key,(l,t,r,b) in {"floor":(155,340,400,483),"door":(240,50,326,199),"staff":(110,318,309,374)}.items():
 assert np.array_equal(base[t:b,l:r],raw[t:b,l:r]),key
# targeted QA snapshots and masks
mask_color=np.uint8(all_mask)*255
save(mask_color,"QA_restoration_mask.png")
save(np.uint8(diff)*255,"QA_frame_diff_mask.png")
before=Image.open(OLD/"entrance_OFF.png").convert("RGB")
after=Image.open(OUT/"entrance_OFF.png").convert("RGB")
board=Image.new("RGB",(W*2,H))
board.paste(before,(0,0));board.paste(after,(W,0))
save(board,"QA_v01_vs_v02_off.png")
board=Image.new("RGB",(W*2,H))
board.paste(after,(0,0));board.paste(Image.fromarray(on),(W,0))
save(board,"QA_OFF_ON_side_by_side.png")
for name,roi in {"front":(395,157,515,247),"rear_left":(102,19,179,90),
                 "rear_right":(376,19,459,90),"sign_west":(0,62,47,140),
                 "sign_east":(499,62,546,140),"counter":(0,298,110,404)}.items():
 l,t,r,b=roi;fac=4
 w,h=(r-l)*fac,(b-t)*fac
 cmp=Image.new("RGB",(w*2,h))
 cmp.paste(before.crop(roi).resize((w,h),Image.Resampling.NEAREST),(0,0))
 cmp.paste(after.crop(roi).resize((w,h),Image.Resampling.NEAREST),(w,0))
 save(cmp,"QA_zoom_before_after_"+name+".png")
manifest={"status":"technical_candidate_pending_visual_approval",
 "source_public_commit":"9ceeca4","canvas":[546,483],
 "official_wood_source":"44 and 49 v07 via v52 overlay, unchanged",
 "new_repairs":["remaining right-front exhibition bar/light","rear exhibition light mounts and warm bloom x138/x414","wall placard shadow residues"],
 "repair_pixels":int(np.any(base!=raw,axis=2).sum()),
 "repair_area_by_group":{"sign":int(changed_sign.sum()),"rear":int(changed_rear.sum()),"right_front":int(changed_front.sum())},
 "repair_mask_total":int(all_mask.sum()),
 "outside_repair_mask_changed_pixels":int((np.any(base!=raw,axis=2)&~all_mask).sum()),
 "on_off_diff_pixels":int(diff.sum()),"outside_frame_alpha_changed_pixels":int((diff&~wood_alpha).sum()),
 "floor_door_characters_unchanged":True,
 "user_art_approval":False,"lv1_decided":False,"game_integrated":False,
 "source_sha256":{"old_off":sha(OLD/"entrance_OFF.png"),"old_on":sha(OLD/"entrance_ON.png"),
 "wood_overlay":sha(D52/"wood_frame_three_only.png")},
 "formal_character_sha256":{nm:sha(D52/nm) for nm in ("butler-front-00.png","curator-front-00.png")},
 "caveat":"Removed-light and unseen wall pixels estimated from neighboring real source artwork; cannot certify exact original unseen surfaces."
}
(OUT/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("BUILD_V02_PASS",json.dumps({k:manifest[k] for k in ("repair_pixels","repair_area_by_group","outside_repair_mask_changed_pixels","on_off_diff_pixels","outside_frame_alpha_changed_pixels")},ensure_ascii=True),flush=True)
