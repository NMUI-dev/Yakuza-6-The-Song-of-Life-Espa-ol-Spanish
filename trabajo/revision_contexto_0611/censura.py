# (claude1, 06-11-2026) Regla del usuario: «nunca censurar las traducciones, hay que mantener la esencia de la obra».
# Marca frases cuyo inglés tiene una grosería o insulto fuerte y cuyo español no tiene NINGUNA palabra fuerte: posible
# suavizado. Sobre lo publicado (v1.0.4) + correcciones.json. Solo marca; se decide a mano con la escena (ver.py).
# Uso: python -I censura.py  -> censura.txt
import csv
import json
import re
from pathlib import Path

aqui = Path(__file__).resolve().parent
TEXTOS = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
csv.field_size_limit(10 ** 9)
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
# ya revisados a mano (rechazadas.json) no se repiten
vistos = {x[0] for x in json.load(open(aqui / "rechazadas.json", encoding="utf-8"))}

FUERTE_EN = re.compile(r"\b(?:fuck\w*|f\*+\w*|shit\w*|bitch\w*|bastard\w*|ass(?:hole)?s?\b|dick\w*|cunt|pussy|"
                       r"motherf\w*|goddamn\w*|dumbass|jackass|piss\w*|whore|slut|cock\w*|son of a)", re.I)
FUERTE_ES = re.compile(r"(?:mierd|carajo|jod|put[ao]|cabr[oó]n|cabrona|pendej|maldit|perra|imb[eé]cil|idiot|culo|verga|"
                       r"bastard|hijo de|hija de|est[uú]pid|cagar|cag[aoó]|zorra|chingad|coj|tarad|infeliz|basura|"
                       r"desgraciad|mocos|lameculos|cretin|animal|marica|demonios|diablos|rayos|maldici[oó]n|p\.\.\.)", re.I)
n = 0
with open(aqui / "censura.txt", "w", encoding="utf-8") as o:
    for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"):
        en = r["ingles"]
        es = corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]
        m = FUERTE_EN.search(en)
        if m and r["id"] not in vistos and es.strip() and es != en and not FUERTE_ES.search(es):
            n += 1
            o.write("#%s [%s] (%s) %s || %s\n" % (r["id"], r["donde"].split("|")[0].strip(), m.group(0),
                                                  en.replace("\n", " / "), es.replace("\n", " / ")))
print("posibles suavizados:", n)
