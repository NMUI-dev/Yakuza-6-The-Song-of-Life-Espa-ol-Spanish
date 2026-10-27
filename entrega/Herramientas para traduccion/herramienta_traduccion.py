# -*- coding: utf-8 -*-
"""Yakuza 6: The Song of Life - herramienta de traducción (Claude Code, 20-10-2026).

Saca TODOS los textos del juego a una hoja (textos.csv, se abre con Excel o LibreOffice) con el inglés original y la
traducción actual al lado, y después vuelve a meter en el juego lo que cambies en la columna «espanol».

  python herramienta_traduccion.py extraer     -> trabajo/textos.csv
  python herramienta_traduccion.py aplicar     -> salida/ (db_e, talk.par, font.par: lo mismo que la carpeta «archivos»)
  python herramienta_traduccion.py aplicar --a-archivos   -> además copia salida/ encima de ../archivos

Opciones: --ingles <carpeta data del juego en inglés> (por defecto: ../respaldo_original que deja el instalador, o el juego
de Steam si aún no tiene la traducción). Ver COMO_USAR.txt y PASO_A_PASO.txt.
"""
import csv, json, os, re, shutil, subprocess, sys, collections, glob

AQUI = os.path.dirname(os.path.abspath(__file__))
PAQUETE = os.path.dirname(AQUI)                         # carpeta del instalador
ARCHIVOS = os.path.join(PAQUETE, 'archivos')            # traducción actual (lo que instala el instalador)
TRABAJO = os.path.join(AQUI, 'trabajo')
SALIDA = os.path.join(AQUI, 'salida')
PARTOOL = os.path.join(AQUI, 'programas', 'ParTool', 'ParTool.exe')
if not os.path.isfile(PARTOOL):
    print('Falta ParTool.exe. Lee «1 - LEEME PRIMERO - Instalar ParTool.txt». Descarga directa:'); print('https://github.com/Kaplas80/ParManager/releases/download/v1.3.4/v1.3.4-windows-x64.zip')
    print('Descomprímelo y copia ParTool.exe en: ' + os.path.dirname(PARTOOL))
    input('Pulsa Intro para salir...'); sys.exit(1)
REARMP = os.path.join(AQUI, 'programas', 'reARMP', 'reARMP.py')
CLASES = json.load(open(os.path.join(AQUI, 'datos', 'clases_grupos.json'), encoding='utf-8'))
CSV_TEXTOS = os.path.join(TRABAJO, 'textos.csv')

# Letras que el juego no sabe medir y se escriben con otro código (la fuente se cambió para dibujarlas ahí).
# v0.9 escribe las tildes reales: vacío. (Desde v0.10: {'Í': '|', 'í': '~'}.)
CAMBIOS_LETRA = {'Í': '|', 'í': '~'}
A_JUEGO = str.maketrans(CAMBIOS_LETRA)
DE_JUEGO = str.maketrans({v: k for k, v in CAMBIOS_LETRA.items()})


