# -*- coding: utf-8 -*-
"""(01-11-2026, claude2) ¿La herramienta pública reproduce el paquete? Compara «Herramientas para traduccion/salida»
(hecha desde el inglés original con extraer + aplicar) con entrega_v1.0.3/archivos: tablas (contenido JSON), cmn.bin de
cada escena de talk.par y de los .par sueltos (hact/auth).
  python comparar_herramienta.py"""
import filecmp, json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
E = 'C:/Mods/yakuza6/entrega_v1.0.3'; H = f'{E}/Herramientas para traduccion/salida'; A = f'{E}/archivos'
W = 'C:/Mods/yakuza6/trabajo/faltan_c2/comparar'; PT = 'C:/Mods/yakuza6/herramientas/partool/ParTool.exe'
REARMP = 'C:/Mods/yakuza6/herramientas/reARMP/reARMP.py'
def _rm(f, p, e): os.chmod(p, 0o666); f(p)
if os.path.isdir(W): shutil.rmtree(W, onexc=_rm)
os.makedirs(W)
def pt(*a): subprocess.run([PT, *a], stdin=subprocess.DEVNULL, capture_output=True, check=True)
def js(bin_, lado):
    d = f'{W}/{lado}'; os.makedirs(d, exist_ok=True); n = os.path.basename(bin_)
    shutil.copy(bin_, f'{d}/{n}'); subprocess.run([sys.executable, REARMP, n], cwd=d, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=True)
    return json.load(open(f'{d}/{n}.json', encoding='utf-8'))
fallos = []
ta, th = sorted(os.listdir(f'{A}/db_e')), sorted(os.listdir(f'{H}/db_e'))
if ta != th: fallos.append(f'tablas distintas: faltan {set(ta) - set(th)} sobran {set(th) - set(ta)}')
for t in sorted(set(ta) & set(th)):
    if filecmp.cmp(f'{A}/db_e/{t}', f'{H}/db_e/{t}', shallow=False): continue
    if js(f'{A}/db_e/{t}', 'a') != js(f'{H}/db_e/{t}', 'h'): fallos.append(f'tabla {t}: contenido distinto')
print('tablas:', len(ta), 'fallos', len(fallos))
def cmns(raiz):
    out = {}
    for r, ds, fs in os.walk(raiz):
        if 'cmn.bin' in fs: out[os.path.relpath(r, raiz).replace(os.sep, '/')] = open(os.path.join(r, 'cmn.bin'), 'rb').read()
    return out
pt('extract', '-r', f'{A}/talk.par', f'{W}/ta'); pt('extract', '-r', f'{H}/talk.par', f'{W}/th')
a, h = cmns(f'{W}/ta'), cmns(f'{W}/th')
dif = [k for k in a if a[k] != h.get(k)]
print('escenas de talk.par:', len(a), 'distintas', len(dif), dif[:10]); fallos += [f'talk {k}' for k in dif]
ea = sorted(os.path.relpath(os.path.join(r, f), f'{A}/extra') for r, ds, fs in os.walk(f'{A}/extra') for f in fs)
for rel in ea:
    hp = f'{H}/extra/{rel}'
    if not os.path.exists(hp): fallos.append(f'extra falta {rel}'); continue
    pt('extract', '-r', f'{A}/extra/{rel}', f'{W}/ea'); pt('extract', '-r', hp, f'{W}/eh')
    if cmns(f'{W}/ea') != cmns(f'{W}/eh'): fallos.append(f'extra distinto {rel}')
    shutil.rmtree(f'{W}/ea', onexc=_rm); shutil.rmtree(f'{W}/eh', onexc=_rm)
print('sueltos:', len(ea))
print('FALLOS', len(fallos)); [print(' ', f) for f in fallos[:40]]
