# -*- coding: utf-8 -*-
"""(01-11, claude2) Mete en el juego lo traducido (traducido.json) sobre la v1.0.2:
  - talk.par (Spanish v1.0.2) + hact/*.par + auth/*.par: cmn.bin escrito en su sitio (mismo hueco, ceros al final).
  - db_e: tablas de la v1.0.2 (o la inglesa si no estaba traducida) con las celdas nuevas, rearmadas con reARMP.
Salida: trabajo/faltan_c2/salida/{talk.par, db_e/*.bin, extra/hact/..., extra/auth/...}
  python aplicar.py"""
import json, os, re, shutil, subprocess, sys, collections
D = 'C:/Mods/yakuza6/trabajo/faltan_c2'
V102 = 'C:/Mods/yakuza6/entrega_v1.0.2/archivos'
GAME = 'D:/SteamLibrary/steamapps/common/Yakuza 6 - The Song of Life/data'
H = 'C:/Mods/yakuza6/entrega_v1.0.2/Herramientas para traduccion'
PT = f'{H}/programas/ParTool/ParTool.exe'
REARMP = 'C:/Mods/yakuza6/herramientas/reARMP/reARMP.py'
sys.argv = sys.argv[:1]; sys.path.insert(0, H)
import herramienta_traduccion as ht
# (01-11) la í va en la casilla «`» (estrecha; la de «~» dejaba hueco: «Subt í tulos»): font.par de letra_i_estrecha.py
A_JUEGO = str.maketrans({'Í': '|', 'í': '`'})
SAL = f'{D}/salida'; OBRA = f'{D}/obra'

def _rm(f, p, e):
    os.chmod(p, 0o666); f(p)
def borrar(d):
    if os.path.isdir(d): shutil.rmtree(d, onexc=_rm)

def partool(*a):
    import time
    for intento in range(5):        # (01-11) a veces Windows aún tiene la carpeta anterior bloqueada: reintentar
        if a[0] == 'extract':
            try: borrar(a[-1])
            except OSError: time.sleep(2); continue
        r = subprocess.run([PT, *a], stdin=subprocess.DEVNULL, capture_output=True)
        if not (r.returncode or b'ERROR:' in r.stdout.upper() or b'EXCEPTION' in r.stdout.upper()): return
        time.sleep(2)
    raise SystemExit(f'ParTool {a}: {r.stdout[-400:]!r} {r.stderr[-300:]!r}')

uni = {u['id']: u for u in json.load(open(f'{D}/unidades.json', encoding='utf-8'))}
tr = json.load(open(f'{D}/traducido.json', encoding='utf-8'))
if os.path.exists(f'{D}/correcciones.json'): tr.update(json.load(open(f'{D}/correcciones.json', encoding='utf-8')))   # a mano
for i, s in tr.items():     # el mismo título en los 5 resúmenes («Los sucesos de 2012» ya está así en el juego)
    if 'kaisou' in uni[int(i)]['donde']: tr[i] = re.sub(r'^Los (eventos|acontecimientos|hechos) de Yakuza', 'Los sucesos de Yakuza', s)
es_de = {uni[int(i)]['en']: s for i, s in tr.items() if s != uni[int(i)]['en']}
print(f'{len(es_de)} textos traducidos distintos del inglés (de {len(tr)} devueltos)')
borrar(SAL); borrar(OBRA); os.makedirs(f'{SAL}/db_e'); os.makedirs(OBRA)
problemas = []

# ---------------------------------------------------------------- cmn.bin
por = collections.defaultdict(list)
for r in json.load(open(f'{D}/cmn_ingles.json', encoding='utf-8')):
    if r['en'] in es_de: por[r['f']].append(r)
