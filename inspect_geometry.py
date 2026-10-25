from pathlib import Path
from PIL import Image
import numpy as np,cv2
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
D43=R/"43_エントランス完成素材_3額縁本体装飾分離_v01"
D44=R/"44_エントランス完成素材_木製額縁木目改善_v02"
for k,p in [("src left",D44/"frame_left_wood_grain_v02.png"),("mask",D43/"exhibition_front_window_mask.png"),("gold",D43/"frame_front_original_gold.png")]:
 a=np.array(Image.open(p))
 ch=a[:,:,3] if a.ndim==3 else a
 c,_=cv2.findContours((ch>0).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 print(k,'bbox',cv2.boundingRect(c[0]),'num_contours',len(c))
 for eps in (.008,.014,.02,.028,.04):
  polygon=cv2.approxPolyDP(c[0],eps*cv2.arcLength(c[0],True),True).reshape(-1,2)
  print(' eps',eps,'verts',polygon.tolist())
