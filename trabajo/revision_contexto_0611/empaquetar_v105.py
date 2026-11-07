# (claude1, 06-11-2026) Zips de la v1.0.5 del Y6 en Entregas, como los de la v1.0.4, comprobando cada archivo:
#  - traducción: AVISO, INSTALAR o QUITAR.bat, LEEME, instalar.ps1 y archivos/ de entrega_v1.0.5
#  - herramientas: lo que tiene el repo de herramientas (git ls-files) + programas/ParTool/ParTool.exe, dentro de
#    «Herramientas para traduccion/»
# Uso: python -I -X utf8 empaquetar_v105.py
import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ENT = Path(r"C:\Mods\Entregas\Entregas Yakuza 6")
ORIG = Path(r"C:\Mods\yakuza6\entrega_v1.0.5")
HERR = Path(r"C:\Mods\github\yakuza6-herramientas")
Z_TR = ENT / "Yakuza 6 - Traduccion al espanol v1.0.5.zip"
Z_HE = ENT / "Yakuza 6 - Herramientas para traduccion v1.0.5.zip"
md5 = lambda b: hashlib.md5(b).hexdigest()
mal = 0


def armar(destino, pares):
    global mal
    if destino.exists():
        destino.unlink()
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for origen, nombre in pares:
            z.write(origen, nombre)
    z = zipfile.ZipFile(destino)
    malos = [n for (o, n) in pares if md5(z.read(n)) != md5(open(o, "rb").read())]
    mal += len(malos)
    print("%s: %d archivos, distintos %d, %.1f MB, sha256 %s" % (destino.name, len(pares), len(malos),
          destino.stat().st_size / 2 ** 20, hashlib.sha256(destino.read_bytes()).hexdigest()[:16]))


# (07-11) el LEEME llevaba «644 textos corregidos» a mano cuando ya eran 677: ahora se comprueba antes de empaquetar
import json
n_corr = len(json.load(open(Path(__file__).resolve().parent / "correcciones.json", encoding="utf-8")))
if "%d textos corregidos" % n_corr not in (ORIG / "LEEME.txt").read_text(encoding="utf-8-sig"):
    sys.exit("PARO: el LEEME no dice «%d textos corregidos» (correcciones.json)" % n_corr)
pares = [(ORIG / f, f) for f in ["AVISO.txt", "INSTALAR o QUITAR.bat", "LEEME.txt", "instalar.ps1"]]
for base, _, nombres in os.walk(ORIG / "archivos"):
    for n in nombres:
        p = Path(base) / n
        pares.append((p, p.relative_to(ORIG).as_posix()))
armar(Z_TR, pares)

lista = subprocess.run(["git", "ls-files"], cwd=HERR, capture_output=True, text=True, check=True).stdout.split("\n")
lista = [x for x in lista if x]
if "programas/ParTool/ParTool.exe" not in lista:   # en el repo ya está: no meterlo dos veces
    lista.append("programas/ParTool/ParTool.exe")
armar(Z_HE, [(HERR / x, "Herramientas para traduccion/" + x) for x in lista])
sys.exit(1 if mal else 0)
