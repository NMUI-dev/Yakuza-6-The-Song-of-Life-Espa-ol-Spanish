# (claude1, 06-11-2026) Avisos de los revisores que aún no tienen decisión (ni en decididas_escenas.json ni en
# rechazadas.json ni en las UNA/TERMINOS de correcciones_v105.py). Uso: python pendientes.py [máx=40]
import json
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
maxi = int(sys.argv[1]) if len(sys.argv) > 1 else 40


def ids(n, k=0):
    p = aqui / n
    return {str(x[k]) for x in json.load(open(p, encoding="utf-8"))} if p.exists() else set()


hechos = ids("decididas_escenas.json") | ids("rechazadas.json")
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8")) if (aqui / "correcciones.json").exists() else {}
hechos |= set(corr)
n = 0
total = 0
for f in sorted((aqui / "resultados").glob("paquete_*.json")):
    for x in json.load(open(f, encoding="utf-8")).get("fallos", []):
        i = str(x.get("id", "")).lstrip("#")
        if i in hechos:
            continue
        total += 1
        if n < maxi:
            n += 1
            print(f.stem[-3:], i, x.get("tipo"), "|", str(x.get("es", ""))[:85], "=>", str(x.get("propuesta", ""))[:85], "|",
                  str(x.get("porque", ""))[:100])
print("pendientes:", total)
