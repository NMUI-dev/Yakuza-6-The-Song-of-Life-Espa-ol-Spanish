# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Prepara los lotes de traducción del Yakuza 6.
Une los textos únicos de db/e (solo grupos TEXTO de clasificar_grupos.py) y de talk (talk_ingles.csv), y los reparte en
trabajo/lotes/lote_NNN.json: [{"id": n, "en": texto, "ctx": "tabla|columna (+ otras tablas donde sale)", "max": bytes o null}].
Las traducciones van en trabajo/lotes/lote_NNN_es.json: {"id": "texto en español"}.  Orden: primero menús e interfaz
(textos cortos), luego misiones/objetos/manual, y al final subtítulos y diálogos (lo más largo).
  python herramientas/preparar_lotes.py [letras_por_lote]
"""
import csv, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clasificar_grupos as C
T = C.T
LOTE = int(sys.argv[1]) if len(sys.argv) > 1 else 12000          # letras de inglés por lote

def prioridad(tabla):
    if tabla.startswith(('sound_auth', 'auth')) or tabla == 'talk': return 3
    if tabla.startswith(('minigame', 'clan_creator')): return 2
    if tabla in ('msg', 'option', 'ui_text', 'ui_preview_text', 'title_root', 'controller_guide', 'qloc_qloc_binding_actions') \
            or tabla.startswith('pause'): return 0
    return 1

if __name__ == '__main__':
    r, g = C.grupos(); cl = C.clasificar(g)
    unico = collections.OrderedDict()                                 # inglés -> {ctx set, max, prio}
    for x in r:
        if cl[(x['archivo'], C.colk(x['ruta']))] != 'TEXTO': continue
        if not x['ingles'].strip(): continue
        u = unico.setdefault(C.norm(x['ingles']), {'ctx': [], 'max': None, 'prio': 9})
        c = f"{x['archivo']}|{C.colk(x['ruta'])}"
        if c not in u['ctx']: u['ctx'].append(c)
        u['prio'] = min(u['prio'], prioridad(x['archivo']))
    talk = list(csv.reader(open(os.path.join(T, 'talk_ingles.csv'), encoding='utf-8-sig'), delimiter=';'))
    cab = talk[0]; ie, im = cab.index('ingles'), cab.index('bytes_max')
    for f in talk[1:]:
        u = unico.setdefault(f[ie], {'ctx': [], 'max': None, 'prio': 9})
        if 'talk' not in u['ctx']: u['ctx'].append('talk')
        m = int(f[im]); u['max'] = m if u['max'] is None else min(u['max'], m)
        u['prio'] = min(u['prio'], prioridad('talk'))
    items = sorted(unico.items(), key=lambda kv: (kv[1]['prio'], kv[1]['ctx'][0]))
    d = os.path.join(T, 'lotes'); os.makedirs(d, exist_ok=True)
    lotes = []; act = []; letras = 0
    for i, (en, u) in enumerate(items):
        act.append({'id': i, 'en': en, 'ctx': ' + '.join(u['ctx'][:3]) + (' …' if len(u['ctx']) > 3 else ''), 'max': u['max']})
        letras += len(en)
        if letras >= LOTE: lotes.append(act); act = []; letras = 0
    if act: lotes.append(act)
    for n, l in enumerate(lotes):
        json.dump(l, open(os.path.join(d, f'lote_{n:03d}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump({en: i for i, (en, _) in enumerate(items)}, open(os.path.join(d, 'indice.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(items), 'textos únicos,', sum(len(e) for e, _ in items), 'letras,', len(lotes), 'lotes;',
          collections.Counter(u['prio'] for _, u in items))
