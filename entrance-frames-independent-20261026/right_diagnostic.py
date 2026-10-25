from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).resolve().parent
pics=["QA_01_no_ornate_frames.png","QA_02_simple_wood_frames.png","QA_04_gold_full_restored.png"]
out=Image.new("RGB",(360*3,600),(250,250,250))
for i,n in enumerate(pics):
 im=Image.open(p/n).convert("RGB").crop((392,163,512,363)).resize((360,600),Image.Resampling.NEAREST)
 out.paste(im,(i*360,0))
out.save(p/"QA_right_frame_3states_3x.png")
