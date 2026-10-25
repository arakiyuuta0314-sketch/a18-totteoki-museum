from pathlib import Path
from PIL import Image
import numpy as np,cv2
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
D43=R/"43_エントランス完成素材_3額縁本体装飾分離_v01"
D44=R/"44_エントランス完成素材_木製額縁木目改善_v02"
d={}
for title,p in [
 ("gold",D43/"frame_front_original_gold.png"),
 ("wood_old",D43/"frame_front_wood_basic.png"),
 ("wood_new",D44/"frame_front_wood_grain_v02.png"),
 ("goldbody",D43/"frame_front_gold_body.png"),
 ("ornament",D43/"frame_front_gold_ornaments.png"),
 ("photo_window",D43/"exhibition_front_window_mask.png"),
 ("empty",D43/"exhibition_front_empty_mat.png")]:
 im=Image.open(p)
 arr=np.asarray(im)
 a=(arr[:,:,3] if arr.ndim==3 and arr.shape[-1]==4 else arr[:,:,0] if arr.ndim==3 else arr)
 ys,xs=np.where(a>0)
 print(title,"shape",arr.shape,"pixels",len(xs),"bbox",((xs.min(),ys.min(),xs.max(),ys.max()) if len(xs)>0 else None))
 d[title]=a>0
print("gold_vs_old_alpha_identical",np.array_equal(d["gold"],d["wood_old"]))
print("gold_vs_new_alpha_identical",np.array_equal(d["gold"],d["wood_new"]))
print("all_gold_alpha_in_wood",np.count_nonzero(d["gold"]&~d["wood_new"]))
print("window_intersection_gold",np.count_nonzero(d["photo_window"] & d["gold"]))
print("window_intersection_wood",np.count_nonzero(d["photo_window"] & d["wood_new"]))
for y in (175,182,188,194,201,210,225,260,290,320,338,346):
 for key in ("gold","wood_new","photo_window"):
  x=np.where(d[key][y,:])[0]
  print(y,key,(int(x.min()),int(x.max()),len(x)) if len(x) else "-")
