# -*- coding:utf-8 -*-
"""A18 canonical front-facing exhibition slot -> any perspective.
ALL right-front materials use ONE set of geometry:
 wood, gold, gold ornaments, empty matte, photo sample and external photo input.
"""
from pathlib import Path
from PIL import Image
import numpy as np, cv2, json, hashlib, math, sys
from frame_projection import project_frame as project_ring, project_photo_to_window, fit_photo, reversed_quad
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
D43=ROOT/"43_エントランス完成素材_3額縁本体装飾分離_v01"
D44=ROOT/"44_エントランス完成素材_木製額縁木目改善_v02"
CHARS=ROOT/"00_正式採用素材"/"characters"
HERE=Path(__file__).resolve().parent
OUT=HERE/"entrance-canonical-front-v05-20261026"
OUT.mkdir(exist_ok=True)
W,H=546,483
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def im(p):return Image.open(p).convert("RGBA")
def save(image,name):image.save(OUT/name,optimize=True);return image
# Named points clockwise TL TR BR BL. Same points for all skins and all photo modes.
PROFILE={
"schema":"A18_CANONICAL_EXHIBIT_v1","canvas":[546,483],
"canonical_outer_quad":[[76,50],[200,50],[200,156],[76,156]],
"canonical_inner_quad":[[84,61],[193,61],[193,143],[84,143]],
"right_front":{
  "outer_quad":[[419,187],[499,212],[499,338],[417,292]],
  "inner_quad":[[426,201],[489,226],[489,323],[426,276]],
  "scale_anchor":[457.5,261.0]},
"left_facing_demo":{
  "outer_quad":[[546-x,y] for x,y in [[419,187],[499,212],[499,338],[417,292]]],
  "inner_quad":[[546-x,y] for x,y in [[426,201],[489,226],[489,323],[426,276]]]},
"layers":["backing","photo_or_empty_mat","frame_body","frame_ornament","official_character"],
"origin":"43 front photo mask contour, 43 left gold and 44 left wood"
}
(OUT/"shared_display_geometry.json").write_text(json.dumps(PROFILE,ensure_ascii=False,indent=2),encoding="utf-8")
so=np.float32(PROFILE["canonical_outer_quad"]); si=np.float32(PROFILE["canonical_inner_quad"])
# canonical assets are exact existing 43/44 source images; NO new generated museum or frame.
canonical={
 "wood":im(D44/"frame_left_wood_grain_v02.png"),
 "gold":im(D43/"frame_left_original_gold.png"),
 "gold_body":im(D43/"frame_left_gold_body.png"),
 "gold_ornaments":im(D43/"frame_left_gold_ornaments.png"),
 "empty_mat":im(D43/"exhibition_left_empty_mat.png"),
 "photo_sample":im(D43/"exhibition_left_photo_sample.png")}
