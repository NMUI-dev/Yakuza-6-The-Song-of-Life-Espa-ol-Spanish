# (claude1, 06-11-2026) Revisión por CONTEXTO del Yakuza 6 (regla del usuario: entender la conversación entera antes de
# tocar una frase). Junta cada escena completa EN ORDEN, con quién habla (nombre y género si se conoce), en inglés y en
# español, y la reparte en paquetes para los revisores.
#   Fuentes: cinemáticas (auth.bin cinema_telop), listas de habla (sound_auth_subtitles_speech_list_*), charlas de talk.par
#   (talk_ingles.csv, por archivo y en orden de offset). El español sale de textos.csv de la v1.0.4 (lo publicado).
# Uso: python armar_escenas.py [KB_por_paquete=45]
import csv
import glob
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

aqui = Path(__file__).resolve().parent
T = Path(r"C:\mods\yakuza6\trabajo")
ARMP = T / "armp_json"
TEXTOS = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
KB = int(sys.argv[1]) if len(sys.argv) > 1 else 45
csv.field_size_limit(10 ** 9)


def norm(s):
    return (s or "").replace("\r\n", "\n").strip()


def clave(s):  # para emparejar: sin \r sueltos ni espacios raros antes de la puntuación
    s = re.sub(r"\s+", " ", (s or "").replace("\r", ""))
    return re.sub(r" ([,.!?])", r"\1", s).strip()


es_de = {}
for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"):
    es_de.setdefault(clave(r["ingles"]), (r["id"], norm(r["espanol"]), r["veces"]))

hab = json.load(open(T / "revision_steam_0511" / "hablantes_y6.json", encoding="utf-8"))


def quien(p):
    h = hab.get("P%s" % p)
    if not h:
        return "P%s" % p
    return "P%s %s (%s)" % (p, h["nombre"], h.get("genero", "?"))


sin_es = []


def linea(en, q=None):
    en = norm(en)
    if not en:
        return None
    idt, es, veces = es_de.get(clave(en), ("?", "", ""))
    en = en.replace(chr(13), "")
    if idt == "?":
        sin_es.append(en)
    marca = " x%s" % veces if veces and veces not in ("1", "2") else ""
    cab = "#%s%s" % (idt, marca)
    who = ("[%s] " % quien(q)) if q is not None else ""
    return "%s %s%s || %s" % (cab, who, en.replace("\n", " / "), es.replace("\n", " / "))


escenas = OrderedDict()

# 1) cinemáticas
auth = json.load(open(ARMP / "auth.bin.json", encoding="utf-8"))
for i in range(auth["ROW_COUNT"]):
    for nombre, v in auth.get(str(i), {}).items():
        if not isinstance(v, dict) or "cinema_telop" not in v:
            continue
        ct = v["cinema_telop"]
        ls = [linea(ct.get(str(j), {}).get("", {}).get("4")) for j in range(ct["ROW_COUNT"])]
        ls = [x for x in ls if x]
        if ls:
            escenas["cinematica " + nombre] = ls

# 2) listas de habla (eventos, subhistorias, peleas, tiendas...)
for f in sorted(glob.glob(str(ARMP / "sound_auth_subtitles_speech_list_*.bin.json"))):
    t = json.load(open(f, encoding="utf-8"))
    nombre = Path(f).name[len("sound_auth_subtitles_speech_list_"):-len(".bin.json")]
    ls = []
    for j in range(t["ROW_COUNT"]):
        x = t.get(str(j), {}).get("", {})
        if isinstance(x.get("4"), str):
            l = linea(x["4"], x.get("1"))
            if l:
                ls.append(l)
    if ls:
        escenas["habla " + nombre] = ls

# 3) charlas de talk.par (por archivo, en orden)
talk = OrderedDict()
for r in csv.DictReader(open(T / "talk_ingles.csv", encoding="utf-8-sig", newline=""), delimiter=";"):
    arch = r["archivo_par"].replace("\\", "/").split("/talk/", 1)[-1]
    talk.setdefault(arch, []).append((int(r["offset"]), r["ingles"]))
for arch, filas in talk.items():
    ls = [linea(en) for _, en in sorted(filas)]
    ls = [x for x in ls if x]
    if ls:
        escenas["charla " + arch] = ls

# paquetes: escenas enteras (una escena larga se parte por trozos con 5 líneas de solape)
sal = aqui / "paquetes"
sal.mkdir(exist_ok=True)
for viejo in sal.glob("paquete_*.txt"):
    viejo.unlink()
paquetes, act, tam = [], [], 0
for nombre, ls in escenas.items():
    trozos = []
    i = 0
    while i < len(ls):
        trozo = ls[max(0, i - 5):i + 250]
        trozos.append(trozo)
        i += 250
    for k, trozo in enumerate(trozos):
        txt = "=== ESCENA %s%s ===\n%s\n" % (nombre, " (parte %d)" % (k + 1) if len(trozos) > 1 else "", "\n".join(trozo))
        b = len(txt.encode("utf-8"))
        if act and tam + b > KB * 1024:
            paquetes.append(act)
            act, tam = [], 0
        act.append(txt)
        tam += b
if act:
    paquetes.append(act)
for n, p in enumerate(paquetes):
    (sal / ("paquete_%03d.txt" % n)).write_text("\n".join(p), encoding="utf-8")

tot = sum(len(v) for v in escenas.values())
tipos = {}
for k, v in escenas.items():
    tipos.setdefault(k.split()[0], [0, 0])
    tipos[k.split()[0]][0] += 1
    tipos[k.split()[0]][1] += len(v)
print("escenas", len(escenas), "lineas", tot, "paquetes", len(paquetes), "| por tipo", tipos)
print("lineas sin español en textos.csv:", len(sin_es), "| distintas", len(set(sin_es)))
json.dump(sorted(set(sin_es)), open(aqui / "sin_es.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
