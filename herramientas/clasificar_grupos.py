# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Agrupa trabajo/db_e_ingles.csv por (tabla, columna) y clasifica cada grupo en TEXTO (lo ve
el jugador), ID (nombres internos, rutas, claves: NO se traducen) o DUDA (revisar a mano). Escribe trabajo/clases_grupos.json.
Las decisiones a mano van en MANUAL (ganan sobre lo automático)."""
import csv, re, collections, json, os, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(RAIZ, 'trabajo')
BARRA = chr(92)
MANUAL = {
    'ui_text|text': 'TEXTO', 'minigame_sandlot_baseball_message|text': 'TEXTO',
    'minigame_live_chat_chat_names|name': 'ID',            # apodos del chat: se dejan
    'scene_scenario_color_set|prefix': 'ID', 'series_reward|title_id': 'ID', 'clan_creator_member|password_to_unlock': 'ID',
    'minigame_live_chat_chat_commands|input_character': 'ID', 'minigame_live_chat_chat_commands_b|input_character': 'ID',  # lo que se teclea, va con «button»
    'sound_category|stream_type': 'ID', 'pause_tutorial|command': 'ID',
}

def colk(ruta):
    p = ruta.split('/')
    return '/'.join(re.sub(r'^\d+$', '#', c) for c in p[2:]) if len(p) > 2 else ruta

def norm(s):
    """Clave de traducción: saltos de línea como \n (los lotes se hicieron así; el juego usa \r\n en algunas tablas)."""
    return s.replace('\r\n', '\n').replace('\r', '\n')

def es_id(s):
    return bool(re.fullmatch(r'[' + BARRA * 2 + r'/A-Za-z0-9_.\-#:]+', s)) and (
        s.isupper() or '_' in s or BARRA in s or '/' in s or '.' in s or re.search(r'\d', s) or s.islower())

def grupos():
    r = list(csv.DictReader(open(os.path.join(T, 'db_e_ingles.csv'), encoding='utf-8-sig', newline='')))   # newline='': conservar los \r\n del juego
    g = collections.defaultdict(list)
    for x in r: g[(x['archivo'], colk(x['ruta']))].append(x['ingles'])
    return r, g

def clasificar(g):
    cl = {}
    for k, v in g.items():
        esp = sum(1 for s in v if ' ' in s.strip() or '\n' in s) / len(v)
        ids = sum(1 for s in v if es_id(s)) / len(v)
        cl[k] = 'ID' if ids >= 0.8 else 'TEXTO' if (esp >= 0.5 or ids == 0) else 'DUDA'
        cl[k] = MANUAL.get(f'{k[0]}|{k[1]}', cl[k])
    return cl

if __name__ == '__main__':
    r, g = grupos(); cl = clasificar(g)
    print(collections.Counter(cl.values()))
    print('filas por clase', collections.Counter(cl[(x['archivo'], colk(x['ruta']))] for x in r))
    json.dump({f'{a}|{b}': v for (a, b), v in cl.items()}, open(os.path.join(T, 'clases_grupos.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    for clase in sys.argv[1:]:
        for k, v in sorted(g.items()):
            if cl[k] == clase:
                u = list(dict.fromkeys(v)); print(clase, k[0], k[1], len(v), ' ¦ '.join(s[:30].replace('\n', '⏎') for s in u[:6]))
