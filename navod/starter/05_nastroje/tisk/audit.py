"""Audits the poster texts: every text inside its box, no '…' except where it is in the data. Usage: python3 audit.py [--w=2500]"""
import sys, os, shutil, tempfile, json
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); WEB=os.path.join(HERE,'..','..','web')
WMM=int(next((a.split('=')[1] for a in sys.argv if a.startswith('--w=')),2500)); work=tempfile.mkdtemp()
shutil.copy(os.path.join(WEB,'data.js'),work); shutil.copy(os.path.join(HERE,'poster.html'),work)
JS='''()=>{ const bad=[], ell=[], raw=JSON.stringify(window.RODOKMEN.people);
  for(const g of document.querySelectorAll('#poster > g > g')){ const r=g.querySelector('rect'); if(!r) continue; const b=r.getBBox();
    for(const t of g.querySelectorAll('text')){ const x=t.getBBox(); if(x.x<b.x-0.05||x.y<b.y-0.05||x.x+x.width>b.x+b.width+0.05||x.y+x.height>b.y+b.height+0.05) bad.push(t.textContent);
      if(t.textContent.includes('…')&&!raw.includes(t.textContent.trim().replace(/^([*†]\\u00a0|roz\\. )/,''))) ell.push(t.textContent); } }
  return {boxes:document.querySelectorAll('#poster > g > g').length,outside:bad,ellipsis:ell}; }'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
    pg.goto('file://'+work+'/poster.html?w=%d'%WMM); pg.wait_for_function('window.POSTER',timeout=60000)
    info=pg.evaluate('window.POSTER'); r=pg.evaluate(JS); b.close()
shutil.rmtree(work)
print(json.dumps({'ok':info.get('ok'),'cut':info.get('cut'),'minFs':info.get('minFs'),'errors':errs,**r},ensure_ascii=False))
sys.exit(0 if info.get('ok') and not info.get('cut') and not errs and not r['outside'] and not r['ellipsis'] else 1)
