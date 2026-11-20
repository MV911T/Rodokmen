#!/usr/bin/env python3
"""Regenerates navod/starter/ (generic starter kit for other family trees) from the LIVE tools of this project.
Runs automatically from publish.sh, so the published starter kit always matches the current web, poster and animation.
- explicit replacements below remove this family's names; a missing target = the tools changed -> fix this list
- leak check: no surname, line or gazetteer place of the real data may remain in the generated tools
- smoke test: the starter must build (validate --strict) with the fictional example family
Usage: python3 navod/sync.py   (exit 1 on any problem)"""
import os, re, sys, shutil, subprocess, tempfile, json
HERE = os.path.dirname(os.path.abspath(__file__)); WEB = os.path.dirname(HERE); TISK = os.path.join(WEB, '..', '05_nastroje', 'tisk')
OUT = os.path.join(HERE, 'starter')
EX = {'nom': 'Tomáš', 'acc': 'Tomáše', 'gen_full': 'Tomáše Pospíšila', 'full': 'Tomáš Pospíšil'}
GENERIC_LINES = ['pospisil', 'hromadka', 'bartos', 'kolar', 'simek', 'lukes', 'zak', 'malec', 'urban', 'sedlak', 'kopecky', 'holub']
URL_PH = 'UZIVATEL.github.io/REPO'
problems = []

def rep(name, s, pairs):
    for a, b in pairs:
        if a not in s: problems.append(f'{name}: replacement target not found (tools changed?): {a[:70]!r}')
        s = s.replace(a, b)
    return s

def read(p): return open(p, encoding='utf8').read()

# ---------- template.html
t = read(os.path.join(WEB, 'template.html'))
t = rep('template.html', t, [
    ('Rodokmen Matěje Veselého', f"Rodokmen {EX['gen_full']}"),
    ('>Na Matěje<', f">Na {EX['acc']}<"),
    ('od Matěje', f"od {EX['acc']}"),
    ('Nahoře je Matěj,', f"Nahoře je {EX['nom']},"),
    ('Matěj at the top', 'root person at the top'),
    ('1 = Matěj,', '1 = root person,'),
    ('under Matěj', 'under the root person'),
])
t = re.sub(r'const LC=\{[^}]*\};', 'const LC={};', t)
# rename the line colour variables (--l-<line>) to generic example lines, same order, same colours
real = list(dict.fromkeys(re.findall(r'--l-([a-z0-9_]+):', t)))
if len(real) > len(GENERIC_LINES): problems.append('more lines than GENERIC_LINES – extend the list')
for i, k in enumerate(real): t = re.sub(r'--l-%s(?=[:);])' % re.escape(k), '--l-' + GENERIC_LINES[i], t)

# ---------- small tools
dt = rep('datatool.js', read(os.path.join(WEB, 'datatool.js')), [('Family tree of Matěj Veselý', f"Family tree of {EX['full']}")])
va = rep('validate.js', read(os.path.join(WEB, 'validate.js')), [('(not connected to Matěj)', '(not connected to the root person)')])
bu = read(os.path.join(WEB, 'build.sh'))
# privacy gate (from the second project): living persons reduced by D.publicLiving before anything reaches the page
JV = os.path.join(WEB, '..', '..', 'Jirka rodokmen', 'web', 'public_data.js')
bu = rep('build.sh', bu, [
    ('first"; exit 1; }\n', 'first"; exit 1; }\n# Privacy gate: living persons are reduced to what the family approved (D.publicLiving) before anything reaches the page.\nnode public_data.js > .public_data.js || { echo "build.sh: public_data.js failed"; exit 1; }\n'),
    ("+open('data.js',encoding='utf8').read()", "+open('.public_data.js',encoding='utf8').read()"),
])
pu = rep('publish.sh', read(os.path.join(WEB, 'publish.sh')), [('https://mv911t.github.io/Rodokmen/', f'https://{URL_PH}/')])
pu = re.sub(r'\n# starter kit.*\n.*navod/sync\.py.*\n', '\n', pu)            # the sync hook belongs to this project only
pu = re.sub(r'git add [^\n]*', 'git add -A', pu, count=1)   # a new project has no README.md/img/print yet
po = rep('poster.html', read(os.path.join(TISK, 'poster.html')), [
    ("'Matěj a sourozenci'", "P[D.root].name.split(' ')[0]+' a sourozenci'"),
    ('mv911t.github.io/Rodokmen', URL_PH),
    ('("Novák st.", "Strusch (Karel Struž)")', '("Pospíšil st.", "Pospischil (Karel Pospíšil)")'),
])
po = re.sub(r'`Prameny: [^`]*`', '`Prameny: matriky, matriční úřady, sčítání lidu a rodinné doklady.`', po)

