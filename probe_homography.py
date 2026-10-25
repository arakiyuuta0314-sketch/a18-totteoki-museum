import numpy as np,cv2
s=np.float32([[84,61],[193,61],[193,143],[84,143]])
t=np.float32([[426,201],[489,226],[489,323],[426,276]])
M=cv2.getPerspectiveTransform(s,t)
for n,x in [("source_outer",[[76,50],[200,50],[200,156],[76,156]]),("source_inner",s.tolist())]:
 mapped=cv2.perspectiveTransform(np.float32(x).reshape(1,4,2),M).reshape(4,2)
 print(n,mapped)
print("M",M)
