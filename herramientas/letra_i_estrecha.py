# -*- coding: utf-8 -*-
"""(01-11-2026, claude2) La «í» minúscula se veía con hueco («Subt í tulos», «viv í a»): el juego da a cada código su
propio ancho y el de «~» (donde se dibujó la í en la v1.0) es ancho. «`» (acento grave) es estrecho como la «i» y no
sale en ningún texto del juego: se dibuja ahí la í y la traducción escribe «`» en lugar de «í».
  - yakuza.dds / yakuza_italic.dds: la í de la casilla «~» se copia a la de «`», con el palo donde estaba la tinta del «`».
  - gothic.bin: los registros de «`» (variantes 0 y 1) apuntan a la casilla y medidas de la í.
Entrada: font.par de la v1.0.2. Salida: el font.par nuevo.
  python letra_i_estrecha.py <font.par entrada> <font.par salida>"""
import os, sys, shutil, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc4, letras_es as L
from letras_ascii import casilla, tinta_x, mover
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PT = os.path.join(R, 'herramientas', 'partool', 'ParTool.exe')
ORIG = os.path.join(R, 'trabajo', 'extraido', 'font', 'e')
NUEVA, VIEJA = '`', '~'

def dds(ruta_in, ruta_out, ref):
    raw = bytearray(open(ruta_in, 'rb').read()); cab, dat = raw[:128], bytearray(raw[128:])
    at = bc4.decodificar(bytes(dat), 256, 512)
    y0, y1, x0, x1 = casilla(ord(VIEJA)); g = at[y0:y1, x0:x1].copy()          # la í ya dibujada
    Y0, Y1, X0, X1 = casilla(ord(NUEVA)); r = ref[Y0:Y1, X0:X1]
    dx = tinta_x(r)[0] - tinta_x(g, 14)[0]                                       # palo de la í donde empieza el «`»
    nuevo = mover(g, dx)
    bc4.editar_casilla(dat, 256, Y0, Y1, X0, X1, lambda reg, c, n=nuevo: (reg.__setitem__((slice(c[0], c[1]), slice(c[2], c[3])), n), reg)[1])
    open(ruta_out, 'wb').write(bytes(cab) + bytes(dat))
    print(os.path.basename(ruta_out), 'dx', dx)

def main(entrada, salida):
    tmp = salida + '_obra'; shutil.rmtree(tmp, ignore_errors=True)
    ext, add = os.path.join(tmp, 'ext'), os.path.join(tmp, 'add', 'e'); os.makedirs(add)
    subprocess.run([PT, 'extract', entrada, ext], stdin=subprocess.DEVNULL, capture_output=True, check=True)
    for f in ('yakuza.dds', 'yakuza_italic.dds'):
        ref = bc4.decodificar(open(os.path.join(ORIG, f), 'rb').read()[128:], 256, 512)
        dds(os.path.join(ext, 'e', f), os.path.join(add, f), ref)
    d, regs = L.leer_bin(os.path.join(ext, 'e', 'gothic.bin')); porc = {(r['code'], r['var']): r for r in regs}
    for var in (0, 1):
        fuente, dest = porc[(L.code_de('í'), var)], porc[(ord(NUEVA), var)]
        d[dest['o'] + 8:dest['o'] + 32] = d[fuente['o'] + 8:fuente['o'] + 32]
    open(os.path.join(add, 'gothic.bin'), 'wb').write(d)
    if os.path.exists(salida): os.remove(salida)
    subprocess.run([PT, 'add', entrada, os.path.join(tmp, 'add'), salida], stdin=subprocess.DEVNULL, capture_output=True, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print('listo', salida, os.path.getsize(salida))

if __name__ == '__main__': main(*sys.argv[1:3])
