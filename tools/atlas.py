import os as _os;R=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))+"/"
import json,glob,os
from PIL import Image
I=R+'img/'
used_fx=['fx_m_fox','fx_m_tal','fx_m_dragon','fx_w_ghost','fx_a_arrow','fx_h_cross']
G1=sorted(glob.glob(I+'k_*.webp'))+[I+f+'.webp' for f in used_fx]
G2=sorted(glob.glob(I+'eq_*.webp')+glob.glob(I+'ic_*.webp')+glob.glob(I+'sk_*.webp')+glob.glob(I+'mi_*.webp')+glob.glob(I+'pot_*.webp')+glob.glob(I+'hud_*.webp'))
PAD=4;MAXW=2048;MAXH=2048
def pack(files,name,ui):
    ims=[(f,Image.open(f).convert('RGBA')) for f in files];ims.sort(key=lambda t:(-t[1].size[1],-t[1].size[0]))
    out=[];cur=[];x=y=PAD;rowh=0
    def flush():
        if not cur:return
        H=max(yy+im.size[1] for f,im,xx,yy in cur)+PAD;W=max(xx+im.size[0] for f,im,xx,yy in cur)+PAD
        idx=len(out);fn=f'atlas_{name}{idx}.webp';A=Image.new('RGBA',(W,H),(0,0,0,0));items={}
        for f,im,xx,yy in cur:A.paste(im,(xx,yy));items['img/'+os.path.basename(f)]=[xx,yy,im.size[0],im.size[1]]
        A.save(I+fn,'WEBP',lossless=True,quality=100,method=6,exact=False);out.append({'f':'img/'+fn,'ui':ui,'it':items});print(fn,(W,H),len(items),os.path.getsize(I+fn))
    for f,im in ims:
        w,h=im.size
        if x+w+PAD>MAXW:x=PAD;y+=rowh+PAD;rowh=0
        if y+h+PAD>MAXH:flush();cur.clear();x=y=PAD;rowh=0
        cur.append((f,im,x,y));x+=w+PAD;rowh=max(rowh,h)
    flush();return out
A=pack(G1,'fx',0)+pack(G2,'ui',1)
json.dump(A,open(R+'tools/atlas.json','w'),separators=(',',':'))
# verify exact pixels
import numpy as np
bad=0
for a in A:
    at=np.array(Image.open(R+a['f']).convert('RGBA'))
    for p,(x,y,w,h) in a['it'].items():
        o=np.array(Image.open(R+p).convert('RGBA'));s=at[y:y+h,x:x+w]
        m=o[...,3]>0
        if not (np.array_equal(o[...,3],s[...,3]) and np.array_equal(o[m],s[m])):bad+=1;print("diff",p)
print('pixel mismatches',bad,'files packed',sum(len(a['it']) for a in A))
