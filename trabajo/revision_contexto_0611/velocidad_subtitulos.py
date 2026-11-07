# (claude1, 06-11-2026) Velocidad de lectura de los subtítulos de las cinemáticas (idea de casi todas las IA consultadas).
# auth.bin -> cinema_telop: columnas 1 y 2 = fotograma de entrada y salida (30 por segundo), 4 = texto inglés.
# Marca los subtítulos cuyo español pide leer demasiado rápido: más de 20 letras por segundo Y bastante más que el inglés
# (el inglés ya fija lo que el juego da por legible). Uso: python velocidad_subtitulos.py [correcciones.json]
import csv
import json
import re
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
csv.field_size_limit(10 ** 9)
ARMP = Path(r"C:\mods\yakuza6\trabajo\armp_json")
TEXTOS = r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv"
FPS = 30.0
corr = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else {}


def clave(s):
    s = re.sub(r"\s+", " ", (s or "").replace("\r", ""))
    return re.sub(r" ([,.!?])", r"\1", s).strip()


def letras(s):
    return len(re.sub(r"<[^>]*>|\s", "", s))


es_de = {}
for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"):
    es = corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]
    es_de.setdefault(clave(r["ingles"]), (r["id"], es))

auth = json.load(open(ARMP / "auth.bin.json", encoding="utf-8"))
vistos, malos, total = set(), [], 0
for i in range(auth["ROW_COUNT"]):
    for escena, v in auth.get(str(i), {}).items():
        if not isinstance(v, dict) or "cinema_telop" not in v:
            continue
        ct = v["cinema_telop"]
        for j in range(ct["ROW_COUNT"]):
            x = ct.get(str(j), {}).get("", {})
            en = x.get("4")
            if not isinstance(en, str) or not en.strip():
                continue
            idt, es = es_de.get(clave(en), (None, ""))
            seg = (float(x.get("2", 0)) - float(x.get("1", 0))) / FPS
            if not idt or not es or seg <= 0:
                continue
            total += 1
            cps_en, cps_es = letras(en) / seg, letras(es) / seg
            if cps_es > 20 and cps_es > cps_en * 1.25 and (idt, escena) not in vistos:
                vistos.add((idt, escena))
                malos.append((cps_es, cps_en, seg, idt, escena, en.replace("\r\n", " / ").replace("\n", " / "),
                              es.replace("\n", " / ")))
malos.sort(reverse=True)
for m in malos:
    print("%.1f l/s (inglés %.1f) en %.1f s | #%s %s | %s || %s" % m)
print("subtítulos medidos:", total, "| demasiado rápidos:", len(malos), "| ids distintos:", len({m[3] for m in malos}))
