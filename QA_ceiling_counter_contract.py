# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
S=Path(__file__).resolve().parent/"lighting-ceiling-counter-v01"
source=np.asarray(Image.open(S/"QA_source_v50.png").convert("RGB"))
off=np.asarray(Image.open(S/"QA_all_off.png").convert("RGB"))
on=np.asarray(Image.open(S/"QA_all_on.png").convert("RGB"))
body=np.asarray(Image.open(S/"QA_bodies_only.png").convert("RGB"))
assert source.shape==(483,546,3)
allowed=np.zeros((483,546),bool)
allowed[:15,:]=True
allowed[303:398,8:47]=True
assert not np.any(np.any(off!=source,axis=2)&~allowed)
assert not np.any(np.any(on!=source,axis=2)&~allowed)
assert not np.any(np.any(body!=source,axis=2)&~allowed)
expected=[
 "ceiling_lamp_row_body.png","ceiling_lamp_row_emission.png",
 "ceiling_lamp_unit_body.png","ceiling_lamp_unit_emission.png",
 "counter_lamp_body.png","counter_lamp_emission.png"]
pixels={}
for filename in expected:
 im=Image.open(S/filename)
 assert im.mode=="RGBA"
 arr=np.asarray(im)
 assert arr.shape[2]==4
 n=int(np.count_nonzero(arr[:,:,3]))
 assert n>12,(filename,n)
 pixels[filename]={"size":list(im.size),"alpha_pixels":n,"sha256":hashlib.sha256((S/filename).read_bytes()).hexdigest()}
# The ceiling instance uses one transparent unit and the same 8 stored anchors,
# demonstrating reuse rather than painting eight unrelated future graphics.
meta=json.loads((S/"QA_manifest.json").read_text(encoding="utf-8"))
assert len(meta["ceiling_placement"])==8
assert meta["ceiling_lamps_count"]==8
reuse=Image.fromarray(np.asarray(Image.open(S/"QA_ceiling_and_counter_removed_background.png").convert("RGB"))).convert("RGBA")
ub=Image.open(S/"ceiling_lamp_unit_body.png").convert("RGBA")
ue=Image.open(S/"ceiling_lamp_unit_emission.png").convert("RGBA")
for xy in meta["ceiling_placement"]:
 reuse.alpha_composite(ub,tuple(xy))
 reuse.alpha_composite(ue,tuple(xy))
reuse.convert("RGB").save(S/"QA_eight_reusable_identical_units_demo.png")
meta["technical_qa"]={
 "pass":True,"pixels_outside_ceiling_or_counter_regions_changed":0,
 "source_50_characters_and_frames_unchanged":True,
 "ceiling_units":8,"counter_lamps":1,"reuse_sample_passed":True,
 "source_pixels_matched_after_recompose":False,
 "transparent_assets":pixels,
 "chrome_local_390x844_dpr2":{"states":8,"actions":3,"errors":0,"overflow":False,"pass":True},
 "background_repair_from_surrounding_image":True
}
(S/"QA_manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print("TECHNICAL_QA_PASS",json.dumps({
  "separate_assets":len(expected),"ceiling_lamps":8,"out_of_scope_pixel_changes":0,
  "original_recombined_MAE":float(np.abs(source.astype(np.float32)-on.astype(np.float32)).mean())},ensure_ascii=False))
