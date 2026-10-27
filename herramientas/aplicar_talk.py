# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Mete la traducción en talk.par (diálogos de subhistorias y minijuegos).
Estructura: talk.par -> <carpeta>/e/<escena>.par -> cmn.par -> cmn.bin (textos en UTF-8 alineados a 4, inglés y chino
intercalados; ver sacar_talk.py). Para cada escena con texto:
  1. comprueba que en cmn.bin, en cada «offset», sigue el inglés esperado;
  2. escribe el español (UTF-8) + ceros hasta el final de su hueco (bytes_max + el cero final; NUNCA pisa el texto chino);
  3. reempaqueta por capas con ParTool «add» (sustituye por ruta): cmn.bin -> cmn.par -> <escena>.par -> talk.par.
Uso: python aplicar_talk.py <talk.par original> <talk.par de salida> [--prueba]   (--prueba: «ES:» + inglés recortado,
para comprobar el camino sin traducción).  Traducciones: trabajo/lotes/lote_*_es.json (por id de indice.json).
"""
import csv, json, os, re, shutil, subprocess, sys, glob
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(RAIZ, 'trabajo'); PT = os.path.join(RAIZ, 'herramientas', 'partool', 'ParTool.exe')
OBRA = os.path.join(T, 'talk_build')

def partool(*a):
    # (20-10) reintentos: a veces el archivo recién extraído sigue bloqueado un instante y ParTool se cae
    import time
    for intento in range(4):
        if a[0] == 'extract' and os.path.isdir(a[2]): shutil.rmtree(a[2], ignore_errors=True)
        r = subprocess.run([PT, *a], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
        if r.returncode == 0 and b'ERROR' not in r.stdout.upper(): return
        time.sleep(2)
    raise RuntimeError(f'ParTool {a[0]}: {r.stdout[-300:]!r} {r.stderr[-300:]!r}')

# (20-10) La letra de menús (font/e/yakuza.dds) deja hueco tras í/Í: sus medidas no salen de la tinta. Se dibujan en las
# casillas de «|» y «~» (nunca usados en el juego, con medidas de letra estrecha) y el texto las escribe así.
# letras_ascii.py prepara la fuente (yakuza, yakuza_italic y gothic) para que esos códigos se vean como Í e í.
ASCII_I = str.maketrans({'Í': '|', 'í': '~'})

def traducciones():
    ind = json.load(open(os.path.join(T, 'lotes', 'indice.json'), encoding='utf-8'))
    porid = {}
    for p in glob.glob(os.path.join(T, 'lotes', 'lote_???_es.json')): porid.update(json.load(open(p, encoding='utf-8')))
    return {en: porid[str(i)].translate(ASCII_I) for en, i in ind.items() if str(i) in porid}

def main():
    orig, salida = sys.argv[1], sys.argv[2]; prueba = '--prueba' in sys.argv
    tr = {} if prueba else traducciones()
    filas = list(csv.DictReader(open(os.path.join(T, 'talk_ingles.csv'), encoding='utf-8-sig'), delimiter=';'))
    raiz_talk = os.path.join(T, 'extraido', 'talk')
    por_par = {}
    for f in filas: por_par.setdefault(os.path.normpath(f['archivo_par']), []).append(f)
    if os.path.isdir(OBRA): shutil.rmtree(OBRA)
    add = os.path.join(OBRA, '_talk_add'); os.makedirs(add)
    n_txt = n_par = 0; faltan = 0
    for par, fs in sorted(por_par.items()):
        rel = os.path.relpath(par, raiz_talk); w = os.path.join(OBRA, os.path.splitext(rel)[0])
        a = os.path.join(w, 'a'); b = os.path.join(w, 'b'); c = os.path.join(w, 'c'); dd = os.path.join(w, 'd')
        partool('extract', par, a)
        partool('extract', os.path.join(a, 'cmn.par'), b)
        ruta_bin = os.path.join(b, 'cmn.bin'); data = bytearray(open(ruta_bin, 'rb').read()); cambio = False
        for f in fs:
            off, mx, en = int(f['offset']), int(f['bytes_max']), f['ingles']
            eb = en.encode('utf-8')
            if bytes(data[off:off + len(eb)]) != eb or data[off + len(eb)] != 0:
                raise RuntimeError(f'{rel} @{off}: el inglés no coincide')
            es = ('ES:' + en)[:mx] if prueba else tr.get(en)
            if es is None: faltan += 1; continue
            nb = es.encode('utf-8')
            if prueba:
                while len(nb) > mx: es = es[:-1]; nb = es.encode('utf-8')
            if len(nb) > mx: raise RuntimeError(f'{rel} @{off}: {len(nb)} bytes > {mx}: {es!r}')
            data[off:off + mx + 1] = nb + bytes(mx + 1 - len(nb)); cambio = True; n_txt += 1
        if not cambio: continue
        open(ruta_bin, 'wb').write(data)
        os.makedirs(c); shutil.copy(ruta_bin, os.path.join(c, 'cmn.bin'))
        os.makedirs(dd); partool('add', os.path.join(a, 'cmn.par'), c, os.path.join(dd, 'cmn.par'))
        destino = os.path.join(add, rel); os.makedirs(os.path.dirname(destino), exist_ok=True)
        partool('add', par, dd, destino); n_par += 1
    if os.path.exists(salida): os.remove(salida)
    partool('add', orig, add, salida)
    print(f'talk: {n_txt} textos en {n_par} escenas; sin traducción todavía: {faltan} -> {salida}')

if __name__ == '__main__':
    main()
