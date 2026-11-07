# (claude1, 06-11-2026) «Lo que queda en ingles v1.0.5» del Y6: la carpeta de la v1.0.4 (lo que se deja en inglés a
# propósito no cambió) + la lista de lo que en la v1.0.4 seguía en inglés SIN estar anotado y en la v1.0.5 se tradujo
# (frases que la herramienta nunca extraía) + el aviso al principio del LEEME.
# Uso: python -I -X utf8 lo_que_queda_v105.py
import json
import shutil
from pathlib import Path

aqui = Path(__file__).resolve().parent
ENT = Path(r"C:\Mods\Entregas\Entregas Yakuza 6")
viejo, nuevo = ENT / "Lo que queda en ingles v1.0.4", ENT / "Lo que queda en ingles v1.0.5"
if nuevo.exists():
    shutil.rmtree(nuevo)
shutil.copytree(viejo, nuevo)
n = json.load(open(aqui / "nuevas_v105.json", encoding="utf-8"))["nuevas"]
# las 136 frases de una palabra que seguían en inglés en la v1.0.4 (medidas el 06-11 contra lo publicado)
perdidos = json.load(open(aqui / "perdidos_ingles_v104.json", encoding="utf-8"))
iguales = [s for s in perdidos if s not in n]
with open(nuevo / "2 Textos (txt)" / "07 Traducido en la v1.0.5 (seguía en inglés sin estar anotado).txt", "w",
          encoding="utf-8-sig") as o:
    o.write("Traducido en la v1.0.5: %d textos que en la v1.0.4 seguían en INGLÉS y NO estaban en esta lista.\n" % len(n))
    o.write("Causa: la herramienta tomaba por código interno las frases de una sola palabra con punto o guion\n"
            "(«B-Bullshit.», «Th-Thanks...») y algunas celdas en minúscula o con «/» (guías de botones, chat en vivo).\n"
            "Además hay %d frases más de ese tipo que son nombres o interjecciones y en español se escriben igual\n"
            "(«Kiryu-san.», «Haruka...», «Ah...», «Tch...»).\n" % len(iguales))
    o.write("Formato: inglés  |  español v1.0.5\n\n")
    for en, es in sorted(n.items(), key=lambda x: x[0].lower()):
        o.write("%s  |  %s\n" % (en, es))
le = nuevo / "LEEME - que hay aqui.txt"
t = le.read_text(encoding="utf-8-sig")
t = t.split("\n", 1)[1] if t.startswith("v1.0.4") else t
cab = ("v1.0.5 (06-11-2026): lo que se deja en inglés A PROPÓSITO es lo mismo que en la v1.0.3/v1.0.4. Lo nuevo:\n"
       "  2 Textos (txt)\\07: %d textos que en la v1.0.4 seguían en inglés sin estar anotados aquí (un fallo de la\n"
       "  herramienta) y ahora están traducidos. Informe completo: INFORME_REVISION_Y6_v1.0.5.txt.\n\n" % len(n))
le.write_text(cab + t, encoding="utf-8-sig")
print("hecho:", nuevo, "| traducidos ahora:", len(n))
