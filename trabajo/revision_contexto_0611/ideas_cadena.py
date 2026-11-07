# (claude1, 06-11-2026) Comprobaciones salidas de la pregunta en cadena a las IA (cadena/lista_acumulada.md) que aplican
# al Y6 y se pueden programar. Sobre lo publicado (v1.0.4) + correcciones.json. Solo marca; se decide a mano.
#  1 honorífico perdido: el inglés dice X-san/-kun/-chan/-sensei/aniki y el español no lo tiene (idea 1)
#  2 verbo de botones: «Pulsa» (España) frente a «Presiona»; las dos formas mezcladas (idea 3)
#  3 cifra o variable seguida de sustantivo: «1 objetos», «${n} vez» (idea 7)
#  4 comillas: tipos mezclados en el juego (« » frente a " " y “ ”) (idea 31)
#  5 dinero: «yenes», «¥», «yen» escritos de varias formas (idea 20)
#  6 dificultad: el nombre de cada nivel, una sola traducción (idea 22)
# Uso: python -I -X utf8 ideas_cadena.py  -> ideas_cadena.txt
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

aqui = Path(__file__).resolve().parent
csv.field_size_limit(10 ** 9)
T = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
filas = []
for r in csv.DictReader(open(T, encoding="utf-8-sig", newline=""), delimiter=";"):
    es = corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]
    if es.strip() and es != r["ingles"]:
        filas.append((r["id"], r["donde"].split("|")[0].strip(), r["ingles"], es))

out = defaultdict(list)
HON = re.compile(r"\b([A-Z][a-z]+)-(san|kun|chan|sensei|senpai|sama|aniki|nee|niisan)\b")
for i, d, en, es in filas:
    for nombre, h in set(HON.findall(en)):
        if nombre + "-" + h not in es and nombre in es:
            out["1 honorífico perdido"].append("#%s [%s] %s-%s || %s" % (i, d, nombre, h, es.replace("\n", " / ")[:110]))

verbos = Counter()
for i, d, en, es in filas:
    for v in re.findall(r"\b(Pulsa|pulsa|Presiona|presiona|Oprime|oprime|Aprieta|aprieta|Toca|toca)\b", es):
        verbos[v.lower()] += 1
    if re.search(r"\b[Pp]ulsa\b", es):
        out["2 «pulsa» (España; el juego usa «presiona»)"].append("#%s [%s] %s" % (i, d, es.replace("\n", " / ")[:120]))

for i, d, en, es in filas:
    for m in re.finditer(r"(?<![\d.,])1 (objetos|veces|puntos|horas|minutos|segundos|días|personas|golpes|yenes|victorias|partidas)\b", es):
        out["3 «1» con plural"].append("#%s [%s] %s" % (i, d, es.replace("\n", " / ")[:120]))
    if re.search(r"\$\{[^}]*\}\s+(vez|objeto|punto|hora|minuto|segundo|día|persona|golpe|victoria)\b", es):
        out["3 variable de número con singular"].append("#%s [%s] %s || %s" % (i, d, en[:60], es.replace("\n", " / ")[:100]))

comillas = Counter()
for i, d, en, es in filas:
    comillas["« »"] += es.count("«")
    comillas['" "'] += es.count('"') // 2
    comillas["“ ”"] += es.count("“")
    if "«" in es:
        out["4 texto con « » (el resto del juego usa \" \")"].append("#%s [%s] %s" % (i, d, es.replace("\n", " / ")[:120]))

dinero = Counter()
for i, d, en, es in filas:
    for m in re.findall(r"\d[\d,.]*\s?(yenes|yen|¥|Yenes)\b|¥\s?\d", es):
        dinero[m or "¥ delante"] += 1

dif = defaultdict(Counter)
for i, d, en, es in filas:
    if en.strip() in ("Easy", "Normal", "Hard", "Legend", "Difficulty", "EX-Hard"):
        dif[en.strip()][es.strip()] += 1

with open(aqui / "ideas_cadena.txt", "w", encoding="utf-8") as o:
    o.write("verbos de botón: %s\ncomillas: %s\ndinero: %s\ndificultad: %s\n\n" % (
        dict(verbos), dict(comillas), dict(dinero), {k: dict(v) for k, v in dif.items()}))
    for k in sorted(out):
        o.write("== %s: %d\n" % (k, len(out[k])))
        for x in out[k][:40]:
            o.write("  " + x + "\n")
print(open(aqui / "ideas_cadena.txt", encoding="utf-8").read()[:600])
for k in sorted(out):
    print(k, len(out[k]))
