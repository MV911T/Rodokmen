"""Renders a region of the poster at 200 dpi (enough to check legibility). Usage: python3 crop.py out.png x_mm y_mm w_mm h_mm"""
import sys, os, subprocess, shutil, tempfile
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); WEB=os.path.join(HERE,'..','..','web')
o,x,y,w,h=sys.argv[1],*map(float,sys.argv[2:6]); work=tempfile.mkdtemp()
shutil.copy(os.path.join(WEB,'data.js'),os.path.join(work,'data.js'))
shutil.copy(os.path.join(HERE,'poster.html'),work); k=200/25.4; pw,ph=int(w*k),int(h*k)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':pw,'height':ph}); pg.goto('file://'+work+'/poster.html?w=2500'); pg.wait_for_function('window.POSTER')
    pg.evaluate('(a)=>{const s=document.getElementById("poster");s.setAttribute("width",a[0]);s.setAttribute("height",a[1]);s.setAttribute("viewBox",a[2])}',[pw,ph,f'{x} {y} {w} {h}'])
    pg.screenshot(path=o,clip={'x':0,'y':0,'width':pw,'height':ph}); b.close()
