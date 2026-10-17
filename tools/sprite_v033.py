# V033: 사용자 제공 왼쪽 보기 시트(incoming/motion/*.png, 가로 1줄) → img/<이름>L/R.webp 띠 + ANIMDEF 값 출력
import os,sys,json,numpy as np
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__));from sprite_base import load,frames,build,R
def charh(f):  # 발끝~머리끝: 발 위치 근처 세로 띠만 봐서 머리 위로 든 무기는 (중앙값으로) 무시
    a=np.array(f['im'])[...,3]>0;mx0,my0,mx1,my1=f['main'];h=my1-my0
    xs=np.where(a[my0+int(h*.7):my1+1,mx0:mx1+1])[1]+mx0;cx=int(np.median(xs));w=max(4,int((mx1-mx0)*.12))
    rows=np.where(a[:,max(0,cx-w):cx+w].any(1))[0];return my1-rows.min()
OUT={}
for nm,n,H in [('archer_atk1',4,240),('archer_myth_atk1',4,240),('mage_atk',4,260),('mage_myth_atk',4,260),('warrior_atk',8,260),('warrior_myth_atk',8,260),('healer_atk',4,260),('healer_myth_atk',4,260)]+[(c+'_walk',8,240) for c in ['archer','archer_myth','mage','mage_myth','warrior','warrior_myth','healer','healer_myth']]:
    fs=[f for f in frames(load(R+f'incoming/motion/{nm}.png'),1,n) if f];assert len(fs)==n,(nm,len(fs))
    m=build(fs,nm+'L',H,refh=float(np.median([charh(f) for f in fs])))
    im=Image.open(R+f'img/{nm}L.webp');fw=im.width//n;rr=Image.new('RGBA',im.size)
    for i in range(n):rr.paste(im.crop((i*fw,0,(i+1)*fw,im.height)).transpose(Image.FLIP_LEFT_RIGHT),(i*fw,0))
    rr.save(R+f'img/{nm}R.webp','WEBP',quality=84,method=6)
    OUT[nm+'L']=dict(n=n,ax=m['ax'],hs=m['hs']);OUT[nm+'R']=dict(n=n,ax=round(1-m['ax'],4),hs=m['hs'])
json.dump(OUT,open(R+'tools/anim_v033.json','w'));print(json.dumps(OUT))
