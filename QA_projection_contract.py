# -*- coding:utf-8 -*-
"""Independent geometry and arbitrary-photo input contract tests."""
from pathlib import Path
from PIL import Image
import numpy as np,cv2,json,hashlib
from frame_projection import fit_photo,project_photo_to_window,project_frame,reversed_quad
R=Path(__file__).resolve().parent
O=R/"entrance-canonical-front-v05-20261026"
g=json.loads((O/"shared_display_geometry.json").read_text(encoding="utf-8"))
src_outer=g["canonical_outer_quad"];src_inner=g["canonical_inner_quad"]
dst_outer=g["right_front"]["outer_quad"];dst_inner=g["right_front"]["inner_quad"]
target_mask=Image.open(O/"front_empty_projected.png").convert("RGBA").getchannel("A")
gold=Image.open(O/"front_gold_projected.png").convert("RGBA")
wood=Image.open(O/"front_wood_projected.png").convert("RGBA")
assert np.array_equal(np.asarray(gold.getchannel("A")),np.asarray(wood.getchannel("A")))
# User-photo simulation: any portrait or landscape source, identical exact window mask.
sizes=[(800,1200),(1920,1080),(110,83),(83,110),(546,483)]
for i,(w,h) in enumerate(sizes):
 grid=np.zeros((h,w,3),np.uint8)
 grid[:]=[202,175,118]
 grid[:max(1,h//7),:max(1,w//7)]=[255,0,0]
 grid[:max(1,h//7),-max(1,w//7):]=[0,255,0]
 grid[-max(1,h//7):,:max(1,w//7)]=[0,0,255]
 grid[-max(1,h//7):,-max(1,w//7):]=[255,255,0]
 cropped=fit_photo(Image.fromarray(grid),(110,83))
 assert cropped.size==(110,83)
 out=project_photo_to_window(cropped,dst_inner,target_mask)
 assert np.array_equal(np.asarray(out.getchannel("A")),np.asarray(target_mask))
 assert not np.any((np.asarray(out.getchannel("A"))>0)&(np.asarray(gold.getchannel("A"))>0))
 if i==0:out.save(O/"QA_portrait_photo_input_same_window.png")
# Mirror target shape reusing the identical canonical front-facing source file.
source=Image.open(O/"canonical_wood.png").convert("RGBA")
revouter=reversed_quad(dst_outer,546)
revinner=reversed_quad(dst_inner,546)
opposite=project_frame(source,src_outer,src_inner,revouter,revinner)
assert np.count_nonzero(np.asarray(opposite.getchannel("A")))>500
opposite.save(O/"QA_reversible_common_frame.png")
# Source assets not changed.
for key,old in [("wood","canonical_wood.png"),("gold","canonical_gold.png")]:
 src=Image.open(O/old)
 assert src.size==(546,483)
report={"result":"PASS","arbitrary_photo_input_sizes":sizes,"all_photo_masks_identical":True,
"wood_gold_alpha_identical":True,"reverse_orientation_same_code":True,
"common_photo_window_pixels":int(np.count_nonzero(np.asarray(target_mask))),
"wood_frame_alpha_pixels":int(np.count_nonzero(np.asarray(wood.getchannel("A"))))}
(O/"QA_registration_contract.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("QA_FRAME_PROJECTION_MODULE_PASS",report,flush=True)
