# (claude1, 06-11-2026) Renglón partido por mal sitio (Netflix es-419; idea de claude2, saltos_sentido_y5.py): un renglón
# de subtítulo que TERMINA en artículo, preposición, conjunción, «no», «que» o pronombre átono. Arreglo: bajar esa palabra
# al renglón siguiente, solo si ningún renglón queda más largo que el más largo de ahora (la caja no crece; mismos saltos,
# mismos bytes). Se salta lo que tenga el formato raro de sound_auth (espacio junto al salto, coma sola).
# Uso: python -I -X utf8 saltos_sentido.py [aplicar]   -> saltos_sentido.txt (y con «aplicar», a decididas_escenas.json)
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
csv.field_size_limit(10 ** 9)
T = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
MAL = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "a", "en", "con", "por", "para", "sin",
       "y", "e", "o", "u", "ni", "que", "no", "me", "te", "se", "le", "les", "lo", "nos", "mi", "tu", "su", "mis", "tus", "sus"}
ETQ = re.compile(r"<[^>]*>")


def largo(s):
    return len(ETQ.sub("", s))


arreglos, sin_arreglo = [], []
for r in csv.DictReader(open(T, encoding="utf-8-sig", newline=""), delimiter=";"):
    if not r["donde"].startswith(("sound_auth", "auth", "talk", "escena")):
        continue
    es = corr.get(r["id"], {}).get("es", r["espanol"]).replace("\r\n", "\n")
    if "\n" not in es or re.search(r" \n|\n |\n,\n", es + r["ingles"]):
        continue
    ren = es.split("\n")
    nuevo = list(ren)
    cambio = False
    for k in range(len(nuevo) - 1):
        lim = ETQ.sub("", nuevo[k]).rstrip()
        m = re.search(r"(?:^|\s)([\wáéíóúñü]+)$", lim.lower())
        if not m or m.group(1) not in MAL or lim.endswith((".", ",", "!", "?", "…", ":", ";")):
            continue
        if ETQ.search(nuevo[k][-25:]):          # con etiqueta al final del renglón, a mano
            sin_arreglo.append((r["id"], es)); break
        # bajar el grupo entero de palabras sueltas del final («de tu», «lo que»), no solo la última
        prueba = list(nuevo)
        for _ in range(4):
            pal = prueba[k].rstrip().rsplit(" ", 1)
            if len(pal) < 2:
                break
            prueba[k] = pal[0]
            prueba[k + 1] = pal[1] + " " + prueba[k + 1]
            fin = re.search(r"(?:^|\s)([\wáéíóúñü]+)$", ETQ.sub("", prueba[k]).rstrip().lower())
            if not fin or fin.group(1) not in MAL or prueba[k].rstrip().endswith((".", ",", "!", "?", "…", ":", ";")):
                break
        if len(prueba[k].split()) >= 2 and max(largo(x) for x in prueba) <= max(largo(x) for x in ren) and \
                not re.search(r"(?:^|\s)(%s)$" % "|".join(MAL), ETQ.sub("", prueba[k]).rstrip().lower()):
            nuevo = prueba; cambio = True
        else:
            sin_arreglo.append((r["id"], es)); break
    if cambio:
        arreglos.append((r["id"], es, "\n".join(nuevo)))

with open(aqui / "saltos_sentido.txt", "w", encoding="utf-8") as o:
    o.write("arreglables: %d | a mano (la caja crecería o hay etiqueta): %d\n\n" % (len(arreglos), len(sin_arreglo)))
    for i, a, b in arreglos:
        o.write("#%s  %s\n   -> %s\n" % (i, a.replace("\n", " / "), b.replace("\n", " / ")))
    o.write("\n== a mano\n")
    for i, a in sin_arreglo:
        o.write("#%s  %s\n" % (i, a.replace("\n", " / ")))
print("arreglables:", len(arreglos), "| a mano:", len(sin_arreglo))
if len(sys.argv) > 1 and sys.argv[1] == "aplicar":
    for i, a, b in arreglos:
        subprocess.run([sys.executable, "-I", "-X", "utf8", str(aqui / "decidir.py"), "si", i, a.replace("\n", " / "),
                        b.replace("\n", " / "), "renglón", "renglón acababa en palabra suelta (artículo/preposición): se baja al "
                        "siguiente sin agrandar la caja (regla de Netflix es-419)"], stdout=subprocess.DEVNULL, cwd=aqui)
    print("aplicados", len(arreglos))
