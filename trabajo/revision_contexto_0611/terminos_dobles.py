# (claude1, 06-11-2026) Términos con dos traducciones (sugerencia de claude2): toma los NOMBRES traducidos de las tablas
# de nombres (objetos, lugares, tiendas, habilidades, misiones, personajes...) y mira cada frase del juego que cita ese
# nombre en inglés: si su español no lleva la misma traducción, la marca. Solo marca: se decide a mano.
# Uso: python terminos_dobles.py > terminos_dobles.txt
import csv
import re
from collections import defaultdict

csv.field_size_limit(10 ** 9)
TEXTOS = r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv"
NOMBRES = ("item |", "map_place |", "shop |", "player_skill |", "mission |", "substory", "character_npc", "minigame_",
           "clan_creator_member |", "ability", "cat_cafe")
filas = list(csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"))


def es_nombre(r):
    d = r["donde"]
    return any(k in d for k in NOMBRES) and ("|name" in d.replace(" ", "") or "name" in d) and "\n" not in r["ingles"]


nombre = {}
for r in filas:
    en, es = r["ingles"].strip(), r["espanol"].strip()
    if not es or en == es or len(en) < 6 or not es_nombre(r):
        continue
    if not re.match(r"^[A-Z][\w'&.\- ]+$", en) or len(en.split()) > 5:
        continue
    nombre.setdefault(en, set()).add(es)

dobles_tabla = {en: v for en, v in nombre.items() if len(v) > 1}
print("== mismo nombre inglés con dos traducciones en las tablas de nombres:", len(dobles_tabla))
for en, v in sorted(dobles_tabla.items()):
    print("TABLA\t%s\t%s" % (en, " | ".join(sorted(v))))

citas = defaultdict(list)
pat = {en: re.compile(r"(?<![\w-])" + re.escape(en) + r"(?![\w-])") for en in nombre}
for r in filas:
    en_txt = r["ingles"]
    if es_nombre(r) or len(en_txt) < 12:
        continue
    es_txt = r["espanol"].lower()
    for en, p in pat.items():
        if p.search(en_txt) and not any(t.lower() in es_txt for t in nombre[en]):
            citas[en].append((r["id"], en_txt.replace("\n", " / ")[:110], r["espanol"].replace("\n", " / ")[:130]))
print("== frases que citan un nombre y no usan su traducción:", sum(len(v) for v in citas.values()), "en", len(citas), "nombres")
for en, v in sorted(citas.items(), key=lambda kv: -len(kv[1])):
    for idt, a, b in v:
        print("CITA\t%s\t%s\t%s\t%s\t%s" % (en, " | ".join(sorted(nombre[en])), idt, a, b))
