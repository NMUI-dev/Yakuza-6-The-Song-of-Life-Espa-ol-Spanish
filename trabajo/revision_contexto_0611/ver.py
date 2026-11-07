# (claude1, 06-11-2026) Muestra cada id con su escena alrededor (de los paquetes), para decidir a mano con contexto.
# Uso: python ver.py [radio=6] id1 id2 ...      (o «python ver.py 6 @resultados/paquete_003.json» para todos sus avisos)
import json
import re
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
radio = int(sys.argv[1])
ids = []
for a in sys.argv[2:]:
    if a.startswith("@"):
        ids += [str(f["id"]).lstrip("#") for f in json.load(open(a[1:], encoding="utf-8")).get("fallos", [])]
    else:
        ids.append(a)
escenas = []
for p in sorted(aqui.glob("paquetes/paquete_*.txt")):
    nombre, ls = None, []
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.startswith("=== ESCENA "):
            if ls:
                escenas.append((nombre, ls))
            nombre, ls = l[11:-4], []
        elif l.strip():
            ls.append(l)
    if ls:
        escenas.append((nombre, ls))
for i in ids:
    pat = re.compile(r"^#%s(?: x\d+)? " % re.escape(i))
    vistos = 0
    for nombre, ls in escenas:
        for k, l in enumerate(ls):
            if pat.match(l):
                vistos += 1
                if vistos > 2:
                    continue
                print("##### %s en %s" % (i, nombre))
                for j in range(max(0, k - radio), min(len(ls), k + radio + 1)):
                    print((">> " if j == k else "   ") + ls[j][:230])
    if vistos > 2:
        print("   (... sale en %d sitios en total)" % vistos)
