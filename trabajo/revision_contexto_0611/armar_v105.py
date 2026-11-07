# (claude1, 06-11-2026) Arma la v1.0.5 del Y6 en entrega_v1.0.5 con la herramienta pública (filtro es_texto arreglado):
#  1 extraer   textos.csv de entrega_v1.0.5 = inglés original (faltan_c2/orig_en) + español de archivos (= v1.0.4)
#  2 meter     correcciones.json y nuevas_v105.json por su texto INGLÉS; comprueba que entra cada una y que nada más cambia
#  3 aplicar   (20-40 min) -> salida -> archivos; luego ui.par de trabajo/ui_v105 (rótulos de Pequeña Asia)
#  4 comparar  db_e celda a celda contra la v1.0.4: toda diferencia tiene que ser una corrección o una frase nueva
# Uso: python -I -X utf8 armar_v105.py [extraer|meter|aplicar|comparar|todo]
import csv
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
Y6 = Path(r"C:\Mods\yakuza6")
HERR = Y6 / "entrega_v1.0.5" / "Herramientas para traduccion"
INGLES = Y6 / "trabajo" / "faltan_c2" / "orig_en"
PUBLICADO = Y6 / "entrega_v1.0.4" / "archivos"
NUEVO = Y6 / "entrega_v1.0.5" / "archivos"
CSV = HERR / "trabajo" / "textos.csv"
REARMP = HERR / "programas" / "reARMP" / "reARMP.py"
csv.field_size_limit(10 ** 9)
paso = sys.argv[1] if len(sys.argv) > 1 else "todo"


def norm(s):
    return s.replace("\r\n", "\n").replace("\r", "\n")


def herramienta(orden):
    # «--a-archivos»: sin él, aplicar deja el resultado solo en salida/ y archivos/ sigue con la versión vieja
    # (la 1.ª prueba del 06-11 comparó archivos/ sin cambios: «0 tablas distintas»)
    extra = ["--a-archivos"] if orden == "aplicar" else []
    r = subprocess.run([sys.executable, "-X", "utf8", "herramienta_traduccion.py", orden, "--ingles", str(INGLES)] + extra,
                       cwd=HERR, stdin=subprocess.DEVNULL)
    if r.returncode:
        sys.exit("la herramienta falló en «%s»" % orden)