files = {
    'web/template.html': t, 'web/datatool.js': dt, 'web/validate.js': va, 'web/build.sh': bu, 'web/publish.sh': pu,
    'web/geo.js': read(os.path.join(WEB, 'geo.js')),
    'web/data.js': read(os.path.join(HERE, 'example', 'data.js')), 'web/gazetteer.js': read(os.path.join(HERE, 'example', 'gazetteer.js')),
    'web/.gitignore': '.DS_Store\n.live_check.log\n.public_data.js\n',
    'web/public_data.js': read(JV),
    '05_nastroje/tisk/poster.html': po,
}
for f in ['render.py', 'audit.py', 'crop.py']: files['05_nastroje/tisk/' + f] = read(os.path.join(TISK, f))
files['05_nastroje/design/shots.py'] = read(os.path.join(WEB, '..', '05_nastroje', 'design', 'shots.py'))

# ---------- leak check (everything except the example data)
env = {}
src = read(os.path.join(WEB, 'data.js')) + '\n' + read(os.path.join(WEB, 'gazetteer.js'))
js = "global.window={};eval(require('fs').readFileSync(0,'utf8'));const D=window.RODOKMEN,s=new Set();" \
     "D.people.concat(D.collateral||[]).forEach(p=>{const w=p.name.split(' ');s.add(w[w.length-1]);if(p.maiden)s.add(p.maiden)});" \
     "Object.values(D.lines).forEach(l=>s.add(l));(window.RODOKMEN_GAZ||[]).forEach(z=>s.add(z.n));console.log(JSON.stringify([...s]))"
tokens = json.loads(subprocess.run(['node', '-e', js], input=src, capture_output=True, text=True, check=True).stdout)
tokens = [x for x in tokens if len(x) >= 4 and x[0].isupper() and x not in ('Morava', 'Slezsko', 'Polsko', 'Slovensko', 'Rakousko', 'Praha', 'Brno', 'Třebíč', 'Jihlava')]
for name, s in files.items():
    if name.endswith(('data.js', 'gazetteer.js', 'geo.js')): continue
    for tok in tokens:
        if re.search(r'(?<!\w)%s(?!\w)' % re.escape(tok), s): problems.append(f'{name}: contains "{tok}" from the real data')
    for w in ('Matěj', 'Matěje', 'Veselý', 'Veselého', 'Votava', 'Votavy', 'Votavová', 'jiri1987', 'mv911t', 'MV911T'):
        if re.search(r'(?<!\w)%s(?!\w)' % w, s): problems.append(f'{name}: contains "{w}"')

if problems:
    print('sync.py: starter NOT updated:'); [print('  -', p) for p in problems]; sys.exit(1)

# ---------- write + smoke test in a temp copy
tmp = tempfile.mkdtemp()
for name, s in files.items():
    p = os.path.join(tmp, name); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf8').write(s)
for sh in ('web/build.sh', 'web/publish.sh'): os.chmod(os.path.join(tmp, sh), 0o755)
r = subprocess.run(['bash', os.path.join(tmp, 'web', 'build.sh')], capture_output=True, text=True)
if r.returncode != 0 or 'ok ' not in r.stdout:
    print('sync.py: starter build FAILED:\n' + r.stdout[-1500:] + r.stderr[-800:]); sys.exit(1)
for f in ('index.html', '.public_data.js'): os.remove(os.path.join(tmp, 'web', f))
shutil.rmtree(OUT, ignore_errors=True); shutil.copytree(tmp, OUT); shutil.rmtree(tmp)
print('sync.py: starter OK (' + r.stdout.strip().splitlines()[-1] + ')')
