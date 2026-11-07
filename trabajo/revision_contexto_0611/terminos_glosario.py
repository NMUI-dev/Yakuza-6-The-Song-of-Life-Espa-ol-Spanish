# (claude1, 06-11-2026) Cada término del glosario del juego (trabajo/lotes/glosario_vivo.md, líneas «inglés → español»)
# con UNA sola traducción en todo el texto (idea de Gemini, Grok y Nemotron: «Heat Action traducido de tres formas»).
# Marca las frases cuyo inglés lleva el término y cuyo español no lleva su traducción. Solo marca: se decide a mano.
# Uso: python terminos_glosario.py [correcciones.json] > terminos_glosario.txt
import collections
import csv
import json
import re
import sys

csv.field_size_limit(10 ** 9)
TEXTOS = r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv"
GLOSARIO = r"C:\mods\yakuza6\trabajo\lotes\glosario_vivo.md"
corr = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else {}

pares = {}
for linea in open(GLOSARIO, encoding="utf-8"):
    linea = re.sub(r"^[^:→]{0,30}:\s", "", linea.strip())          # «Gimnasio: Bench Press → ...»
    for trozo in linea.split(";"):
        if trozo.count("→") != 1:
            continue
        en, es = [x.strip() for x in trozo.split("→")]
        es = re.sub(r"\s*\(.*$", "", es).strip(" .")
        en = re.sub(r"\s*\(.*?\)", "", en).strip(" .")
        ens, ess = [x.strip() for x in en.split(" / ")], [x.strip() for x in es.split(" / ")]
        if len(ens) != len(ess):
            ens, ess = [en], [es]
        for a, b in zip(ens, ess):
            if len(a) >= 4 and b and a.lower() != b.lower() and "se deja" not in b and not re.search(r"[«»]", a + b):
                pares[a] = b

cuenta = collections.Counter()
for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"):
    es = (corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]).lower().replace("\n", " ")
    if not es.strip():
        continue
    en = r["ingles"].replace("\n", " ")
    for a, b in pares.items():
        if re.search(r"(?<![\w-])" + re.escape(a) + r"(?![\w-])", en, re.I) and b.lower()[:max(4, len(b) - 2)] not in es:
            cuenta[a] += 1
            print("%s\t%s\t%s\t%s\t%s" % (a, b, r["id"], en[:110], es[:130]))
print("términos del glosario:", len(pares), "| frases que no usan la traducción:", sum(cuenta.values()))
for a, n in cuenta.most_common(40):
    print("   %4d  %s -> %s" % (n, a, pares[a]))
