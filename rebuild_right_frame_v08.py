# -*- coding: utf-8 -*-
"""A18 v08: restore complete right foreground wood photo frame from formal v07 PNG.
v07 undecorated architectural master is immutable; ON is an independent layer.
"""
from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json,shutil
BASE=Path(__file__).resolve().parent
OLD=BASE/'entrance-plain-master-v07-right-column'
OUT=BASE/'entrance-plain-master-v08-right-frame'
OUT.mkdir(exist_ok=True)
G=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
D49=next(x for x in G.iterdir() if x.is_dir() and x.name.startswith('49_'))
base=Image.open(OLD/'entrance_OFF.png').convert('RGBA')
wood=Image.open(D49/'right_front_frame_wood.png').convert('RGBA')
mask=Image.open(D49/'right_front_shared_window_mask.png').convert('L')
assert base.size==wood.size==mask.size==(546,483)
# The published OFF base must not mutate even by PNG re-encoding.
shutil.copy2(OLD/'entrance_OFF.png',OUT/'entrance_OFF.png')
on=base.copy()
on.alpha_composite(wood)
on=on.convert('RGB')
on.save(OUT/'entrance_ON.png',optimize=True)
wood.save(OUT/'right_front_frame_wood_formal_v07.png',optimize=True)
shutil.copy2(OLD/'entrance_OFF.png',OUT/'reference_v07_OFF.png')
m=np.asarray(wood.getchannel('A'))>0
a=np.asarray(base.convert('RGB'));b=np.asarray(on)
dif=np.any(a!=b,axis=2)
assert int(dif.sum())>2500
assert not np.any(dif&~m),'other architectural structure altered'
window=np.asarray(mask)>0
assert not np.any(window & m),'frame alpha intrudes into photo window'
# Ensure the right rear column was actually retained from v07.
assert np.array_equal(a[:213,513:546],b[:213,513:546])
# 546x483, formal subject, position, and geometry all preserved.
qa=Image.new('RGB',(1092,483))
qa.paste(base.convert('RGB'),(0,0));qa.paste(on,(546,0))
qa.save(OUT/'QA_off_vs_full_frame.png',optimize=True)
for label,box in [('right_front',(387,151,536,388)),('top_corner',(406,157,515,250)),('lower_edge',(415,293,523,380))]:
 x0,y0,x1,y1=box;w=3*(x1-x0);h=3*(y1-y0)
 pair=Image.new('RGB',(2*w,h))
 for idx,source in enumerate((base.convert('RGB'),on)):
  pair.paste(source.crop(box).resize((w,h),Image.Resampling.NEAREST),(idx*w,0))
 pair.save(OUT/('QA_'+label+'_comparison.png'),optimize=True)
Image.fromarray(m.astype(np.uint8)*255).save(OUT/'QA_formal_frame_allowed_mask.png')
Image.fromarray(dif.astype(np.uint8)*255).save(OUT/'QA_actual_pixel_diff.png')
report={
 'version':'v08','approval':'art_review_pending','canvas':[546,483],
 'OFF_base':'v07 c4257f2 exact original PNG bytes unchanged',
 'ON_frame':'49 formal right_front_frame_wood.png, 546x483 registered',
 'reason':'v07 plain OFF omitted optional frame; no evidence that v07 pillar compositing removed it',
 'v07_OFF_sha256':hashlib.sha256((OLD/'entrance_OFF.png').read_bytes()).hexdigest(),
 'v08_OFF_sha256':hashlib.sha256((OUT/'entrance_OFF.png').read_bytes()).hexdigest(),
 'frame_source_sha256':hashlib.sha256((D49/'right_front_frame_wood.png').read_bytes()).hexdigest(),
 'ON_minus_OFF_changed_pixels':int(dif.sum()),
 'wood_alpha_area':int(m.sum()),
 'changed_pixels_outside_frame_alpha':int(np.sum(dif&~m)),
 'frame_overlap_with_registered_window':int(np.sum(window&m)),
 'right_rear_column_unchanged':True,
 'other_architecture_people_unchanged':True,
 'game_integrated':False,'lv1_decided':False,
 'note':'OFF is still intentionally a frame-less architecture base; ON displays the restored formal 49 frame. Art quality not yet approved.'
}
(OUT/'QA_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('V08_BUILD_QA_PASS',json.dumps({k:report[k] for k in ('ON_minus_OFF_changed_pixels','wood_alpha_area','changed_pixels_outside_frame_alpha','frame_overlap_with_registered_window','right_rear_column_unchanged')}))
