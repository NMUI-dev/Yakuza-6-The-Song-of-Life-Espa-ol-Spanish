# (claude1, 07-11-2026) Ideas de la 2.ª respuesta de GROK del usuario (cadena_final/manual_08_grok_usuario.json). Solo marca.
#  1 calcos del inglés: hacer sentido, llamar de vuelta, en la misma página, dar un chance, hacer un punto, fuera de la
#    caja, tomar ventaja, aplicar para, en base a, estar supuesto a, jugar un rol/papel importante (de inglés), a la larga
#  2 estar + gerundio con verbos de estado (estoy sabiendo, estoy teniendo, estás queriendo): esos sí son calco
# Las muletillas y apodos de un país («la neta», «qué onda», «carnal», «culero») NO se añaden: el español es neutro y
# fiel al original (GUIA_TRADUCCION.md). Groserías: ya revisadas con censura.py (NUNCA CENSURAR).
# Uso: python -I -X utf8 ideas_cadena7.py -> ideas_cadena7.txt
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

aqui = Path(__file__).resolve().parent
csv.field_size_limit(10 ** 9)
T = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
ETQ = re.compile(r"<[^>]*>")
out = defaultdict(list)
CALCO = re.compile(r"\b(?:hac\w+ sentido|llam\w+ de vuelta|en la misma página|d\w+ (?:un|una) chance|hac\w+ un punto|"
                   r"fuera de la caja|tom\w+ ventaja|aplic\w+ (?:para|a) (?:un|el|la) (?:trabajo|puesto|empleo)|en base a|"
                   r"(?:estoy|estás|está|estaba) supuest[oa] a|ten\w+ sentido para mí|es tu llamada)\b", re.I)
GER = re.compile(r"\b(?:estoy|estás|está|estamos|están) (?:sabiendo|teniendo|queriendo|siendo|conociendo|necesitando|odiando|amando)\b", re.I)
for r in csv.DictReader(open(T, encoding="utf-8-sig", newline=""), delimiter=";"):
    es = corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]
    e = ETQ.sub("", es)
    for k, rx in (("1 calco del inglés", CALCO), ("2 estar + gerundio de estado", GER)):
        m = rx.search(e)
        if m:
            out[k].append("«%s» #%s [%s] %s || %s" % (m.group(0), r["id"], r["donde"].split("|")[0][:30],
                          r["ingles"].replace("\n", " / ")[:70], es.replace("\n", " / ")[:100]))
with open(aqui / "ideas_cadena7.txt", "w", encoding="utf-8") as o:
    for k in sorted(out):
        o.write("== %s: %d\n" % (k, len(out[k])))
        for x in out[k]:
            o.write("  " + x + "\n")
print(open(aqui / "ideas_cadena7.txt", encoding="utf-8").read() or "nada marcado")
