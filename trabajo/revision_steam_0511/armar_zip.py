# Arma el zip de la traducción (instalador + archivos/, sin herramientas) y comprueba cada archivo contra el original.
# Uso: python armar_zip.py <carpeta de la entrega> <zip de salida>
import hashlib
import os
import sys
import zipfile

origen, destino = sys.argv[1], sys.argv[2]
if os.path.exists(destino):
    sys.exit("YA EXISTE: " + destino)
os.chdir(origen)
archivos = ["AVISO.txt", "INSTALAR o QUITAR.bat", "LEEME.txt", "instalar.ps1"]
for base, _, nombres in os.walk("archivos"):
    for n in nombres:
        archivos.append(os.path.join(base, n).replace(os.sep, "/"))
with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for a in archivos:
        z.write(a, a)

md5 = lambda b: hashlib.md5(b).hexdigest()
z = zipfile.ZipFile(destino)
malos = [n for n in z.namelist() if md5(z.read(n)) != md5(open(n, "rb").read())]
print(len(z.namelist()), "archivos; distintos:", len(malos), "; MB", round(os.path.getsize(destino) / 2 ** 20, 1))
print("sha256", hashlib.sha256(open(destino, "rb").read()).hexdigest())
sys.exit(1 if malos else 0)
