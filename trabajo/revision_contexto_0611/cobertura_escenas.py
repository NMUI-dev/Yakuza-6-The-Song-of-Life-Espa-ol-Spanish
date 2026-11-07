# (claude1, 07-11-2026) ¿Está traducida cada cinemática y escena? Cuenta, en el textos.csv armado, las frases de escenas
# (subtítulos de cinemáticas sound_auth, escenas auth/hact, diálogos talk, rótulos caption, títulos) y lista las que siguen
# vacías o iguales al inglés. Escribe COBERTURA_ESCENAS.txt; el resultado se copia a NOTAS (no volver a revisar el juego).
# Uso: python -I -X utf8 cobertura_escenas.py [textos.csv]   (por defecto logs/textos_queria_v105.csv, lo que se armó)
import csv
import re
import sys
from collections import Counter
from pathlib import Path

aqui = Path(__file__).resolve().parent
csv.field_size_limit(10 ** 9)
F = Path(sys.argv[1]) if len(sys.argv) > 1 else aqui / "logs" / "textos_queria_v105.csv"
TIPOS = ("sound_auth", "auth", "talk", "escena", "caption", "title_movie", "title_movie_chapter")
tot, sin, iguales = Counter(), Counter(), set()
for r in csv.DictReader(open(F, encoding="utf-8-sig", newline=""), delimiter=";"):
    d = r["donde"].split("|")[0].strip().split("/")[0]
    if d not in TIPOS:
        continue
    tot[d] += 1
    es, en = r["espanol"].strip(), r["ingles"].strip()
    if not es or es == en:
        sin[d] += 1
        iguales.add(re.sub(r"<[^>]*>", "", en).replace("\n", " / ")[:60])
L = ["COBERTURA DE ESCENAS DEL Y6 (%s)" % F.name, "frases de escenas: %d | iguales al inglés: %d (%d distintas)" % (
     sum(tot.values()), sum(sin.values()), len(iguales))]
L += ["  %-22s %6d frases, %4d iguales al inglés" % (d, tot[d], sin[d]) for d in TIPOS if tot[d]]
L += ["", "Las iguales al inglés (mirar que solo sean nombres, interjecciones iguales y datos internos):"] + sorted(iguales)
(aqui / "COBERTURA_ESCENAS.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:9]))
