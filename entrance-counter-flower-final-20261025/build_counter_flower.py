# -*- coding: utf-8 -*-
"""A18 E03 independent counter vase: deterministic reconstruction from approved source
and pre-authored editable mask/background patch files in this directory.
No network, no AI redraws, no mutation of game code.
"""
from pathlib import Path
from PIL import Image
import numpy as np,cv2,hashlib,json
R=Path(r"C:\Users\User\source\repos\a18-entrance-flowerpot-20261025")
O=Path(__file__).resolve().parent
SRC=R/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
G=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
ref=Image.open(SRC).convert("RGB");src=np.asarray(ref)
assert ref.size==(546,483)
flower_rect=(68,318,112,393)
l,t,r,b=flower_rect
alpha=Image.open(O/"source_flower_alpha_mask.png").convert("L")
assert alpha.size==(r-l,b-t)
fg=ref.crop(flower_rect).convert("RGBA")
fg.putalpha(alpha);fg.save(O/"entrance_counter_flower_vase.png",optimize=True)
alpha.save(O/"entrance_counter_flower_alpha_mask.png",optimize=True)
bg=src.copy()
pl,pt,pr,pb=69,325,118,391
patch=np.asarray(Image.open(O/"source_tabletop_restoration_patch.png").convert("RGB"))
mask=np.asarray(Image.open(O/"source_tabletop_restoration_mask.png").convert("L"))>0
assert patch.shape==(pb-pt,pr-pl,3) and mask.shape==(pb-pt,pr-pl)
roi=bg[pt:pb,pl:pr].copy()
roi[mask]=patch[mask]
bg[pt:pb,pl:pr]=roi
base=Image.fromarray(bg,"RGB")
base.save(O/"entrance_bg_without_counter_flower.png",optimize=True)
preview=Image.open(O/"source_approved_preview_photos_formal_characters.png").convert("RGB")
im=np.asarray(preview).copy()
roi=im[pt:pb,pl:pr].copy()
roi[mask]=patch[mask]
im[pt:pb,pl:pr]=roi
demo_base=Image.fromarray(im,"RGB")
demo_base.save(O/"QA_photos_characters_no_counter_flower.png",optimize=True)
# Anchor is centre bottom of the original vase; scales respect centre and floor contact.
anchor=(22,70)
def add(base,scale=1.,shift=0):
 img=base.convert("RGBA")
 width,height=round(44*scale),round(75*scale)
 transformed=fg.resize((width,height),Image.Resampling.LANCZOS)
 x=round(l+anchor[0]+shift-anchor[0]*scale)
 y=round(t+anchor[1]-anchor[1]*scale)
 img.alpha_composite(transformed,(x,y))
 return img.convert("RGB")
scales=(.90,1.,1.10)
for scale in scales:
 n=f"{round(scale*100):03d}"
 add(demo_base,scale).save(O/f"QA_photos_characters_flower_{n}pct.png",optimize=True)
add(demo_base,1,-5).save(O/"QA_flower_repositioned_5px_left.png",optimize=True)
all=add(demo_base)
side=Image.new("RGB",(1092,483))
side.paste(all,(0,0));side.paste(demo_base,(546,0))
side.save(O/"QA_flower_on_off_comparison.png",optimize=True)
comparison=Image.new("RGB",(546*3,483))
for i,scale in enumerate(scales):comparison.paste(add(demo_base,scale),(i*546,0))
comparison.save(O/"QA_three_sizes.png",optimize=True)
reassembled=add(base)
reassembled.save(O/"QA_flower_original_reassembly.png",optimize=True)
diff=np.abs(np.int16(reassembled)-np.int16(src))
mae=float(diff.mean());maxerror=int(diff.max())
untouched=np.ones((483,546),bool);untouched[pt:pb,pl:pr]=False
assert np.array_equal(np.asarray(base)[untouched],src[untouched])
assert np.array_equal(np.asarray(reassembled)[untouched],src[untouched])
# Originals are not regenerated. They are in the previously approved reference preview.
hashes={}
for n in ("curator-front-00.png","butler-front-00.png"):
 a=G/"00_正式採用素材"/"characters"/n
 b=R/"entrance-rear-frames-final-20261025"/n
 assert a.read_bytes()==b.read_bytes(),n
 hashes[n]=hashlib.sha256(a.read_bytes()).hexdigest()
assert fg.mode=="RGBA" and (np.asarray(fg.getchannel("A"))==0).sum()>1000
manifest={
 "source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
 "source_size":[546,483],"seed_masks_are_editable":True,
 "plant_sprite":{"file":"entrance_counter_flower_vase.png","width":44,"height":75,
 "reference_offset":[68,318],"anchor_offset":[22,70]},
 "underlay":{"file":"entrance_bg_without_counter_flower.png","patch_rect":[pl,pt,pr,pb],
 "changed_pixels":int(mask.sum())},
 "verified":{"scale_percent":[90,100,110],"shift_left_px":5,
 "photo_and_formal_characters":True,"outside_restoration_rect_exact":True,
 "mean_abs_rgb_error_vs_reference":round(mae,5),"max_abs_rgb_error_vs_reference":maxerror,
 "pixel_exact_reference":mae==0},
 "official_character_png_sha256":hashes,"game_integrated":False,
 "status":"completed candidate; user art approval pending"
}
(O/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("ART_QA_COMPLETE",json.dumps(manifest["verified"]), "FILES",len(list(O.iterdir())))
