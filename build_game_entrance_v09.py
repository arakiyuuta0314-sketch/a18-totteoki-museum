"""Derive gameplay-safe architecture + photo-window masks from approved v09 OFF.
Original art remains immutable; fail when source hashes/geometries drift.
"""
from pathlib import Path
from PIL import Image
import numpy as np, cv2, json, hashlib
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'entrance-plain-master-v09-right-mat'/'entrance_OFF.png'
CLEAN=ROOT/'entrance-wood-onoff-v01-20261026'/'entrance_OFF_no_characters.png'
FRONT=ROOT/'entrance-wall-plane-v07-20261026'/'right_front_shared_window_mask.png'
OUT=ROOT/'layout-test'/'assets'/'entrance'/'v09'
OUT.mkdir(parents=True,exist_ok=True)
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(SRC)=='1cf45e2d2edca55f142af07b28e15b8d2cfe05fd4f4de421facd6b3b5f5dfc1c'
a=np.array(Image.open(SRC).convert('RGB'))
b=np.array(Image.open(CLEAN).convert('RGB'))
assert a.shape==b.shape==(483,546,3)
region=np.zeros((483,546),bool)
region[305:384,111:171]=True
region[305:384,258:320]=True
changes=region & np.any(a!=b,axis=2)
assert changes.sum()==1934,changes.sum()
assert not np.any(changes[[305,383],:]) and not np.any(changes[:,[111,319]])
final=a.copy()
final[changes]=b[changes]
assert np.array_equal(a[~changes],final[~changes])
assert np.array_equal(b[changes],final[changes])
Image.fromarray(final).save(OUT/'entrance_architecture_v09.png', optimize=True)

# Extract the two rear luminous paper interiors from the canonical frame-OFF.
# Masks do not bake the screenshot's source content into gameplay.
mask_meta={}
for name,(x0,y0,x1,y1),min_area in [
 ('rear_left',(30,48,204,160),11000),
 ('rear_right',(357,48,520,162),10000)]:
 sub=final[y0:y1,x0:x1]
 red,green,blue=[sub[:,:,k] for k in range(3)]
 candidate=np.uint8((red>125)&(green>100)&(blue>64))
 n,lab,stats,cent=cv2.connectedComponentsWithStats(candidate,8)
 assert n>=2
 idx=1+np.argmax(stats[1:,4])
 s=stats[idx]
 assert s[4]>=min_area, (name,s)
 # One-pixel inset keeps the original architectural edging intact.
 component=np.uint8(lab==idx)
 component=cv2.erode(component,np.ones((3,3),np.uint8),iterations=1)
 out=np.zeros((483,546),np.uint8)
 out[y0:y1,x0:x1]=component*255
 yy,xx=np.where(out>0)
 rect=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 assert rect[2]-rect[0]>100 and rect[3]-rect[1]>70,(name,rect)
 Image.fromarray(out,'L').save(OUT/f'{name}_photo_mask_v09.png', optimize=True)
 mask_meta[name]={'rect':rect,'pixels':int((out>0).sum())}
front=np.array(Image.open(FRONT).convert('L'))
assert front.shape==(483,546)
assert int((front>0).sum())==6595
Image.fromarray(front,'L').save(OUT/'front_photo_mask_v09.png', optimize=True)
mask_meta['front']={'rect':[421,195,494,326],'pixels':int((front>0).sum())}
manifest={
  'version':'a18-entrance-game-v09-v1',
  'canvas':[546,483],
  'source_v09_OFF':str(SRC.relative_to(ROOT)).replace('\\','/'),
  'source_sha256':digest(SRC),
  'old_character_free_source':str(CLEAN.relative_to(ROOT)).replace('\\','/'),
  'front_mask_original':str(FRONT.relative_to(ROOT)).replace('\\','/'),
  'char_pixels_replaced':int(changes.sum()),
  'changed_pixels_outside_characters':0,
  'masks':mask_meta,
  'derived_files':{p.name:digest(p) for p in sorted(OUT.glob('*.png'))},
  'status':'isolated_integration_staging_not_released',
}
(OUT/'entrance_game_v09_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('BASE_QA_PASS changed_char_pixels',len(np.where(changes)[0]),'masks',mask_meta)
for fn,sha in manifest['derived_files'].items():print(fn,sha)
