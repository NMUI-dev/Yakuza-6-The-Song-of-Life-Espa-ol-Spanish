# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Mete la traducción en las tablas ARMP de data/db/e.
Lee trabajo/armp_json/<tabla>.bin.json (exportadas del original con reARMP), cambia SOLO las celdas de los grupos TEXTO
(clasificar_grupos.py) cuyo inglés tiene traducción, guarda el JSON y lo rearma con reARMP -> <salida>/<tabla>.bin.
Las tablas sin cambios no se copian (el juego usa las suyas).
  python aplicar_db.py <carpeta de salida (data/db/e)> [--prueba]   (--prueba: «ES:» delante, sin traducción)
"""
import json, os, shutil, subprocess, sys, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clasificar_grupos as C
from aplicar_talk import traducciones
T = C.T; REARMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reARMP', 'reARMP.py')

def poner(d, ruta, viejo, nuevo):
    o = d; ks = ruta.split('/')
    for k in ks[:-1]: o = o[int(k)] if isinstance(o, list) else o[k]
    k = ks[-1]; k = int(k) if isinstance(o, list) else k
    if o[k] != viejo: raise RuntimeError(f'{ruta}: esperaba {viejo!r}, hay {o[k]!r}')
    o[k] = nuevo

def main():
    salida = sys.argv[1]; prueba = '--prueba' in sys.argv
    tr = {} if prueba else traducciones()
    r, g = C.grupos(); cl = C.clasificar(g)
    por_tabla = collections.defaultdict(list)
    for x in r:
        if cl[(x['archivo'], C.colk(x['ruta']))] == 'TEXTO' and x['ingles'].strip(): por_tabla[x['archivo']].append(x)
    obra = os.path.join(T, 'db_build'); os.makedirs(obra, exist_ok=True); os.makedirs(salida, exist_ok=True)
    tot = falt = 0
    for tabla, xs in sorted(por_tabla.items()):
        d = json.load(open(os.path.join(T, 'armp_json', f'{tabla}.bin.json'), encoding='utf-8')); n = 0
        for x in xs:
            es = ('ES:' + C.norm(x['ingles'])) if prueba else tr.get(C.norm(x['ingles']))
            if es is None: falt += 1; continue
            if '\r\n' in x['ingles']: es = es.replace('\n', '\r\n')       # el mismo salto de línea que el original
            poner(d, x['ruta'], x['ingles'], es); n += 1
        if not n: continue
        js = os.path.join(obra, f'{tabla}.bin.json')
        json.dump(d, open(js, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        if os.path.exists(js + '.bin'): os.remove(js + '.bin')
        subprocess.run([sys.executable, REARMP, js], cwd=obra, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=True)
        shutil.copy(js + '.bin', os.path.join(salida, f'{tabla}.bin')); tot += n
        print(f'  {tabla}: {n}')
    print(f'db/e: {tot} textos; sin traducción todavía: {falt} -> {salida}')

if __name__ == '__main__':
    main()
