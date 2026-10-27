"""Fail-fast confirmation that editor uses verified independent art, not SVG stand-ins."""
from PIL import Image
from pathlib import Path
import hashlib
HOME=Path(__file__).resolve().parent
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\65_配置エディター実素材_20261027")
SOURCE={
"counter_original.png":"cfd66ca09b6c25a48b67f0e6b0c4ec59eee251efe2bb84d1c4490301d8ac5b44",
"wall_original.png":"22835c06450257f81f7d23eea092e164bc101c7574c37e9af1a3b3ac35f1141a",
}
for n,sha in SOURCE.items():
 p=ROOT/n
 assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==sha,(n,"source mutated")
for name in ("counter-real.webp","wall-real-noframe.webp"):
 p=HOME/name;im=Image.open(p)
 assert im.mode=="RGBA" and im.getchannel("A").getextrema()[0]==0,(name,"not transparent")
 assert p.stat().st_size>20000
 assert im.width>=330 and im.height>=500
wall=Image.open(HOME/"wall-real-noframe.webp").convert("RGBA")
ctr=wall.getpixel((wall.width//2,wall.height//2))
assert ctr[1]>ctr[0]*1.4 and ctr[1]>ctr[2]*0.9,(ctr,"frame/mat still in center")
html=(HOME/"index.html").read_text(encoding="utf-8")
assert 'src="./counter-real.webp"' in html
assert 'src="./wall-real-noframe.webp"' in html
assert 'src="./counter.svg"' not in html and 'src="./wall.svg"' not in html
assert (HOME/"reference-game.png").is_file()
print("PASS | immutable original PNG checksums, translucent alpha, central green wall, actual assets loaded")
