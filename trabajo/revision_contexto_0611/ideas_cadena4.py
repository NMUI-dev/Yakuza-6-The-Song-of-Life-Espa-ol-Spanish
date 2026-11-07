# (claude1, 07-11-2026) Ideas de GEMINI 3.7 en la ronda final (cadena_final/paso_05) que se pueden programar. Solo marca.
#  1 los 5 tipos de EXP (Strength, Agility, Spirit, Technique, Charm): cómo se tradujo cada uno en todo el juego
#  2 restos de consola (PlayStation, PS4, DUALSHOCK, touchpad, OPTIONS, SHARE...) que no estén en el inglés
#  3 dardos: Bust, Hat Trick, Bull, Cricket traducidos al pie de la letra (grillo, busto, sombrero)
#  4 llaves de lucha libre (Rainmaker, High Fly Flow, Destino...): que se conserve el nombre
#  5 textos con «poem»/«haiku» (estelas de poemas) para mirarlos con su respuesta
#  6 Snack (Gaudi): las réplicas de Kiryu junto a su inglés
# Uso: python -I -X utf8 ideas_cadena4.py  -> ideas_cadena4.txt
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
    if es.strip():
        filas.append((r["id"], r["donde"].split("|")[0].strip(), r["ingles"], es))
ETQ = re.compile(r"<[^>]*>")
out = defaultdict(list)
fmt = lambda i, d, en, es: "#%s [%s] %s || %s" % (i, d[:40], en.replace("\n", " / ")[:80], es.replace("\n", " / ")[:110])

EXP = {"Strength": r"Fuerza", "Agility": r"Agilidad", "Spirit": r"Espíritu", "Technique": r"Técnica", "Charm": r"Encanto"}
usos = defaultdict(Counter)
LUCHA = ["Rainmaker", "High Fly Flow", "Destino", "Gedo Clutch", "Styles Clash", "Kinshasa", "Gory Bomb"]
for i, d, en, es in filas:
    e = ETQ.sub("", es)
    for k, bueno in EXP.items():
        if re.search(r"\b%s EXP\b|\b%s (?:experience|points)\b" % (k, k), en, re.I):
            m = re.search(r"\b(?:EXP|experiencia|puntos)\s+(?:de\s+)?(\w+)|(\w+)\s+EXP", e)
            usos[k][(m.group(1) or m.group(2)) if m else "?"] += 1
            if not re.search(bueno, e):
                out["1 EXP sin su nombre fijo (%s = %s)" % (k, bueno)].append(fmt(i, d, en, es))
    m = re.search(r"\b(?:PlayStation|PS4|PS5|DUALSHOCK|DualShock|touchpad|panel táctil|barra (?:de )?lu[zm]\w*|OPTIONS|SHARE)\b", es)
    if m and not re.search(re.escape(m.group(0)) if m.group(0).isascii() else r"touch ?pad|light ?bar", en, re.I):
        out["2 resto de consola que no está en el inglés"].append("«%s» " % m.group(0) + fmt(i, d, en, es))
    if "dart" in d.lower() or re.search(r"\b(?:Bust|Hat Trick|Bull|Cricket)\b", en):
        m = re.search(r"\b(?:grillo|busto|sombrero|toro|quebrad\w*)\b", e, re.I)
        if m:
            out["3 dardos al pie de la letra"].append("«%s» " % m.group(0) + fmt(i, d, en, es))
    for n in LUCHA:
        if n in en and n not in es:
            out["4 llave de lucha libre sin su nombre"].append("«%s» " % n + fmt(i, d, en, es))
    if re.search(r"\b(?:poem|haiku|tanka)\b", en, re.I):
        out["5 poemas"].append(fmt(i, d, en, es))
    if d.startswith("minigame_snack"):
        out["6 snack: réplicas"].append(fmt(i, d, en, es))
with open(aqui / "ideas_cadena4.txt", "w", encoding="utf-8") as o:
    for k, c in usos.items():
        o.write("EXP %s -> %s\n" % (k, dict(c)))
    for k in sorted(out):
        o.write("== %s: %d\n" % (k, len(out[k])))
        for x in out[k]:
            o.write("  " + x + "\n")
for k, c in usos.items():
    print("EXP", k, dict(c))
for k in sorted(out):
    print(k, len(out[k]))
