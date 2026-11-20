#!/usr/bin/env python3
"""Design QA for the family-tree web: screenshots of every tab + detail dialog
at desktop and phone size, a contact sheet, and automatic checks:
  - console/page errors
  - horizontal overflow (page wider than the viewport)
  - WCAG text contrast of every visible text element (actual rendered colours)
  - text clipped by its box, tap targets < 32 px on phone
Usage: python3 shots.py [path/to/index.html] [outdir]
"""
import sys, os, json
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'../../web/index.html'))
OUT=os.path.abspath(sys.argv[2] if len(sys.argv)>2 else os.path.join(HERE,'out'))
os.makedirs(OUT,exist_ok=True)
TABS=[('tree','#tabTree'),('wide','#tabWide'),('map','#tabMap'),('print','#tabPrint'),('anim','#tabAnim')]
SIZES=[('desk',1440,900),('phone',390,844)]
AUDIT=r"""() => {
 const lum=c=>{const m=c.match(/[\d.]+/g);if(!m)return null;const [r,g,b]=m.slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return {L:.2126*r+.7152*g+.0722*b,a:m[3]===undefined?1:+m[3]}};
 const bgOf=el=>{for(let e=el;e;e=e.parentElement){const s=getComputedStyle(e);if(s.backgroundImage!=='none')return null;const l=lum(s.backgroundColor);if(l&&l.a>.9)return l}return lum('rgb(0,0,0)')};
 const out={contrast:[],clip:[],tap:[]};const seen=new Set();
 for(const el of document.querySelectorAll('body *')){
  if(!el.offsetParent&&getComputedStyle(el).position!=='fixed')continue;
  const r=el.getBoundingClientRect(); if(r.width<2||r.height<2||r.bottom<0||r.top>innerHeight)continue;
  const own=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
  const s=getComputedStyle(el);
  if(own&&s.visibility!=='hidden'&&+s.opacity>.5&&!el.closest('svg,canvas')){
   const f=lum(s.color),b=bgOf(el); if(f&&b){const c=(Math.max(f.L,b.L)+.05)/(Math.min(f.L,b.L)+.05);const big=parseFloat(s.fontSize)>=18.6||(parseFloat(s.fontSize)>=14&&+s.fontWeight>=600);
    if(c<(big?3:4.5)){const k=el.tagName+'.'+el.className+'|'+s.color;if(!seen.has(k)){seen.add(k);out.contrast.push({el:el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+(el.className&&typeof el.className=='string'?'.'+el.className.split(' ').join('.'):''),text:el.textContent.trim().slice(0,40),ratio:+c.toFixed(2),need:big?3:4.5})}}}
   if(el.scrollWidth>el.clientWidth+2&&s.overflow!=='visible'&&s.textOverflow!=='ellipsis'&&!/auto|scroll/.test(s.overflowX))out.clip.push(el.tagName+'.'+el.className+': '+el.textContent.trim().slice(0,30));
  }
  if(innerWidth<600&&el.matches('button,a,[role=tab],input,select')&&(r.height<32||r.width<32)&&!el.closest('#canvas,svg,p,li,dd,.meta,label')&&!el.matches('.plink,input[type=range]'))out.tap.push(el.tagName+(el.id?'#'+el.id:'')+' '+Math.round(r.width)+'×'+Math.round(r.height));
 }
 out.overflowX=document.documentElement.scrollWidth>innerWidth+1?document.documentElement.scrollWidth:0;
 out.clip=out.clip.slice(0,15);out.tap=[...new Set(out.tap)].slice(0,15);return out}"""
report={}
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    for sz,W,H in SIZES:
        ctx=b.new_context(viewport={'width':W,'height':H},device_scale_factor=1 if sz=='desk' else 2,reduced_motion='no-preference')
        pg=ctx.new_page(); errs=[]
        pg.on('console',lambda m: errs.append(m.type+': '+m.text) if m.type=='error' else None)
        pg.on('pageerror',lambda e: errs.append('PAGEERR '+str(e)))
        for attempt in range(3):   # Google Fonts / CDN sometimes stall – retry instead of failing the whole run
            try: pg.goto('file://'+SRC,wait_until='domcontentloaded',timeout=60000); break
            except Exception as e: print('goto retry',attempt+1,str(e)[:80])
        pg.set_default_timeout(60000); pg.wait_for_timeout(1500)
        for name,sel in TABS:
            pg.click(sel); pg.wait_for_timeout(9000 if name=='anim' else 1400)
            pg.screenshot(path=f'{OUT}/{sz}_{name}.png')
            report[f'{sz}_{name}']=pg.evaluate(AUDIT)
            if name=='tree':
                pg.evaluate("document.querySelector('.card.root')?.click()"); pg.wait_for_timeout(700)
                pg.screenshot(path=f'{OUT}/{sz}_dialog.png'); report[f'{sz}_dialog']=pg.evaluate(AUDIT)
                pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
        report[f'{sz}_errors']=errs; ctx.close()
    b.close()
try:
    from PIL import Image
    ims=[Image.open(f'{OUT}/{sz}_{n}.png') for sz,_,_ in SIZES for n in [t[0] for t in TABS]+['dialog']]
    tw=480; th=lambda im:int(im.height*tw/im.width)
    rows=[ims[:6],ims[6:]]; hh=[max(th(i) for i in r) for r in rows]
    sheet=Image.new('RGB',(tw*6+70,sum(hh)+30),'#222')
    y=10
    for r,h in zip(rows,hh):
        for i,im in enumerate(r): sheet.paste(im.convert('RGB').resize((tw,th(im))),(10+i*(tw+10),y))
        y+=h+10
    sheet.save(f'{OUT}/_sheet.png')
except Exception as e: print('sheet:',e)
json.dump(report,open(f'{OUT}/report.json','w'),ensure_ascii=False,indent=1)
bad=0
for k,v in report.items():
    if k.endswith('errors'):
        if v: bad+=1; print(k,v[:5])
        continue
    issues={x:v[x] for x in ('contrast','clip','tap') if v[x]}
    if v['overflowX']: issues['overflowX']=v['overflowX']
    if issues: bad+=1; print(k, json.dumps(issues,ensure_ascii=False)[:900])
print('OK – no issues' if not bad else f'{bad} views with issues', '→', OUT)
