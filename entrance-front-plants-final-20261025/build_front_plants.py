# -*- coding: utf-8 -*-
"""A18 E01/E02 independently movable front greenery, faithfully sourced from adopted JPG.
Editable source inputs: two alpha masks, two restoration patches, two restoration masks.
Does not redraw actors, architecture, or update the playable game.
"""
from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json
R=Path(r"C:\Users\User\source\repos\a18-entrance-plants-both-20261025")
O=Path(__file__).parent
SRC=R/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
SPR=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\00_正式採用素材\characters")
raw=Image.open(SRC).convert("RGB")
rgb=np.asarray(raw);W,H=raw.size;assert (W,H)==(546,483)
cfg={
 "left":{"rect":(0,398,66,483),"anchor":(21,85),"preferred_id":"E01"},
 "right":{"rect":(450,398,538,483),"anchor":(51,85),"preferred_id":"E02"}
}
back=rgb.copy()
assets={}
maskChanged=np.zeros((H,W),bool)
for k,c in cfg.items():
 l,t,r,b=c["rect"];sz=(r-l,b-t)
 alpha=Image.open(O/f"source_{k}_foliage_and_vase_mask.png").convert("L")
 restore=Image.open(O/f"source_{k}_restoration_patch.png").convert("RGB")
 restore_mask=Image.open(O/f"source_{k}_restoration_change_mask.png").convert("L")
 assert alpha.size==restore.size==restore_mask.size==sz
 plant=raw.crop((l,t,r,b)).convert("RGBA")
 plant.putalpha(alpha)
 assert np.count_nonzero(np.asarray(alpha)>60)>1700,k
 assert np.count_nonzero(np.asarray(alpha)==0)>1000,k
 plant.save(O/f"entrance_plant_{k}.png",optimize=True)
 alpha.save(O/f"entrance_plant_{k}_mask.png",optimize=True)
 changed=np.asarray(restore_mask)>0
 view=back[t:b,l:r].copy()
 view[changed]=np.asarray(restore)[changed]
 back[t:b,l:r]=view
 maskChanged[t:b,l:r]=changed
 assets[k]=plant
 # proof of independent extraction alpha and untouched real material
 checker=Image.new("RGBA",sz,(192,196,198,255))
 checker.alpha_composite(plant)
 checker.resize((sz[0]*5,sz[1]*5),Image.Resampling.NEAREST).convert("RGB").save(O/f"QA_{k}_isolated_5x.png")
background=Image.fromarray(back,"RGB")
background.save(O/"entrance_bg_without_front_plants.png",optimize=True)
# Also supply left-only/right-only individually restored background PNGs,
# important if future drawing/removal of one plant changes.
for k,c in cfg.items():
 l,t,r,b=c["rect"]
 single=rgb.copy()
 m=np.asarray(Image.open(O/f"source_{k}_restoration_change_mask.png"))>0
 rpatch=np.asarray(Image.open(O/f"source_{k}_restoration_patch.png").convert("RGB"))
 ar=single[t:b,l:r].copy();ar[m]=rpatch[m];single[t:b,l:r]=ar
 Image.fromarray(single,"RGB").save(O/f"entrance_bg_without_{k}_plant.png",optimize=True)
photo=Image.open(O/"source_approved_photo_and_sprites_preview.png").convert("RGB")
assert photo.size==raw.size
preview=np.asarray(photo).copy();preview[maskChanged]=back[maskChanged]
base=Image.fromarray(preview,"RGB")
base.save(O/"QA_both_plants_off_photo_and_formal_sprites.png",optimize=True)
def layer_on(base_img,shown=("left","right"),scales=None,shifts=None):
 img=base_img.convert("RGBA")
 scales=scales or {};shifts=shifts or {}
 for k,c in cfg.items():
  if k not in shown:continue
  l,t,r,b=c["rect"];sx,sy=c["anchor"]
  scale=float(scales.get(k,1.))
  off=int(shifts.get(k,0))
  dw,dh=round((r-l)*scale),round((b-t)*scale)
  overlay=assets[k].resize((dw,dh),Image.Resampling.LANCZOS)
  xx=round(l+sx+off-sx*scale);yy=round(t+sy-sy*scale)
  img.alpha_composite(overlay,(xx,yy))
 return img.convert("RGB")
