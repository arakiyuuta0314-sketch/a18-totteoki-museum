# -*- coding: utf-8 -*-
"""A18 entrance right-front exhibition: unify ALL variants under ONE H.
Sources exactly 43/44/47. The established gold silhouette outer 4 points are target truth.
Source images, sprites, base architecture and main branch remain untouched.
"""
from pathlib import Path
from PIL import Image
import cv2, json, numpy as np, hashlib, math
from frame_projection_v06 import compute_H,derived_inner,warp_rgba,warp_mask,projected_photo,fit_photo
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
D43=R/"43_エントランス完成素材_3額縁本体装飾分離_v01"
D44=R/"44_エントランス完成素材_木製額縁木目改善_v02"
D47=R/"47_エントランス完成素材_右手前展示枠共通変形化_v05"
CHARS=R/"00_正式採用素材"/"characters"
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"entrance-canonical-single-H-v06-20261026"
OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def img(p):return Image.open(p).convert("RGBA")
def save(im,n):im.save(OUT/n,optimize=True);return im
W,Hh=546,483
source_geometry=json.loads((D47/"shared_display_geometry.json").read_text(encoding="utf-8"))
so=np.float32(source_geometry["canonical_outer_quad"])
si=np.float32(source_geometry["canonical_inner_quad"])
dest_outer=np.float32(source_geometry["right_front"]["outer_quad"])
M=compute_H(so,dest_outer)
dest_inner=derived_inner(M,si)
old_inner=np.float32(source_geometry["right_front"]["inner_quad"])
old_inner_displacement=np.linalg.norm(dest_inner-old_inner,axis=1)
source_rect_mask=img(D43/"exhibition_left_window_mask.png").getchannel("A") if False else Image.open(D43/"exhibition_left_window_mask.png").convert("L")
# Geometry uses source outer points alone, target inner is ALWAYS derived, not a second input.
geometry={"version":"A18_CANONICAL_H_SINGLE_PLANE_v06","canvas":[W,Hh],
"source_outer":so.tolist(),"source_inner":si.tolist(),
"target_right_front_outer":dest_outer.tolist(),"derived_inner":np.round(dest_inner,5).tolist(),
"source_to_target_H":M.tolist(),
"old_v05_inner_for_diagnostics_only":old_inner.tolist(),
"old_v05_inner_displacement_px":np.round(old_inner_displacement,4).tolist(),
"canonical_photo_rect":[84,61,194,144],
"quality_contract":"ONE H applied to skin, ornaments, mask, mat, sample and arbitrary user photo",
"reverse_angle_use":"same image and derived points from a different target outer quad; no dedicated art creation"}
(OUT/"single_H_geometry.json").write_text(json.dumps(geometry,ensure_ascii=False,indent=2),encoding="utf-8")
# Source original parts. Both styles have exactly the same canonical alpha.
canonical={k:img(f) for k,f in {
"wood":D44/"frame_left_wood_grain_v02.png",
"gold":D43/"frame_left_original_gold.png",
"gold_body":D43/"frame_left_gold_body.png",
"gold_ornaments":D43/"frame_left_gold_ornaments.png",
"empty":D43/"exhibition_left_empty_mat.png",
"photos":D43/"exhibition_left_photo_sample.png"}.items()}
for k,v in canonical.items():save(v,f"canonical_{k}.png")
def alpha(im):return np.asarray(im.getchannel("A"))
assert np.array_equal(alpha(canonical["wood"]),alpha(canonical["gold"]))
src_mask_array=np.asarray(source_rect_mask)
assert int(np.count_nonzero(src_mask_array))==110*83
window=save(warp_mask(source_rect_mask,M),"right_front_shared_window_mask.png")
wm=alpha(window)>0 if False else np.asarray(window)>0
assert np.count_nonzero(wm)>1000
layers={}
for k in ("wood","gold","gold_body","gold_ornaments"):
 p=np.asarray(warp_rgba(canonical[k],M)).copy()
 # Absolute priority: the PHOTO window mask is authoritative for all variants.
 p[wm]=0
 layers[k]=save(Image.fromarray(p,"RGBA"),f"right_front_frame_{k}.png")
 assert not np.any((alpha(layers[k])>0)&wm),k
