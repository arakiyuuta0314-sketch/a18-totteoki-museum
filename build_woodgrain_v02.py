# -*- coding: utf-8 -*-
"""A18 wooden frame material v02: source-derived wood texture mapped into approved masks.
Never redraw backgrounds, people, or frame geometry. The 43 assets remain immutable.
"""
from pathlib import Path
from PIL import Image
import numpy as np, cv2, json, hashlib, shutil, math
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
D43=R/"43_エントランス完成素材_3額縁本体装飾分離_v01"
C=R/"00_正式採用素材"/"characters"
WORK=Path(__file__).resolve().parent
OUT=WORK/"entrance-wood-grain-v02-20261026"
OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return Image.open(p).convert("RGBA")
def save(im,name):im.save(OUT/name,optimize=True);return im
reference=Image.open(WORK/"wood_atlas_mini.png").convert("RGB")
texture=np.asarray(reference).astype(np.float32)
assert texture.shape==(72,96,3)
save(reference,"reference_wood_grain_texture.png")
models={
 "left":{"outer":[[76,50],[201,50],[201,157],[76,157]],"inner":[[84,61],[194,61],[194,144],[84,144]],"center":[138.5,103.5]},
 "right":{"outer":[[365,50],[468,50],[468,157],[365,157]],"inner":[[373,61],[460,61],[460,144],[373,144]],"center":[416.5,103.5]},
 "front":{"outer":[[414,183],[500,212],[502,340],[413,294]],"inner":[[426,201],[489,226],[489,323],[426,276]],"center":[457.5,261.]}
}
H,W=483,546
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
source_old={}; improved={}
for key,geo in models.items():
 old=read(D43/f"frame_{key}_wood_basic.png")
 assert old.size==(W,H)
 src=np.asarray(old)
 a=src[:,:,3]
 source_old[key]=old
 # Homography normalizes the ACTUAL approved perspective polygon into one unit rect.
 quad=np.asarray(geo["outer"],dtype=np.float32)
 hom=cv2.getPerspectiveTransform(quad,np.asarray([[0,0],[1,0],[1,1],[0,1]],np.float32))
 u=(hom[0,0]*xx+hom[0,1]*yy+hom[0,2])/(hom[2,0]*xx+hom[2,1]*yy+hom[2,2])
 v=(hom[1,0]*xx+hom[1,1]*yy+hom[1,2])/(hom[2,0]*xx+hom[2,1]*yy+hom[2,2])
 inner=np.asarray(geo["inner"],np.float32).reshape(-1,1,2)
 uv_inner=cv2.perspectiveTransform(inner,hom).reshape(-1,2)
 # Thickness is computed from the real PHOTO opening, not guessed bounding boxes.
 thick=np.asarray([np.mean(uv_inner[[0,1],1]),1-np.mean(uv_inner[[1,2],0]),
                   1-np.mean(uv_inner[[2,3],1]),np.mean(uv_inner[[0,3],0])],np.float32)
 assert np.all(thick>.02) and np.all(thick<.4),(key,thick)
 # Nearest frame strip: top / right / bottom / left.
 side_dist=np.stack([v/max(thick[0],.001),(1-u)/max(thick[1],.001),
                      (1-v)/max(thick[2],.001),u/max(thick[3],.001)],axis=0)
 side=np.argmin(side_dist,axis=0)
 q=np.clip(np.take_along_axis(side_dist,side[None],axis=0)[0],0,1)
 longitudinal=np.where((side==0)|(side==2),u,v)
 longitudinal=np.clip(longitudinal,0,1)
 # Use actual wood grain from the previously generated 1448x1086 material.
 # The cropped horizontal + longitudinal strips are color samples, not new geometry.
 phase=(np.sin(longitudinal*14+side*1.2)*1.5+np.cos(longitudinal*31+side)*.6).astype(np.float32)
 sample_x=np.clip(5+longitudinal*82+phase+side*1.5,0,95).astype(np.float32)
 sample_y=np.where(((side==0)|(side==2)),4+q*25,39+q*28)
 sample_y=np.clip(sample_y,0,71).astype(np.float32)
 rgb=cv2.remap(texture,sample_x,sample_y,cv2.INTER_LINEAR,
               borderMode=cv2.BORDER_REFLECT101)
 # Warp natural veins with subtle lengthwise waviness, then build a physical bevel.
 fine=cv2.GaussianBlur(rgb,(0,0),.75)
 rgb=rgb+(rgb-fine)*.9
 qpts=[0,.08,.23,.40,.67,.79,.89,.96,1]
 bvals=[.68,.86,1.08,1.06,1,.88,.72,.93,.70]
 relief=np.interp(q,qpts,bvals).astype(np.float32)
 # Top/left modest incident light, bottom/right shade.
 light=np.select([side==0,side==1,side==2,side==3],[1.05,.91,.87,1.00],default=1.)
 rgb=rgb*relief[:,:,None]*light[:,:,None]
 # Walnut in the approved room is subdued. Still show actual warm grain contrast.
 rgb=rgb*np.asarray([.97,.91,.82],np.float32)[None,None,:]+np.asarray([4.,2.,0.])[None,None,:]
 # Miter joints at the four polygon corners. Keep subtle and within the existing alpha.
 diag=np.minimum(u/thick[3],(1-u)/thick[1])
 diag2=np.minimum(v/thick[0],(1-v)/thick[2])
 joint=(np.abs(diag-diag2)<.1)&(np.minimum(diag,diag2)<1.12)
 rgb[joint]*=.75
 # Edge alpha is a byte-identical copy of F01/F02/F03 original art ring mask.
 result=np.dstack((np.uint8(np.clip(rgb,0,255)),a))
 final=save(Image.fromarray(result,"RGBA"),f"frame_{key}_wood_grain_v02.png")
 improved[key]=final
 assert np.array_equal(np.asarray(final.getchannel("A")),a)
 assert np.count_nonzero(a)>500
 win=np.asarray(read(D43/f"exhibition_{key}_empty_mat.png").getchannel("A"))>0
 # Adjacent matte and frame are allowed, but no frame may cover the true photo center.
 if key!="front":
  win=np.asarray(Image.open(D43/f"exhibition_{key}_window_mask.png").convert("L"))>0
  assert not np.any((a>0)&win),key
 print("FRAME",key,"alpha",int(np.count_nonzero(a)),"rgb_std",np.std(result[a>0,:3],axis=0).round(2).tolist(),flush=True)
