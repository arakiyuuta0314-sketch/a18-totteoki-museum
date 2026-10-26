# -*- coding: utf-8 -*-
"""A18 plain architectural reconstruction candidate v06.
Uses only existing exact 546x483 licensed/approved raster materials from 55.
Replaces remnants by rebuilding wall surface and upper ceiling material, not local inpaint.
No image generation, no new characters, no gameplay modification.
"""
from pathlib import Path
import cv2,numpy as np,json,hashlib,shutil
from PIL import Image
ROOT=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
D55=next(p for p in ROOT.iterdir() if p.name.startswith('55_'))
HERE=Path(__file__).resolve().parent
OUT=HERE/'entrance-plain-master-v06-study'
OUT.mkdir(exist_ok=True)
old=np.asarray(Image.open(D55/'candidate_off.png').convert('RGB'))
assert old.shape==(483,546,3)
W,H=546,483
base=old.copy()
reconstruction_mask=np.zeros((H,W),np.uint8)
# Rebuild entire TWO ceiling-fascia surfaces using wooden pixels from the
# source wood cornice itself. Remove baked spotlights as part of new material.
# Model a horizontal plank, retaining its real horizontal color banding.
for x0,x1 in [(30,208),(359,516)]:
 source=old[0:31,x0:x1].copy()
 # For each row robust horizontal median suppresses vertical glow residue.
 # Smoothed ORIGINAL image grain is retained in a controlled amount.
 med=cv2.medianBlur(source,5)
 texture=cv2.GaussianBlur(med,(0,0),.75)
 for yy in range(0,29):
  px=source[yy].astype(np.float32)
  low=cv2.GaussianBlur(source[yy:yy+1],(0,0),16)[0].astype(np.float32)
  # large undamaged regions show wood color; avoid changing underside trim.
  idx=np.arange(x1-x0)
  # Reference medians across the entire beam account for clean wood shade.
  avg=np.median(source[yy],axis=0).astype(np.float32)
  smooth=cv2.GaussianBlur(source[yy:yy+1],(0,0),14)[0].astype(np.float32)
  img=np.clip(avg*.92+smooth*.08 + np.clip(px-smooth,-2.0,2.0)*.45,0,255)
  edge=np.minimum(idx,(x1-x0-1)-idx)
  a=np.clip(edge/5.,0,1)
  ay=np.clip((29-yy)/4.,0,1)
  alpha=(a*ay*.92)[:,None]
  result=np.uint8(np.rint(px*(1-alpha)+img*alpha))
  changed=np.any(result!=old[yy,x0:x1],axis=1)
  reconstruction_mask[yy,x0:x1][changed]=255
  base[yy,x0:x1]=result
# Replace both stained large green rear exhibition backing surfaces by a
# continuous painterly dark-green wall material. Never touch the off-white
# photo paper, carved wooden rim, or architecture outside these two fields.
rng=np.random.default_rng(20261026)
noisetile=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),.85)
for x0,x1,slot0,slot1 in [
 (31,210,39,196), (357,516,370,510)
]:
 for y in range(39,167):
  for x in range(x0,x1):
   # Distinguish still-photographic green from paper/corner wood.
   orig=old[y,x]
   isgreen=(int(orig[0])<99 and int(orig[1])<113 and int(orig[2])<91)
   # x~40-195 and 370-510 are old empty mattes, deliberately preserved.
   if not isgreen: continue
   # Keep the original photo-paper edge and its 3px retaining rim.
   if (x0<100 and 36<=x-x0<=168 and 58<=y<=149) or (x0>100 and 10<=x-x0<=155 and 58<=y<=149): continue
   if y>=164:continue
   xx=(x-x0)/max(1,x1-x0-1)
   yy=(y-39)/125.
   # Warm-lit museum green, with realistic source-based dark-patina pattern.
   frame_depth=np.clip(np.minimum(xx,1-xx)*10,0,1)
   diffuse=-5*yy+3.5*frame_depth+1.5*np.sin(xx*np.pi)
   # Real image palette sampled from existing unlit wall at x=36,60,360.
   col=np.array([17.8,35.1,22.0])+diffuse*np.array([.7,.82,.65])
   grain=noisetile[y,x]*np.array([1.55,2.15,1.45])
   q=np.uint8(np.clip(np.rint(col+grain),0,255))
   # Prevent sharp edge against retained photo trim and carved frame
   # by ramping in only among green-neighbourhood pixels.
   near=(y>=42 and y<=160 and x>=x0+3 and x<=x1-4)
   fac=.94 if near else .75
   b=np.uint8(np.clip(np.rint(orig*(1-fac)+q*fac),0,255))
   if np.any(b!=orig):reconstruction_mask[y,x]=255
   base[y,x]=b
# Recover the parts hidden by the optical repair in the 55 study:
# only top 6 pix at far corners (no geometry).
for l,r,donor in [(0,6,(14,20)),(540,546,(524,532))]:
 for y in range(0,9):
  sample=np.median(old[y,donor[0]:donor[1]],axis=0)
  for x in range(l,r):
   alpha=np.clip((9-y)/3,0,1)*(.87 if x in (0,1,544,545) else .56)
   v=np.uint8(np.clip(np.rint(old[y,x]*(1-alpha)+sample*alpha),0,255))
   if np.any(base[y,x]!=v):reconstruction_mask[y,x]=255
   base[y,x]=v
# Strict immutability for foreground and game interaction-friendly regions.
assert np.array_equal(old[212:],base[212:]),"Foreground/floor unexpectedly changed"
assert np.array_equal(old[43:211,213:351],base[43:211,213:351]),"Door unexpectedly changed"
# The half-open green rear wall is the subject of this phase, not photo frame.
Image.fromarray(base).save(OUT/'entrance_OFF.png')
Image.fromarray(reconstruction_mask).save(OUT/'QA_rebuilt_material_mask.png')
Image.fromarray(old).save(OUT/'reference_v05_OFF.png')
board=Image.new('RGB',(W*2,H))
board.paste(Image.fromarray(old),(0,0));board.paste(Image.fromarray(base),(W,0))
board.save(OUT/'QA_before_after.jpg',quality=93)
for name,rect in {
 'left_back':(0,0,219,214),'right_back':(337,0,546,214),
 'ceiling':(0,0,546,44),
 'left_frame':(27,31,215,175),'right_frame':(351,31,520,175)
 }.items():
 x0,y0,x1,y1=rect
 w=(x1-x0)*2;h=(y1-y0)*2
 p=Image.new('RGB',(w*2,h))
 p.paste(Image.fromarray(old).crop(rect).resize((w,h),Image.Resampling.NEAREST),(0,0))
 p.paste(Image.fromarray(base).crop(rect).resize((w,h),Image.Resampling.NEAREST),(w,0))
 p.save(OUT/('QA_'+name+'_before_after.png'))
meta={'source':'55 v05 unapproved, reference exact 546x483',
 'status':'technical_candidate_art_review_pending',
 'base_only':True,'no_lamps':True,'new_image_generation':False,
 'canvas':[W,H],
 'changed_pixels':int(np.any(old!=base,axis=2).sum()),
 'changed_outside_reconstruction_mask':int(np.sum(np.any(old!=base,axis=2)&(reconstruction_mask==0))),
 'building_above_y212_recomposed':True,
 'floor_door_characters_pixel_identical':True,
 'Lv1_decided':False,'game_unchanged':True,
 'warnings':'Green surface is reconstructed with source-sampled palette; not restored original under fixtures. Need visual art approval. Wooden frame ON not part of v06 base.'}
(OUT/'QA_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
print('BASE_V06_CREATED',meta['changed_pixels'],flush=True)
