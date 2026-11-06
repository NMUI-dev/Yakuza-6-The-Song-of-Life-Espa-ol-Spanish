# Mete correcciones.json en un textos.csv de la herramienta de traducción del Y6, con el mismo formato
# (BOM, ; , todo entre comillas, \r\n entre filas, \n dentro de las celdas).
# Se niega si alguna frase actual no coincide con «antes» (alguien la cambió) y comprueba al final que solo cambiaron esas.
# Uso: python poner_correcciones.py <textos.csv>
import csv
import json
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
destino = Path(sys.argv[1])
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))

with open(destino, encoding="utf-8-sig", newline="") as fh:
    lector = csv.reader(fh, delimiter=";")
    cab = next(lector)
    filas = list(lector)
iid, ies = cab.index("id"), cab.index("espanol")

hechas, mal = 0, []
for f in filas:
    c = corr.get(f[iid])
    if not c:
        continue
    if f[ies].replace("\r\n", "\n") != c["antes"]:
        mal.append(f[iid])
        continue
    f[ies] = c["es"]
    hechas += 1
if mal or hechas != len(corr):
    sys.exit("NO SE ESCRIBE: no coinciden %s; hechas %d de %d" % (mal, hechas, len(corr)))

with open(destino, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    w.writerow(cab)
    w.writerows(filas)

# Comprobación: releer y comparar con lo pedido.
with open(destino, encoding="utf-8-sig", newline="") as fh:
    nuevas = {r["id"]: r["espanol"] for r in csv.DictReader(fh, delimiter=";")}
assert all(nuevas[i] == c["es"] for i, c in corr.items())
print("puestas %d correcciones en %s" % (hechas, destino))
