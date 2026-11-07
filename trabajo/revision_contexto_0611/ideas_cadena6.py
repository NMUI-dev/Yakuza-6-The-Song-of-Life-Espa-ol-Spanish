# (claude1, 07-11-2026) Ideas de GROK del usuario (cadena_final/manual_07_grok_usuario.json) que se pueden programar. Solo marca.
#  1 colectivos: «la yakuza» frente a «los yakuza», «la mafia» ... cuántas de cada forma
#  2 locales del mapa (map_place) citados en frases: con artículo y sin él
#  3 interjecciones inglesas que quedaron en el español (Ugh, Argh, Gah, Hmph, Whoa, Oops, Yikes, Ouch, Damn...)
#  4 platos japoneses escritos de varias formas (ramen/rámen, gyoza/gyōza, takoyaki, okonomiyaki, yakitori, sushi...)
# Uso: python -I -X utf8 ideas_cadena6.py -> ideas_cadena6.txt
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
# (07-11) también las frases NUEVAS de la v1.0.5: «Urgh...» -> «Ugh...» se escapó porque solo se miraba lo publicado
for en, es in json.load(open(aqui / "nuevas_v105.json", encoding="utf-8"))["nuevas"].items():
    filas.append(("nueva", "nuevas_v105", en, es))
ETQ = re.compile(r"<[^>]*>")
out = defaultdict(list)
cuenta = defaultdict(Counter)
fmt = lambda i, d, en, es: "#%s [%s] %s || %s" % (i, d[:40], en.replace("\n", " / ")[:80], es.replace("\n", " / ")[:110])
lugares = sorted({ETQ.sub("", es).strip() for i, d, en, es in filas if d == "map_place" and 4 <= len(es.strip()) <= 30}, key=len, reverse=True)
INTERJ = re.compile(r"\b(?:Ugh|Argh|Gah|Hmph|Whoa|Oops|Yikes|Ouch|Damn|Geez|Jeez|Gosh|Wow|Huh|Phew|Ew|Yay|Ow|Ack|Bah|Meh|Pfft|Tsk|Ahem|Uh-oh|Woo|Yo)\b")
PLATOS = {"ramen": r"r[aá]men", "gyoza": r"gy[oō]zas?|gioza\w*", "takoyaki": r"tak[oō]yaki", "okonomiyaki": r"okonomiyaki|okonomi-yaki",
          "yakitori": r"yakitori|yaki-tori", "sushi": r"sushi|susi", "udon": r"ud[oó]n", "soba": r"soba", "tempura": r"t[eé]mpura",
          "sake": r"sak[eé]", "onigiri": r"onigiri", "miso": r"miso"}
for i, d, en, es in filas:
    e = ETQ.sub("", es)
    for m in re.finditer(r"\b(la|los|las|el) (yakuza|yakuzas|mafia|tríada|tríadas)\b", e, re.I):
        cuenta["1 colectivos"][m.group(0).lower()] += 1
    if d != "map_place":
        for L in lugares:
            if L in e and not L.lower().startswith(("el ", "la ", "los ", "las ")):
                k = "con artículo" if re.search(r"\b(?:el|la|los|las|del|al) " + re.escape(L), e) else "sin artículo"
                cuenta["2 " + L][k] += 1
                if k == "sin artículo" and len(out["2 ejemplos sin artículo: " + L]) < 3:
                    out["2 ejemplos sin artículo: " + L].append(fmt(i, d, en, es))
    m = INTERJ.search(e)
    if m and not re.search(r"\b(?:Wow|Huh|Yo)\b", m.group(0)):
        out["3 interjección inglesa en el español"].append("«%s» " % m.group(0) + fmt(i, d, en, es))
    for p, rx in PLATOS.items():
        for m in re.finditer(r"\b(?:%s)\b" % rx, e, re.I):
            cuenta["4 " + p][m.group(0).lower()] += 1
with open(aqui / "ideas_cadena6.txt", "w", encoding="utf-8") as o:
    for k in sorted(cuenta):
        if k.startswith("2 ") and len(cuenta[k]) < 2:
            continue
        o.write("%s: %s\n" % (k, dict(cuenta[k])))
    for k in sorted(out):
        o.write("== %s: %d\n" % (k, len(out[k])))
        for x in out[k]:
            o.write("  " + x + "\n")
print(open(aqui / "ideas_cadena6.txt", encoding="utf-8").read()[:6000])