assert np.array_equal(alpha(layers["wood"]),alpha(layers["gold"]))
# Store source matte RGB without authoring a new background. Canonical 43 matte is the
# same front-plane artwork for every frame variant.
original_matte=canonical["empty"].crop((84,61,194,144)).convert("RGB")
oldphoto=canonical["photos"].crop((84,61,194,144)).convert("RGB")
def projected(source):
 return projected_photo(source,M,window)
content={"empty":original_matte,"photos":oldphoto}
# registration QA with visibly different colors in all four corners; no user data.
checks=np.zeros((83,110,3),np.uint8)
checks[:]=[220,191,158]
cv2.rectangle(checks,(0,0),(16,16),(220,55,50),-1)
cv2.rectangle(checks,(93,0),(109,16),(49,184,68),-1)
cv2.rectangle(checks,(0,66),(16,82),(43,74,222),-1)
cv2.rectangle(checks,(93,66),(109,82),(224,210,45),-1)
cv2.line(checks,(0,0),(109,82),(86,53,34),2)
content["registration"]=Image.fromarray(checks,"RGB")
for k,v in content.items():
 save(v,f"canonical_content_{k}.png")
 projected_layer=save(projected(v),f"right_front_content_{k}.png")
 assert np.array_equal(alpha(projected_layer)>0,wm)
# Arbitrary registered picture input contract using exactly same H, exact same mask.
photosizes=[(800,1200),(1920,1080),(500,500),(83,110),(1280,720)]
for i,(w,h) in enumerate(photosizes):
 test=Image.new("RGB",(w,h),(90+20*i,143,99))
 sample=projected(test)
 assert np.array_equal(alpha(sample)>0,wm)
 if i==0: save(sample,"QA_portrait_input_800x1200.png")
