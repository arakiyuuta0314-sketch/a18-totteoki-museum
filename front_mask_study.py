from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\43_エントランス完成素材_3額縁本体装飾分離_v01")
src=np.asarray(Image.open(R/"frame_front_original_gold.png").convert("RGBA"))
gold=np.asarray(Image.open(R/"view_gold_full_restored.png").convert("RGB")) if (R/"view_gold_full_restored.png").exists() else np.asarray(Image.open(R/"view_gold_full_empty_100.png").convert("RGB"))
none=np.asarray(Image.open(R/"view_none_empty_100.png").convert("RGB"))
alpha=src[:,:,3]>0
hsv=cv2.cvtColor(src[:,:,:3],cv2.COLOR_RGB2HSV)
g=(hsv[:,:,0]>4)&(hsv[:,:,0]<37)&(hsv[:,:,1]>70)&(hsv[:,:,2]>95)&alpha
d=np.max(np.abs(gold.astype(np.int16)-none.astype(np.int16)),axis=2)
m=d>32
print("alpha",np.sum(alpha),"metal",np.sum(g),"composite diff",np.sum(m),"metal among alpha",np.sum(g&alpha),flush=True)
for y in [185,190,195,200,205,210,215,225,240,255,270,290,310,325,335]:
    for k,v in [('a',alpha),('g',g),('diff',m)]:
      x=np.where(v[y,400:510])[0]+400
      print(y,k,(int(x.min()),int(x.max()),len(x)) if x.size else "-",end="; ")
    print("")
crop=(402,175,511,350)
panels=[]
for n,a in [('gold',gold),('none',none),('wood',np.asarray(Image.open(R/"QA_02_simple_wood_frames.png").convert("RGB")))]:
    panels.append(Image.fromarray(a).crop(crop).resize((436,700),Image.Resampling.NEAREST))
for n,msk in [('alpha',alpha),('hsv_gold',g),('diff',m)]:
    tmp=none.copy()
    tmp[msk]=[230,55,55]
    panels.append(Image.fromarray(tmp).crop(crop).resize((436,700),Image.Resampling.NEAREST))
out=Image.new("RGB",(436*len(panels),700),(0,0,0))
for i,p in enumerate(panels):out.paste(p,(i*436,0))
dest=Path(__file__).resolve().parent/"QA_front_geometry_study.png";out.save(dest)
print('STUDY',dest,flush=True)
