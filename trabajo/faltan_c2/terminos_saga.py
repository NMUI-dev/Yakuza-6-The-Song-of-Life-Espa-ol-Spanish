# -*- coding: utf-8 -*-
"""(01-11-2026, claude2) Y6 v1.0.3: lo que sigue EN INGLÉS (traducido.json igual al inglés) y la saga oficial latina sí
traduce (glosario de claude1: yakuza5/trabajo/saga/glosario.json) = se nos pasó. Mismas reglas que el Y5 (terminos_v103.py):
Heat, DEALER, HOME RUN, Cricket/Count-Up, marcas y nombres se quedan; si lo oficial no cabe (menús cortos o hueco del
cmn.bin), se deja el inglés. Escribe saga_cambios.json [{id, donde, en, oficial, n}] y saga_correcciones.json {id: oficial}.
  python terminos_saga.py"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Mods/yakuza6/trabajo/faltan_c2'
DEJAR = re.compile(r'\bheat\b|\bdealer\b|home ?run|cricket|count-?up|bull\b|\bsega\b|don quijote|\bboss\b|club\b', re.I)
g = json.load(open('C:/Mods/yakuza5/trabajo/saga/glosario.json', encoding='utf-8'))
uni = json.load(open(f'{D}/unidades.json', encoding='utf-8'))
tr = json.load(open(f'{D}/traducido.json', encoding='utf-8'))
nb = lambda s: len(s.replace('í', '`').encode('utf-8'))
cambios = []
for u in uni:
    en = u['en']; t = tr.get(str(u['id']))
    if t is None or t.strip().lower() != en.strip().lower(): continue
    k = en.strip()
    if k not in g or DEJAR.search(k) or not re.search('[a-z]', k): continue
    of = max(g[k], key=g[k].get).strip(); n = g[k][of]
    if of.lower() == k.lower() or ('\n' in of) != ('\n' in k) or not re.search('[a-záéíóúñ]', of): continue
    if len(k) <= 25 and len(of) > max(len(k) * 1.6, len(k) + 8): continue
    if u['max'] and nb(of) > u['max']: continue
    cambios.append({'id': u['id'], 'donde': u['donde'], 'en': en, 'oficial': of, 'n': n})
json.dump(cambios, open(f'{D}/saga_cambios.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for c in cambios: print(f"{c['donde'][:40]:40} {c['en']!r:40} -> {c['oficial']!r} ({c['n']})")
print(len(cambios), 'cambios')
