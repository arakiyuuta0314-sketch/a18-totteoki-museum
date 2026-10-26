# -*- coding: utf-8 -*-
from pathlib import Path
import json,shutil,zipfile
BASE=Path(__file__).resolve().parent
OUT=BASE/'entrance-plain-master-v06-study'
meta=OUT/'QA_manifest.json'
obj=json.loads(meta.read_text(encoding='utf8'))
obj["local_browser_QA"]={"viewport":[390,844],"DPR":2,"Chrome_result":"PASS","switch_new_previous":2,"zoom_images_loaded":3,"HTTP_JS_errors":0}
obj["remaining_art_issues"]=["thin aged matte edging has rough pixels","central gold hanging architectural ornament still visible","some upper wooden cornice joins and perspective require manual aesthetic approval","architectural base rebuilt synthetically from existing texture; not recovered hidden original"]
meta.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
readme="""# A18 エントランス無装飾背景・構造再構築 v06（試作・未承認）
2026-10-26

## 目的・元データ
- 55番(v05未承認)の「左右端の柱、拡張された2つの背面展示面」を大枠として継承。
- 画像生成は使用しない。既存の546x483公式素材のみを下地とし、天井の木部・緑壁面を色パレット・周辺実画像から再構築。
- 木製額縁ONを主役にせず、OFF無装飾版だけを基準候補にする。
- 床、扉、手すり、受付、既存キャラクターは固定。 y>=212 のすべての画素、および中央扉領域は旧版と完全一致。
- 構造を縦横に一括変形しない。

## 今回作成
- entrance_OFF.png：新しい無装飾基準候補
- reference_v05_OFF.png：前回の拡幅構図、実際の原画を保持
- QA_*before_after.png / QA_before_after.jpg：再修復部分の画像
- QA_rebuilt_material_mask.png：再合成した画素
- index.html：スマホ切替・拡大できる比較ページ
- rebuild_plain_v06.py：合成ソース
- QA_browser_v06.cjs：390x844ChromeブラウザQA
- QA_manifest.json：作成経緯・不変領域・残課題

## 実行QA
- Python局所素材再構築を実行。画像546×483。
- 旧v05と比較して変更は天井・背面左右の緑壁面のみ。下半分、ドア、前景・キャラは不変。
- Chrome mobile 390x844 DPR2で切替、写真拡大3点、表示、HTTP/JavaScriptエラーなし。
- 現在はユーザー美術QA待ち。**完成背景マスターとして固定しない**。

## 未解決（実画像検査済み）
- 照明跡を面単位で直したが、完全に新規レンダリングした建築ではないため木部の継ぎ目・自然さには未解決箇所あり。
- 緑壁面と空き写真台紙の1〜2pixelの縁が一部荒い。
- 扉上の中央金具は元の建築から維持。装飾としてさらに除くか未決定。
- 写真展示枠木製ONの再構成は、このOFF版への美術承認後に独立工程。

## Git保護
既存アプリ本体・main・旧v05・v03は変更しない。独立worktreeのみ。
"""
(OUT/'README.md').write_text(readme,encoding='utf8')
print('V06_DOCS_COMPLETE')
