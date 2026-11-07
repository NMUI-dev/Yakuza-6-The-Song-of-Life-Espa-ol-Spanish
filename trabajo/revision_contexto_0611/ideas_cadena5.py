# (claude1, 07-11-2026) Ideas del GEMINI DEL USUARIO (cadena_final/manual_06_gemini_usuario.json). Solo marca.
#  1 santuarios, Jizo, ofrendas, templos, omikuji: imperativos de tú y de usted en la misma tabla o frase
#  2 Creador de Clanes: sustantivo plural con adjetivo/participio singular (o al revés) justo detrás
# Uso: python -I -X utf8 ideas_cadena5.py -> ideas_cadena5.txt
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
TU = r"\b(?:reza|ofrece|lanza|toca|elige|tira|inténtalo|vuelve|sigue|recibe|espera|ten|haz|pon|ve|sé)\b|\b\w+(?:te|lo|la)\b(?=\s*[.!])"
USTED = r"\b(?:rece|ofrezca|lance|toque|elija|tire|inténtelo|vuelva|siga|reciba|espere|tenga|haga|ponga|vaya|sea|usted|su)\b"
SANTO = re.compile(r"jizo|shrine|temple|offertory|omikuji|prayer|kannon|buddha|god|deity", re.I)
por_tabla = defaultdict(lambda: Counter())
for i, d, en, es in filas:
    e = ETQ.sub("", es)
    if SANTO.search(d) or SANTO.search(en):
        t, u = re.search(TU, e), re.search(USTED, e)
        if t:
            por_tabla[d]["tú"] += 1
        if u:
            por_tabla[d]["usted"] += 1
        if t and u:
            out["1 tú y usted en la misma frase (santuarios)"].append("«%s»/«%s» " % (t.group(0), u.group(0)) + fmt(i, d, en, es))
    if d.startswith("clan_creator"):
        m = re.search(r"\b(?:tropas|unidades|bonificaciones|miembros|aliados|enemigos|habilidades|líderes|ataques)\s+(\w+[oa])\b(?!\s+de)", e)
        m2 = re.search(r"\b(?:tropa|unidad|bonificación|miembro|aliado|enemigo|habilidad|líder|ataque)\s+(\w+(?:os|as))\b", e)
        for x in (m, m2):
            if x and not re.fullmatch(r"(?:para|contra|cerca|hacia|durante|sobre|como|ya|todo|toda|sea|nada|algo|ahora|era|esta|esto|aparecerá|aumenta|recibe|ataca|cura|carga|baja|sube|se\w*|\w+ará|\w+ía|\w+aba)", x.group(1)):
                out["2 número que no concuerda (Creador de Clanes)"].append("«%s» " % x.group(0) + fmt(i, d, en, es))
with open(aqui / "ideas_cadena5.txt", "w", encoding="utf-8") as o:
    for d, c in sorted(por_tabla.items()):
        if c["tú"] and c["usted"]:
            o.write("tabla con los dos tratos: %s %s\n" % (d, dict(c)))
    for k in sorted(out):
        o.write("== %s: %d\n" % (k, len(out[k])))
        for x in out[k]:
            o.write("  " + x + "\n")
for d, c in sorted(por_tabla.items()):
    if c["tú"] and c["usted"]:
        print("tabla con los dos tratos:", d, dict(c))
for k in sorted(out):
    print(k, len(out[k]))