# Opposite direction example ONLY, not a game room asset.
reflect=lambda quad:[[float(W-x),float(y)] for x,y in quad]
inverse_H=compute_H(so,reflect(dest_outer))
inverse_inner=derived_inner(inverse_H,si)
save(warp_rgba(canonical["wood"],inverse_H),"QA_opposite_angle_same_source.png")
# Keep exactly same background and rear-side frame sprites across all modes.
backing=img(D43/"entrance_bare_three_frame_backing.png")
rear_frames={k:img(D44/f"frame_{k}_wood_grain_v02.png") for k in ("left","right")}
rear_empty={k:img(D43/f"exhibition_{k}_empty_mat.png") for k in ("left","right")}
rear_photos={k:img(D43/f"exhibition_{k}_photo_sample.png") for k in ("left","right")}
centers={"left":[138.5,103.5],"right":[416.5,103.5],"front":[457.5,261]}
characters=[("butler-front-00.png",140,371,43),("curator-front-00.png",287,366,35)]
def shift(layer,center,pct):
 if pct==100:return layer
 A=cv2.getRotationMatrix2D(tuple(center),0,pct/100)
 warped=cv2.warpAffine(np.asarray(layer.convert("RGBA")),A,(W,Hh),flags=cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 return Image.fromarray(warped,"RGBA")
styles=("none","wood","gold","gold_body")
def comp(style,mode="empty",pct=100):
 assert style in styles and mode in content
 canvas=backing.copy()
 for k in ("left","right"):
  canvas.alpha_composite(shift(rear_photos[k] if mode=="photos" else rear_empty[k],centers[k],pct))
  canvas.alpha_composite(shift(rear_frames[k],centers[k],pct))
 canvas.alpha_composite(shift(img(OUT/f"right_front_content_{mode}.png"),centers["front"],pct))
 if style!="none":
  canvas.alpha_composite(shift(layers[style],centers["front"],pct))
 for fn,cx,foot,w in characters:
  sp=img(CHARS/fn);h=round(sp.height*w/sp.width)
  canvas.alpha_composite(sp.resize((w,h),Image.Resampling.NEAREST),(round(cx-w/2),foot-h))
 return canvas.convert("RGB")
for style in styles:
 for mode in content:
  for pct in (90,100,110):
   save(comp(style,mode,pct),f"view_{style}_{mode}_{pct}.png")
# QA: all style changes limited only to derived front frame alpha, other architecture untouched.
for pct in (90,100,110):
 for mode in content:
  nw=np.asarray(comp("wood",mode,pct))
  gl=np.asarray(comp("gold",mode,pct))
  a=alpha(shift(layers["wood"],centers["front"],pct))>0
  assert np.count_nonzero(np.any(nw!=gl,axis=2)&~a)==0,(pct,mode)
# The SAME masked pixel positions for photograph, blank mat and a registered photo.
for mode in content:
 assert np.array_equal(alpha(img(OUT/f"right_front_content_{mode}.png"))>0,wm)
assert np.count_nonzero((alpha(layers["gold"])>0)&wm)==0
# Demonstrate no geometric contradictions: one H maps both outer and derived inner.
outer_proj=cv2.perspectiveTransform(so.reshape(1,4,2),M).reshape(4,2)
inner_proj=cv2.perspectiveTransform(si.reshape(1,4,2),M).reshape(4,2)
assert np.max(np.abs(outer_proj-dest_outer))<1e-3
assert np.max(np.abs(inner_proj-dest_inner))<1e-3
# Pixel based plane test: inner and frame form near continuous outer polygon.
outer_region=np.zeros((Hh,W),np.uint8)
cv2.fillConvexPoly(outer_region,np.rint(dest_outer).astype(np.int32),1)
filled=(alpha(layers["wood"])>0)|wm
gaps=np.uint8((outer_region>0)&(~filled))
n,lab,stats,cent=cv2.connectedComponentsWithStats(gaps)
gap_components=sorted([int(stats[i,cv2.CC_STAT_AREA]) for i in range(1,n)],reverse=True)
print("PLANE_GAPS",int(gaps.sum()),"largest",gap_components[:3])
# No fake 0-gap claim. Record the diagnostic as shown.
board=Image.new("RGB",(W*4,Hh))
for i,s in enumerate(styles):
 board.paste(comp(s),(i*W,0))
save(board,"QA_4_styles_single_H.png")
crop=(400,176,510,350)
zoom=Image.new("RGB",((crop[2]-crop[0])*3*3,(crop[3]-crop[1])*3))
for i,s in enumerate(("none","wood","gold")):
 ci=comp(s).crop(crop).resize(((crop[2]-crop[0])*3,(crop[3]-crop[1])*3),Image.Resampling.NEAREST)
 zoom.paste(ci,(i*(crop[2]-crop[0])*3,0))
save(zoom,"QA_three_styles_right_front_3x.png")
for k in content:
 c=Image.new("RGB",(W*2,Hh))
 for i,s in enumerate(("wood","gold")):c.paste(comp(s,k),(i*W,0))
 save(c,f"QA_wood_vs_gold_{k}.png")
meta={"status":"art_candidate_pending_user_approval",
"one_h_exact_common":True,"source_outer_to_target_outer_max_error_px":float(np.max(np.abs(outer_proj-dest_outer))),
"source_inner_to_derived_inner_max_error_px":float(np.max(np.abs(inner_proj-dest_inner))),
"old_v05_inner_max_deviation_px":float(np.max(old_inner_displacement)),
"wood_gold_alpha_equal":True,"photo_empty_registration_alpha_equal":True,
"photo_window_overlap":0,"old_photo_mask_unused":True,
"frame_outer_union_raster_gap_pixels":int(gaps.sum()),"largest_gap_components_pixels":gap_components[:5],
"user_photo_input_sizes_tested":photosizes,"inverse_angle_same_transform_supported":True,
"canvas":[W,Hh],"states":36,"source_sha256":{k:sha(D43/f"frame_left_{'original_gold' if k=='gold' else 'gold_body'}.png") for k in ("gold","body")},
"official_character_sha256":{fn:sha(CHARS/fn) for fn,_,_,_ in characters},
"game_integrated":False,"level1_decided":False,"main_modified":False}
(OUT/"QA_manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print("V06_BUILD_PASS",len(list(OUT.glob("view_*.png"))),"variants; derived inner",np.round(dest_inner,2).tolist())
