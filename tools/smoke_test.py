import time,json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
  b=p.chromium.launch();errs=[]
  for CLS in ['warrior','archer','mage','healer']:
    pg=b.new_page(viewport={'width':1280,'height':720});pg.on('pageerror',lambda e,c=CLS: errs.append(c+': '+str(e)))
    pg.goto('http://localhost:8765/index.html');time.sleep(1.5)
    pg.evaluate(f"localStorage.clear();loadRoot();newGame('{CLS}','t');vnEnd();G.vn=null;closeModal()")
    time.sleep(.5)
    r=pg.evaluate(f"""(()=>{{pl.lv=100;pl.pas={{a1:20,d1:20,u1:5,u3:20,u4:20,u2:5,u5:1}};SLOTS.forEach(sl=>pl.gear[sl]=makeSetItem(sl,'{CLS}',100));recalc();pl.god=true;pl.q=qIdx('어둠을 삼키는 것');buildSkillBar();travel('sealed',null,{{force:1}});G.vn=null;$('#vn').hidden=true;
      for(let f=0;f<900;f++){{pl.cds=pl.cds.map(c=>Math.min(c,.05));update(1/30)}}drawWorld();
      const out={{cp:myCP(),kills:pl.st.kills,set:setCount(),rng:rngMul(),cd:cdAtkMul(),kp:G.kp.length,turrets:(G.turrets||[]).length,dashMax:dashMax()}};
      for(const k of ['bag','stat','skill','map','quest','relic','board','shop','set','pet','party','ach']){{G.modal=null;openPanel(k);if(k==='skill'){{G.skTab='pas';renderPanel();G.skTab='cls'}}}}closeModal();
      return out}})()""")
    print(CLS,r);pg.close()
  print('ERRS',errs[:10]);b.close()