# (01-11) frases cortas («Yes», «Go», «Cheers!») que ningún extractor cogía: hueco medido en cmn_sueltas.json
SUELTAS = json.load(open(f'{D}/sueltas_es.json', encoding='utf-8'))
for r in json.load(open(f'{D}/cmn_sueltas.json', encoding='utf-8')):
    if SUELTAS.get(r['en'], r['en']) != r['en']: es_de.setdefault(r['en'], SUELTAS[r['en']]); por[r['f']].append(r)
# los diálogos ya traducidos en la v1.0 (talk_indice): solo cambiar «~» -> «`» dentro del texto
for f in ht.indice_talk():
    por[f"talk.par_par/{f['escena'].replace(os.sep, '/')}/cmn.par"].append({'off': int(f['offset']), 'solo_i': True})
def parte(rel):
    """x/<rel> -> (contenedor, ruta dentro). talk.par_par/kaisou/e/ryu01.par/cmn.par -> ('talk', 'kaisou/e/ryu01.par')"""
    rel = rel[:-len('/cmn.par')]
    if rel.startswith('talk.par_par/'): return 'talk', rel[len('talk.par_par/'):]
    return 'suelto', rel[:-len('_par')] if rel.endswith('.par_par') else rel
talk_add = f'{OBRA}/talk_add'; n_cmn = n_i = 0
for rel, rs in sorted(por.items()):
    tipo, ruta = parte(rel)
    w = f'{OBRA}/w'; borrar(w)
    if tipo == 'talk':
        par = f'{OBRA}/talk_escenas/{ruta}'
        if not os.path.exists(par):
            # sacar la escena del talk.par de la v1.0.2 (sin recursión: el .par de la escena entero)
            if not os.path.isdir(f'{OBRA}/talk_escenas'): partool('extract', f'{V102}/talk.par', f'{OBRA}/talk_escenas')
    else:
        par = f'{GAME}/{ruta}'
    partool('extract', par, f'{w}/a'); partool('extract', f'{w}/a/cmn.par', f'{w}/b')
    data = bytearray(open(f'{w}/b/cmn.bin', 'rb').read())
    for r in rs:
        if r.get('solo_i'):
            fin = data.index(0, r['off'])
            if b'~' in data[r['off']:fin]: data[r['off']:fin] = data[r['off']:fin].replace(b'~', b'`'); n_i += 1
            continue
        off, mx = r['off'], r['max']
        actual = data[off:data.index(0, off)].decode('utf-8')
        if actual != r['en']: problemas.append(f'{rel}@{off}: no coincide el inglés ({actual[:40]!r})'); continue
        nb = es_de[r['en']].translate(A_JUEGO).encode('utf-8')
        if len(nb) > mx: problemas.append(f'{rel}@{off}: no cabe ({len(nb)}>{mx}) {es_de[r["en"]][:50]!r}'); continue
        if any(data[off + len(r['en'].encode()):off + mx + 1]): problemas.append(f'{rel}@{off}: hueco no vacío'); continue
        data[off:off + mx + 1] = nb + bytes(mx + 1 - len(nb)); n_cmn += 1
    os.makedirs(f'{w}/c'); open(f'{w}/c/cmn.bin', 'wb').write(data)
    os.makedirs(f'{w}/d'); partool('add', f'{w}/a/cmn.par', f'{w}/c', f'{w}/d/cmn.par')
    dest = f'{talk_add}/{ruta}' if tipo == 'talk' else f'{SAL}/extra/{ruta}'
    os.makedirs(os.path.dirname(dest), exist_ok=True); partool('add', par, f'{w}/d', dest)
print(f'cmn: {n_cmn} textos nuevos, {n_i} con í cambiada, en {len(por)} archivos')
if os.path.isdir(talk_add): partool('add', f'{V102}/talk.par', talk_add, f'{SAL}/talk.par')

# ---------------------------------------------------------------- db_e
EJ = 'C:/Mods/yakuza6/trabajo/armp_json'; SJ = f'{D}/es_json'
cel = collections.defaultdict(list)
for r in json.load(open(f'{D}/db_faltan.json', encoding='utf-8')):
    if r['en'] in es_de: cel[r['tabla']].append(r)
