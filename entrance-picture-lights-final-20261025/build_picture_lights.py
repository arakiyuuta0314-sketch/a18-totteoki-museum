# -*- coding:utf-8 -*-
"""A18 approved-source picture lights, independent originals and wall/gold-top restoration."""
from pathlib import Path
from PIL import Image
import numpy as np, cv2, json, hashlib
ROOT=Path(r"C:\Users\User\source\repos\a18-entrance-greenery-20261025")
OUT=ROOT/"entrance-picture-lights-final-20261025"
SRC=ROOT/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
ref=Image.open(SRC).convert("RGB")
src=np.asarray(ref).astype(np.float32);base=src.copy()
rects={"west":[116,30,161,69],"east":[391,30,438,69]}
for name,(l,t,r,b) in rects.items():
 left=np.median(src[t:b,l-9:l-3],axis=1)
 right=np.median(src[t:b,r+3:r+9],axis=1)
 for y in range(t,b):
  for x in range(l,r):
   f=(x-l)/max(1,r-l-1)
   val=left[y-t]*(1-f)+right[y-t]*f
   a=min(1,(x-l+.1)/3,(r-x-.1)/3,(y-t+.1)/3,(b-y-.1)/3)
   base[y,x]=src[y,x]*(1-a)+val*a
base=np.uint8(np.clip(np.rint(base),0,255))
Image.fromarray(base,"RGB").save(OUT/"entrance_bg_without_picture_lights.png",optimize=True)
for name,(l,t,r,b) in rects.items():
 S=src[t:b,l:r];B=base[t:b,l:r].astype(np.float32)
 dist=np.max(np.abs(S-B),axis=2)
 minA=np.maximum(np.where(S>B,(S-B)/np.maximum(1,255-B),0),
                 np.where(S<B,(B-S)/np.maximum(1,B),0)).max(axis=2)
 alpha=np.where(dist<.1,0,np.minimum(1,np.maximum(dist/24,minA+.02)))
 a=np.uint8(np.rint(alpha*255))
 c=np.zeros_like(S)
 hit=a>0
 for ch in range(3):
  c[:,:,ch][hit]=np.clip(np.rint((S[:,:,ch][hit]*255-B[:,:,ch][hit]*(255-a[hit]))/a[hit]),0,255)
 C=np.uint8(c)
 Image.fromarray(np.dstack((C,a)),"RGBA").save(OUT/f"entrance_picture_light_{name}.png",optimize=True)
 # Transparent glazing: registered photos must remain full contrast below the fixture.
 # Only the central actual bulb glow can overlay the photo where y>=61.
 safe=a.copy()
 yy_full,xx_full=np.mgrid[t:b,l:r]
 cx=138 if name=="west" else 414
 soft=np.clip(1-((xx_full-cx)/11.5)**2-((yy_full-58)/12.0)**2,0,1)
 safe[yy_full>=61]=np.uint8(np.rint(safe[yy_full>=61]*soft[yy_full>=61]))
 Image.fromarray(np.dstack((C,safe)),"RGBA").save(OUT/f"entrance_picture_light_{name}_photo_safe.png",optimize=True)
 # Compare original crop and transparently separated illumination on checkerboard
 h,w=a.shape; yy,xx=np.indices((h,w))
 cv=np.where((xx//6+yy//6)%2,215,164).astype(np.float32)
 chick=np.repeat(cv[:,:,None],3,axis=2)
 merged=np.uint8(np.clip(C*alpha[:,:,None]+chick*(1-alpha[:,:,None]),0,255))
 sheet=Image.new("RGB",(w*8,h*4))
 sheet.paste(ref.crop((l,t,r,b)).resize((w*4,h*4),Image.Resampling.NEAREST),(0,0))
 sheet.paste(Image.fromarray(merged).resize((w*4,h*4),Image.Resampling.NEAREST),(w*4,0))
 sheet.save(OUT/f"QA_picture_light_isolation_{name}.png")
def composite(enabled,previous=None):
 im=np.asarray(Image.open(previous).convert("RGB")).copy() if previous else np.asarray(ref).copy()
 for l,t,r,b in rects.values():
  # In the photo-backed preview, do not repaint any registered user photo at y>=61.
  cutoff=61 if previous else b
  im[t:cutoff,l:r]=base[t:cutoff,l:r]
 canvas=Image.fromarray(im,"RGB").convert("RGBA")
 for name,(l,t,r,b) in rects.items():
  if name in enabled:
   filename=f"entrance_picture_light_{name}_photo_safe.png" if previous else f"entrance_picture_light_{name}.png"
   canvas.alpha_composite(Image.open(OUT/filename).convert("RGBA"),(l,t))
 return canvas.convert("RGB")
rebuild=composite(rects.keys());rebuild.save(OUT/"QA_original_reassembled_two_lights.png",optimize=True)
empty=composite([]);empty.save(OUT/"QA_empty_wall_no_picture_lights.png",optimize=True)
west=composite(["west"]);west.save(OUT/"QA_west_only.png",optimize=True)
east=composite(["east"]);east.save(OUT/"QA_east_only.png",optimize=True)
pre=ROOT/"entrance-rear-frames-final-20261025"/"QA_photos_100pct.png"
assert pre.is_file()
withphoto=composite(rects.keys(),pre);without=composite([],pre)
withphoto.save(OUT/"QA_photos_sprites_both_lights.png",optimize=True)
without.save(OUT/"QA_photos_sprites_no_lights.png",optimize=True)
split=Image.new("RGB",(1092,483));split.paste(withphoto,(0,0));split.paste(without,(546,0))
split.save(OUT/"QA_picture_lights_on_off.png",optimize=True)
# Outside the tiny safe bulb halo, photo content is byte-for-byte preserved.
pbase=np.asarray(Image.open(pre).convert("RGB"))
changed=np.any(np.asarray(withphoto)!=pbase,axis=2)
photo_pixels=np.zeros((483,546),bool)
photo_pixels[69:144,84:194]=True
photo_pixels[69:144,373:460]=True
assert not np.any(changed&photo_pixels),"Registered photo modified below allowed bulb halo"
diff=np.abs(np.asarray(rebuild).astype(np.int16)-np.asarray(ref).astype(np.int16))
outside=np.ones((483,546),bool)
for l,t,r,b in rects.values():outside[t:b,l:r]=False
assert np.array_equal(np.asarray(rebuild)[outside],np.asarray(ref)[outside])
mae=float(diff.mean());assert mae==0,mae
manifest={"source":str(SRC),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
"canvas":[546,483],"rectangles":rects,"source_pixel_identical_when_all_shown":True,
"mean_abs_rgb_diff":mae,"non_target_pixels_unchanged":True,
"background":"entrance_bg_without_picture_lights.png","layer_blend":"normal source over RGBA",
"phone_browser_qa":"pending","game_integrated":False,
"user_approval":"pending","art_note":"Off-state gold frame top repaired by horizontal donors from original room; photo registration mask unmodified."}
(OUT/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS",len(rects),"picture lights","MAE",mae,"files",len(list(OUT.iterdir())))
