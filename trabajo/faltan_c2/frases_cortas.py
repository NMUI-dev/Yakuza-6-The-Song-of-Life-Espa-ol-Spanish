# -*- coding: utf-8 -*-
"""(01-11-2026, claude2; idea de claude1: yakuza5/herramientas/frases_cortas_ingles.py) Frases CORTAS (una palabra o una
letra: «Thanks.», «I...», «I'm...», «Y-Yeah...») que sigan en inglés en lo ARMADO del Y6: TODAS las tablas de db/e (las
de salida/db_e o, si no se tocaron, las originales) y los cmn.bin extraídos por barrido_final.py (barrido_x).
  python frases_cortas.py"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Mods/yakuza6/trabajo/faltan_c2'
EN = set("""i i... thanks thank sorry right yeah yes yep yup nope welcome okay please what wait huh hmm hm sure fine great damn
shit hello hi bye goodbye ready stop look listen i'm i you me him her it really seriously indeed alright understood
excellent perfect exactly correct wow whoa what's who where why when how well hey uh um er boss bro brother sir kid
nothing something everyone everybody anyone someone good bad nice cool awesome idiot fool liar dammit fuck jeez geez
cheers congratulations congrats later next simple presumably certainly obviously absolutely definitely maybe perhaps
again enough go come move run help leave shut die kill fight hurry quiet relax calm easy careful agreed gotcha crap
father daddy mother mom thanks apologies interesting strange true finally basically anyway because but and so then""".split())
ES_TAMBIEN = {'no', 'oh', 'ah', 'eh', 'hey', 'ok', 'uy', 'bip', 'grr', 'boss'}
def es_corta_ingles(t):
    t2 = re.sub(r'<[^>]*>', '', t).strip()
    if re.search('[áéíóúñ¿¡`|]', t2) or len(t2) > 30: return False
    if not re.fullmatch(r"[\[(\"]?[.…]*[A-Z][A-Za-z'\-]*[.!?…,]*[\])\"]?", t2): return False     # texto de verdad, no ids
    w = re.findall(r"[A-Za-z][a-z']*", re.sub(r'\b([A-Za-z])-(?=\1)', '', t2, flags=re.I))   # «Y-Yeah» -> «Yeah»
    return len(w) == 1 and w[0].lower() in EN and w[0].lower() not in ES_TAMBIEN
res = collections.Counter()
EJ = 'C:/Mods/yakuza6/trabajo/armp_json'; BJ = f'{D}/barrido_db'
for f in os.listdir(EJ):
    if not f.endswith('.bin.json') or f == 'msg.bin.json': continue
    p = f'{BJ}/{f}' if os.path.exists(f'{BJ}/{f}') else f'{EJ}/{f}'
    for s in re.findall(r'"((?:[^"\\]|\\.)*)"', open(p, encoding='utf-8').read()):
        try: s = json.loads(f'"{s}"')
        except Exception: continue
        if es_corta_ingles(s): res[(s, 'db/' + f[:-9])] += 1
for raiz, ds, fs in os.walk(f'{D}/barrido_x'):
    if 'cmn.bin' not in fs: continue
    d = open(os.path.join(raiz, 'cmn.bin'), 'rb').read()
    for m in re.finditer(rb'(?<=\x00)[ -~]{1,30}(?=\x00)', d):
        s = m.group().decode()
        if es_corta_ingles(s): res[(s, os.path.relpath(raiz, f'{D}/barrido_x').replace(os.sep, '/'))] += 1
json.dump([{'en': s, 'donde': w, 'veces': n} for (s, w), n in res.items()], open(f'{D}/frases_cortas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for (s, w), n in sorted(res.items()): print(n, repr(s), w)
print(len(res), 'frases cortas en inglés')