# ---------------------------------------------------------------- utilidades
def partool(*a):
    for intento in range(4):
        if a[0] == 'extract' and os.path.isdir(a[-1]): shutil.rmtree(a[-1], ignore_errors=True)
        r = subprocess.run([PARTOOL, *a], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode == 0 and b'ERROR' not in r.stdout.upper(): return
    raise RuntimeError(f'ParTool {a[0]} falló: {r.stdout[-300:]!r} {r.stderr[-300:]!r}')

def norm(s):
    return s.replace('\r\n', '\n').replace('\r', '\n')

def colk(ruta):
    p = ruta.split('/')
    return '/'.join(re.sub(r'^\d+$', '#', c) for c in p[2:]) if len(p) > 2 else ruta

def es_texto(s):
    """Lo que el jugador lee (no nombres de archivo, claves internas ni códigos)."""
    if not s or not s.strip(): return False
    if re.search(r'[぀-ヿ一-鿿]', s): return False
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

def leer_ruta(d, ruta):
    o = d
    for k in ruta.split('/'):
        o = o[int(k)] if isinstance(o, list) else o.get(k)
        if o is None: return None
    return o

def poner_ruta(d, ruta, nuevo):
    o = d; ks = ruta.split('/')
    for k in ks[:-1]: o = o[int(k)] if isinstance(o, list) else o[k]
    o[int(ks[-1]) if isinstance(o, list) else ks[-1]] = nuevo

def exportar_armp(bin_origen, carpeta):
    """Tabla ARMP (.bin) -> JSON con reARMP. Devuelve el diccionario."""
    os.makedirs(carpeta, exist_ok=True)
    nombre = os.path.basename(bin_origen); js = os.path.join(carpeta, nombre + '.json')
    if not os.path.exists(js):
        shutil.copy(bin_origen, os.path.join(carpeta, nombre))
        subprocess.run([sys.executable, REARMP, nombre], cwd=carpeta, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, check=True)
        os.remove(os.path.join(carpeta, nombre))
    return json.load(open(js, encoding='utf-8'))

def buscar_juego():
    import winreg
    carpetas = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam') as k: steam = winreg.QueryValueEx(k, 'SteamPath')[0]
        carpetas.append(steam)
        vdf = os.path.join(steam, 'steamapps', 'libraryfolders.vdf')
        if os.path.exists(vdf): carpetas += [m.replace('\\\\', '\\') for m in re.findall(r'"path"\s+"([^"]+)"', open(vdf, encoding='utf-8').read())]
    except OSError: pass
    for c in carpetas:
        d = os.path.join(c, 'steamapps', 'common', 'Yakuza 6 - The Song of Life', 'data')
        if os.path.exists(os.path.join(d, 'talk.par')): return d
    return None

def origen_ingles():
    """Carpeta con talk.par, font.par y db_e/ (o db/e/) ORIGINALES en inglés."""
    if '--ingles' in sys.argv: d = sys.argv[sys.argv.index('--ingles') + 1]
    elif os.path.exists(os.path.join(PAQUETE, 'respaldo_original', 'talk.par')): d = os.path.join(PAQUETE, 'respaldo_original')
    else:
        d = buscar_juego()
        if not d: sys.exit('No encontré el juego. Usa: --ingles "<carpeta data del juego>"')
        if os.path.exists(os.path.join(d, 'traduccion_es_version.txt')):
            sys.exit('El juego de Steam ya tiene la traducción puesta y no hay respaldo_original junto al instalador.\n'
                     'Quita la traducción o usa Steam > Propiedades > Archivos instalados > Verificar integridad.')
    db = os.path.join(d, 'db_e') if os.path.isdir(os.path.join(d, 'db_e')) else os.path.join(d, 'db', 'e')
    print(f'Inglés original: {d}')
    return d, db

def tablas():
    return sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ARCHIVOS, 'db_e', '*.bin')))

def filas_tabla(tabla, d_en):
    """Celdas de texto de una tabla: (ruta, inglés)."""
    out = []; recorrer(d_en, [], out)
    return [(r, s) for r, s in out if es_texto(s) and s.strip() and CLASES.get(f'{tabla}|{colk(r)}') == 'TEXTO']

def indice_talk():
    return list(csv.DictReader(open(os.path.join(AQUI, 'datos', 'talk_indice.csv'), encoding='utf-8-sig'), delimiter=';'))

def leer_cmn(ruta, off):
    data = open(ruta, 'rb').read(); fin = data.index(0, off)
    return data[off:fin].decode('utf-8')


