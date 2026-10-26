from pathlib import Path
import urllib.request,hashlib,json
base=Path(r'C:\Users\User\source\repos\a18-entrance-plain-master-v06-20261026\entrance-plain-master-v06-study')
url='https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-plain-master-v06-study/'
for fn in ('entrance_OFF.png','reference_v05_OFF.png','QA_ceiling_before_after.png','QA_left_back_before_after.png','QA_right_back_before_after.png'):
 with urllib.request.urlopen(url+fn+'?v=20261026v06',timeout=25) as f:content=f.read();assert f.status==200
 assert content==(base/fn).read_bytes(),fn
 print('LIVE_BYTES_MATCH',fn,len(content),hashlib.sha256(content).hexdigest()[:14])
manifest=base/'QA_manifest.json'
data=json.loads(manifest.read_text(encoding='utf8'))
data['published_URL']=url
data['published_commit']='a89926b'
data['published_mobile_Chrome_QA']='PASS'
data['published_image_byte_identity']='PASS_5_of_5'
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('LIVE_VERIFIED')
