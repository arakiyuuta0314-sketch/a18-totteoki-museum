from pathlib import Path
import urllib.request,hashlib,json
r=Path(r'C:\Users\User\source\repos\a18-entrance-plain-master-v06-20261026')
d=r/'entrance-plain-master-v08-right-frame'
url='https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-plain-master-v08-right-frame/'
names=('index.html','entrance_OFF.png','entrance_ON.png','QA_right_front_comparison.png','QA_top_corner_comparison.png','QA_lower_edge_comparison.png')
for n in names:
 with urllib.request.urlopen(url+n+'?v=20261026v08',timeout=25) as h:
  body=h.read();assert h.status==200,(n,h.status)
 expected=(d/n).read_bytes()
 if n=='index.html':
  assert body.replace(b'\r\n',b'\n')==expected.replace(b'\r\n',b'\n')
 else:
  assert body==expected,(n,len(body),len(expected))
 print('PAGES_V08_VERIFIED',n,len(body),flush=True)
manifest=d/'QA_manifest.json'
m=json.loads(manifest.read_text(encoding='utf8'))
m['published_url']=url;m['publish_commit']='d0d5bd5'
m['published_artifact_verification']='5 PNGs byte-identical; HTML EOL-normalized identical'
m['mobile_published_Chrome_QA']='PASS'
manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print('PUBLISHED_AND_BYTES_VERIFIED',flush=True)
