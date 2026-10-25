# -*- coding: utf-8 -*-
"""A18 carpet gold trim: retain original 546x483 painted pixels with a reversible border layer."""
from pathlib import Path
from PIL import Image
import cv2,numpy as np,json,hashlib
R=Path(r"C:\Users\User\source\repos\a18-entrance-carpet-trim-20261025")
S=R/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
O=Path(r"C:\Users\User\AppData\Local\Temp\a18_carpet_trim_candidate");O.mkdir(exist_ok=True)
source=Image.open(S).convert("RGB");assert source.size==(546,483)
orig=np.array(source)
# Pixel-traced quadrilaterals: keep outer carpet silhouette and 3px dark rim in the base.
outer=np.array([(194,240),(364,240),(387,431),(177,431)],np.int32)
inner=np.array([(207,253),(351,253),(372,417),(191,417)],np.int32)
m_out=np.zeros((483,546),np.uint8);m_in=m_out.copy()
cv2.fillConvexPoly(m_out,outer,255);cv2.fillConvexPoly(m_in,inner,255)
m=np.where((m_out==255)&(m_in==0),255,0).astype(np.uint8)
# Source material for a natural red-carpet underlay beneath the independent trim:
# perspective-warp the actual red inner-carpet textile to the larger rug interior.
A=np.float32([(207,253),(351,253),(372,417),(191,417)])
B=np.float32([(194,240),(364,240),(387,431),(177,431)])
trans=cv2.getPerspectiveTransform(A,B)
projected=cv2.warpPerspective(orig,trans,(546,483),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
base=orig.copy()
base[m>0]=projected[m>0]
Image.fromarray(base,"RGB").save(O/"entrance_bg_carpet_without_gold_trim.png",optimize=True)
# Cropped transparent original trim, with no red interior covering the photo/player.
xl,yt,xr,yb=173,235,393,438
rgba=Image.fromarray(np.dstack((orig[yt:yb,xl:xr],m[yt:yb,xl:xr])),"RGBA")
rgba.save(O/"entrance_carpet_gold_trim.png",optimize=True)
Image.fromarray(m[yt:yb,xl:xr],"L").save(O/"entrance_carpet_gold_trim_mask.png",optimize=True)
def compose(show=True,basephoto=None):
 scene=np.array(Image.open(basephoto).convert("RGB")).copy() if basephoto else orig.copy()
 scene[m>0]=base[m>0]
 if show:scene[m>0]=orig[m>0]
 return Image.fromarray(scene,"RGB")
on=compose();on.save(O/"QA_trim_on_original_match.png")
off=compose(False);off.save(O/"QA_trim_off_red_carpet.png")
ref=R/"entrance-rear-frames-final-20261025"/"QA_photos_100pct.png";assert ref.is_file()
p_on=compose(True,ref);p_off=compose(False,ref)
p_on.save(O/"QA_photos_and_formal_sprites_trim_on.png")
p_off.save(O/"QA_photos_and_formal_sprites_trim_off.png")
board=Image.new("RGB",(1092,483));board.paste(p_on,(0,0));board.paste(p_off,(546,0))
board.save(O/"QA_carpet_trim_on_off.png",optimize=True)
# Focus on decorative band in raster 3x
origzoom=source.crop((163,225,399,450)).resize((708,675),Image.Resampling.NEAREST)
origzoom.save(O/"QA_carpet_source_crop_3x.png")
diff=np.abs(np.asarray(on).astype(np.int16)-orig.astype(np.int16))
assert diff.max()==0
assert np.array_equal(np.asarray(off)[m==0],orig[m==0]),"Off altered pixels outside trim"
print("CHANGED_INSIDE",np.count_nonzero(np.any(np.asarray(off)!=orig,axis=2)),"MASK",np.count_nonzero(m))
assert (np.array(p_on)!=np.array(Image.open(ref).convert("RGB"))).sum()==0
manifest={"source":str(S),"source_sha256":hashlib.sha256(S.read_bytes()).hexdigest(),
"canvas":[546,483],"outer":outer.tolist(),"inner":inner.tolist(),"crop":[xl,yt,xr,yb],
"trim_pixel_count":int(np.count_nonzero(m)),"standard_source_exact":True,
"original_outside_trim_unchanged":True,"character_source":"QA photos+formal sprites from previous approved composites",
"state":"image candidate awaiting quality review","game_integrated":False}
(O/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS_INITIAL",manifest["trim_pixel_count"],"pixels, on exact")
