from pathlib import Path
from PIL import Image
import numpy as np,cv2,json
ROOT=Path(__file__).resolve().parent
D=ROOT/"entrance-front-homography-v04-20261026"
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
A=np.asarray(Image.open(D/"frame_front_wood_from_rect_source_v04.png").convert("RGBA"))[:,:,3]
G=np.asarray(Image.open(R/"43_エントランス完成素材_3額縁本体装飾分離_v01"/"frame_front_original_gold.png").convert("RGBA"))
hsv=cv2.cvtColor(G[:,:,:3],cv2.COLOR_RGB2HSV)
metal=(hsv[:,:,0]>4)&(hsv[:,:,0]<37)&(hsv[:,:,1]>70)&(hsv[:,:,2]>95)&(G[:,:,3]>0)
inner=(np.asarray(Image.open(R/"43_エントランス完成素材_3額縁本体装飾分離_v01"/"exhibition_front_window_mask.png").convert("L"))>0)
metal&=~inner
# Gold has ornamental studs that are not part of basic wood and are intentionally not reproduced.
within=cv2.dilate((A>0).astype(np.uint8),np.ones((5,5),np.uint8))>0
print('METAL_NEAR_WOOD',round(np.count_nonzero(metal&within)/np.count_nonzero(metal),4))
print('NEW_ALPHA',np.count_nonzero(A),'PHOTO_OVERLAP',np.count_nonzero((A>0)&inner))
# Validate the new frame only touches 43's existing managed front frame halo.
ring=(G[:,:,3]>0)
new=(A>0)
print('WOOD_OUTSIDE_GOLD_MASK',np.count_nonzero(new&~cv2.dilate(ring.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)))
