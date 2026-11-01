# (01-11, claude2) Celdas de db/e que siguen en inglés: inglés original (trabajo/armp_json) contra la v1.0.2 (es_json).
import json, os, re, sys, collections
sys.path.insert(0, 'C:/Mods/yakuza5/herramientas')
from barrido import EN, ES
H = 'C:/Mods/yakuza6/entrega_v1.0.2/Herramientas para traduccion'
sys.argv = ['x']; sys.path.insert(0, H)
import herramienta_traduccion as ht
EJ = 'C:/Mods/yakuza6/trabajo/armp_json'; SJ = 'C:/Mods/yakuza6/trabajo/faltan_c2/es_json'
res = []
for f in sorted(os.listdir(EJ)):
    if not f.endswith('.bin.json'): continue
    t = f[:-9]
    if t == 'msg': continue                       # contrato de licencia: se queda en inglés (orden del usuario)
    a = json.load(open(f'{EJ}/{f}', encoding='utf-8'))
    b = json.load(open(f'{SJ}/{f}', encoding='utf-8')) if os.path.exists(f'{SJ}/{f}') else None
    out = []; ht.recorrer(a, [], out)
    for r, s in out:
        if not ht.es_texto(s): continue
        es = ht.leer_ruta(b, r) if b else None
        if isinstance(es, str) and es != s: continue
        w = [x.lower() for x in re.findall(r"[A-Za-z][a-z']*", s)]
        en = sum(x in EN for x in w)
        if not en and not os.environ.get("TODO"): continue
        res.append({'tabla': t, 'ruta': r, 'col': ht.colk(r), 'clase': ht.CLASES.get(f'{t}|{ht.colk(r)}'), 'en': s})
json.dump(res, open('C:/Mods/yakuza6/trabajo/faltan_c2/db_faltan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
c = collections.Counter((x['tabla'], x['col'], x['clase']) for x in res)
for k, n in c.most_common(): print(n, k, [x['en'][:50] for x in res if (x['tabla'], x['col'], x['clase']) == k][:3])
print('TOTAL', len(res), 'unicos', len({x['en'] for x in res}))
