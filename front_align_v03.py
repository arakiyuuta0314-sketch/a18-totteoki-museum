# -*- coding: utf-8 -*-
"""A18 front wooden frame visual alignment to approved gold trim; only front frame material changed."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, cv2, json, hashlib
HERE=Path(__file__).resolve().parent
OUT=HERE/"entrance-front-wood-aligned-v03-20261026"
OUT.mkdir(exist_ok=True)
V02=HERE/"entrance-wood-grain-v02-20261026"
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
D43=ROOT/"43_エントランス完成素材_3額縁本体装飾分離_v01"
W,H=546,483
def get(p):return Image.open(p).convert("RGBA")
def save(im,name):im.save(OUT/name,optimize=True);return im
gold=get(D43/"frame_front_original_gold.png")
wood=get(V02/"frame_front_wood_grain_v02.png")
orig_alpha=np.asarray(gold.getchannel("A"))
assert np.array_equal(orig_alpha,np.asarray(wood.getchannel("A")))
window=np.asarray(Image.open(D43/"exhibition_front_window_mask.png").convert("L"))>0
# Canonical visual footprint based on the ACTUAL gilded frame's visible location.
# Outer points trace the metal border, not its broad temporary separation halo.
# Inner cutout derives directly from the existing photograph window mask.
outer=[[420,191],[496,215],[497,334],[419,288]]
S=4
m=Image.new("L",(W*S,H*S),0);d=ImageDraw.Draw(m)
d.polygon([(x*S,y*S) for x,y in outer],fill=255)
outer_alpha=np.asarray(m.resize((W,H),Image.Resampling.LANCZOS))
outer_alpha=np.minimum(outer_alpha,orig_alpha)
outer_alpha[window]=0
# Ensure the cutout stays contiguous and transparent. The material is isolated
# by the source alpha so no architecture pixels can change outside original target.
aligned=wood.copy()
rgba=np.asarray(aligned).copy()
rgba[:,:,3]=outer_alpha
aligned=save(Image.fromarray(rgba,"RGBA"),"frame_front_wood_grain_aligned_v03.png")
assert (np.asarray(aligned.getchannel("A"))[window]==0).all()
assert not np.any((outer_alpha>0)&(orig_alpha==0))
def sized(img,cx,cy,percent):
 if percent==100:return img
 M=cv2.getRotationMatrix2D((cx,cy),0,percent/100)
 arr=cv2.warpAffine(np.asarray(img),M,(W,H),flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 return Image.fromarray(arr,"RGBA")
coord={"left":(138.5,103.5),"right":(416.5,103.5),"front":(457.5,261)}
def build(style,photos=False,percent=100):
 # All toggles change ONLY the right-front frame. Rear wood and characters remain fixed.
 assert style in ("none","old","new","gold")
 photo="photos" if photos else "empty"
 canvas=get(V02/f"view_none_{photo}_{percent}.png")
 for name in ("left","right"):
  canvas.alpha_composite(sized(get(V02/f"frame_{name}_wood_grain_v02.png"),*coord[name],percent))
 front={"none":None,"old":wood,"new":aligned,"gold":gold}[style]
 if front is not None:
  canvas.alpha_composite(sized(front,*coord["front"],percent))
 return canvas.convert("RGB")
for style in ("none","old","new","gold"):
 for percent in (90,100,110):
  for photos in (False,True):
   save(build(style,photos,percent),f"view_{style}_{'photos' if photos else 'empty'}_{percent}.png")
# Verify the visual revision affects only the right-front registered frame at every supported size.
for scale in (90,100,110):
 for photo in (False,True):
  suffix="photos" if photo else "empty"
  revised=np.asarray(build("new",photo,scale),dtype=np.int16)
  previous=np.asarray(Image.open(V02/f"view_new_{suffix}_{scale}.png").convert("RGB"),dtype=np.int16)
  changed=np.any(revised!=previous,axis=2)
  scaled_source=np.asarray(sized(gold,*coord["front"],scale).getchannel("A"))>0
  assert not np.any(changed & (~scaled_source)),("Unrelated modification",scale,photo)
# The actual physical metallic front frame appears narrower than the v02 separated halo.
gold_arr=np.asarray(gold)
hsv=cv2.cvtColor(gold_arr[:,:,:3],cv2.COLOR_RGB2HSV)
bright=(hsv[:,:,0]>4)&(hsv[:,:,0]<37)&(hsv[:,:,1]>70)&(hsv[:,:,2]>95)&(orig_alpha>0)
# Exclude ornamental glints (bulbs) from fit metric; compare the visible metal bars.
roi=np.zeros((H,W),bool);roi[190:334,418:498]=True
metal=bright & roi
mask=outer_alpha>0
coverage=float(np.sum(mask & metal))/max(np.sum(metal),1)
# Grounded footprint QA. Wider threshold accounts for 1px anti-aliasing.
mask_bbox=np.where(mask)
print("METAL_COVERAGE",round(coverage,4),"new ring pixels",int(mask.sum()),"original halo",int(np.count_nonzero(orig_alpha)),
"new bbox",int(mask_bbox[1].min()),int(mask_bbox[0].min()),int(mask_bbox[1].max()),int(mask_bbox[0].max()),flush=True)
old_scene=np.asarray(build("old"),np.int16);new_scene=np.asarray(build("new"),np.int16)
dif=np.any(old_scene!=new_scene,axis=2)
src_alpha=orig_alpha>0
assert np.count_nonzero(dif & (~src_alpha))==0
assert np.count_nonzero(dif)>300
# Gold and wood reference inner photo window remains identical, unaffected by frame material.
none_photo=np.asarray(build("none",photos=True))
new_photo=np.asarray(build("new",photos=True))
assert np.array_equal(none_photo[window],new_photo[window])
# Overlay actual gold and new canonical wood boundary, for future registration by one anchor geometry.
qa=np.asarray(build("gold"),np.uint8).copy()
overlay=qa.copy()
contour=cv2.Canny(np.uint8(mask)*255,80,120)
overlay[contour>0]=[50,245,250]
save(Image.fromarray(overlay),"QA_gold_with_wood_footprint_overlay.png")
# Side by side focus, three scenes gold, old wood and corrected wood
box=(402,175,509,348)
b=Image.new("RGB",((box[2]-box[0])*4,(box[3]-box[1])))
for i,style in enumerate(("gold","old","new","none")):
 b.paste(build(style).crop(box),(i*(box[2]-box[0]),0))
save(b.resize((b.width*3,b.height*3),Image.Resampling.NEAREST),"QA_right_front_4states_3x.png")
compare=Image.new("RGB",(W*4,H))
for i,style in enumerate(("gold","old","new","none")):
 compare.paste(build(style),(i*W,0))
save(compare,"QA_entire_entrance_4states.png")
report={"status":"visual_art_candidate_requires_approval","source_v02_git_commit":"a2a0660",
 "source_front_gold_sha256":hashlib.sha256((D43/"frame_front_original_gold.png").read_bytes()).hexdigest(),
 "source_front_wood_sha256":hashlib.sha256((V02/"frame_front_wood_grain_v02.png").read_bytes()).hexdigest(),
 "reference_outer_quad":outer,"photo_window_source":"43/exhibition_front_window_mask.png",
 "photo_window_kept_intact":True,"outside_former_front_alpha_changed_pixels":int(np.count_nonzero(dif&(~src_alpha))),
 "front_alpha_visual_fit_to_metal_ratio":coverage,
 "front_mask_old_pixels":int(np.count_nonzero(orig_alpha)),"front_mask_new_pixels":int(np.count_nonzero(mask)),
 "only_front_frame_changed":True,"rear_frames_unchanged":True,"approved_characters_unchanged":True,
 "game_integrated":False,"lv1_design_fixed":False}
(OUT/"QA_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("PREVIEW_PASS",report["outside_former_front_alpha_changed_pixels"],"outside front source pixels changed",flush=True)
