# (claude1, 06-11-2026) Cada letra del español debe existir en la fuente del juego (font.par: e/gothic.bin), o sale en
# blanco. Fallo real (idea de Gemini): «6.º piso», «1.ª victoria», « », «déjà vu»: la fuente no tiene º ª « » à.
# Uso: python letras_fuente.py <textos.csv> <carpeta con font.par extraído (la que tiene e/gothic.bin)> [correcciones.json]
import csv
import json
import struct
import sys
from pathlib import Path

csv.field_size_limit(10 ** 9)
textos, fuente = sys.argv[1], Path(sys.argv[2])
corr = json.load(open(sys.argv[3], encoding="utf-8")) if len(sys.argv) > 3 else {}
d = open(fuente / "e" / "gothic.bin", "rb").read()
n = struct.unpack_from("<I", d, 0x10)[0]
codigos = {struct.unpack_from("<I", d, 0x30 + i * 32)[0] for i in range(n)}
CAMBIADAS = {"Í": "|", "í": "`"}   # la herramienta las escribe en otra casilla (ver herramienta_traduccion.py)


def tiene(ch):
    ch = CAMBIADAS.get(ch, ch)
    return ch in "\n\r\t " or int.from_bytes(ch.encode("utf-8"), "big") in codigos


faltan = {}
for r in csv.DictReader(open(textos, encoding="utf-8-sig", newline=""), delimiter=";"):
    es = corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]
    es_sin_etq = "".join(es.split("<")[0:1]) + "".join(x.split(">", 1)[-1] for x in es.split("<")[1:])
    for ch in set(es_sin_etq):
        if not tiene(ch) and ch not in r["ingles"]:   # si el inglés original ya la lleva (©), es cosa del juego
            faltan.setdefault(ch, []).append(r["id"])
for ch, ids in sorted(faltan.items(), key=lambda kv: -len(kv[1])):
    print("FALTA %r (U+%04X) en %d textos: %s" % (ch, ord(ch), len(ids), " ".join(ids[:15])))
print("letras que la fuente no tiene:", len(faltan))
sys.exit(1 if faltan else 0)
