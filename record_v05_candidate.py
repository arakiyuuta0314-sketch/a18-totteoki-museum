from pathlib import Path
import shutil,zipfile,json,hashlib
repo=Path(r'C:\Users\User\source\repos\a18-entrance-art-polish-v03-20261026')
d=repo/'entrance-rebuilt-background-panel-composite-v05-candidate'
manifest=json.loads((d/'QA_manifest.json').read_text(encoding='utf8'))
manifest['qa']={'mobile_chrome_390x844_DPR2':'PASS','html_works':True,
  'geometry':'prototype','art_quality':'NOT_APPROVED','room_floor_door_NPC_foreground_exact':True,
  'lamp_residual_status':'not solved by this iteration',
  'rear_right_frame_derived_from_left_source':'yes mirrored as geometry prototype; NOT formal independent right frame',
  'wood_seam_status':'visible artifacts; requires rebuilding from matching baseline'}
(d/'QA_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
readme='''# A18 広幅背面展示枠・端柱の構図試作 v05（未承認）
2026-10-26

**これは採用済みの新背景ではない。美術QA未合格の比較試作。ゲーム本体・既存のPages v03は変更しない。**

## 目的
- 背面の左右展示面を両端へ広げ、両端の柱を構図上移した場合の見え方を確認する。
- 546×483、正式キャラクター原本、中央扉、床、受付と左右手前展示面を変えない。
- 赤絨毯・額縁OFF/ONの2状態をスマホで比較する。
- AI画像生成は使わず、既存の写真PNGと分離された前景透明マスクのみを使う。

## 原本の確認
- v03技術候補: Git 26b2466、正式採用ではない。
- 24番の別構図画像、22・23番Blender試作、28番背面枠、40/41番合成画像の実物を確認。
- 過去の「左右端まで拡げて端に柱」の完成画像として完全に一致する正式原本は確認できなかった。その画像の再使用とは主張しない。

## 今回の技術
- 背景全体を座標変形する試作v04は、前景手すりと右側展示壁の重複・破綻が生じたため不採用。
- v05では左右背面展示パネル・下部木製壁・端の柱のみの範囲を別々に既存画像から再合成。
- 背面右の元枠形状そのままではない。暫定の左右対称案として左の背景パネル画像を反転使用。ここは正式化前に右の分離額縁から作り直す必要がある。
- 既存の前景透過マスク27/32/39を使い、キャラ・北扉・床・受付の画素維持を検証。

## 美術QA（不合格／要再製作）
- 木製壁の接合部・柱の端、右手前との重なりに違和感が残る。
- v03を土台にした照明跡はこの工程では根本解決していない。
- 写真台紙の厳密な窓変形、右背面独立フレーム、壁/柱の透過素材化は未完了。
- Lv.1のOFF/ON採否は未決定。現在の本番背景との入れ替えを行わない。

## 公開目的
旧v03とv05試作の構図比較、およびv05試作内部で木製額縁OFF/ON比較するための一時的なプレビュー。
'''
(d/'README.md').write_text(readme,encoding='utf8')
R=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
assert R.exists()
dest=R/'55_エントランス背面展示拡幅_柱端配置_構図試作_v05_未承認'
dest.mkdir(exist_ok=True)
for p in d.iterdir():
 if p.is_file():shutil.copy2(p,dest/p.name)
for nm in ('build_architecture_panel_v05_candidate.py','prepare_v05_candidate_page.py','QA_public_verify_v05.py','record_public_v05_study.py','record_v05_candidate.py'):
 shutil.copy2(repo/nm,dest/nm)
# Rejected v04 evidence only; no merge with the selected candidate.
p4=repo/'entrance-rebuilt-background-wide-panels-v04-candidate'
if (p4/'QA_legacy_vs_new_OFF_ON.png').exists():
 shutil.copy2(p4/'QA_legacy_vs_new_OFF_ON.png',dest/'QA_rejected_v04_distorted_foreground.png')
z=dest/'A18_v05_architecture_comparison_UNAPPROVED.zip'
if z.exists():z.unlink()
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED) as arch:
 for p in dest.iterdir():
  if p.is_file() and p!=z:arch.write(p,p.name)
with zipfile.ZipFile(z) as arch:assert arch.testzip() is None
print('DRIVE_CANDIDATE_SAVED',str(dest),z.stat().st_size,len(list(dest.iterdir())),flush=True)
