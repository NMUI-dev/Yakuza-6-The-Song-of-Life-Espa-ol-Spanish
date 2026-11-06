# Junta lo que proponen los ayudantes (recortes/res_parte_*.json), comprueba cada cambio y prepara la revisión a mano.
# - antes == español actual del lote; mismas etiquetas <...>, mismas «/» y mismos \n; bytes_max (UTF-8, í = 1 byte).
# - solo cambian palabras de género (o/a, el/la, un/una...): lo demás se marca como SOSPECHOSO.
# Salidas: recortes/para_revisar.txt (cambios con su escena), recortes/hablantes.json, y un resumen en pantalla.
# Uso: python juntar_correcciones.py
import csv
import glob
import json
import re
from pathlib import Path

aqui = Path(__file__).resolve().parent
TEXTOS = Path(r"C:\mods\yakuza6\entrega_v1.0.3\Herramientas para traduccion\trabajo\textos.csv")

items = {}
for f in sorted(glob.glob(str(aqui / "lotes" / "lote_[0-9][0-9][0-9].json"))):
    for it in json.load(open(f, encoding="utf-8")):
        items[str(it["id"])] = it

bytes_max = {}
with open(TEXTOS, encoding="utf-8-sig", newline="") as fh:
    for r in csv.DictReader(fh, delimiter=";"):
        if r["bytes_max"].strip():
            bytes_max[r["id"]] = int(r["bytes_max"])


def tam(s):
    return len(s.encode("utf-8")) - s.count("í")  # en el juego la í se escribe con «`»: 1 byte


PARES = {("el", "la"), ("él", "ella"), ("lo", "la"), ("los", "las"), ("un", "una"), ("unos", "unas"),
         ("este", "esta"), ("ese", "esa"), ("aquel", "aquella"), ("estos", "estas"), ("esos", "esas"),
         ("del", "de"), ("al", "a"), ("todo", "toda"), ("todos", "todas"), ("ninguno", "ninguna"),
         ("algún", "alguna"), ("ningún", "ninguna"), ("señor", "señora"), ("hijo", "hija")}


def de_genero(a, b):
    a, b = a.lower(), b.lower()
    if a == b:
        return True
    if (a, b) in PARES or (b, a) in PARES:
        return True
    raiz = lambda w: re.sub(r"(os|as|o|a|e|es)$", "", w)
    if raiz(a) == raiz(b) and len(raiz(a)) >= 3:
        return True
    if a + "a" == b or b + "a" == a or a + "as" == b or b + "as" == a:  # trabajador/trabajadora
        return True
    return False


def palabras(s):
    return re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+|[^\w\s]", s)


propuestas, hablantes, problemas = {}, {}, []
for f in sorted(glob.glob(str(aqui / "recortes" / "res_parte_*.json"))):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        problemas.append("%s: no se puede leer (%s)" % (Path(f).name, e))
        continue
    for i, c in (d.get("correcciones") or {}).items():
        propuestas[str(i)] = dict(c, parte=Path(f).stem)
    for p, h in (d.get("hablantes") or {}).items():
        hablantes.setdefault(p, []).append(dict(h, parte=Path(f).stem))

buenas, malas = [], []
for i, c in sorted(propuestas.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
    it = items.get(i)
    fallos = []
    if it is None:
        fallos.append("id que no está en los lotes")
    else:
        actual, nuevo = it["es"], c.get("es", "")
        if c.get("antes") not in (None, actual):
            fallos.append("«antes» no coincide con el lote")
        if nuevo == actual:
            fallos.append("no cambia nada")
        if re.findall(r"<[^>]*>", nuevo) != re.findall(r"<[^>]*>", actual):
            fallos.append("etiquetas distintas")
        if nuevo.count("/") != actual.count("/") or nuevo.count("\n") != actual.count("\n"):
            fallos.append("barras o saltos distintos")
        if i in bytes_max and tam(nuevo) > bytes_max[i]:
            fallos.append("se pasa de bytes (%d > %d)" % (tam(nuevo), bytes_max[i]))
        pa, pn = palabras(actual), palabras(nuevo)
        if len(pa) != len(pn):
            fallos.append("SOSPECHOSO: cambia el número de palabras")
        elif not all(de_genero(a, b) for a, b in zip(pa, pn)):
            fallos.append("SOSPECHOSO: cambia algo que no es género")
    (malas if fallos else buenas).append((i, c, fallos))

with open(aqui / "recortes" / "para_revisar.txt", "w", encoding="utf-8") as out:
    for i, c, fallos in buenas + malas:
        it = items.get(i, {})
        out.write("### %s | %s | escena %s | veces %s | %s\n" % (i, c["parte"], it.get("escena"), it.get("veces"),
                                                                  "; ".join(fallos) or "pasa los filtros"))
        out.write("ANTES: %s\nPROP.: %s\nMOTIVO: %s\n" % (it.get("es"), c.get("es"), c.get("motivo")))
        ctx = it.get("ctx") or []
        m = next((k for k, l in enumerate(ctx) if l.startswith(">>")), 0)
        for l in ctx[max(0, m - 4): m + 4]:
            out.write("   " + l[:300] + "\n")
        out.write("\n")

json.dump(hablantes, open(aqui / "recortes" / "hablantes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
contradicen = [p for p, v in hablantes.items() if len({h.get("genero") for h in v}) > 1]
print("partes leídas:", len(glob.glob(str(aqui / "recortes" / "res_parte_*.json"))))
print("propuestas:", len(propuestas), "| pasan los filtros:", len(buenas), "| con fallos:", len(malas))
print("hablantes apuntados:", len(hablantes), "| con género contradictorio:", len(contradicen), contradicen[:10])
for p in problemas:
    print("PROBLEMA:", p)
