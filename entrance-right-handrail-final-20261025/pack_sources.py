from pathlib import Path
from shutil import copy2
R=Path(r"C:\Users\User\source\repos\a18-entrance-right-handrail-20261025")
A=R/"entrance-right-frame-final-20261025"
D=R/"entrance-right-handrail-final-20261025"
for src,name in [("entrance_photo_frame_03.png","source_frame_03.png"),("entrance_photo_empty_03.png","source_frame_empty_03.png"),("demo_photo_03_warped.png","source_photo_03.png")]:
 copy2(A/src,D/name)
print("CROSS_ART_REFERENCES_COPIED")