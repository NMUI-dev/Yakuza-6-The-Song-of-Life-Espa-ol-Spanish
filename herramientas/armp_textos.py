# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Saca los textos en inglés de las tablas ARMP de data/db/e (exportadas a JSON con reARMP)
a un CSV: archivo, ruta dentro del JSON, texto. Separa lo que parece TEXTO PARA EL JUGADOR de lo que parece un
identificador (nombres de archivo, claves, códigos: sin espacios y con _ / . o todo minúsculas sin vocales...).
  python herramientas/armp_textos.py trabajo/armp_json trabajo/db_e_ingles.csv
"""
import csv, json, os, re, sys

def es_texto(s):
    if not s or not s.strip(): return False
    if re.search(r'[぀-ヿ一-鿿]', s): return False          # japonés/chino: no es la columna inglesa
    if ' ' in s.strip() or '\n' in s: return True
    if re.fullmatch(r'[A-Za-z0-9_./\-:#]+', s) and ('_' in s or '/' in s or '.' in s or s.islower()): return False
    return bool(re.search(r'[A-Za-z]{2,}', s))

def recorrer(o, ruta, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k.startswith('reARMP_') or k in ('columnValidity', 'columnTypes', 'columnTypes2', 'COLUMN_INDICES'): continue
            recorrer(v, ruta + [k], out)
    elif isinstance(o, list):
        for i, v in enumerate(o): recorrer(v, ruta + [str(i)], out)
    elif isinstance(o, str):
        out.append(('/'.join(ruta), o))

if __name__ == '__main__':
    carpeta, salida = sys.argv[1], sys.argv[2]
    filas = []; por_archivo = {}
    for n in sorted(os.listdir(carpeta)):
        if not n.endswith('.bin.json'): continue
        d = json.load(open(os.path.join(carpeta, n), encoding='utf-8'))
        out = []; recorrer(d, [], out)
        t = [(r, s) for r, s in out if es_texto(s)]
        por_archivo[n[:-9]] = len(t)
        for r, s in t: filas.append((n[:-9], r, s))
    with open(salida, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['archivo', 'ruta', 'ingles']); w.writerows(filas)
    unicos = len({s for _, _, s in filas})
    print(f'{len(filas)} textos ({unicos} únicos, {sum(len(s) for _, _, s in filas)} letras) en {sum(1 for v in por_archivo.values() if v)} tablas')
    for n, c in sorted(por_archivo.items(), key=lambda x: -x[1])[:40]: print(f'  {c:6d}  {n}')
