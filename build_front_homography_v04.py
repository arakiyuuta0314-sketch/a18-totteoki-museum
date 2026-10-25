# -*- coding:utf-8 -*-
"""A18 common front-facing frame source -> right foreground homography.
No new room or character generation. Right-side transform can be mirrored for future left-facing displays.
"""
from pathlib import Path
from PIL import Image
import numpy as np, cv2, json, hashlib
HERE=Path(__file__).resolve().parent
O=HERE/"entrance-front-homography-v04-20261026"
O.mkdir(exist_ok=True)
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
D43=ROOT/"43_エントランス完成素材_3額縁本体装飾分離_v01"
D44=ROOT/"44_エントランス完成素材_木製額縁木目改善_v02"
D45=ROOT/"45_エントランス完成素材_右手前木製額縁金縁位置合わせ_v03"
def rgba(p):return Image.open(p).convert("RGBA")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(img,n):img.save(O/n,optimize=True);return img
old_gold=rgba(D43/"frame_front_original_gold.png")
oldwood=rgba(D44/"frame_front_wood_grain_v02.png")
v03wood=rgba(D45/"frame_front_wood_grain_aligned_v03.png")
src=rgba(D44/"frame_left_wood_grain_v02.png")
goldalpha=np.asarray(old_gold.getchannel("A"))
photo_window=np.asarray(Image.open(D43/"exhibition_front_window_mask.png").convert("L"))>0
# Exact source photo opening: existing rectangular rear-left frame, not an invented asset.
src_corners=np.float32([[84,61],[193,61],[193,143],[84,143]])
# Exact destination photo opening: extracted with OpenCV contour from official 43 mask.
contours,_=cv2.findContours(np.uint8(photo_window),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
assert len(contours)==1
poly=cv2.approxPolyDP(contours[0],.014*cv2.arcLength(contours[0],True),True).reshape(-1,2)
assert len(poly)==4,poly
# Sort target corners by left x and y, then right x and y
order=np.vstack((poly[poly[:,0].argsort()[:2]][np.argsort(poly[poly[:,0].argsort()[:2]][:,1])],
                 poly[poly[:,0].argsort()[2:]][np.argsort(poly[poly[:,0].argsort()[2:]][:,1])]))
dst_corners=np.float32([order[0],order[2],order[3],order[1]])
M=cv2.getPerspectiveTransform(src_corners,dst_corners)
assert np.linalg.det(M)!=0
# A projective transform alone cannot match BOTH inner window and differing frame widths.
# Use one reusable front-facing source and 4 projective strips (top/right/bottom/left).
# Source inner/outer and target inner/outer quads are fixed shared geometry; no manual patching.
src_outer=np.float32([[76,50],[200,50],[200,156],[76,156]])
# Outer visual edge of the approved gold frame, sampled from the original image,
# not the much broader 43 separation alpha mask including hidden green backing.
dst_outer=np.float32([[419,187],[499,212],[499,338],[417,292]])
def warp_ring(common, so, si, do, di):
    up=3
    ww,hh=546*up,483*up
    source=np.asarray(common).astype(np.float32)
    out=np.zeros((hh,ww,4),np.float32)
    segments=[([0,1,5,4], [so[0],so[1],si[1],si[0]], [do[0],do[1],di[1],di[0]]),
              ([1,2,6,5], [so[1],so[2],si[2],si[1]], [do[1],do[2],di[2],di[1]]),
              ([3,2,6,7], [so[3],so[2],si[2],si[3]], [do[3],do[2],di[2],di[3]]),
              ([0,3,7,4], [so[0],so[3],si[3],si[0]], [do[0],do[3],di[3],di[0]])]
    premul=source.copy()
    premul[:,:,:3]*=(premul[:,:,3:4]/255.)
    for _,squad,dquad in segments:
        xform=cv2.getPerspectiveTransform(np.float32(squad),np.float32(dquad)*up)
        piece=cv2.warpPerspective(premul,xform,(ww,hh),flags=cv2.INTER_LINEAR,
                                  borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
        cover=np.zeros((hh,ww),np.uint8)
        cv2.fillConvexPoly(cover,np.round(np.float32(dquad)*up).astype(np.int32),255)
        cover=cover.astype(np.float32)/255.
        a=np.clip(piece[:,:,3]/255.*cover,0,1)
        # At joins prioritize the first side; separate quads already have the same seam.
        empty=np.clip(1-out[:,:,3]/255.,0,1)
        effective=a*empty
        out[:,:,:3]+=piece[:,:,:3]*cover[:,:,None]*empty[:,:,None]
        out[:,:,3]+=effective*255
    # Remove pre-multiplication before downsampling, preserving soft antialiasing.
    rgba=cv2.resize(out,(546,483),interpolation=cv2.INTER_AREA)
    alpha=rgba[:,:,3:4]
    rgb=np.where(alpha>0.02,rgba[:,:,:3]*255./np.maximum(alpha,.02),0)
    return np.uint8(np.clip(np.dstack([rgb,alpha]),0,255))
warp=warp_ring(src,src_outer,src_corners,dst_outer,dst_corners)
# Keep all transformations within the previously approved assembly footprint.
allowed=cv2.dilate(goldalpha,np.ones((3,3),np.uint8))>0
warp[~allowed]=0
warp[photo_window]=0
frame=save(Image.fromarray(warp,"RGBA"),"frame_front_wood_from_rect_source_v04.png")
# Reverse-direction proof: same original front-facing source, reflected destination quads.
# This is an isolated transform QA demonstration, not an approved new display location.
def reverse_quad(points):
    result=np.float32(points).copy()
    result[:,0]=546-result[:,0]
    return result
reverse=warp_ring(src,src_outer,src_corners,reverse_quad(dst_outer),reverse_quad(dst_corners))
save(Image.fromarray(reverse,"RGBA"),"QA_reverse_angle_same_source_example.png")
# Full 43 and 44 unchanged source canvases; the right-front layer is the only variable.
centers={"left":(138.5,103.5),"right":(416.5,103.5),"front":(457.5,261.)}
def scaled(img,key,percent):
 if percent==100:return img
 x,y=centers[key]
 A=cv2.getRotationMatrix2D((x,y),0,percent/100)
 mat=cv2.warpAffine(np.asarray(img),A,(546,483),flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 return Image.fromarray(mat,"RGBA")
rear_frames=[rgba(D44/f"frame_{k}_wood_grain_v02.png") for k in ("left","right")]
versions={"new":frame,"old":oldwood,"v03":v03wood,"gold":old_gold,"none":None}
def comp(mode,photos=False,percent=100):
 key="photos" if photos else "empty"
 scene=rgba(D44/f"view_none_{key}_{percent}.png")
 for name,im in zip(("left","right"),rear_frames):scene.alpha_composite(scaled(im,name,percent))
 if versions[mode] is not None: scene.alpha_composite(scaled(versions[mode],"front",percent))
 return scene.convert("RGB")
for style in versions:
 for percent in (90,100,110):
  for photos in (False,True):
   save(comp(style,photos,percent),f"view_{style}_{'photos' if photos else 'empty'}_{percent}.png")
# Extracted full original front-frame area is already registered to the photo aperture.
# No retouching left-lower or right-upper corners by hand.
projection=cv2.perspectiveTransform(np.float32([[76,50],[200,50],[200,156],[76,156]]).reshape(1,4,2),M).reshape(4,2)
m=np.asarray(frame.getchannel("A"))
masks={"old":np.asarray(oldwood.getchannel("A")),"v03":np.asarray(v03wood.getchannel("A")),"new":m}
window_overlap=np.count_nonzero((m>0)&photo_window)
assert window_overlap==0
assert np.any(m>0)
assert np.count_nonzero((m>0)&(~allowed))==0
# At 100%, all pixels other than the original front slot are unchanged.
for photos in (False,True):
 old=np.asarray(comp("old",photos,100))
 now=np.asarray(comp("new",photos,100))
 mask=np.any(old!=now,axis=2)
 assert np.count_nonzero(mask&(~allowed))==0
 assert np.count_nonzero(mask)>100
 assert np.array_equal(np.asarray(comp("none",photos,100))[photo_window],
                       np.asarray(comp("new",photos,100))[photo_window])
# Corroborate source photo edges in the canonical transform.
inner_project=cv2.perspectiveTransform(src_corners.reshape(1,4,2),M).reshape(4,2)
assert np.max(np.abs(inner_project-dst_corners))<.01
# Visual target marks onto gold image for QA
bg=np.asarray(comp("gold",False,100)).copy()
overlay=bg.copy()
cont,_=cv2.findContours((m>0).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(overlay,cont,-1,(0,255,245),1)
save(Image.fromarray(overlay),"QA_projection_outline_on_gold.png")
# old / v03 / v04 / gold 4-up compare
views=["old","v03","new","gold"]
contact=Image.new("RGB",(546*4,483))
for i,key in enumerate(views):contact.paste(comp(key),(i*546,0))
save(contact,"QA_old_v03_projective_gold_comparison.png")
# zoom-in 4 views about foreground
crop=(402,175,510,351)
zoom=Image.new("RGB",((crop[2]-crop[0])*4*3,(crop[3]-crop[1])*3))
for i,k in enumerate(views):
 pic=comp(k).crop(crop).resize(((crop[2]-crop[0])*3,(crop[3]-crop[1])*3),Image.Resampling.NEAREST)
 zoom.paste(pic,(i*(crop[2]-crop[0])*3,0))
save(zoom,"QA_right_front_4way_3x.png")
meta={"status":"art_candidate_pending_review","geometry_method":"four_strip_projective_mapping_from_one_front_facing_frame",
      "source_img":"44/frame_left_wood_grain_v02.png","src_corners":src_corners.astype(float).tolist(),
      "dst_photo_corners":dst_corners.astype(float).tolist(),
      "target_outer_visual_corners":dst_outer.tolist(),
      "projected_outer_from_single_homography_not_used":projection.tolist(),
      "homography_inner_window_reference":M.tolist(),
      "geometry_method":"4_side_projective_mesh_source_front_facing_with_common_outer_and_inner_quads",
      "reverse_direction_geometry_supported":True,
      "window_mask_source":"43/exhibition_front_window_mask.png",
      "photo_window_overlap":int(window_overlap),"outside_target_allowed_changed":0,
      "gold_original_alpha_sha256":sha(D43/"frame_front_original_gold.png"),
      "front_facing_source_sha256":sha(D44/"frame_left_wood_grain_v02.png"),
      "target_window_mask_sha256":sha(D43/"exhibition_front_window_mask.png"),
      "source_resolution":[546,483],"states":30,"rear_frames_unchanged":True,
      "official_chars_unchanged":True,"lv_assigned":False,"game_integrated":False}
(O/"QA_manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print("PROJECTION",projection.tolist())
print("QA_PASSED",meta["photo_window_overlap"],"window pixels overpainted",int((m>0).sum()),"alpha pixels")
