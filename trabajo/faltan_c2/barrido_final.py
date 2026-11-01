# -*- coding: utf-8 -*-
"""(01-11-2026, claude2) Barrido final de lo ARMADO (regla de cierre): extrae salida/talk.par y los .par sueltos
(hact/auth del juego + los de salida/extra encima) y busca inglés con cmn_scan.py; en db_e compara cada celda con el
inglés original (lo que siga igual y parezca inglés). Escribe barrido_final.json y un resumen.
  python barrido_final.py"""
import json, os, re, shutil, subprocess, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Mods/yakuza6/trabajo/faltan_c2'; SAL = os.environ.get('SAL', f'{D}/salida'); X = f'{D}/barrido_x'
PT = 'C:/Mods/yakuza6/herramientas/partool/ParTool.exe'
GAME = 'D:/SteamLibrary/steamapps/common/Yakuza 6 - The Song of Life/data'
REARMP = 'C:/Mods/yakuza6/herramientas/reARMP/reARMP.py'
def _rm(f, p, e): os.chmod(p, 0o666); f(p)
if os.path.isdir(X): shutil.rmtree(X, onexc=_rm)
os.makedirs(X)
def pt(*a): subprocess.run([PT, *a], stdin=subprocess.DEVNULL, capture_output=True, check=True)
print('extrayendo talk.par armado...'); pt('extract', '-r', f'{SAL}/talk.par', f'{X}/talk.par_par')
for carpeta in ('hact', 'auth'):
    for raiz, ds, fs in os.walk(f'{GAME}/{carpeta}'):
        for f in fs:
            if not f.endswith('.par'): continue
            rel = os.path.relpath(os.path.join(raiz, f), GAME).replace(os.sep, '/')
            src = f'{SAL}/extra/{rel}' if os.path.exists(f'{SAL}/extra/{rel}') else os.path.join(raiz, f)
            try: pt('extract', '-r', src, f'{X}/{rel}_par')
            except subprocess.CalledProcessError: pass
print('buscando inglés en cmn.bin...')
subprocess.run([sys.executable, '-I', f'{D}/cmn_scan.py', X, f'{D}/barrido_cmn.json'], check=True)
cmn = json.load(open(f'{D}/barrido_cmn.json', encoding='utf-8'))
# db_e armado
print('tablas...')
obra = f'{D}/barrido_db'; os.makedirs(obra, exist_ok=True)
H = 'C:/Mods/yakuza6/entrega_v1.0.2/Herramientas para traduccion'; sys.argv = sys.argv[:1]; sys.path.insert(0, H)
import herramienta_traduccion as ht
EJ = 'C:/Mods/yakuza6/trabajo/armp_json'
db = []
for f in sorted(os.listdir(f'{SAL}/db_e')):
    js = f'{obra}/{f}.json'
    if not os.path.exists(js):
        shutil.copy(f'{SAL}/db_e/{f}', f'{obra}/{f}')
        subprocess.run([sys.executable, REARMP, f], cwd=obra, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=True)
        os.remove(f'{obra}/{f}')
    a = json.load(open(f'{EJ}/{f}.json', encoding='utf-8')); b = json.load(open(js, encoding='utf-8'))
    o = []; ht.recorrer(a, [], o)
    for r, s in o:
        if ht.leer_ruta(b, r) != s or not re.search(r'[a-z]{3}', s): continue
        w = re.findall(r"[a-z']+", s.lower())
        if len(w) >= 2 or re.fullmatch(r"[.…]*[A-Z][a-z']+[.!?…]+", s): db.append({'tabla': f[:-4], 'ruta': r, 'en': s})
json.dump({'cmn': cmn, 'db': db}, open(f'{D}/barrido_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('cmn que parecen inglés:', len(cmn), collections.Counter('/'.join(x['f'].split('/')[:2]) for x in cmn).most_common(10))
print('db iguales al inglés (frases o palabras sueltas):', len(db), collections.Counter(x['tabla'] for x in db).most_common(15))