layer_on(base).save(O/"QA_both_plants_on_photo_and_formal_sprites.png",optimize=True)
layer_on(base,shown=("left",)).save(O/"QA_left_only_photo_and_formal_sprites.png",optimize=True)
layer_on(base,shown=("right",)).save(O/"QA_right_only_photo_and_formal_sprites.png",optimize=True)
layer_on(base,scales={"left":.90,"right":.90}).save(O/"QA_both_090pct.png",optimize=True)
layer_on(base,scales={"left":1.10,"right":1.10}).save(O/"QA_both_110pct.png",optimize=True)
layer_on(base,shifts={"left":5,"right":-5}).save(O/"QA_both_shift_inward_5px.png",optimize=True)
# Comparative, directly verified image (the original reference is *not* overwritten)
board=Image.new("RGB",(1092,483))
board.paste(layer_on(base),(0,0));board.paste(base,(546,0))
board.save(O/"QA_on_off_comparison.jpg",quality=94)
triptych=Image.new("RGB",(546*3,483))
for i,scale in enumerate((.90,1.,1.10)):
 triptych.paste(layer_on(base,scales={"left":scale,"right":scale}),(546*i,0))
triptych.save(O/"QA_3_sizes.jpg",quality=94)
assert np.array_equal(back[~maskChanged],rgb[~maskChanged])
# Source characteristics are confined to these two architecture-local zones.
outside=np.ones((H,W),bool)
outside[398:483,0:66]=False
outside[398:483,450:538]=False
assert not np.any(maskChanged & outside),"Restoration escaped its scene region"
both=np.asarray(layer_on(base))
prior=np.asarray(photo)
diff=np.abs(np.int16(both)-np.int16(prior))
# Pixel-exact outside two small regions, not within the repaired pot areas.
assert np.array_equal(both[outside],prior[outside])
assert np.array_equal(np.asarray(base)[outside],prior[outside])
source_hashes={}
for name in ("butler-front-00.png","curator-front-00.png"):
 assert (SPR/name).is_file()
 orig_sprite=R/"entrance-rear-frames-final-20261025"/name
 assert (SPR/name).read_bytes()==orig_sprite.read_bytes(),name
 source_hashes[name]=hashlib.sha256((SPR/name).read_bytes()).hexdigest()
def shafile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={
 "title":"A18 Entrance E01 E02 front left and right independent plants v01",
 "source_sha256":shafile(SRC),"canvas":[W,H],
 "components":{k:{"source_rect_xyxy":list(c["rect"]),"anchor_local_xy":list(c["anchor"]),
                       "asset":f"entrance_plant_{k}.png",
                       "object_id":c["preferred_id"]} for k,c in cfg.items()},
 "verified_scales":[0.90,1.00,1.10],
 "verified_horizontal_shift_inward_px":5,
 "repair":{"exact_outside_plant_regions":True,"changed_pixels":int(maskChanged.sum()),
   "original_with_both_reassembled_mean_abs_rgb_error":round(float(diff.mean()),4),
   "source_pixel_exact_inside_repair":False,
   "background_is_reconstructed_not_source_truth":True},
 "characters":{"original_file_sha256":source_hashes,"regenerated":False},
 "tests":{"isolated_alpha_both":True,"registered_photo_unchanged_outside_regions":True,
 "independent_show_hide":True,"both_states":True,"three_size_states":True},
 "game_integrated":False,"user_art_approval":"pending"
}
(O/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("QA_BOTH",json.dumps(manifest["repair"],ensure_ascii=False),"OUT",len(list(O.iterdir())))
