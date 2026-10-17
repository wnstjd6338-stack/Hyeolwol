import os as _os;R=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))+"/"
import numpy as np, json, sys, pickle
from PIL import Image
from scipy import ndimage
U=R+'incoming/'
def load(f,fringe=True,amin=100):
    a=np.array(Image.open(f if f.endswith('.png') else U+f+'-image.png').convert('RGBA')).copy()
    al=a[...,3].astype(int);r,g,b=[a[...,i].astype(int) for i in range(3)]
    kill=al<amin
    if fringe:
        kill|=(r>195)&(g<90)&(b<90)          # pure red halo
        kill|=(r>190)&(g>170)&(b<110)&(r-b>110) # yellow halo
        kill|=(al<230)&(r>g+70)&(r>b+70)
    a[...,3]=np.where(kill,0,a[...,3]);return a
def cuts(prof,n,frac=.32):
    L=len(prof);res=[0]
    for k in range(1,n):
        c=int(k*L/n);w=int(L/n*frac);lo,hi=max(1,c-w),min(L-1,c+w)
        seg=np.convolve(prof,np.ones(7)/7,'same')[lo:hi];res.append(lo+int(np.argmin(seg)))
    res.append(L);return res
def frames(a,rows,cols,keep=.02,grow=4,xcuts=None,ycuts=None):
    m=a[...,3]>0
    ys=ycuts or cuts(m.sum(1),rows);out=[]
    for r in range(rows):
        band=m[ys[r]:ys[r+1]]
        xs=xcuts or cuts(band.sum(0),cols)
        for c in range(cols):
            sub=a[ys[r]:ys[r+1],xs[c]:xs[c+1]].copy();sm=sub[...,3]>0
            lab,n=ndimage.label(ndimage.binary_dilation(sm,iterations=grow))
            if n==0: out.append(None);continue
            sz=ndimage.sum(sm,lab,range(1,n+1));big=sz.max()
            ok=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>=big*keep])
            sub[...,3]=np.where(ok&sm,sub[...,3],0)
            # main body = largest component (for anchor/height)
            main=lab==(np.argmax(sz)+1)
            im=Image.fromarray(sub,'RGBA');bb=im.getbbox()
            mb=np.argwhere(main&sm);my0,mx0=mb.min(0);my1,mx1=mb.max(0)
            out.append(dict(im=im.crop(bb),bb=bb,main=(mx0-bb[0],my0-bb[1],mx1-bb[0],my1-bb[1])))
    return out
def build(fr,name,outH,ref='first',anchor='bottom',refh=None):
    fr=[f for f in fr if f]
    anc=[];base=[]
    for f in fr:
        a=np.array(f['im'])[...,3]>0;mx0,my0,mx1,my1=f['main'];h=my1-my0
        band=a[my0+int(h*.7):my1+1,mx0:mx1+1];xs=np.where(band)[1]+mx0
        anc.append(float(np.median(xs)) if len(xs) else (mx0+mx1)/2);base.append(my1)
    AL=max(anc);AR=max(f['im'].size[0]-x for f,x in zip(fr,anc))
    up=max(b for b in base);down=max(f['im'].size[1]-1-b for f,b in zip(fr,base))
    W=int(np.ceil(AL+AR));Hc=int(up+down+1)
    hs=[f['main'][3]-f['main'][1] for f in fr]
    refh=refh or (hs[0] if ref=='first' else float(np.median(hs)))
    s=outH/Hc;fw=max(1,round(W*s));n=len(fr)
    strip=Image.new('RGBA',(fw*n,outH),(0,0,0,0))
    for i,(f,x,b) in enumerate(zip(fr,anc,base)):
        c=Image.new('RGBA',(W,Hc),(0,0,0,0));c.alpha_composite(f['im'],(int(round(AL-x)),int(up-b)))
        strip.alpha_composite(c.resize((fw,outH),Image.LANCZOS),(i*fw,0))
    strip.save(R+f'img/{name}.webp','WEBP',quality=84,method=6);strip.save(f'{name}.png')
    meta=dict(n=n,ax=round(AL/W,4),ay=round((up+1)/Hc,4),hs=round(Hc/refh,4))
    print(name,meta,'strip',strip.size);return meta
META={}
if __name__=='__main__':
  def walk6(f,cls,fr=True):
    a=load(f,fringe=fr);fs=frames(a,2,6)
    META[cls+'_walkL']=build(fs[:6],cls+'_walkL',240,'median');META[cls+'_walkR']=build(fs[6:],cls+'_walkR',240,'median')
  walk6('7be696a5','archer');walk6('fd94fce2','mage');walk6('177b772d','warrior');walk6('89ac813d','healer')
  json.dump(META,open('meta1.json','w'))
