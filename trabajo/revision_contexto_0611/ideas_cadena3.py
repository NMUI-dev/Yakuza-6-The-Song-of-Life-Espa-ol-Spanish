# (claude1, 07-11-2026) Comprobaciones de las ideas de GEMINI en la ronda final (cadena_final/paso_03 y paso_04) que se
# pueden programar. Sobre lo publicado (v1.0.4) + correcciones.json. Solo marca; se decide a mano.
#  1 «¿No...?» seguida de respuesta «Sí/No» (paradoja sí/no)                       (3.8 idea 1) -> lista para mirar
#  2 béisbol con la acepción común: guardar, caminar, huelga, volar, robo, ataque     (3.8 idea 2)
#  3 cabaret: cartas de tema (textos cortos) junto a su inglés                        (3.8 idea 3) -> lista para mirar
#  4 preposición calcada: consistir de, depender en, pensar de, soñar de              (3.8 idea 4)
#  5 muletillas al empezar (Bueno, Mira, Verás, O sea, Digo,) frente al inglés        (3.8 idea 5)
#  6 plantillas con variable y participio fijo en masculino                           (3.5 idea 1)
#  7 guías de botones / acciones más largas que el inglés                             (3.5 idea 4)
# Las mayúsculas con tilde (3.5 idea 2) ya las cubre letras_fuente.py; el chat en vivo (3.5 idea 3) el control de largo.
# Uso: python -I -X utf8 ideas_cadena3.py  -> ideas_cadena3.txt
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
fmt = lambda i, d, en, es: "#%s [%s] %s || %s" % (i, d[:40], en.replace("\n", " / ")[:70], es.replace("\n", " / ")[:100])

for n, (i, d, en, es) in enumerate(filas):
    e = ETQ.sub("", es)
    # 1: pregunta negativa y la frase siguiente de la misma escena empieza por Sí/No
    if re.search(r"¿\s*(?:No|Nunca|Acaso no)\b", e) and n + 1 < len(filas) and filas[n + 1][1] == d:
        sig = ETQ.sub("", filas[n + 1][3]).lstrip("¡¿.… ")
        if re.match(r"(?:Sí|No)\b", sig):
            out["1 pregunta negativa + Sí/No (mirar el inglés)"].append(fmt(i, d, en, es) + "  ->  " + fmt(*filas[n + 1]))
    # 1b (lado inglés): pregunta negativa y la réplica dice «Yeah/Yes» seguido de una negación (confirma lo negativo)
    if n + 1 < len(filas) and filas[n + 1][1] == d and re.search(r"\b\w+n't\b[^?]*\?|\bnot\b[^?]*\?", en) and \
            re.match(r"[.…\s]*(?:Yeah|Yes|Yep|Uh-huh)\b.*\b(?:\w+n't|not|never|no one|nothing)\b", filas[n + 1][2], re.S):
        out["1b réplica Yeah + negación a pregunta negativa"].append(fmt(i, d, en, es) + "  ->  " + fmt(*filas[n + 1]))
    if "baseball" in d or "batting" in d:
        m = re.search(r"\b(?:guard\w*|camin\w*|huelga\w*|vol(?:ar|ó|ad\w*)|vuela\w*|ataque\w*)\b", e, re.I)
        if m:
            out["2 béisbol con la acepción común"].append("«%s» " % m.group(0) + fmt(i, d, en, es))
    if d.startswith("minigame_cabaret") and len(en) <= 30:
        out["3 cabaret: textos cortos (cartas)"].append(fmt(i, d, en, es))
    m = re.search(r"\b(?:consist\w* de|depend\w* en|pens\w* de|piens\w* de|soñ\w* de|sueñ\w* de)\b", e, re.I)
    if m and not re.search(r"\b(?:pens\w*|piens\w*) de (?:mí|ti|él|ella|nosotros|ellos|ellas|usted|eso|esto|lo que)\b", e, re.I):
        out["4 preposición calcada"].append("«%s» " % m.group(0) + fmt(i, d, en, es))
    m = re.match(r"(?:Bueno|Mira|Verás|O sea|Digo),", e.strip())
    if m and not re.match(r"(?:Well|Look|You see|I mean|Listen|Okay|OK|Alright|So|Now|Uh|Um|See)\b", en.strip(), re.I):
        out["5 muletilla que no está en el inglés"].append(fmt(i, d, en, es))
    if re.search(r"%[sd]|\{\w+\}|<\w*(?:item|name)\w*>", es, re.I) and re.search(r"\b(?:añadido|equipado|obtenido|vendido|comprado|usado|conseguido|desbloqueado)\b", e):
        out["6 plantilla con participio fijo"].append(fmt(i, d, en, es))
    if d in ("controller_guide", "qloc_qloc_binding_actions", "pad_button", "ui_preview_text") and len(e) > len(ETQ.sub("", en)) + 4:
        out["7 guía de botones más larga que el inglés"].append("%d>%d " % (len(e), len(ETQ.sub("", en))) + fmt(i, d, en, es))

# 5b: frecuencia de muletillas sobre el total de frases de diálogo
dial = [f for f in filas if f[1].split("/")[0] in ("sound_auth", "auth", "talk", "escena")]
mul = Counter(re.match(r"(Bueno|Mira|Verás|O sea|Digo),", ETQ.sub("", f[3]).strip()).group(1) for f in dial
              if re.match(r"(Bueno|Mira|Verás|O sea|Digo),", ETQ.sub("", f[3]).strip()))
with open(aqui / "ideas_cadena3.txt", "w", encoding="utf-8") as o:
    o.write("muletillas al empezar en %d frases de diálogo: %s (%.1f%%)\n" % (len(dial), dict(mul), 100 * sum(mul.values()) / max(1, len(dial))))
    for k in sorted(out):
        o.write("== %s: %d\n" % (k, len(out[k])))
        for x in out[k]:
            o.write("  " + x + "\n")
print("muletillas: %s de %d frases de diálogo (%.1f%%)" % (dict(mul), len(dial), 100 * sum(mul.values()) / max(1, len(dial))))
for k in sorted(out):
    print(k, len(out[k]))
