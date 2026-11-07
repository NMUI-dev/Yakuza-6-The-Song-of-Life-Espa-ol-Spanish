# (claude1, 06-11-2026) Comprobaciones de la RONDA FINAL de preguntas en cadena (cadena_final/lista_acumulada.md) que se
# pueden programar. Sobre lo publicado (v1.0.4) + correcciones.json + nuevas_v105.json. Solo marca; se decide a mano.
#  1 «a el» / «de el» sin contraer (salvo «a él», «de El ...» con nombre propio)          (idea 1)
#  2 usted con verbo de tú o tú con verbo de usted en la misma frase                     (idea 2)
#  3 doble negación mal ordenada: «nadie no», «nunca no», «nada no»                       (idea 3)
#  4 punto o coma DENTRO de las comillas al cerrar («...hola."» -> «...hola".»)            (idea 5)
#  5 género de préstamos japoneses: «el katana», «la sushi», «la ramen», «la sake»...       (idea 6)
#  6 nombres de la saga escritos de dos formas (Kiryu/Kiriyu, Haruka/Haluka...)            (idea 13)
# Uso: python -I -X utf8 ideas_cadena2.py  -> ideas_cadena2.txt
import csv
import json
import re
from collections import defaultdict
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
REGLAS = {
    "1 «a el»/«de el» sin contraer": re.compile(r"\b[aA] el\b|\b[dD]e el\b"),
    "2 usted con verbo de tú (o al revés)": re.compile(r"\busted (?:tienes|eres|estás|puedes|quieres|sabes|vas|has)\b|"
                                                        r"\btú (?:tiene|es|está|puede|quiere|sabe|va|ha)\b", re.I),
    "3 doble negación mal ordenada": re.compile(r"\b(?:nadie|nunca|nada|ninguno|jamás) no\b", re.I),
    "4 punto o coma dentro de las comillas": re.compile(r"[.,]\"(?=\s|$)"),
    "5 género de préstamos": re.compile(r"\b(?:el|un) katana\b|\b(?:la|una) (?:sushi|ramen|sake|karaoke|kimono|manga|yen)\b", re.I),
}
for i, d, en, es in filas:
    e = ETQ.sub("", es)
    for k, rx in REGLAS.items():
        m = rx.search(e)
        if m:
            out[k].append("#%s [%s] «%s» | %s || %s" % (i, d, m.group(0), en.replace("\n", " / ")[:60], es.replace("\n", " / ")[:90]))
# 6: variantes de nombres de la saga
NOMBRES = {"Kiryu": r"Kiriyu|Kiryū|Kyriu", "Haruka": r"Haluka|Harka", "Haruto": r"Halto|Haruto-chan", "Majima": r"Mashima",
           "Akiyama": r"Akiyamma", "Saejima": r"Saeshima", "Daigo": r"Daygo", "Nagumo": r"Nagumu", "Kamurocho": r"Kamuro-cho|Kamurochō"}
for bueno, malos in NOMBRES.items():
    for i, d, en, es in filas:
        m = re.search(r"\b(?:%s)\b" % malos, es)
        if m:
            out["6 nombre escrito distinto"].append("#%s [%s] «%s» (es «%s») || %s" % (i, d, m.group(0), bueno, es[:90]))
with open(aqui / "ideas_cadena2.txt", "w", encoding="utf-8") as o:
    for k in sorted(out):
        o.write("== %s: %d\n" % (k, len(out[k])))
        for x in out[k][:60]:
            o.write("  " + x + "\n")
for k in sorted(REGLAS) + ["6 nombre escrito distinto"]:
    print(k, len(out.get(k, [])))
