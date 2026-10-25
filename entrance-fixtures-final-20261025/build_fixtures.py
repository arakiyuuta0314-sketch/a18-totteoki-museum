# -*- coding: utf-8 -*-
from pathlib import Path
import cv2,numpy as np,json,hashlib
from PIL import Image
ROOT=Path(r"C:\Users\User\source\repos\a18-entrance-greenery-20261025")
OUT=ROOT/"entrance-fixtures-final-20261025"
refpath=ROOT/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
ref=Image.open(refpath).convert("RGB");assert ref.size==(546,483)
src=np.asarray(ref).astype(np.float32)
base=src.copy()
spec={
 "west_sign":((4,61,43,116),(54,61),(116,124)),
 "east_sign":((503,61,543,116),(54,61),(116,124)),
 "west_sconce":((214,83,233,129),(76,83),(129,139)),
 "east_sconce":((334,83,354,129),(76,83),(129,139))
}
for name,(rect,top,bot) in spec.items():
 l,t,r,b=rect
 T=np.median(src[top[0]:top[1],l:r],axis=0)
 B=np.median(src[bot[0]:bot[1],l:r],axis=0)
 T=cv2.GaussianBlur(T.reshape(1,r-l,3),(7,1),0)[0]
 B=cv2.GaussianBlur(B.reshape(1,r-l,3),(7,1),0)[0]
 for y in range(t,b):
  vv=(y-t)/max(1,b-t-1);vv=vv*vv*(3-2*vv)
  for x in range(l,r):
   fade=min(1,(x-l+.2)/4,(r-x-.2)/4,(y-t+.2)/5,(b-y-.2)/5)
   base[y,x]=src[y,x]*(1-fade)+(T[x-l]*(1-vv)+B[x-l]*vv)*fade
base=np.uint8(np.rint(np.clip(base,0,255)))
Image.fromarray(base).save(OUT/"entrance_bg_without_signs_sconces.png",optimize=True)
# Normal alpha PNG, inverted to reconstruct actual source-over RGB.
for name,(rect,_,__) in spec.items():
 l,t,r,b=rect
 S=src[t:b,l:r]
 B=base[t:b,l:r].astype(np.float32)
 diff=np.abs(S-B);amp=diff.max(axis=2)
 amin=np.maximum(np.where(S>B,(S-B)/np.maximum(1,255-B),0),
                 np.where(S<B,(B-S)/np.maximum(1,B),0)).max(axis=2)
 a=np.minimum(1,np.maximum(amp/26,amin+.02))
 a=np.where(amp<.1,0,a)
 A=np.uint8(np.rint(a*255))
 rgb=np.zeros_like(S)
 active=A>0
 for ch in range(3):
  rgb[:,:,ch][active]=np.clip(np.rint((S[:,:,ch][active]*255-B[:,:,ch][active]*(255-A[active]))/A[active]),0,255)
 rgba=Image.fromarray(np.dstack([np.uint8(rgb),A]),"RGBA")
 rgba.save(OUT/f"entrance_{name}.png",optimize=True)
 # Checker proof
 h,w=A.shape
 yy,xx=np.indices((h,w))
 ck=np.where((xx//6+yy//6)%2==0,158,220).astype(np.float32)
 checker=np.stack([ck]*3,axis=2)
 image=rgb*a[:,:,None]+checker*(1-a[:,:,None])
 panel=Image.new("RGB",(w*8,h*4))
 panel.paste(ref.crop(rect).resize((w*4,h*4),Image.Resampling.NEAREST),(0,0))
 panel.paste(Image.fromarray(np.uint8(np.clip(image,0,255))).resize((w*4,h*4),Image.Resampling.NEAREST),(w*4,0))
 panel.save(OUT/f"QA_isolation_{name}.png")
def render(visible,reference=None):
 baseline=np.array(Image.open(reference).convert("RGB")) if reference else np.array(ref)
 for name,(rect,_,__) in spec.items():
  l,t,r,b=rect;baseline[t:b,l:r]=base[t:b,l:r]
 canvas=Image.fromarray(baseline,"RGB").convert("RGBA")
 for name,(rect,_,__) in spec.items():
  if name in visible:canvas.alpha_composite(Image.open(OUT/f"entrance_{name}.png").convert("RGBA"),rect[:2])
 return canvas.convert("RGB")
keys=list(spec)
on=render(keys);on.save(OUT/"QA_all_four_reassembled.png",optimize=True)
off=render([]);off.save(OUT/"QA_all_four_removed.png",optimize=True)
refphotos=ROOT/"entrance-rear-frames-final-20261025"/"QA_photos_100pct.png"
assert refphotos.is_file()
photos_on=render(keys,refphotos);photos_off=render([],refphotos)
photos_on.save(OUT/"QA_photos_sprites_all_four.png",optimize=True)
photos_off.save(OUT/"QA_photos_sprites_none.png",optimize=True)
board=Image.new("RGB",(1092,483))
board.paste(photos_on,(0,0));board.paste(photos_off,(546,0))
board.save(OUT/"QA_fixture_photo_comparison.png",optimize=True)
orig=np.array(ref);new=np.array(on)
outside=np.ones((483,546),bool)
for rect,_,__ in spec.values():
 l,t,r,b=rect;outside[t:b,l:r]=False
assert np.array_equal(orig[outside],new[outside])
mae=float(np.abs(np.int16(orig)-np.int16(new)).mean())
assert mae<.05,mae
assert np.array_equal(np.array(Image.open(refphotos).convert("RGB"))[outside],np.array(photos_on)[outside])
manifest={"source":str(refpath),"source_sha256":hashlib.sha256(refpath.read_bytes()).hexdigest(),
 "canvas":[546,483],"fixture_rectangles":{n:list(z[0]) for n,z in spec.items()},
 "normal_blend_alpha_png":True,"unmodified_outside_regions":True,"mean_channel_abs_error_returned":mae,
 "formal_characters":"Original sprites from prior approved photo-frame composited QA; not regenerated",
 "qa":["reassembly","alpha","restored walls","photo and characters"],
 "game_integration":False,"user_art_approval":"pending"}
(OUT/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS",len(spec),"fixture sources; RGB MAE",round(mae,6),"files",len(list(OUT.iterdir())))
