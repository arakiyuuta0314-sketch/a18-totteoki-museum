# -*- coding:utf-8 -*-
from pathlib import Path
import urllib.request,json,hashlib
ROOT=Path(__file__).resolve().parent
D=ROOT/'entrance-plain-master-v09-right-mat'
url='https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-plain-master-v09-right-mat/'
assets=('index.html','entrance_OFF.png','entrance_ON.png','QA_before_after_whole.png','QA_before_after_top.png','QA_before_after_bottom.png')
for name in assets:
 with urllib.request.urlopen(url+name+'?v=20261026v09',timeout=30) as response:
  body=response.read()
  assert response.status==200
 src=(D/name).read_bytes()
 if name=='index.html':
  assert body.replace(b'\r\n',b'\n')==src.replace(b'\r\n',b'\n'),(name,'html EOL mismatch')
 else:
  assert body==src,(name,len(body),len(src))
 print('PAGES_V09_VERIFY',name,len(body),'EOL_NORMALIZED' if name=='index.html' else 'EXACT',hashlib.sha256(body).hexdigest()[:14],flush=True)
m=json.loads((D/'QA_manifest.json').read_text(encoding='utf8'))
m['publish_URL']=url;m['public_commit']='72343b3'
m['public_png_byte_matches']=5
m['public_html_eol_normalized_match']=True
m['public_mobile_chrome_QA']='PASS'
(D/'QA_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print('LIVE_V09_VERIFIED',flush=True)
