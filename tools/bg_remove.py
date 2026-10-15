import os as _os;R=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))+"/"
import onnxruntime as ort,numpy as np,sys
from PIL import Image
U=R+'incoming/'
S=ort.InferenceSession(R+'tools/isnet-anime.onnx',providers=['CPUExecutionProvider'])
def mask(im):
  x=im.convert('RGB').resize((1024,1024),Image.LANCZOS);a=np.array(x).astype(np.float32)/255.
  a=(a-np.array([.485,.456,.406]))/np.array([1,1,1]);a=a.transpose(2,0,1)[None].astype(np.float32)
  o=S.run(None,{S.get_inputs()[0].name:a})[0][0,0];o=(o-o.min())/(o.max()-o.min()+1e-8)
  return Image.fromarray((o*255).astype(np.uint8)).resize(im.size,Image.LANCZOS)
NM={'a6dab709':'healer','d78563fc':'mage','ebf640e0':'warrior','46ef035c':'archer','4c3dead4':'gumiho','5f64c0ed':'guardian','4eccf7a7':'king','f92cce1f':'reaper','cbbad5d5':'npc','47442d6d':'smith','a9bf2f0a':'seol','9d954267':'dragon','4f00cf19':'yeoni'}
for f,n in NM.items():
  im=Image.open(U+f+'-image.png').convert('RGBA')
  m=np.array(mask(im)).astype(np.float32)/255
  a=np.array(im)
  if (a[...,3]<255).mean()>.05: al=a[...,3].astype(np.float32)/255*np.clip(m*1.4,0,1)  # already transparent: keep alpha, clean
  else: al=np.clip((m-.08)/.84,0,1)
  a[...,3]=(al*255).astype(np.uint8)
  Image.fromarray(a).save(f'raw_{n}.png');print(n,im.size)
