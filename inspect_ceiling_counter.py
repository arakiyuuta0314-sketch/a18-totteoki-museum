from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
files={
"v49":R/"49_エントランス完成素材_右手前壁面基準再投影_v07"/"view_wood_empty_100.png",
"v50":R/"50_エントランス完成候補_追加壁灯4点分離_v01"/"QA_all_four_sconces_on.png",
"orig":R/"43_エントランス完成素材_3額縁本体装飾分離_v01"/"entrance_bare_three_frame_backing.png",
}
out=Image.new("RGB",(870*3,550*2),(34,35,36))
for j,(name,p) in enumerate(files.items()):
 im=Image.open(p).convert("RGB")
 crops={"ceiling":(0,0,546,35),"desk":(0,305,128,431)}
 for k,(a,b,c,d) in crops.items():
  crop=im.crop((a,b,c,d))
  sz=(int(crop.width*min(860/crop.width,260/crop.height)),int(crop.height*min(860/crop.width,260/crop.height)))
  crop=crop.resize(sz,Image.Resampling.NEAREST)
  row=0 if k=="ceiling" else 1
  x=j*870+5;y=row*275+20
  out.paste(crop,(x,y));ImageDraw.Draw(out).text((x,y-17),name+"_"+k,fill="white")
dst=Path(__file__).parent/"QA_ceiling_desk_source_inspection.png";out.save(dst)
print(dst)
