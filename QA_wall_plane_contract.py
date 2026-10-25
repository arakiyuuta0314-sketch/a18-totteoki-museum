# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import numpy as np, cv2, json, math
HERE=Path(__file__).resolve().parent
OUT=HERE/"entrance-wall-plane-v07-20261026"
OLD=HERE/"entrance-canonical-single-H-v06-20261026"
a=json.loads((OUT/"single_H_geometry.json").read_text(encoding="utf-8"))
m=json.loads((OUT/"QA_manifest.json").read_text(encoding="utf-8"))
wp=np.float32(a["wall_plane_quad"])
fp=np.float32(a["target_right_front_outer"])
def slope(quad,edge):
 if edge=="top":v0,v1=quad[0],quad[1]
 else:v0,v1=quad[3],quad[2]
 return float((v1[1]-v0[1])/(v1[0]-v0[0]))
old=np.float32([[419,187],[499,212],[499,338],[417,292]])
wall_slope=[slope(wp,"top"),slope(wp,"bottom")]
new_slope=[slope(fp,"top"),slope(fp,"bottom")]
old_slope=[slope(old,"top"),slope(old,"bottom")]
errors_new=[abs(v-w) for v,w in zip(new_slope,wall_slope)]
errors_old=[abs(v-w) for v,w in zip(old_slope,wall_slope)]
assert all(x<y for x,y in zip(errors_new,errors_old)),(errors_new,errors_old)
for mode in ("empty","photos","registration"):
 for st in ("wood","gold"):
  curr=np.asarray(Image.open(OUT/f"view_{st}_{mode}_100.png").convert("RGB"))
  previous=np.asarray(Image.open(OLD/f"view_{st}_{mode}_100.png").convert("RGB"))
  diff=np.any(curr!=previous,axis=2)
  permitted=np.zeros((483,546),bool);permitted[172:372,400:513]=True
  assert not np.any(diff&(~permitted)),("Other architecture altered",st,mode)
assert m["one_h_exact_common"] and m["wood_gold_alpha_equal"] and m["photo_empty_registration_alpha_equal"]
assert m["photo_window_overlap"]==0
assert m["frame_outer_union_raster_gap_pixels"]<=2
report={"result":"PASS","wall_quad_manual_trace_source":"43/entrance_bare_three_frame_backing.png",
"wall_quad_px":wp.tolist(),"new_display_outer_px":fp.tolist(),
"wall_top_bottom_slope":wall_slope,"v06_top_bottom_slope":old_slope,
"v07_top_bottom_slope":new_slope,
"old_absolute_slope_error":errors_old,"new_absolute_slope_error":errors_new,
"both_edges_improved":True,"photo_and_frame_one_H":True,
"other_architecture_delta_pixels":0,
"raster_gap_pixels":m["frame_outer_union_raster_gap_pixels"],
"source_wall_corners_approximate_not_approved":True,
"all_rooms_regression_tested":False}
(OUT/"QA_wall_plane_contract.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("QA_WALL_CONTRACT_PASS",json.dumps({k:report[k] for k in ("old_absolute_slope_error","new_absolute_slope_error","raster_gap_pixels")},ensure_ascii=False))
