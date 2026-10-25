from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, cv2
D=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
P=D/"43_エントランス完成素材_3額縁本体装飾分離_v01"/"entrance_bare_three_frame_backing.png"
base=Image.open(P).convert("RGB")
walls={
 "measured":np.float32([[405,157],[509,197],[501,369],[405,294]]),
 "inset":np.float32([[407,161],[507,200],[501,359],[407,295]]),
}
src=np.float32([[0,0],[1,0],[1,1],[0,1]])
candidates={
 "A_15_18_85_82":(.15,.18,.85,.82),
 "B_17_20_85_79":(.17,.20,.85,.79),
 "C_16_16_86_83":(.16,.16,.86,.83)}
out=Image.new("RGB",(546*len(candidates),483*len(walls)))
for j,(wn,wall) in enumerate(walls.items()):
 H=cv2.getPerspectiveTransform(src,wall)
 for i,(k,(l,t,r,b)) in enumerate(candidates.items()):
  quad=cv2.perspectiveTransform(np.float32([[l,t],[r,t],[r,b],[l,b]]).reshape(1,4,2),H).reshape(4,2)
  im=base.copy();d=ImageDraw.Draw(im)
  d.line([tuple(p) for p in wall]+[tuple(wall[0])],fill=(0,255,255),width=2)
  d.line([tuple(p) for p in quad]+[tuple(quad[0])],fill=(255,45,45),width=2)
  for p in quad:d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill=(255,50,50))
  out.paste(im,(i*546,j*483))
  print(wn,k,np.round(quad,1).tolist(),'top slope',round((quad[1,1]-quad[0,1])/(quad[1,0]-quad[0,0]),3),'bottom slope',round((quad[2,1]-quad[3,1])/(quad[2,0]-quad[3,0]),3))
dest=Path(__file__).resolve().parent/"QA_wall_plane_candidates.png"
out.save(dest)
print(dest)