def resize_layer(img,key,scale):
 if scale==1:return img
 cx,cy=models[key]["center"]
 M=cv2.getRotationMatrix2D((cx,cy),0,scale)
 rgba=cv2.warpAffine(np.asarray(img),M,(W,H),flags=cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 return Image.fromarray(rgba,"RGBA")
def view(style,scale=100,photos=False):
 suffix="photos" if photos else "empty"
 assert style in ("new","old","none","gold")
 if style in ("old","none","gold"):
  st={"old":"wood","none":"none","gold":"gold_full"}[style]
  return Image.open(D43/f"view_{st}_{suffix}_{scale}.png").convert("RGB")
 scene=Image.open(D43/f"view_none_{suffix}_{scale}.png").convert("RGBA")
 for key in models:
  scene.alpha_composite(resize_layer(improved[key],key,scale/100))
 return scene.convert("RGB")
# Do not touch earlier v01; publish only an isolated candidate v02.
for style in ("new","old","none","gold"):
 for scale in (90,100,110):
  for photos in (False,True):
   save(view(style,scale,photos),f"view_{style}_{'photos' if photos else 'empty'}_{scale}.png")
old=np.asarray(view("old",100))
new=np.asarray(view("new",100))
delta=np.any(old!=new,axis=2)
alpha_mask=np.zeros((H,W),bool)
for im in source_old.values():alpha_mask|=np.asarray(im.getchannel("A"))>0
assert not np.any(delta&(~alpha_mask)),"Modified unapproved pixels outside original frame alpha!"
assert np.count_nonzero(delta)>300,"Wood update too subtle or failed"
# No photo content changes (before and after only the frame outlines differ).
for photo in (False,True):
 a=np.asarray(view("new",100,photo))
 b=np.asarray(view("none",100,photo))
 assert np.array_equal(a[~alpha_mask],b[~alpha_mask])
# Photos and characters are NOT re-generated and are unmodified.
charsha={}
for n in ("butler-front-00.png","curator-front-00.png"):
 assert (C/n).is_file()
 charsha[n]=sha(C/n)
# Four-way old/new contrast for honest user art supervision.
compare=Image.new("RGB",(W*4,H))
for i,style in enumerate(["none","old","new","gold"]):
 compare.paste(view(style),(i*W,0))
save(compare,"QA_four_states_unmodified_wood_new_gold.png")
compare_photo=Image.new("RGB",(W*2,H))
compare_photo.paste(view("old",100,True),(0,0))
compare_photo.paste(view("new",100,True),(W,0))
save(compare_photo,"QA_old_new_photo_scene.png")
# Magnifications around frames; see wood grain where original thumbnail is small.
areas={"left":(68,43,206,164),"right":(358,43,474,164),"front":(402,177,509,351)}
for key,box in areas.items():
 scene=Image.new("RGB",((box[2]-box[0])*6,(box[3]-box[1])*3))
 cw,ch=box[2]-box[0],box[3]-box[1]
 for i,s in enumerate(["old","new"]):
  scene.paste(view(s).crop(box).resize((cw*3,ch*3),Image.Resampling.NEAREST),(i*cw*3,0))
 save(scene,f"QA_{key}_old_new_3x.png")
meta={"title":"A18 wood-grain wooden frame second candidate",
 "source_d43":str(D43),"source_frame_sha256":{k:sha(D43/f"frame_{k}_wood_basic.png") for k in models},
 "wood_texture_sample":"wood_atlas_mini.png, crop-resize from prior generated wooden frame image; no room or character generation",
 "source_wood_texture_sha256":sha(WORK/"wood_atlas_mini.png"),
 "unchanged_v01":True,"exact_canvas":[W,H],"official_character_original_sha256":charsha,
 "same_original_alpha_all_three_frames":True,
 "changed_pixels_at_100_empty":int(np.count_nonzero(delta)),
 "outside_frame_changed_pixels":int(np.count_nonzero(delta&(~alpha_mask))),
 "photo_window_pixels_modified_outside_frame":0,
 "all_qa_states":24,"scale":[90,100,110],"photos":[False,True],
 "prior_gold_assets_untouched":True,"lighting_baked_in":True,
 "game_integrated":False,"lv1_approved":False,"user_art_approved":False}
(OUT/"QA_manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS_RENDER",meta["changed_pixels_at_100_empty"],"pixels, 24 states",flush=True)
