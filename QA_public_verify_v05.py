import urllib.request,hashlib
from pathlib import Path
d=Path(r'C:\Users\User\source\repos\a18-entrance-art-polish-v03-20261026\entrance-rebuilt-background-panel-composite-v05-candidate')
b='https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-wide-backwall-v05-study-20261026/'
for fn in ('entrance_OFF.png','entrance_ON.png','previous_v03_OFF.png','previous_v03_ON.png'):
 with urllib.request.urlopen(b+fn,timeout=20) as r:
  data=r.read()
 local=(d/fn).read_bytes()
 assert data==local,(fn,len(data),len(local))
 print('LIVE_MATCH',fn,len(data),hashlib.sha256(data).hexdigest()[:12])
