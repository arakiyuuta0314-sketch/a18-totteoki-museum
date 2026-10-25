from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
root=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
img=Image.open(root/"50_エントランス完成候補_追加壁灯4点分離_v01"/"QA_all_four_sconces_on.png").convert("RGB")
roi=(0,296,85,409)
z=6
part=img.crop(roi).resize(((roi[2]-roi[0])*z,(roi[3]-roi[1])*z),Image.Resampling.NEAREST)
d=ImageDraw.Draw(part)
for x in range(0,85,5):
 d.line([(x*z,0),(x*z,113*z)],fill=(100,225,225),width=1)
 d.text((x*z+1,1),str(x),fill=(255,255,255),stroke_width=1,stroke_fill=(20,20,20))
for y in range(300,409,5):
 yy=(y-roi[1])*z;d.line([(0,yy),(85*z,yy)],fill=(100,225,225),width=1)
 d.text((1,yy+1),str(y),fill=(255,255,255),stroke_width=1,stroke_fill=(20,20,20))
path=Path(__file__).parent/"QA_desk_pixel_coordinate_grid.png";part.save(path);print(path)
