"""Renders poster.html (W x 1000 mm, W via --w=, default 2500) to print files.
Usage: python3 render.py <outdir> [--full]
  always: preview JPEG + PDF (vector); --full [--dpi=400]: JPEG (q100, 4:4:4), LZW TIFF and uncompressed TIFF."""
import sys, os, subprocess, shutil, datetime, json
from playwright.sync_api import sync_playwright
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__)); WEB = os.path.join(HERE, '..', '..', 'web')
out = os.path.abspath(sys.argv[1]); full = '--full' in sys.argv
WMM = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--w=')), 2500))
DPI = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--dpi=')), 400))
os.makedirs(out, exist_ok=True); work = os.path.join(out, '_work'); os.makedirs(work, exist_ok=True)
data = open(os.path.join(WEB, 'data.js'), encoding='utf8').read()   # this web publishes data.js unchanged (no public_data.js)
now = datetime.datetime.now()
data += "\nwindow.RODOKMEN_BUILD=%r;\n" % ('%d. %d. %d' % (now.day, now.month, now.year))
open(os.path.join(work, 'data.js'), 'w', encoding='utf8').write(data)
shutil.copy(os.path.join(HERE, 'poster.html'), os.path.join(work, 'poster.html'))
PXW, PXH = round(WMM / 25.4 * DPI), round(1000 / 25.4 * DPI)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 2000, 'height': 1000})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto('file://' + os.path.join(work, 'poster.html') + '?w=%d' % WMM); pg.wait_for_function('window.POSTER', timeout=60000)
    info = pg.evaluate('window.POSTER'); print(json.dumps(info, ensure_ascii=False)); print('errors:', errs)
    if not info.get('ok'): sys.exit(1)
    pg.pdf(path=os.path.join(out, 'rodokmen_tisk_%dx1000mm.pdf' % WMM), width='%dmm' % WMM, height='1000mm', print_background=True, page_ranges='1')
    # preview: 4000 px wide
    PW = round(4000 * WMM / 2000); pg.set_viewport_size({'width': PW, 'height': 2000})
    pg.evaluate('(()=>{const s=document.getElementById("poster");s.setAttribute("width","%d");s.setAttribute("height","2000")})()' % PW)
    pg.screenshot(path=os.path.join(work, 'prev.png'), clip={'x': 0, 'y': 0, 'width': PW, 'height': 2000})
    Image.open(os.path.join(work, 'prev.png')).convert('RGB').save(os.path.join(out, 'rodokmen_tisk_nahled.jpg'), quality=85, optimize=True, progressive=True)
    if full:
        T = 2048; big = Image.new('RGB', (PXW, PXH)); mm = WMM / PXW
        pg.set_viewport_size({'width': T, 'height': T})
        pg.evaluate('(()=>{const s=document.getElementById("poster");s.setAttribute("width","%d");s.setAttribute("height","%d")})()' % (T, T))
        for ty in range(0, PXH, T):
            for tx in range(0, PXW, T):
                pg.evaluate('document.getElementById("poster").setAttribute("viewBox","%f %f %f %f")' % (tx * mm, ty * mm, T * mm, T * mm))
                f = os.path.join(work, 'tile.png'); pg.screenshot(path=f, clip={'x': 0, 'y': 0, 'width': T, 'height': T})
                big.paste(Image.open(f).convert('RGB'), (tx, ty))
        big.save(os.path.join(out, 'rodokmen_tisk_%ddpi.jpg' % DPI), quality=100, subsampling=0, dpi=(DPI, DPI))
        big.save(os.path.join(out, 'rodokmen_tisk_%ddpi.tif' % DPI), compression='tiff_lzw', dpi=(DPI, DPI))          # lossless, pixel-identical
        big.save(os.path.join(out, 'rodokmen_tisk_%ddpi_bez_komprese.tif' % DPI), compression=None, dpi=(DPI, DPI))  # ~1.9 GB at 400 dpi, local only (07_tisk/)
    b.close()
shutil.rmtree(work)
for f in sorted(os.listdir(out)): print(f, round(os.path.getsize(os.path.join(out, f)) / 1e6, 1), 'MB')
