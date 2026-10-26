# -*- coding:utf-8 -*-
"""A18 v03: source-based wall fixture residue restoration and photo-frame material finish."""
from pathlib import Path
from PIL import Image
import numpy as np,cv2,json,hashlib,shutil
HERE=Path(__file__).resolve().parent
SRC=HERE/"entrance-wood-onoff-v02-20261026"
OUT=HERE/"entrance-art-polish-v03-20261026";OUT.mkdir(exist_ok=True)
W,H=546,483
def pic(path,mode="RGBA"):return Image.open(path).convert(mode)
def saved(im,name):
 p=OUT/name
 (im if isinstance(im,Image.Image) else Image.fromarray(im)).save(p,optimize=True)
 return p
def hashfile(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
before=np.asarray(pic(SRC/"entrance_OFF.png","RGB")).copy()
base=before.copy()
patches=np.zeros((H,W),np.uint8)
# Two bright edge-most light remnants were outside the earlier 8-unit
# ceiling-lamp atlas. Copy neighboring exposed ceiling pixels, only y=0..10.
for left in (True,False):
 xvals=range(0,10) if left else range(W-10,W)
 donor=range(14,23) if left else range(W-23,W-14)
 for y in range(0,12):
  clean=np.median(before[y,list(donor)],axis=0)
  for x in xvals:
   dx=(10-x) if left else (x-(W-11))
   boundary=np.clip(dx/8.0,0,1)
   taper=np.clip((12-y)/4.0,0,1)
   strength=boundary*taper*.98
   v=np.uint8(np.clip(np.rint(before[y,x]*(1-strength)+clean*strength),0,255))
   if not np.array_equal(v,base[y,x]):patches[y,x]=255
   base[y,x]=v
# Restore warm architectural material without turning all room lights 'off':
# edit only artifacts left after actual fixtures were separately removed.
# Existing wood cornice y25-36 and green exhibition panel y39-61.
for cx in (138,414):
 # x-intervals are limited to formerly mounted rear exhibition bulbs.
 # Use untouched wood pixels from the same row on both sides of the fixture.
 wood_box=(cx-9,cx+10,26,37)
 for y in range(wood_box[2],wood_box[3]):
  left=np.median(before[y,cx-24:cx-15],axis=0)
  right=np.median(before[y,cx+16:cx+25],axis=0)
  for x in range(wood_box[0],wood_box[1]):
   f=np.clip((x-wood_box[0])/(wood_box[1]-wood_box[0]),0,1)
   proposed=left*(1-f)+right*f
   # Feather away from the relevant mounting point and protect horizontal trim.
   ex=np.clip((min(x-wood_box[0],wood_box[1]-1-x)+1)/3,0,1)
   ey=np.clip((min(y-wood_box[2],wood_box[3]-1-y)+1)/3,0,1)
   a=.94*ex*ey
   new=np.uint8(np.clip(np.rint(before[y,x]*(1-a)+proposed*a),0,255))
   if not np.array_equal(new,before[y,x]):patches[y,x]=255
   base[y,x]=new
 # From left/right original green wall, interpolate existing green tones per
 # horizontal scanline. Blend across a broad soft mask to avoid v02's oval stains.
 x0,x1=cx-26,cx+27
 for y in range(40,60):
  L=np.median(before[y,cx-39:cx-29],axis=0)
  R=np.median(before[y,cx+30:cx+40],axis=0)
  for x in range(x0,x1):
   t=np.clip((x-x0)/(x1-x0-1),0,1)
   proposed=L*(1-t)+R*t
   border=min((x-x0+1)/(7.),(x1-x)/(7.),(y-40+1)/5.,(60-y)/5.)
   strength=np.clip(border,0,1)*.96
   new=np.uint8(np.clip(np.rint(before[y,x]*(1-strength)+proposed*strength),0,255))
   if not np.array_equal(new,before[y,x]):patches[y,x]=255
   base[y,x]=new
# right-front exhibition lamp location: previous v02 used oriented source pixels
# to remove bulb; finish faint luminous specks ONLY in same sloping dark green plane.
# Keep this intentionally conservative to avoid changes to wooden handrail.
for y in range(197,205):
 for x in range(447,471):
  # source material from nearby unaltered dark-green portion at the same y
  p=np.median(before[y,486:492],axis=0)
  q=np.median(before[y,425:432],axis=0)
  f=(x-447)/24
  proposed=q*(1-f)+p*f
  edge=min((x-447+1)/6,(471-x)/6,(y-197+1)/3,(205-y)/3)
  strength=np.clip(edge,0,1)*.38
  new=np.uint8(np.clip(np.rint(base[y,x]*(1-strength)+proposed*strength),0,255))
  if not np.array_equal(new,base[y,x]):patches[y,x]=255
  base[y,x]=new
# Floor, door and characters are completely untouched.
for key,(x0,y0,x1,y1) in {"floor":(160,320,388,483),"door":(242,58,328,195),
                          "characters":(110,319,310,378)}.items():
 assert np.array_equal(base[y0:y1,x0:x1],before[y0:y1,x0:x1]),key
saved(base,"entrance_OFF.png")
saved(patches,"QA_lighting_residue_restoration_mask.png")
layers={k:pic(SRC/("layer_"+k+".png")) for k in ("rear_left","rear_right","right_front_v07")}
def enhanced(layer,mode):
 arr=np.asarray(layer).copy()
 a=arr[:,:,3]
 inside=a>6
 raw=arr[:,:,:3].astype(np.float32)
 # Enhance *existing* woodgrain from original sprite, never invent texture.
 blur=cv2.GaussianBlur(raw,(0,0),1.15)
 detail=raw-blur
 params={
  "subtle":(15,1.08,8,.18),
  "balanced":(24,1.13,12,.28),
  "defined":(28,1.17,16,.35)}
 warmth,contrast,bevel,shadow=params[mode]
 # Brighten brown wood, recover natural warm mids, preserve deepest grooves.
 mean=np.array([111,65,38],np.float32)
 t=(raw-mean)*contrast+mean+np.array([warmth,warmth*.66,warmth*.40],np.float32)
 t+=detail*.28
 # raised bevel from actual material silhouette incl. inner rim; top and left
 # edges brighten while bottom / right edges deepen.
 norm=cv2.GaussianBlur((a/255).astype(np.float32),(0,0),.7)
 gx=cv2.Sobel(norm,cv2.CV_32F,1,0,ksize=3)
 gy=cv2.Sobel(norm,cv2.CV_32F,0,1,ksize=3)
 rim=np.clip((gx+gy)*.55,-1,1)
 t+=rim[:,:,None]*np.array([bevel,bevel*.73,bevel*.46],np.float32)[None,None,:]
 # Never change transparent alpha/window registration.
 arr[:,:,:3]=np.uint8(np.clip(np.rint(t),0,255))
 arr[:,:,3]=a
 return Image.fromarray(arr,"RGBA"),shadow
def render(mode):
 c=Image.fromarray(base,"RGB").convert("RGBA")
 for nm,l in layers.items():
  frame,sh=enhanced(l,mode)
  alpha=np.asarray(frame.getchannel("A"))
  binary=np.uint8(alpha>0)*255
  # external silhouette contact shadow ONLY: registered photo area excluded.
  shapes,_=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  solid=np.zeros((H,W),np.uint8)
  cv2.drawContours(solid,shapes,-1,255,cv2.FILLED)
  outer=cv2.dilate(solid,np.ones((7,7),np.uint8),iterations=1)
  blur=cv2.GaussianBlur(outer,(0,0),1.2)
  shadow=np.maximum(0,blur.astype(np.float32)-solid.astype(np.float32))
  shadow=np.uint8(np.clip(np.rint(shadow*sh),0,255))
  # Crop soft halo to the measured 4px outer silhouette region.
  shadow[cv2.dilate(solid,np.ones((9,9),np.uint8))==0]=0
  rgba=np.zeros((H,W,4),np.uint8)
  rgba[:,:,:3]=[25,12,5]
  rgba[:,:,3]=shadow
  c.alpha_composite(Image.fromarray(rgba,"RGBA"))
  c.alpha_composite(frame)
 return c.convert("RGB")
qa=Image.new("RGB",(W*4,H))
qa.paste(pic(SRC/"entrance_ON.png","RGB"),(0,0))
for i,st in enumerate(("subtle","balanced","defined"),start=1):
 r=render(st);saved(r,"QA_wood_style_"+st+".png");qa.paste(r,(W*i,0))
saved(qa,"QA_frame_styling_four_options.png")
# Selected: defined; strong enough at smartphone size, no new geometry.
wood=render("defined")
saved(wood,"entrance_ON.png")
for nm,frame in layers.items():
 f,_=enhanced(frame,"defined");saved(f,"frame_"+nm+"_wood_v03.png")
# Important: ON's differences are limited to 3-frame original silhouette plus
# 3px soft contact shadows. Underlying OFF remains byte-identical elsewhere.
alpha_all=np.zeros((H,W),np.uint8)
for layer in layers.values():
 q=np.uint8(np.asarray(layer.getchannel("A"))>0)*255
 contours,_=cv2.findContours(q,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 solid=np.zeros_like(q);cv2.drawContours(solid,contours,-1,255,cv2.FILLED)
 alpha_all=cv2.max(alpha_all,cv2.dilate(solid,np.ones((9,9),np.uint8)))
changed=np.any(np.asarray(wood)!=base,axis=2)
bad=changed&(alpha_all==0)
if np.any(bad):
 ys,xs=np.where(bad)
 print('QA_OUTSIDE_MASK',int(bad.sum()),'bbox',[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'samples',list(zip(xs[:12].tolist(),ys[:12].tolist())),flush=True)
assert not np.any(bad),"pixel changed outside managed frame+3px shadow area"
assert changed.sum()>10000
saved(alpha_all,"QA_allowed_wood_and_shadow_mask.png")
saved((changed*255).astype(np.uint8),"QA_actual_wood_change_mask.png")
contact=Image.new("RGB",(W*2,H))
contact.paste(Image.fromarray(base),(0,0));contact.paste(wood,(W,0))
saved(contact,"QA_OFF_ON_side_by_side.png")
# Scaled QA crops
for nm,box in {"rear_left":(68,40,210,170),"rear_right":(355,40,478,170),
               "right_front":(400,169,516,360),
               "rear_lighting":(98,18,183,79),
               "front_lighting":(407,165,501,224)}.items():
 x0,y0,x1,y1=box;w=(x1-x0)*3;h=(y1-y0)*3
 sheet=Image.new("RGB",(w*2,h))
 for i,image in enumerate((Image.fromarray(base),wood)):
  sheet.paste(image.crop(box).resize((w,h),Image.Resampling.NEAREST),(i*w,0))
 saved(sheet,"QA_zoom_"+nm+".png")
for fn in ("butler-front-00.png","curator-front-00.png"):
 shutil.copy2(SRC/fn,OUT/fn);assert hashfile(SRC/fn)==hashfile(OUT/fn)
manifest={
"version":"v03","canvas":[W,H],"lv1_decided":False,"art_approved":False,
"source":"v02 17a8865","method":"local source-pixel donor blending; original sprite wooden detail contrast + bevel; image generation unused",
"prior_source_hashes":{n:hashfile(SRC/n) for n in ("entrance_OFF.png","entrance_ON.png","layer_rear_left.png","layer_rear_right.png","layer_right_front_v07.png")},
"source_sprite_hashes":{n:hashfile(OUT/n) for n in ("butler-front-00.png","curator-front-00.png")},
"lighting_repair_changed_pixels":int((patches>0).sum()),
"wood_ON_changed_pixels":int(changed.sum()),
"outside_managed_frame_plus_shadow_changed_pixels":int((changed&(alpha_all==0)).sum()),
"base_outside_repair_changed_pixels":int((np.any(base!=before,axis=2)&(patches==0)).sum()),
"caveat":"Unseen fixture backgrounds remain source-neighbor estimates; art approval pending."}
(OUT/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
print("V03_BUILD_PASS",json.dumps(manifest,ensure_ascii=False)[:1800])
