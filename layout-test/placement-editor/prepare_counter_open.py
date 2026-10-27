"""Controlled single-object edit: delete chair/books in existing independent counter.
Photo, walls, background and save data never touched. Output is preview only.
"""
from PIL import Image
from pathlib import Path
import hashlib
from numpy import asarray,array
BASE=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\65_配置エディター実素材_20261027\counter_original.png")
OUT=Path(__file__).resolve().parent
EXPECTED="cfd66ca09b6c25a48b67f0e6b0c4ec59eee251efe2bb84d1c4490301d8ac5b44"
assert BASE.is_file() and hashlib.sha256(BASE.read_bytes()).hexdigest()==EXPECTED
original=Image.open(BASE).convert("RGBA")
assert original.size==(1086,1448)
pixels=asarray(original).copy()
# Only the interior, behind the L-shaped counter, is cleared.
# Keep cream marble countertop and its front woodwork intact.
for y in range(555):
    for x in range(650):
        rr,gg,bb,aa=map(int,pixels[y,x])
        if y<529 or (y<554 and not(rr>170 and gg>128 and bb>85)):
            pixels[y,x,3]=0
changed=Image.fromarray(pixels,"RGBA")
before=asarray(original)
# Strict difference fence: outside 0<=x<650, 0<=y<555 every RGBA sample identical.
assert (pixels[555:,:,:]==before[555:,:,:]).all()
assert (pixels[:,:][:,650:,:]==before[:,:][:,650:,:]).all()
assert (pixels[:,:,:3]==before[:,:,:3]).all()
assert int((pixels[:,:,3]!=before[:,:,3]).sum())>35000
cropped=changed.crop(changed.getchannel("A").getbbox())
preview=cropped.copy()
preview.thumbnail((420,740),Image.Resampling.LANCZOS)
path=OUT/"counter-open.webp"
preview.save(path,format="WEBP",quality=93,method=4)
check=Image.open(path).convert("RGBA")
assert check.getchannel("A").getextrema()[0]==0 and check.size[0]>=350
print("PASS: original SHA, alpha-only, chair/book region cleared, intact marble/front")
print("OUTPUT",path,check.size,path.stat().st_size)
