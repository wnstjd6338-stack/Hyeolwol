import math,random
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
def sigil(kind,seed):
  N=1024;c=N/2;im=Image.new('L',(N,N),0);d=ImageDraw.Draw(im);R=random.Random(seed)
  def ring(r,w):d.ellipse([c-r,c-r,c+r,c+r],outline=255,width=w)
  def poly(n,step,r,w,rot=0):
    pts=[(c+r*math.cos(rot+2*math.pi*i/n-math.pi/2),c+r*math.sin(rot+2*math.pi*i/n-math.pi/2)) for i in range(n)]
    for i in range(n):a=pts[i];b=pts[(i+step)%n];d.line([a,b],fill=255,width=w)
    return pts
  ring(500,10);ring(470,5)
  # rune band between 470 and 400
  n=36 if kind==0 else 28
  for i in range(n):
    a=2*math.pi*i/n;ca,sa=math.cos(a),math.sin(a);tx,ty=-sa,ca
    rr=435;L=22
    for _ in range(R.randint(2,3)):
      p=[(R.uniform(-1,1),R.uniform(-1,1)) for _ in range(2)]
      pts=[(c+ca*(rr+u*L)+tx*v*L*.7,c+sa*(rr+u*L)+ty*v*L*.7) for u,v in p]
      d.line(pts,fill=255,width=5)
    if R.random()<.4:
      x,y=c+ca*rr,c+sa*rr;d.ellipse([x-5,y-5,x+5,y+5],fill=255)
  ring(400,7)
  if kind==0:
    pts=poly(6,2,400,6);ring(300,4)
    for x,y in pts:d.ellipse([x-26,y-26,x+26,y+26],outline=255,width=5)
    ring(200,8);ring(185,3);poly(6,1,200,4,math.pi/6)
    for i in range(12):
      a=2*math.pi*i/12;d.line([(c+math.cos(a)*200,c+math.sin(a)*200),(c+math.cos(a)*300,c+math.sin(a)*300)],fill=255,width=3)
    ring(70,6);ring(40,10)
  else:
    poly(8,3,400,6);ring(330,4);poly(8,3,330,3,math.pi/8);ring(250,8)
    for i in range(24):
      a=2*math.pi*i/24;r1=250;r2=250+(30 if i%2 else 55)
      d.line([(c+math.cos(a)*r1,c+math.sin(a)*r1),(c+math.cos(a)*r2,c+math.sin(a)*r2)],fill=255,width=4)
    ring(150,5);poly(4,1,150,4);poly(4,1,150,4,math.pi/4);ring(60,10)
    for i in range(8):
      a=2*math.pi*i/8;x,y=c+math.cos(a)*330,c+math.sin(a)*330;d.ellipse([x-14,y-14,x+14,y+14],fill=255)
  g=im.filter(ImageFilter.GaussianBlur(10))
  a=np.clip(np.array(im,float)*.85+np.array(g,float)*1.1,0,255)
  out=Image.fromarray(a.astype(np.uint8)).resize((512,512),Image.LANCZOS)
  o=Image.new('RGBA',(512,512),(255,255,255,0));o.putalpha(out);return o
for k,n in [(0,'msig1'),(1,'msig2')]:
  sigil(k,7+k).save(f'img/k_{n}.webp','WEBP',lossless=True,method=6,exact=False)