extra_db = json.load(open(f'{D}/db_extra.json', encoding='utf-8')) if os.path.exists(f'{D}/db_extra.json') else {}
for t in extra_db: cel.setdefault(t, [])
# (01-11) subtítulos de UNA palabra («Thanks.», «Right.») que el extractor de la v1.0 tomaba por códigos
# pasada general por TODAS las tablas: celdas de texto (no ID) iguales a una clave de sueltas_es.json
for f in os.listdir(EJ):
    if not f.endswith('.bin.json') or f == 'msg.bin.json': continue
    t = f[:-9]; a = json.load(open(f'{EJ}/{f}', encoding='utf-8')); o = []; ht.recorrer(a, [], o)
    for r, s_en in o:
        clase = ht.CLASES.get(f'{t}|{ht.colk(r)}')
        # sin puntuación («Yes», «Go») podría ser un código interno: solo en columnas marcadas como TEXTO
        if s_en in SUELTAS and SUELTAS[s_en] != s_en and clase != 'ID' and (clase == 'TEXTO' or re.search(r'[.!?…)]$', s_en)):
            extra_db.setdefault(t, {})[r] = SUELTAS[s_en].translate(A_JUEGO); cel.setdefault(t, [])
for f in os.listdir(SJ):
    if f.endswith('.bin.json'): cel.setdefault(f[:-9], [])
def cambiar_i(o):
    if isinstance(o, dict): return {k: cambiar_i(v) for k, v in o.items()}
    if isinstance(o, list): return [cambiar_i(v) for v in o]
    return o.replace('~', '`') if isinstance(o, str) else o
# (01-11) términos de la saga oficial APROBADOS por el usuario (claude1: trabajo/terminos_aprobados_y6.json): la celda
# cuyo inglés original es «en» y que sigue igual (o como «ahora») pasa a «nuevo»
TERM = json.load(open('C:/Mods/yakuza6/trabajo/terminos_aprobados_y6.json', encoding='utf-8'))['cambios']
TERM_EN = {x['en']: x for x in TERM}
for x in TERM:
    for c in x['ctx'].split(' + '): cel.setdefault(c.split('|')[0].strip(), [])
n_db = n_term = 0
for t, rs in sorted(cel.items()):
    base = f'{SJ}/{t}.bin.json' if os.path.exists(f'{SJ}/{t}.bin.json') else f'{EJ}/{t}.bin.json'
    d = json.load(open(base, encoding='utf-8'))
    for r in rs:
        ht.poner_ruta(d, r['ruta'], es_de[r['en']].translate(A_JUEGO)); n_db += 1
    for ruta, v in extra_db.get(t, {}).items():
        ht.poner_ruta(d, ruta, v); n_db += 1
    if os.path.exists(f'{SJ}/{t}.bin.json'): d = cambiar_i(d)
    a_en = json.load(open(f'{EJ}/{t}.bin.json', encoding='utf-8')); celdas = []; ht.recorrer(a_en, [], celdas)
    for r, s_en in celdas:
        x = TERM_EN.get(s_en)
        if x and ht.leer_ruta(d, r) in (x['en'], x['ahora']):
            ht.poner_ruta(d, r, x['nuevo'].translate(A_JUEGO)); n_term += 1
    js = f'{OBRA}/{t}.bin.json'
    json.dump(d, open(js, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    subprocess.run([sys.executable, REARMP, t + '.bin.json'], cwd=OBRA, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=True)
    shutil.move(js + '.bin', f'{SAL}/db_e/{t}.bin')
print(f'db: {n_db} celdas en {len(cel)} tablas; términos oficiales: {n_term} celdas')
open(f'{SAL}/PROBLEMAS.txt', 'w', encoding='utf-8').write('\n'.join(problemas) + '\n')
print(f'{len(problemas)} problemas (salida/PROBLEMAS.txt)')
