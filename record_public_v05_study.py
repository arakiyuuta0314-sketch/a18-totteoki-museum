# -*- coding:utf-8 -*-
from pathlib import Path
import json
base=Path(r'C:\Users\User\source\repos\a18-entrance-art-polish-v03-20261026')
d=base/'entrance-rebuilt-background-panel-composite-v05-candidate'
p=d/'QA_manifest.json'
m=json.loads(p.read_text(encoding='utf8'))
m['public_qa']={'preview_commit':'026cd01',
 'live_url':'https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-wide-backwall-v05-study-20261026/',
 'pages_build':'success','mobile_chrome_390x844_DPR2':'PASS',
 'button_transitions':3,'comparison_switches':2,'javascript_http_errors':0,
 'exact_remote_png_matches':['entrance_OFF.png','entrance_ON.png','previous_v03_OFF.png','previous_v03_ON.png'],
 'visual_art_qa':'FAIL / review only'}
p.write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf8')
with (d/'README.md').open('a',encoding='utf8') as f:
 f.write('\n## 公開QA\n- Pages公開コミット 026cd01、390×844/DPR2ブラウザ操作と画像4点のリモート一致を検証済み。\n- 技術公開がPASSでも美術採用は不合格のまま。\n')
print('RECORDED')
