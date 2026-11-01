# -*- coding: utf-8 -*-
"""(01-11-2026, claude2) «Lo que queda en ingles v1.0.3» del Yakuza 6, ordenado como pidió el usuario: SIN nombres de
personajes ni canciones (solo se cuentan); lo demás por grupos, cada texto con lo que dice la saga oficial latina
(glosario de claude1) para ver la coherencia. Salida: <carpeta>/2 Textos (txt)/NN grupo.txt
  python lista_ingles.py <carpeta destino>"""
import collections, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Mods/yakuza6/trabajo/faltan_c2'
DEST = sys.argv[1]
uni = json.load(open(f'{D}/unidades.json', encoding='utf-8'))
tr = json.load(open(f'{D}/traducido.json', encoding='utf-8'))
tr.update(json.load(open(f'{D}/correcciones.json', encoding='utf-8')))
g = json.load(open('C:/Mods/yakuza5/trabajo/saga/glosario.json', encoding='utf-8'))

PERSONAJES = ('character', 'caption', 'player', 'soldier', 'clan_creator_member', 'cabaret', 'npc', 'sound_auth',
              'auth', 'chat_names', 'darts_rival', 'complete_checklist')
CANCIONES = ('karaoke', 'song', 'music', 'snack_song')
GRUPOS = [  # (nombre del archivo, prueba sobre «donde» y el texto, por qué se deja)
    ('01 Objetos, comidas y bebidas (marcas)', lambda d, t: 'item' in d or 'food' in d or 'drink' in d,
     'Marcas y productos reales (se escriben igual en la saga oficial).'),
    ('02 Lugares y locales', lambda d, t: 'map_place' in d or 'shop' in d or 'stage' in d or 'loading' in d,
     'Nombres propios de locales y calles (la saga oficial también los deja).'),
    ('03 Minijuegos (términos)', lambda d, t: 'minigame' in d or 'manual' in d or 'controller_guide' in d,
     'Términos de juego: Cricket/Count-Up/dardos, Mahjong (yaku japoneses), nombres de juegos de Club SEGA.'),
    ('04 Opciones y menús', lambda d, t: 'option' in d or 'ui_text' in d or 'pause' in d,
     'Siglas técnicas (FXAA, SSAA, HDR...) y abreviaturas de estadísticas.'),
    ('05 Frases de diálogo', lambda d, t: d.startswith(('talk', 'hact', 'auth/')),
     'Interjecciones, nombres dichos en voz alta o textos que ya son iguales en español.'),
]
OTROS = ('06 Otros', 'Resto: códigos, nombres de modelos y textos iguales en los dos idiomas.')

def es_nombre_pj(d, t):
    if any(k in d for k in PERSONAJES) and not re.search(r'\b(the|of|and|you|to)\b', t): return True
    s = re.sub(r'<[^>]*>|[.!?,…]', '', t).strip()
    return bool(re.fullmatch(r"([A-Z][a-z]+|[A-Z]+)(-(san|kun|chan|aniki|chi|senpai|sama))?( [A-Z][a-z]+)?", s))

sys.path.insert(0, 'C:/Mods/yakuza5/herramientas')
from barrido import EN, ES
_p = json.load(open(f'{D}/pares_db.json', encoding='utf-8'))
_pal = lambda textos: collections.Counter(w.lower() for x in textos for w in re.findall(r"[A-Za-z][a-z']+", x))
VOC_EN, VOC_ES = _pal(_p.keys()), _pal(v.replace('~', 'í') for v in _p.values())
ES_VALORES = {v.replace('~', 'í') for v in _p.values()}
def ya_espanol(t):
    if re.search('[áéíóúñ¿¡]', t) or t in ES_VALORES or re.search(r'vaya|Iniciar', t): return True
    w = [x.lower() for x in re.findall(r"[A-Za-z][a-z']+", t)]
    es = sum(1 for x in w if VOC_ES[x] > 3 * VOC_EN[x]); en = sum(1 for x in w if VOC_EN[x] > 3 * VOC_ES[x])
    return es > en
def codigo(t):
    s = re.sub(r'<[^>]*>|\$\{[^}]*\}|color\[[^]]*\]|size\[[^]]*\]', '', t)
    letras = re.findall(r'[A-Za-z]{2,}', s)
    return (not letras or re.search(r'[{}#@\\[\]^]', s) or re.fullmatch(r'sample_\w+.*', t.strip())
            or re.fullmatch(r'[a-z_]+(,[a-z_]+)+', t.strip()) or 'TGT' in t or 'http' in t)

quedan = []; n_pj = n_can = n_es = n_cod = 0
for u in uni:
    t = tr.get(str(u['id']))
    if t is None or t != u['en']: continue
    d, en = u['donde'], u['en']
    if ya_espanol(en): n_es += 1; continue
    if codigo(en): n_cod += 1; continue
    if any(k in d for k in CANCIONES): n_can += 1; continue
    if es_nombre_pj(d, en): n_pj += 1; continue
    quedan.append(u)

por = collections.defaultdict(list)
for u in quedan:
    for nombre, prueba, _ in GRUPOS:
        if prueba(u['donde'], u['en']): por[nombre].append(u); break
    else: por[OTROS[0]].append(u)
txt = os.path.join(DEST, '2 Textos (txt)'); os.makedirs(txt, exist_ok=True)
motivo = {n: m for n, _, m in GRUPOS}; motivo[OTROS[0]] = OTROS[1]
resumen = []
for nombre in sorted(por):
    lineas = [f'{nombre[3:]}: {len(por[nombre])} textos. {motivo[nombre]}',
              'Formato: texto en inglés  |  saga oficial latina (Yakuza 0 DC, Kiwami 1/2/3)  |  dónde', '']
    for u in sorted(por[nombre], key=lambda u: u['en'].lower()):
        k = u['en'].strip(); of = g.get(k)
        saga = 'no sale en la saga' if not of else (lambda o: 'IGUAL en la saga' if o.strip() == k else f'saga: «{o.strip()}»')(max(of, key=of.get))
        lineas.append(f"{k.replace(chr(13), '').replace(chr(10), ' / ')}  |  {saga}  |  {u['donde']}")
    open(os.path.join(txt, nombre + '.txt'), 'w', encoding='utf-8-sig').write('\n'.join(lineas) + '\n')
    resumen.append((nombre, len(por[nombre])))
json.dump({'grupos': resumen, 'personajes': n_pj, 'canciones': n_can, 'ya_en_espanol': n_es, 'codigos': n_cod}, open(os.path.join(DEST, 'resumen.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(resumen, 'personajes', n_pj, 'canciones', n_can, 'ya español', n_es, 'códigos', n_cod)