# ---------------------------------------------------------------- extraer
def extraer():
    d_en, db_en = origen_ingles()
    os.makedirs(TRABAJO, exist_ok=True)
    unicos = collections.OrderedDict()          # inglés -> {es, donde, veces, bytes_max}
    def anotar(en, es, donde, bmax=None):
        k = norm(en); u = unicos.setdefault(k, {'es': '', 'donde': donde, 'veces': 0, 'bytes_max': None})
        u['veces'] += 1
        if es and not u['es']: u['es'] = norm(es).translate(DE_JUEGO)
        if bmax is not None: u['bytes_max'] = bmax if u['bytes_max'] is None else min(u['bytes_max'], bmax)
    print('Tablas de menús, objetos, misiones, subtítulos (db/e)...')
    for t in tablas():
        a = exportar_armp(os.path.join(db_en, t + '.bin'), os.path.join(TRABAJO, 'en', 'db_json'))
        b = exportar_armp(os.path.join(ARCHIVOS, 'db_e', t + '.bin'), os.path.join(TRABAJO, 'es', 'db_json'))
        for r, s in filas_tabla(t, a):
            es = leer_ruta(b, r)
            anotar(s, es if isinstance(es, str) and es != s else '', f'{t} | {colk(r)}')
    print('Diálogos de subhistorias y minijuegos (talk.par)... (medio minuto por cada talk.par)')
    for lado, par in (('en', os.path.join(d_en, 'talk.par')), ('es', os.path.join(ARCHIVOS, 'talk.par'))):
        dest = os.path.join(TRABAJO, lado, 'talk_todo')
        if not os.path.isdir(dest): partool('extract', '-r', par, dest)
    for f in indice_talk():
        rel = os.path.join(f['escena'], 'cmn.par', 'cmn.bin'); off = int(f['offset'])
        en = leer_cmn(os.path.join(TRABAJO, 'en', 'talk_todo', rel), off)
        es = leer_cmn(os.path.join(TRABAJO, 'es', 'talk_todo', rel), off)
        anotar(en, es if es != en else '', 'talk | ' + f['escena'].replace('\\', '/'), int(f['bytes_max']))
    with open(CSV_TEXTOS, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh, delimiter=';', quoting=csv.QUOTE_ALL)
        w.writerow(['id', 'donde', 'veces', 'bytes_max', 'ingles', 'espanol'])
        for i, (en, u) in enumerate(unicos.items()):
            w.writerow([i, u['donde'], u['veces'], '' if u['bytes_max'] is None else u['bytes_max'], en, u['es']])
    faltan = sum(1 for u in unicos.values() if not u['es'])
    print(f'\nListo: {len(unicos)} textos distintos en {CSV_TEXTOS}\n'
          f'  ({faltan} sin traducción: nombres propios, onomatopeyas o textos que se dejaron igual a propósito)')


# ---------------------------------------------------------------- aplicar
def leer_csv():
    if not os.path.exists(CSV_TEXTOS): sys.exit('Primero ejecuta «extraer» (no existe trabajo/textos.csv).')
    tr = {}
    with open(CSV_TEXTOS, encoding='utf-8-sig', newline='') as fh:
        primera = fh.readline(); fh.seek(0)
        sep = ';' if primera.count(';') >= primera.count(',') else ','     # Excel en otros idiomas guarda con comas
        for f in csv.DictReader(fh, delimiter=sep):
            es = norm(f.get('espanol') or '')
            if es.strip(): tr[norm(f['ingles'])] = es
    return tr

