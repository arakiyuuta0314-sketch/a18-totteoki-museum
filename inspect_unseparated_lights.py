# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
orig=Image.open(P/"43_エントランス完成素材_3額縁本体装飾分離_v01"/"entrance_bare_three_frame_backing.png").convert("RGB")
rects={
"left_outer_wall":(30,70,70,147),
"right_outer_wall":(465,70,507,147),
"right_front_inner":(381,195,426,287),
"right_front_outer":(488,241,533,328),
"counter_lamp":(5,303,55,385),
"ceiling_lamps":(0,0,546,45),
}
board=Image.new("RGB",(4*320,2*360),(35,41,42))
for i,(name,rect) in enumerate(rects.items()):
 crop=orig.crop(rect)
 crop.thumbnail((298,294),Image.Resampling.NEAREST)
 sz=(int(crop.width*min(298/crop.width,295/crop.height)),int(crop.height*min(298/crop.width,295/crop.height)))
 crop=crop.resize(sz,Image.Resampling.NEAREST)
 x=(i%4)*320+8; y=(i//4)*360+29
 board.paste(crop,(x,y))
 d=ImageDraw.Draw(board);d.text((x,y-21),name,fill="white")
path=Path(__file__).parent/"QA_unseparated_light_source_crops.png"
board.save(path)
print("WROTE",path)
