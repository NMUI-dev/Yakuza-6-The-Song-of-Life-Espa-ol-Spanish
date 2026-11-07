# (claude1, 06-11-2026) Texto de MENÚS que puede salirse de su caja (idea de casi todas las IA): para cada columna de cada
# tabla (lo que dice «donde», sin subtítulos ni diálogos), el texto en español más largo que el inglés más largo de esa
# columna. Ahí el juego nunca ha tenido que pintar un texto tan largo. Solo marca: se mira en el juego o se acorta.
# Uso: python largo_menus.py [correcciones.json] > largo_menus.txt
import collections
import csv
import json
import re
import sys

csv.field_size_limit(10 ** 9)
TEXTOS = r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv"
corr = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else {}
filas = list(csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"))
NO = ("sound_auth", "auth |", "talk", "escena", "manual", "pause_mail", "minigame_live_chat", "pause_sns", "mission_kind | mission_info",
      "item | explanation", "complete | explanation", "loading_text", "pause_tutorial")


def ancho(s):
    return max(len(x) for x in re.sub(r"<[^>]*>", "", s.replace("\r\n", "\n")).split("\n"))


maximo = collections.Counter()
for r in filas:
    maximo[r["donde"]] = max(maximo[r["donde"]], ancho(r["ingles"]))
n = collections.Counter()
for r in filas:
    if r["donde"].startswith(NO):
        continue
    es = corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]
    if not es.strip():
        continue
    a, tope = ancho(es), maximo[r["donde"]]
    if a > tope and a > ancho(r["ingles"]) * 1.3 and a - tope >= 3:
        n[r["donde"].split(" | ")[0]] += 1
        print("%d > %d\t%s\t%s\t%s\t%s" % (a, tope, r["id"], r["donde"][:45], r["ingles"].replace("\n", " / ")[:60],
                                           es.replace("\n", " / ")[:80]))
print("marcados:", sum(n.values()), dict(n.most_common(15)))
