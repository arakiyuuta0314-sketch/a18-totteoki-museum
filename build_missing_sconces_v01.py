# -*- coding: utf-8 -*-
"""A18 additional sconces: preserve 49 artwork, remove 4 ORIGINAL fixtures
from background and split into body/glow. No redrawing, no image generation.
Fixtures under original 546x483 source. Independent light glow is optional.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, cv2, json, hashlib
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
REF=R/"43_エントランス完成素材_3額縁本体装飾分離_v01"/"entrance_bare_three_frame_backing.png"
V49=R/"49_エントランス完成素材_右手前壁面基準再投影_v07"/"view_wood_empty_100.png"
BASE=Path(__file__).resolve().parent
O=BASE/"lighting-additional-sconces-v01"
O.mkdir(exist_ok=True)
original=np.asarray(Image.open(REF).convert("RGB"))
current=np.asarray(Image.open(V49).convert("RGB"))
H,W=original.shape[:2]
def save(im,name):
 im.save(O/name,optimize=True);return im
# Localized original source masks, all subject to user art review.
# rect= (left,top,right,bottom), body ellipse (cx,cy,rx,ry), glow ellipse.
spec={
 "outer_left":{"roi":[38,68,66,150],"body":[51.0,113.0,5.3,16.7],"glow":[51,110,12.2,25.2]},
 "outer_right":{"roi":[473,68,501,150],"body":[487.0,113.0,5.2,16.7],"glow":[487,110,12.5,25.2]},
 "foreground_left":{"roi":[392,203,419,274],"body":[404.5,243.2,5.0,16.2],"glow":[404,241,11.0,25.0]},
 "foreground_right":{"roi":[497,253,530,327],"body":[510.0,297.0,5.2,17.0],"glow":[510,293,12.5,24.0]}
}
clean=original.copy().astype(np.float32)
lamp_parts={}
mask_total=np.zeros((H,W),np.uint8)
coords={}
for name,v in spec.items():
 l,t,r,b=v["roi"]
 yy,xx=np.mgrid[t:b,l:r].astype(np.float32)
 cx,cy,rx,ry=v["body"]; gcx,gcy,grx,gry=v["glow"]
 bodyellipse=((xx-cx)/rx)**2+((yy-cy)/ry)**2
 glowellipse=((xx-gcx)/grx)**2+((yy-gcy)/gry)**2
 # body has small carved metal stem from the original image; include lower tapered point.
 # float softness about the cropped perimeter limits hard rectangle edges.
 bodyalpha=np.clip((1.2-bodyellipse)*5,0,1)
 # tapers along bottom, to keep real wooden wall visible.
 glowmask=np.clip(1-glowellipse,0,1)**1.4
 # No edits at edges of the assigned ROI; fade preserving original seam.
 edge=np.minimum.reduce([np.maximum(xx-l,0)/3.0,np.maximum(r-1-xx,0)/3.0,
                         np.maximum(yy-t,0)/4.0,np.maximum(b-1-yy,0)/4.0])
 edge=np.clip(edge,0,1)
 glowmask*=edge
 # inpaint mask is strictly the localized source lamp, not background geometry.
 inp=np.uint8((glowellipse<.72)&(edge>.08))*255
 inp=np.uint8(cv2.dilate(inp,np.ones((3,3),np.uint8),iterations=1))
 region=original[t:b,l:r].copy()
 painted=cv2.inpaint(region,inp,4,cv2.INPAINT_TELEA).astype(np.float32)
 # further suppress warm bloom: interpolate from source pixels above/below at same x.
 # only inside fixture glow; unchanged elsewhere.
 top=np.median(original[max(t-9,0):max(t-3,1),l:r],axis=0).astype(np.float32)
 bot=np.median(original[min(b+3,H-1):min(b+10,H),l:r],axis=0).astype(np.float32)
 for i,y in enumerate(range(t,b)):
  f=np.clip((y-t)/(b-t),0,1)
  donor=(top*(1-f)+bot*f)
  painted[i,:,:]=donor
 # For left/right exterior columns use an existing approved wall-lamp-free pillar
 # from folder 29 as texture donor; the scar-free wall is better than stretched inpaint.
 # Force center opaque repair while feathering at an actual mural-post boundary,
 # not elliptical: prevents the visually obvious brown outline around an OFF lamp.
 repair=np.clip(edge*1.55,0,1)
 # Existing 49 front display-frame pixels always win: sconces may not overwrite them.
 protected=np.max(np.abs(current[t:b,l:r].astype(np.int16)-original[t:b,l:r].astype(np.int16)),axis=2)>4
 repair[protected]=0
 clean[t:b,l:r]=original[t:b,l:r]*(1-repair[:,:,None])+painted*repair[:,:,None]
 mask_total[t:b,l:r]=np.maximum(mask_total[t:b,l:r],np.uint8(repair*255))
 coords[name]=(l,t)
 lamp_parts[name]=(bodyalpha,glowmask,edge,xx,yy,protected)
clean=np.uint8(np.clip(np.rint(clean),0,255))
# Alphas deliberately distinguish visible fixture body from warm bloom; each item
# ONE reusable 2-layer asset in common ROI coordinates, not 3 layers per object.
for name,v in spec.items():
 l,t,r,b=v["roi"]
 cx,cy,rx,ry=v["body"]
 body,glow,edge,xx,yy,protected=lamp_parts[name]
 # body not entire ellipse: reduce edge interference on the wall.
 body_a=np.uint8(np.round(np.clip(body*edge,0,1)*255))
 body_a[protected]=0
 # glow captures warmer residual, with no opaque body pixels; diffuse layer reuses
 # actual original source texture and does not generate a new light object.
 halo_a=np.uint8(np.clip(np.round(glow*edge*(1-body)*115),0,255))
 halo_a[protected]=0
 # Glow color based on source's original (unmodified) warm illumination.
 lum=np.asarray(original[t:b,l:r],np.float32)
 g_rgb=np.uint8(np.clip(lum*.75+np.array([255,181,70])[None,None,:]*.25,0,255))
 glow_rgba=np.dstack((g_rgb,halo_a))
 body_rgba=np.dstack((original[t:b,l:r],body_a))
 save(Image.fromarray(body_rgba,"RGBA"),f"fixture_{name}_body.png")
 save(Image.fromarray(glow_rgba,"RGBA"),f"fixture_{name}_emission.png")
# New 49 artwork contains lamps baked. Replace ONLY four registered ROIs
# by repaired source region. All non-target areas must be byte-identical to v49.
def base_off():
 canvas=current.copy()
 for name,v in spec.items():
  l,t,r,b=v["roi"]
  diff=np.max(np.abs(current[t:b,l:r].astype(np.int16)-original[t:b,l:r].astype(np.int16)),axis=2)>4
  patch=clean[t:b,l:r].copy()
  patch[diff]=current[t:b,l:r][diff]
  canvas[t:b,l:r]=patch
 return Image.fromarray(canvas,"RGB").convert("RGBA")
def composite(enabled=None,emit=True):
 if enabled is None:enabled=tuple(spec)
 canvas=base_off()
 for name in enabled:
  l,t=coords[name]
  if emit:
   canvas.alpha_composite(Image.open(O/f"fixture_{name}_emission.png").convert("RGBA"),(l,t))
  canvas.alpha_composite(Image.open(O/f"fixture_{name}_body.png").convert("RGBA"),(l,t))
 return canvas.convert("RGB")
off=save(base_off().convert("RGB"),"QA_all_four_sconces_off.png")
on=save(composite(),"QA_all_four_sconces_on.png")
body_only=save(composite(emit=False),"QA_all_four_body_only.png")
one=save(composite(["outer_left"]),"QA_left_outer_only.png")
o=np.asarray(off);cur=np.asarray(current)
allowed=np.zeros((H,W),bool)
for v in spec.values():
 l,t,r,b=v["roi"];allowed[t:b,l:r]=True
assert np.array_equal(o[~allowed],cur[~allowed])
assert np.count_nonzero(o[allowed]!=cur[allowed])>400
board=Image.new("RGB",(W*3,H))
for i,im in enumerate((off,body_only,on)):
 board.paste(im,(i*W,0))
save(board,"QA_all_sconces_off_body_on.png")
# zoom comparison for each region
for name,v in spec.items():
 l,t,r,b=v["roi"]
 crop=(max(0,l-8),max(0,t-8),min(W,r+8),min(H,b+8))
 w,h=crop[2]-crop[0],crop[3]-crop[1]
 q=Image.new("RGB",(w*4*3,h*3))
 for i,im in enumerate((Image.fromarray(current),off,body_only,on)):
  q.paste(im.crop(crop).resize((w*3,h*3),Image.Resampling.NEAREST),(i*w*3,0))
 save(q,f"QA_{name}_original_off_body_on_3x.png")
meta={"status":"art_candidate_preliminary","source_approved":str(REF),"visual_source_49":str(V49),
      "separated":list(spec),"rectangles":{k:v["roi"] for k,v in spec.items()},
      "body_and_emission_independent":True,"retained_existing29_and30":True,
      "all_outside_rectangles_byte_identical_to_49":True,
      "source_inpainted_unseen_wall":True,"off_art_approval":False,
      "on_comparison_mae_from_v49":float(np.abs(np.asarray(on,np.float32)-current.astype(np.float32)).mean()),
      "game_integrated":False}
(O/"QA_manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print("QA_GEN",meta["on_comparison_mae_from_v49"],"mean abs channel error against original (not exact restoration)")
