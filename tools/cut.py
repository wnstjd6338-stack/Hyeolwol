import sys,json,os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
import os as _o;SRC=_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))+'/incoming/fx_skill/'; OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)  # 사용: python3 tools/cut.py 출력폴더
PICK={'마법사3':{0:'mf0',1:'mf1',2:'mf2',3:'mf3',6:'mfox',7:'mf7',8:'mf8',9:'mf9',10:'mdrg',11:'mdb1',12:'mdb2',13:'mdb3',14:'mtail',15:'mclaw',18:'mwing'},
      '마법사2':{0:'mb0',1:'mb1',2:'mb2',3:'mb3',4:'mb4',5:'mb5',10:'mbo',11:'mbs',12:'mc1',13:'mc2',14:'mw',15:'mc3',16:'mb6',18:'mbd',19:'mb7'},
      '마법사1':{0:'mi0',2:'mi2',3:'mi3',5:'mi5',6:'mi6',7:'mi7',8:'mi8',9:'mi9',10:'mi10',12:'mi12',13:'mi13',14:'mi14',15:'mi15',16:'mi16',17:'mi17'}}
for sheet,pk in PICK.items():
  a=np.array(Image.open(SRC+sheet+'.png').convert('RGBA')).astype(np.float32)
  lum=(a[...,0]*.3+a[...,1]*.59+a[...,2]*.11)/255
  al=a[...,3]/255*np.clip(lum,0,1)**1.3; al[a[...,3]<40]=0
  m=nd.binary_dilation(al>.12,iterations=10); lab,n=nd.label(m); objs=nd.find_objects(lab)
  res=[]
  for i,s in enumerate(objs):
    y0,y1,x0,x1=s[0].start,s[0].stop,s[1].start,s[1].stop
    if (y1-y0)*(x1-x0)<3600: continue
    res.append((x0,y0,x1,y1,i+1))
  res.sort(key=lambda b:(round(b[1]/250),b[0]))
  for idx,name in pk.items():
    x0,y0,x1,y1,li=res[idx]
    alc=np.where(lab[y0:y1,x0:x1]==li,al[y0:y1,x0:x1],0)
    alc=np.clip((alc-.03)/.97,0,1)
    ys,xs=np.nonzero(alc>.02); alc=alc[ys.min():ys.max()+1,xs.min():xs.max()+1]
    h,w=alc.shape; P=int(max(h,w)*.04)+2
    alc=np.pad(alc,P); h,w=alc.shape; M=max(h,w); alc=np.pad(alc,(((M-h)//2,M-h-(M-h)//2),((M-w)//2,M-w-(M-w)//2)))
    im=Image.fromarray((alc*255).astype(np.uint8),'L')
    S=320 if name in('mdrg',) else 256
    k=S/max(im.size); 
    if k<1: im=im.resize((max(1,round(im.size[0]*k)),max(1,round(im.size[1]*k))),Image.LANCZOS)
    out=Image.new('RGBA',im.size,(255,255,255,0)); out.putalpha(im)
    out.save(f'{OUT}/k_{name}.webp','WEBP',lossless=True,method=6,exact=False)
    print(name,im.size,os.path.getsize(f'{OUT}/k_{name}.webp'))