def meter():
    corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
    nuevas = json.load(open(aqui / "nuevas_v105.json", encoding="utf-8"))["nuevas"]
    quiero = {}                                     # inglés -> (español actual esperado, español nuevo, de dónde)
    for i, c in corr.items():
        quiero[norm(c["en"])] = (norm(c["antes"]), norm(c["es"]), "corrección #" + i)
    for en, es in nuevas.items():
        quiero[norm(en)] = (None, es, "nueva")
    filas = list(csv.reader(open(CSV, encoding="utf-8-sig", newline=""), delimiter=";"))
    cab, filas = filas[0], filas[1:]
    i_en, i_es = cab.index("ingles"), cab.index("espanol")
    puestas, raras = set(), []
    for f in filas:
        en = norm(f[i_en])
        if en not in quiero:
            continue
        antes, es, de = quiero[en]
        actual = norm(f[i_es])
        if antes is not None and actual != antes.replace("í", "í"):
            raras.append("%s: el CSV dice %r y la corrección esperaba %r" % (de, actual[:60], antes[:60]))
        if antes is None and actual and actual != en:
            raras.append("%s: ya tenía traducción %r" % (de, actual[:60]))
        f[i_es] = es
        puestas.add(en)
    faltan = [quiero[k][2] + " " + repr(k[:50]) for k in quiero if k not in puestas]
    with open(CSV, "w", encoding="utf-8-sig", newline="") as o:
        w = csv.writer(o, delimiter=";", quoting=csv.QUOTE_ALL)
        w.writerow(cab)
        w.writerows(filas)
    print("puestas: %d de %d | no encontradas en el CSV: %d | con texto distinto del esperado: %d"
          % (len(puestas), len(quiero), len(faltan), len(raras)))
    for x in (faltan + raras)[:30]:
        print("   ", x)
    return not faltan and not raras


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def exportar(bin_, destino):
    destino.mkdir(parents=True, exist_ok=True)
    shutil.copy(bin_, destino / bin_.name)
    subprocess.run([sys.executable, str(REARMP), bin_.name], cwd=destino, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    return json.load(open(destino / (bin_.name + ".json"), encoding="utf-8"))


def hojas(x, ruta=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from hojas(v, ruta + "/" + k)
    elif isinstance(x, list):
        for k, v in enumerate(x):
            yield from hojas(v, ruta + "/" + str(k))
    else:
        yield ruta, x


def comparar():
    JUEGO = str.maketrans({"Í": "|", "í": "`"})      # la herramienta escribe la í en la casilla de «`»
    corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
    nuevas = json.load(open(aqui / "nuevas_v105.json", encoding="utf-8"))["nuevas"]
    esperado = {}
    for c in corr.values():
        for sep in ("\n", "\r\n"):
            esperado.setdefault(c["antes"].translate(JUEGO).replace("\n", sep), set()).add(c["es"].translate(JUEGO).replace("\n", sep))
    for en, es in nuevas.items():
        esperado.setdefault(en, set()).add(es.translate(JUEGO))
    # una celda que en lo publicado seguía IGUAL al inglés y ahora lleva la traducción común de ese inglés (el CSV junta
    # todas las celdas con el mismo inglés): es esperado; se cuenta aparte
    comun = {}
    for f in csv.DictReader(open(CSV, encoding="utf-8-sig", newline=""), delimiter=";"):
        if f["espanol"].strip():
            for sep in ("\n", "\r\n"):
                comun[norm(f["ingles"]).replace("\n", sep)] = norm(f["espanol"]).translate(JUEGO).replace("\n", sep)
    unificadas = []
    tmp = Path(os.environ.get("TEMP", ".")) / "comparar_v105"
    shutil.rmtree(tmp, ignore_errors=True)
    distintas = [Path(p).name for p in sorted(glob.glob(str(PUBLICADO / "db_e" / "*.bin")))
                 if md5(p) != md5(NUEVO / "db_e" / Path(p).name)]
    ok, raros = 0, []
    for t in distintas:
        a = dict(hojas(exportar(PUBLICADO / "db_e" / t, tmp / "a")))
        b = dict(hojas(exportar(NUEVO / "db_e" / t, tmp / "b")))
        for k in sorted(set(a) | set(b)):
            if a.get(k) == b.get(k):
                continue
            if (k.endswith(("/button", "/limit_time")) and "live_chat" in t) or k.endswith("/TEXT_COUNT"):
                ok += 1
            elif isinstance(a.get(k), str) and b.get(k) in esperado.get(a.get(k), ()):
                ok += 1
            elif isinstance(a.get(k), str) and comun.get(a.get(k)) == b.get(k):
                unificadas.append((t, k, a.get(k), b.get(k)))
            else:
                raros.append((t, k, a.get(k), b.get(k)))
    print("tablas distintas:", len(distintas), "| celdas cambiadas esperadas:", ok, "| INESPERADAS:", len(raros))
    if not distintas:
        print("PARO: ninguna tabla cambió; archivos/ no tiene lo armado")
        return False
    print("celdas que seguían en inglés y ahora usan la traducción común:", len(unificadas))
    with open(aqui / "logs" / "comparar_v105.txt", "w", encoding="utf-8") as o:
        for r in raros:
            o.write("INESPERADA %s %s %r -> %r\n" % r)
        for r in unificadas:
            o.write("UNIFICADA %s %s %r -> %r\n" % r)
    with open(aqui / "logs" / "comparar_v105_resumen.txt", "w", encoding="utf-8") as o:
        o.write("Comparación celda a celda de las tablas db_e con la v1.0.4 publicada: %d tablas distintas, %d celdas "
                "cambiadas por las correcciones, %d celdas que seguían en inglés y ahora usan la traducción común, %d "
                "inesperadas.\n" % (len(distintas), ok, len(unificadas), len(raros)))
    for r in raros[:30]:
        print("  ", r[0], r[1], repr(r[2])[:70], "->", repr(r[3])[:70])
    return not raros


if paso in ("extraer", "todo"):
    herramienta("extraer")
if paso in ("meter", "todo") and not meter() and paso == "todo":
    sys.exit("PARO: hay correcciones que no entraron bien (arriba)")
if paso in ("aplicar", "todo"):
    herramienta("aplicar")
    shutil.copy(Y6 / "trabajo" / "ui_v105" / "ui.par", NUEVO / "ui.par")
    print("ui.par de trabajo/ui_v105 copiado")
if paso in ("comparar", "todo"):
    sys.exit(0 if comparar() else 1)
