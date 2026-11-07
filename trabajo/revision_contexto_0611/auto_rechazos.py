# (claude1, 06-11-2026) Rechaza solo los avisos de los revisores que ya sabemos que son falsos, comprobándolo uno a uno
# contra el CSV publicado (los paquetes juntan los renglones del inglés y los revisores no ven su forma real):
#  A) «renglones partidos / espacio tras el salto»: el inglés ORIGINAL tiene los mismos saltos que el español -> formato
#     de sound_auth (LEEME punto 12), se deja.
#  B) línea «sin traducción» con id «?»: frase que la herramienta no extraía (es_texto). Si la propuesta es igual al
#     inglés (un nombre), se queda igual; si no, ya está en nuevas_v105.json o se apunta para decidir a mano.
# Uso: python -I -X utf8 auto_rechazos.py   (escribe en rechazadas.json e imprime lo que deja para decidir a mano)
import csv
import json
import re
from pathlib import Path

aqui = Path(__file__).resolve().parent
csv.field_size_limit(10 ** 9)
T = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
filas = {r["id"]: r for r in csv.DictReader(open(T, encoding="utf-8-sig", newline=""), delimiter=";")}
nuevas = json.load(open(aqui / "nuevas_v105.json", encoding="utf-8"))["nuevas"]
rech = json.load(open(aqui / "rechazadas.json", encoding="utf-8"))
dec = json.load(open(aqui / "decididas_escenas.json", encoding="utf-8"))
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
hechos = {str(x[0]) for x in rech} | {str(x[0]) for x in dec} | set(corr)
n_a = n_b = 0
mano = []
for f in sorted((aqui / "resultados").glob("paquete_*.json")):
    for x in json.load(open(f, encoding="utf-8")).get("fallos", []):
        i = str(x.get("id", "")).lstrip("#")
        if i in hechos:
            continue
        txt = (str(x.get("porque", "")) + " " + str(x.get("es", ""))).lower()
        r = filas.get(i)
        if r and re.search(r"renglon|renglón|línea|linea|salto|doble espacio|coma suelta", txt):
            en, es = r["ingles"].replace("\r\n", "\n"), r["espanol"].replace("\r\n", "\n")
            if en.count("\n") == es.count("\n") and en.count("\n") >= 2:
                rech.append([i, "auto A: el inglés original tiene los mismos %d saltos (formato de sound_auth)" % en.count("\n")])
                hechos.add(i); n_a += 1
                continue
        if not i.isdigit() and not str(x.get("es", "")).strip():
            prop = str(x.get("propuesta", "")).strip()
            # el inglés de la línea vacía: lo que el revisor copió (propuesta) o lo que pone el id
            if prop in nuevas.values() or prop in nuevas or re.fullmatch(r"[\[\]A-Za-z\-. ]+", prop or "-"):
                # (las 136 frases sin extraer salen de TODOS los archivos, perdidos_ingles.json: con el filtro nuevo de
                # es_texto entran todas en la v1.0.5, así que ningún «?» queda sin mirar)
                rech.append([i, "auto B: frase que no extraía la herramienta (es_texto); nombre que se "
                             "queda igual o ya traducida en nuevas_v105.json"])
                hechos.add(i); n_b += 1
                continue
        mano.append((f.stem[-3:], i, x.get("tipo"), str(x.get("es", ""))[:70], str(x.get("propuesta", ""))[:70]))
json.dump(rech, open(aqui / "rechazadas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("auto A (renglones del original):", n_a, "| auto B (líneas vacías = nombres/nuevas):", n_b, "| a mano:", len(mano))
