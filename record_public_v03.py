# -*- coding:utf-8 -*-
from pathlib import Path
import json
BASE=Path(__file__).resolve().parent
D=BASE/"entrance-art-polish-v03-20261026"
M=D/"QA_manifest.json"
m=json.loads(M.read_text(encoding="utf8"))
m["public_qa"]={"url":"https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-art-polish-v03-20261026/",
 "pages_commit":"2aaa38e","pages_deployment":"success",
 "mobile_chrome_390x844_dpr2":"PASS",
 "off_on_buttons":"PASS","side_by_side_toggle":"PASS","three_zoom_views":"PASS",
 "console_js_http_errors":0,"horizontal_overflow":False,
 "http_files_identical_to_local":["entrance_OFF.png","entrance_ON.png","QA_zoom_rear_left.png","QA_zoom_rear_right.png","QA_zoom_right_front.png"]}
M.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf8")
with (D/"README.md").open("a",encoding="utf8") as f:
 f.write("\n## 公開配信QA\n")
 f.write("- GitHub Pagesコミット: 2aaa38e。実際のURLで390×844 DPR2 Chromeボタン3回、比較切替2回、拡大3点すべて正常。HTTP/JSエラー0。\n")
 f.write("- 公開PNG5点について、ローカル正式成果物とバイト単位で一致することを確認。\n")
print("PUBLIC_QA_RECORDED")