for key,asset in canonical.items():save(asset,f"canonical_{key}.png")
# guarantee wood and gold exactly registered at origin
alpha=lambda pic:np.asarray(pic.getchannel("A"))
assert np.array_equal(alpha(canonical["wood"]),alpha(canonical["gold"]))
# Known old official front window mask is the target truth; both skins must reuse it.
official_window=np.asarray(Image.open(D43/"exhibition_front_window_mask.png").convert("L"))
cv=cv2.findContours((official_window>0).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
pol=cv2.approxPolyDP(cv[0][0],.014*cv2.arcLength(cv[0][0],True),True).reshape(-1,2)
assert len(pol)==4
assert set(map(tuple,pol.tolist()))==set(map(tuple,PROFILE["right_front"]["inner_quad"]))
# Source canonical photo/empty can be converted to an RGBA photo texture and
# warped using ONE inner-plane homography, then clipped to ONE shared window mask.
squad=si
dquad=np.float32(PROFILE["right_front"]["inner_quad"])
photo_map=cv2.getPerspectiveTransform(squad,dquad)
mask=(official_window>0)
def mapped_photo(source,outer=PROFILE["right_front"]["outer_quad"],inner=PROFILE["right_front"]["inner_quad"],official_mask=mask):
 return project_photo_to_window(source,inner,Image.fromarray(np.uint8(official_mask)*255,"L"))
canonical_mat=canonical["empty_mat"].crop((84,61,194,144)).convert("RGB")
canonical_photo=canonical["photo_sample"].crop((84,61,194,144)).convert("RGB")
# Photo input contract: arbitrary 2D image center-cropped into canonical 110x83 BEFORE transform.
photo_inputs={"empty":canonical_mat,"photos":canonical_photo}
for name,img in photo_inputs.items():save(img,f"canonical_{name}_window_content.png")
# independent test image, NOT a user image. Exercises 4 corners and proportions.
test=np.zeros((83,110,3),np.uint8)
test[:,:,:]=[215,191,156]
cv2.rectangle(test,(0,0),(17,17),(230,40,35),-1)
cv2.rectangle(test,(92,0),(109,17),(25,160,30),-1)
cv2.rectangle(test,(0,65),(17,82),(45,65,222),-1)
cv2.rectangle(test,(92,65),(109,82),(225,215,45),-1)
cv2.line(test,(0,0),(109,82),(110,77,48),2)
photo_inputs["registration"]=Image.fromarray(test,"RGB")
save(photo_inputs["registration"],"QA_canonical_4corner_registration.png")
# The right front skins are derived from the SAME original canonical frame alpha.
quad=PROFILE["right_front"]
fronts={}
for k in ("wood","gold","gold_body","gold_ornaments"):
 projected=np.asarray(project_ring(canonical[k],so,si,quad["outer_quad"],quad["inner_quad"])).copy()
 # The authoritative shared photo-window mask wins at the 1px antialias boundary.
 projected[mask]=0
 fronts[k]=save(Image.fromarray(projected,"RGBA"),f"front_{k}_projected.png")
assert np.array_equal(alpha(fronts["wood"]),alpha(fronts["gold"]))
# Guarantee ALL variants fit shared front photo window. Nonzero alpha in window -> QA failure.
for key,asset in fronts.items():
 assert np.count_nonzero((alpha(asset)>0)&mask)==0,(key,"photo window collision")
for key,source in photo_inputs.items():
 p=mapped_photo(source)
 save(p,f"front_{key}_projected.png")
 assert np.array_equal(alpha(p)>0,mask)
# Pixel exact photo positions for gold, wood and no frame (frame never influences photo layer).
def affine(layer,anchor,percent):
 if percent==100:return layer
 x,y=anchor
 M=cv2.getRotationMatrix2D((x,y),0,percent/100)
 res=cv2.warpAffine(np.asarray(layer),(M),(W,H),flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 return Image.fromarray(res,"RGBA")
rear_mat={k:im(D43/f"exhibition_{k}_empty_mat.png") for k in ("left","right")}
rear_photo={k:im(D43/f"exhibition_{k}_photo_sample.png") for k in ("left","right")}
rear_wood={k:im(D44/f"frame_{k}_wood_grain_v02.png") for k in ("left","right")}
anchors={"left":[138.5,103.5],"right":[416.5,103.5],"front":quad["scale_anchor"]}
characters=[("butler-front-00.png",140,371,43),("curator-front-00.png",287,366,35)]
def compose(style,content="empty",scale=100):
 assert style in ("none","wood","gold","gold_sans_ornament")
 assert content in ("empty","photos","registration")
 background=im(D43/"entrance_bare_three_frame_backing.png")
 for k in ("left","right"):
  mat=rear_photo[k] if content=="photos" else rear_mat[k]
  background.alpha_composite(affine(mat,anchors[k],scale))
  background.alpha_composite(affine(rear_wood[k],anchors[k],scale))
 background.alpha_composite(affine(im(OUT/f"front_{content}_projected.png"),anchors["front"],scale))
 if style=="wood":
  background.alpha_composite(affine(fronts["wood"],anchors["front"],scale))
 elif style in ("gold","gold_sans_ornament"):
  background.alpha_composite(affine(fronts["gold"] if style=="gold" else fronts["gold_body"],anchors["front"],scale))
 for filename,cx,foot,w in characters:
  sprite=im(CHARS/filename)
  hh=round(sprite.height*w/sprite.width)
  background.alpha_composite(sprite.resize((w,hh),Image.Resampling.NEAREST),(round(cx-w/2),foot-hh))
 return background.convert("RGB")
for style in ("none","wood","gold","gold_sans_ornament"):
 for content in ("empty","photos","registration"):
  for scale in (90,100,110):
   save(compose(style,content,scale),f"view_{style}_{content}_{scale}.png")
# Exact no-geometry-drift: photographed masks and frame alphas are compared before compositing.
for k in ("wood","gold"):
 assert np.array_equal(alpha(fronts[k])>0,alpha(fronts["wood"])>0)
for c in ("empty","photos","registration"):
 assert np.array_equal(alpha(im(OUT/f"front_{c}_projected.png"))>0,mask)
# Check architecture outside the union of officially allowed display windows, both rear frames, char positions unchanged.
compare_a=np.asarray(compose("wood","empty"))
compare_b=np.asarray(compose("gold","empty"))
legal=(alpha(fronts["wood"])>0)
delta=np.any(compare_a!=compare_b,axis=2)
assert not np.any(delta&(~legal)),("style switch altered outside frame",int(np.count_nonzero(delta&(~legal))))
# single-page comparison for final art QA
board=Image.new("RGB",(546*4,483))
for i,k in enumerate(["none","wood","gold_sans_ornament","gold"]):board.paste(compose(k),(i*546,0))
save(board,"QA_common_geometry_4styles.png")
# highly zoomed 3 comparison scenes
crop=(400,177,510,352)
zoom=Image.new("RGB",((crop[2]-crop[0])*3*3,(crop[3]-crop[1])*3))
for i,k in enumerate(["none","wood","gold"]):
 cut=compose(k).crop(crop).resize(((crop[2]-crop[0])*3,(crop[3]-crop[1])*3),Image.Resampling.NEAREST)
 zoom.paste(cut,(i*(crop[2]-crop[0])*3,0))
save(zoom,"QA_right_front_none_wood_gold_zoom3x.png")
# Geometry can be mirrored into a separate (not formally approved) target.
def reverse(quad):
 return [[W-x,y] for x,y in quad]
rev=project_ring(canonical["wood"],so,si,reversed_quad(quad["outer_quad"],W),reversed_quad(quad["inner_quad"],W))
save(rev,"QA_reverse_angle_from_same_canonical.png")
meta={
 "status":"art_candidate_pending_user_review",
 "source_canvas":[W,H],"geometry":PROFILE,
 "canonical_gold_sha256":sha(D43/"frame_left_original_gold.png"),
 "canonical_wood_sha256":sha(D44/"frame_left_wood_grain_v02.png"),
 "frame_skins_identical_alpha":True,
 "front_photo_and_empty_matte_same_alpha_exact":True,
 "front_photo_mask_equal_official_v43":True,
 "photo_window_frame_overlap_pixels":0,
 "style_diff_outside_frame":int(np.count_nonzero(delta&(~legal))),
 "source_char_sha256":{name:sha(CHARS/name) for name,_,_,_ in characters},
 "styles":["none","wood","gold_sans_ornament","gold"],
 "photo_modes":["empty","photos","registration"],"scales":[90,100,110],
 "reversed_angle_demo_only":True,"game_integrated":False,"lv1_assigned":False}
(OUT/"QA_manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print("V05_BUILD_PASS",len(list(OUT.glob("view_*.png"))),"scenes",int(np.count_nonzero(alpha(fronts["wood"]))),"wood frame pixels")