def aplicar():
    d_en, db_en = origen_ingles()
    tr = leer_csv(); problemas = []
    if os.path.isdir(SALIDA): shutil.rmtree(SALIDA)
    os.makedirs(os.path.join(SALIDA, 'db_e'))
    obra = os.path.join(TRABAJO, 'obra'); shutil.rmtree(obra, ignore_errors=True); os.makedirs(obra)
    print('Tablas (db/e)...'); n_db = 0
    for t in tablas():
        d = exportar_armp(os.path.join(db_en, t + '.bin'), os.path.join(TRABAJO, 'en', 'db_json'))
        d = json.loads(json.dumps(d))                                        # copia limpia
        n = 0
        for r, s in filas_tabla(t, d):
            es = tr.get(norm(s))
            if es is None: continue
            if '\r\n' in s: es = es.replace('\n', '\r\n')                   # mismo salto de línea que el original
            poner_ruta(d, r, es.translate(A_JUEGO)); n += 1
        if not n: shutil.copy(os.path.join(db_en, t + '.bin'), os.path.join(SALIDA, 'db_e', t + '.bin')); continue
        js = os.path.join(obra, t + '.bin.json')
        json.dump(d, open(js, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        subprocess.run([sys.executable, REARMP, t + '.bin.json'], cwd=obra, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=True)
        shutil.move(js + '.bin', os.path.join(SALIDA, 'db_e', t + '.bin')); n_db += n
    print(f'  {n_db} textos en {len(tablas())} tablas')
    print('Diálogos (talk.par)... (tarda: se rearma escena por escena)')
    capas = os.path.join(TRABAJO, 'en', 'talk_escenas')
    if not os.path.isdir(capas): partool('extract', os.path.join(d_en, 'talk.par'), capas)
    por_escena = collections.defaultdict(list)
    for f in indice_talk(): por_escena[f['escena']].append(f)
    add = os.path.join(obra, '_talk'); n_txt = 0
    for i, (esc, fs) in enumerate(sorted(por_escena.items())):
        par = os.path.join(capas, esc); w = os.path.join(obra, 'talk', os.path.splitext(esc)[0])
        a, b, c, dd = (os.path.join(w, x) for x in 'abcd')
        partool('extract', par, a); partool('extract', os.path.join(a, 'cmn.par'), b)
        ruta_bin = os.path.join(b, 'cmn.bin'); data = bytearray(open(ruta_bin, 'rb').read()); cambio = False
        for f in fs:
            off, mx = int(f['offset']), int(f['bytes_max'])
            en = leer_cmn(ruta_bin, off); es = tr.get(norm(en))
            if es is None: continue
            nb = es.translate(A_JUEGO).encode('utf-8')
            if len(nb) > mx:
                problemas.append(f'DEMASIADO LARGO ({len(nb)} bytes, caben {mx}), se deja en inglés: {es!r}'); continue
            data[off:off + mx + 1] = nb + bytes(mx + 1 - len(nb)); cambio = True; n_txt += 1
        if cambio:
            open(ruta_bin, 'wb').write(data)
            os.makedirs(c); shutil.copy(ruta_bin, os.path.join(c, 'cmn.bin'))
            os.makedirs(dd); partool('add', os.path.join(a, 'cmn.par'), c, os.path.join(dd, 'cmn.par'))
            destino = os.path.join(add, esc); os.makedirs(os.path.dirname(destino), exist_ok=True)
            partool('add', par, dd, destino)
        shutil.rmtree(w, ignore_errors=True)
        if i % 50 == 0: print(f'  escena {i + 1}/{len(por_escena)}')
    partool('add', os.path.join(d_en, 'talk.par'), add, os.path.join(SALIDA, 'talk.par'))
    print(f'  {n_txt} textos en {len(por_escena)} escenas')
    shutil.copy(os.path.join(ARCHIVOS, 'font.par'), os.path.join(SALIDA, 'font.par'))   # letra con tildes, ñ, ¿ ¡
    shutil.rmtree(obra, ignore_errors=True)
    if problemas:
        open(os.path.join(SALIDA, 'PROBLEMAS.txt'), 'w', encoding='utf-8').write('\n'.join(problemas) + '\n')
        print(f'\nOJO: {len(problemas)} textos no caben (lista en salida/PROBLEMAS.txt). Acórtalos y vuelve a aplicar.')
    if '--a-archivos' in sys.argv:
        shutil.copytree(SALIDA, ARCHIVOS, dirs_exist_ok=True)
        print(f'Copiado encima de {ARCHIVOS}: ahora ejecuta «INSTALAR o QUITAR.bat» y elige 1.')
    else:
        print(f'\nListo: {SALIDA}\nPara probarlo, copia su contenido encima de la carpeta «archivos» y ejecuta el instalador.')


if __name__ == '__main__':
    orden = sys.argv[1] if len(sys.argv) > 1 else ''
    if orden == 'extraer': extraer()
    elif orden == 'aplicar': aplicar()
    else: print(__doc__)
