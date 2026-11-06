# Compara celda por celda las tablas ARMP de dos versiones (p. ej. v1.0.3 y v1.0.4) y comprueba que cada diferencia sea
# una corrección de correcciones.json (o el «button»/«limit_time» que acompaña a lo que se teclea en el chat en vivo).
# Uso: python comparar_tablas.py <db_e antes> <db_e después> <carpeta temporal>
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
REARMP = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\programas\reARMP\reARMP.py")
antes, despues, tmp = map(Path, sys.argv[1:4])
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
JUEGO = str.maketrans({"Í": "|", "í": "`"})          # la herramienta escribe la í en la casilla de «`»
esperado = {}
for c in corr.values():
    esperado.setdefault(c["antes"].translate(JUEGO).replace("\n", "\r\n"), set()).add(c["es"].translate(JUEGO).replace("\n", "\r\n"))
    esperado.setdefault(c["antes"].translate(JUEGO), set()).add(c["es"].translate(JUEGO))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def exportar(bin_, destino):
    destino.mkdir(parents=True, exist_ok=True)
    shutil.copy(bin_, destino / bin_.name)
    subprocess.run([sys.executable, str(REARMP), bin_.name], cwd=destino, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    return json.load(open(destino / (bin_.name + ".json"), encoding="utf-8"))


def hojas(x, ruta=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from hojas(v, ruta + "/" + k)
    else:
        yield ruta, x


distintas = [Path(p).name for p in sorted(glob.glob(str(antes / "*.bin")))
             if md5(p) != md5(despues / Path(p).name)]
ok, raros = 0, []
for t in distintas:
    a = dict(hojas(exportar(antes / t, tmp / "a")))
    b = dict(hojas(exportar(despues / t, tmp / "b")))
    for k in sorted(set(a) | set(b)):
        if a.get(k) == b.get(k):
            continue
        if k.endswith(("/button", "/limit_time")) and "live_chat" in t:
            ok += 1
        elif k.endswith("/TEXT_COUNT"):
            ok += 1  # cuántos textos distintos guarda la tabla: cambia solo si una corrección separa dos textos iguales
        elif isinstance(a.get(k), str) and b.get(k) in esperado.get(a.get(k), ()):
            ok += 1
        else:
            raros.append((t, k, a.get(k), b.get(k)))
print("tablas distintas:", len(distintas), "| celdas cambiadas esperadas:", ok, "| INESPERADAS:", len(raros))
for r in raros[:40]:
    print("  ", r[0], r[1], repr(r[2])[:80], "->", repr(r[3])[:80])
sys.exit(1 if raros else 0)
