# (01-11, claude2) Textos de cmn.bin (talk/hact/auth) que siguen en inglés en el juego instalado (v1.0).
# Cada texto va en un hueco de tamaño fijo (múltiplo de 16, ceros al final) seguido de su versión china; el tamaño del
# hueco está escrito poco antes del texto (cabecera). Hueco = ese tamaño - 1 (el 0 final). Si no se encuentra la
# cabecera, hueco = lo que ocupa el inglés redondeado a 16 (lo seguro).
import json, os, re, struct, sys, collections
sys.path.insert(0, 'C:/Mods/yakuza5/herramientas')
from barrido import EN, ES
# (barrido final de lo ARMADO: python cmn_scan.py <carpeta extraída> <salida.json>)
X = sys.argv[1] if len(sys.argv) > 2 else 'C:/Mods/yakuza6/trabajo_barrido/b3110/x'
SALIDA = sys.argv[2] if len(sys.argv) > 2 else 'C:/Mods/yakuza6/trabajo/faltan_c2/cmn_ingles.json'

def es_ingles(t):
    if re.search('[áéíóúñ¿¡ÁÉÍÓÚÑ~|`]', t): return False
    w = [x.lower() for x in re.findall(r"[A-Za-z][a-z']*", re.sub(r'<[^>]*>', '', t))]
    en = sum(x in EN for x in w); es = sum(x in ES for x in w)
    return en > es or (en == es == 0 and len(w) >= 2)

res = []; cabe = collections.Counter()
for raiz, ds, fs in os.walk(X):
    if 'cmn.bin' not in fs: continue
    rel = os.path.relpath(raiz, X).replace(os.sep, '/')
    if not rel.startswith(('talk.par_par', 'hact', 'auth')): continue
    d = open(os.path.join(raiz, 'cmn.bin'), 'rb').read()
    for s in range(16, len(d) - 4, 4):
        if d[s] == 0 or d[s - 1] != 0: continue
        e = d.find(b'\0', s)
        if e < 0 or e - s < 4: continue
        try: t = d[s:e].decode('utf-8')
        except UnicodeDecodeError: continue
        if not t.replace('\r', '').replace('\n', '').replace('\t', '').isprintable(): continue
        if re.search(r'[\u3000-\u9fff\uac00-\ud7af\uff00-\uffef]', t): continue
        sin = re.sub(r'<[^>]*>', '', t)
        if not re.search(r'[A-Za-z]{3}', sin) or sum(c.isalpha() or c == ' ' for c in sin) < 0.75 * len(sin): continue
        if ' ' not in sin.strip() and not re.fullmatch(r"[A-Z][a-z]+[.!?]*", sin): continue
        f = e
        while f < len(d) and d[f] == 0: f += 1
        hueco = (f - s) // 16 * 16
        if hueco and struct.pack('<I', hueco) in d[max(0, s - 48):s]: mx = hueco - 1; cabe['cabecera'] += 1
        else: mx = max(len(t.encode()), (len(t.encode()) + 16) // 16 * 16 - 1); cabe['seguro'] += 1
        if es_ingles(t): res.append({'f': rel, 'off': s, 'max': mx, 'en': t})
json.dump(res, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
c = collections.Counter('/'.join(r['f'].split('/')[:2]) for r in res)
print(len(res), 'únicos', len({r['en'] for r in res}), dict(cabe), c.most_common(40))
