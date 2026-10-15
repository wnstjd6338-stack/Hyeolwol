import os as _os;R=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))+"/"
import numpy as np, json, sys
from PIL import Image, ImageOps
from scipy import ndimage as nd
SRC=R+'incoming/ch2/'
OUT=R+'img/'
src=open(R+'tools/sprite_base.py').read()
exec(src.split("def load")[0])
exec("def cuts"+src.split("def cuts")[1].split("META={}")[0])  # cuts, frames, build
import os
os.makedirs(R+'tools/_work',exist_ok=True);os.chdir(R+'tools/_work')
def load(f):
    a=np.array(Image.open(SRC+f+'.png').convert('RGBA')).copy()
    al=a[...,3].astype(int);r,g,b=[a[...,i].astype(int) for i in range(3)]
    kill=(al<110)|((al<235)&(r>g+80)&(r>b+80))
    a[...,3]=np.where(kill,0,a[...,3]);return a
def groups(a,n,grow=6):
    sm=a[...,3]>0
    for gr in [grow,4,3,2,1,0]:
        lab,k=nd.label(nd.binary_dilation(sm,iterations=gr) if gr else sm)
        sz=nd.sum(sm,lab,range(1,k+1));order=np.argsort(-sz)[:n]
        if len(order)==n and sz[order[-1]]>sz.max()*.2: break
    big=[i+1 for i in order]
    dts=[nd.distance_transform_edt(lab!=b) for b in big]
    grp=np.zeros(lab.shape,int)
    for bi,b in enumerate(big):grp[lab==b]=bi+1
    for i in range(1,k+1):
        if i in big or sz[i-1]<sz.max()*.002:continue
        m=lab==i;cy,cx=[int(v) for v in nd.center_of_mass(m)];j=int(np.argmin([d[cy,cx] for d in dts]));grp[m]=j+1
    out=[]
    for j in range(n):
        sub=a.copy();keep=(grp==j+1)&sm;sub[...,3]=np.where(keep,sub[...,3],0)
        im=Image.fromarray(sub,'RGBA');bb=im.getbbox();ys,xs=np.where((lab==big[j])&sm)
        out.append(dict(im=im.crop(bb),bb=bb,main=(xs.min()-bb[0],ys.min()-bb[1],xs.max()-bb[0],ys.max()-bb[1])))
    return out
META={}
def flipf(f):
    im=ImageOps.mirror(f['im']);w=im.size[0];mx0,my0,mx1,my1=f['main']
    return dict(im=im,bb=f['bb'],main=(w-1-mx1,my0,w-1-mx0,my1))
def stand(f,name,H):
    im=f['im'];bb=im.getbbox();im=im.crop(bb);s=H/im.size[1];im=im.resize((max(1,round(im.size[0]*s)),H),Image.LANCZOS)
    im.save(OUT+name+'.webp','WEBP',quality=84,method=6);return im
def mask(im,S=64):
    a=np.array(im.convert('RGBA').resize((S,S)))[...,3]>40;return a
def iou(a,b):return (a&b).sum()/max(1,(a|b).sum())
def mob(sheet,key,H=230):
    a=load(sheet);fr=frames(a,2,4,keep=.03,grow=4)
    top=[f for f in fr[:4] if f];bot=[f for f in fr[4:] if f]
    META[key+'_walkL']=build(top,key+'_walkL',240,'median');META[key+'_walkR']=build(bot,key+'_walkR',240,'median')
    return top,bot
def mobs(dg,keys):
    from scipy.optimize import linear_sum_assignment
    a=load(f'ch2_dg{dg}_mob_base');bs=groups(a,5);tops=[]
    for k,(rc,key) in enumerate(keys):
        top,bot=mob(f'ch2_dg{dg}_mob_{rc}_walk',key);tops.append(top[0])
    S=np.zeros((5,5));F=np.zeros((5,5),int)
    for i,t in enumerate(tops):
        ref=mask(t['im'])
        for j,b in enumerate(bs):
            s0=iou(mask(b['im']),ref);s1=iou(mask(ImageOps.mirror(b['im'])),ref)
            # aspect ratio similarity helps
            ar=lambda im:im.size[0]/im.size[1]
            pen=abs(np.log(ar(t['im'])/ar(b['im'])))
            S[i,j]=max(s0,s1)-pen*.5;F[i,j]=int(s1>s0)
    r,c=linear_sum_assignment(-S)
    for i,j in zip(r,c):
        key=keys[i][1];b=bs[j];L=flipf(b) if F[i,j] else b
        stand(L,key+'_L',230);stand(flipf(L),key+'_R',230);print(key,'base',j,'flip',F[i,j],round(S[i,j],2))
def boss(n,key):
    a=load(f'ch2_boss{n}_base');bs=sorted(groups(a,2),key=lambda f:f['bb'][0])
    stand(bs[0],key+'_L',300);stand(bs[1],key+'_R',300)
    a=load(f'ch2_boss{n}_walk');fs=sorted(groups(a,4,grow=4),key=lambda f:f['bb'][0])
    META[key+'_walkR']=build(fs,key+'_walkR',300,'median');META[key+'_walkL']=build([flipf(f) for f in fs],key+'_walkL',300,'median')
which=sys.argv[1:]
MOBK={1:[('r1c1','c2_crowsam'),('r1c2','c2_censer'),('r1c3','c2_crow'),('r2c1','c2_firewolf'),('r2c2','c2_maple')],
 2:[('r1c1','c2_turtsol'),('r1c2','c2_snakesh'),('r1c3','c2_turtle'),('r2c1','c2_serp'),('r2c2','c2_toad')],
 3:[('r1c1','c2_tigwar'),('r1c2','c2_tigarch'),('r1c3','c2_btiger'),('r2c1','c2_changgwi'),('r2c2','c2_weasel')],
 4:[('r1c1','c2_dragsp'),('r1c2','c2_talis'),('r1c3','c2_dragbeast'),('r2c1','c2_bamboo'),('r2c2','c2_catfish')],
 5:[('r1c1','c2_goldwar'),('r1c2','c2_crone'),('r1c3','c2_goldliz'),('r2c1','c2_golem'),('r2c2','c2_pangolin')]}
BK=['c2b_jujak','c2b_hyeonmu','c2b_baekho','c2b_cheong','c2b_hwang']
for d in range(1,6):
    if 'mobs' in which: mobs(d,MOBK[d])
    if 'boss' in which: boss(d,BK[d-1])
json.dump(META,open('meta_%s.json'%'_'.join(which),'w'))
