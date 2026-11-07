# (claude1, 06-11-2026) Subtítulos con una línea más larga que la línea inglesa más larga de su tabla (barrido_extra.py,
# LARGO): reparte las MISMAS palabras entre el MISMO número de líneas para que la más larga sea lo más corta posible.
# Solo se propone si así ya no pasa del máximo inglés. Las de una sola línea se listan aparte (no se pueden partir sin
# cambiar los saltos). Escribe las propuestas como decisiones (decidir.py) y lista lo que queda.
# Uso: python equilibrar_lineas.py
import csv
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
csv.field_size_limit(10 ** 9)
TEXTOS = r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv"
ETQ = re.compile(r"<[^>]*>")
filas = {r["id"]: r for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";")}
largos = [l.split("\t") for l in open(aqui / "barrido_extra.txt", encoding="utf-8") if l.startswith("LARGO\t")]


def ancho(s):
    return len(ETQ.sub("", s))


def mejor(palabras, n):
    """reparte palabras en n líneas minimizando la más larga (fuerza bruta sobre los cortes)"""
    res = None
    for cortes in itertools.combinations(range(1, len(palabras)), n - 1):
        ls = [" ".join(palabras[a:b]) for a, b in zip((0,) + cortes, cortes + (len(palabras),))]
        m = max(ancho(x) for x in ls)
        if res is None or m < res[0]:
            res = (m, ls)
    return res


una_linea = []
for _, idt, detalle, _, _ in largos:
    r = filas[idt]
    es = r["espanol"].replace("\r\n", "\n")
    tope = int(re.search(r"tabla: (\d+)", detalle).group(1))
    n = es.count("\n") + 1
    if n == 1 and r["donde"].startswith("auth_costume"):   # nombre de traje en un menú: no se parte
        una_linea.append((idt, ancho(es), tope, es))
        continue
    if n == 1:      # subtítulo de una línea: en estas tablas hay subtítulos de 2 líneas, así que se parte en 2
        n = 2
    if "\n\n" in es:
        continue
    m, ls = mejor(es.split(), n)
    nuevo = "\n".join(ls)
    if (m <= tope or m < max(ancho(x) for x in es.split("\n"))) and nuevo != es:
        subprocess.run([sys.executable, str(aqui / "decidir.py"), "si", idt, es, nuevo, "largo",
                        "línea de %d letras > %d (la más larga del inglés en esa tabla): mismas palabras, saltos repartidos"
                        % (max(ancho(x) for x in es.split("\n")), tope)], check=True)
    else:
        una_linea.append((idt, ancho(es), tope, es))
print("no se pueden equilibrar (una línea o no baja del tope):")
for x in una_linea:
    print("  %s  %d > %d  %s  [%s]" % (x[0], x[1], x[2], x[3].replace("\n", " / ")[:120], filas[x[0]]["donde"][:40]))
