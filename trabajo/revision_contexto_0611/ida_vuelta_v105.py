# (claude1, 07-11-2026) Ida y vuelta de la v1.0.5: guarda el textos.csv que dejó «meter» (lo que se quería meter), vuelve a
# EXTRAER de archivos/ (lo armado) y compara fila a fila (inglés + español). Tiene que dar 0 diferencias.
# Un español igual al inglés sale vacío al extraer (la herramienta no lo saca): cuenta como igual.
# Uso (después de armar_v105.py todo): python -I -X utf8 ida_vuelta_v105.py
import csv
import shutil
import subprocess
import sys
from pathlib import Path

HERR = Path(r"C:\Mods\yakuza6\entrega_v1.0.5\Herramientas para traduccion")
INGLES = Path(r"C:\Mods\yakuza6\trabajo\faltan_c2\orig_en")
CSV = HERR / "trabajo" / "textos.csv"
QUERIA = Path(__file__).resolve().parent / "logs" / "textos_queria_v105.csv"
csv.field_size_limit(10 ** 9)
norm = lambda s: s.replace("\r\n", "\n").replace("\r", "\n")


def leer(p):
    return {(r["donde"], norm(r["ingles"])): norm(r["espanol"])
            for r in csv.DictReader(open(p, encoding="utf-8-sig", newline=""), delimiter=";")}


shutil.copy(CSV, QUERIA)
r = subprocess.run([sys.executable, "-X", "utf8", "herramienta_traduccion.py", "extraer", "--ingles", str(INGLES)],
                   cwd=HERR, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
if r.returncode:
    sys.exit("extraer falló")
a, b = leer(QUERIA), leer(CSV)
dif = []
for k in sorted(set(a) | set(b)):
    x, y = a.get(k), b.get(k)
    if x == y or (x == k[1] and y == "") or (y == k[1] and x == ""):
        continue
    dif.append((k, x, y))
print("filas que se querían: %d | filas extraídas de lo armado: %d | diferencias: %d" % (len(a), len(b), len(dif)))
for k, x, y in dif[:30]:
    print("  ", k[0][:50], repr(k[1][:40]), repr((x or "")[:50]), "->", repr((y or "")[:50]))
sys.exit(1 if dif else 0)
