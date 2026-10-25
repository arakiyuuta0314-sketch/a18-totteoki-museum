from PIL import Image
from pathlib import Path
import numpy as np,json,hashlib
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
S=Path(__file__).resolve().parent/"lighting-additional-sconces-v01"
manifest=json.loads((S/"QA_manifest.json").read_text(encoding="utf-8"))
ref=np.asarray(Image.open(ROOT/"43_エントランス完成素材_3額縁本体装飾分離_v01"/"entrance_bare_three_frame_backing.png").convert("RGB"))
base=np.asarray(Image.open(ROOT/"49_エントランス完成素材_右手前壁面基準再投影_v07"/"view_wood_empty_100.png").convert("RGB"))
off=np.asarray(Image.open(S/"QA_all_four_sconces_off.png").convert("RGB"))
on=np.asarray(Image.open(S/"QA_all_four_sconces_on.png").convert("RGB"))
allowed=np.zeros((483,546),bool)
qa={}
for name,roi in manifest["rectangles"].items():
 l,t,r,b=roi;allowed[t:b,l:r]=True
 body=Image.open(S/f"fixture_{name}_body.png").convert("RGBA")
 glow=Image.open(S/f"fixture_{name}_emission.png").convert("RGBA")
 assert body.size==glow.size==(r-l,b-t)
 n_body=np.count_nonzero(np.asarray(body.getchannel("A")))
 n_glow=np.count_nonzero(np.asarray(glow.getchannel("A")))
 assert n_body>100 and n_glow>100,(name,n_body,n_glow)
 diff=np.max(np.abs(ref[t:b,l:r].astype(np.int16)-base[t:b,l:r].astype(np.int16)),axis=2)>4
 # Pixels differing from 43 background in latest 49 are treated as approved new foreground.
 assert np.array_equal(off[t:b,l:r][diff],base[t:b,l:r][diff]),(name,"approved current art overwritten off")
 # Also on-state may have transparent sprite where 49 has a new foreground element.
 assert np.array_equal(on[t:b,l:r][diff],base[t:b,l:r][diff]),(name,"approved current art overwritten on")
 qa[name]={"body_alpha_pixels":int(n_body),"emission_alpha_pixels":int(n_glow),
           "preserved_latest_foreground_pixels":int(diff.sum())}
assert np.array_equal(off[~allowed],base[~allowed])
assert np.array_equal(on[~allowed],base[~allowed])
diffOff=np.any(off!=base,axis=2)
assert diffOff.any()
manifest["technical_QA"]={
 "result":"PASS",
 "outside_4_registered_rectangles_changed_pixels_off":int(np.count_nonzero(np.any(off!=base,axis=2)&~allowed)),
 "outside_4_registered_rectangles_changed_pixels_on":int(np.count_nonzero(np.any(on!=base,axis=2)&~allowed)),
 "v49_new_frame_pixels_preserved":True,
 "fixtures":qa,
 "mobile_browser_states":32,
 "off_background_exact_source":False,
 "photo_input_game_integrated":False
}
manifest["files_sha256"]={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in S.glob("fixture_*.png")}
(S/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("QA_CONTRACT_PASS",json.dumps(manifest["technical_QA"],ensure_ascii=False))
