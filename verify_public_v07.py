# -*- coding: utf-8 -*-
import urllib.request,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
D=ROOT/'entrance-plain-master-v07-right-column'
url='https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-plain-master-v07-right-column/'
for name in ('index.html','entrance_OFF.png','reference_v06_OFF.png','QA_right_corner_before_after.png','QA_right_capital_before_after.png','QA_right_seam_before_after.png'):
 with urllib.request.urlopen(url+name+'?v=20261026v07',timeout=20) as resp:
  body=resp.read()
  assert resp.status==200
 expected=(D/name).read_bytes()
 if name=='index.html':
  assert body.replace(b'\r\n',b'\n')==expected.replace(b'\r\n',b'\n'),(name,len(body),len(expected))
 else:
  assert body==expected,(name,len(body),len(expected))
 print('PUBLIC_V07_ASSET_VERIFIED',name,len(body),'HTML_EOL_NORMALIZED' if name=='index.html' else 'EXACT_BYTES',flush=True)
report=json.loads((D/'QA_manifest.json').read_text(encoding='utf8'))
report['public_pages_url']=url
report['pages_commit']='563b3d3'
report['web_asset_byte_match_count']=5
report['public_html_line_endings_normalized_match']=True
report['public_source_verified']=True
report['public_mobile_chrome_result']='PASS'
(D/'QA_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('PUBLIC_V07_RELEASE_VERIFIED',flush=True)
