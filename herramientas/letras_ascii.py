# -*- coding: utf-8 -*-
"""(Claude Code, 20-10-2026) Í e í en las casillas de «|» y «~» de la fuente del Yakuza 6.
Motivo: en la letra de menús (font/e/yakuza.dds) el juego no mide las letras por su tinta: cada código trae sus medidas
(no están en el .dds ni en el .exe a la vista). La Í/í de Latin-1 deja un hueco detrás («DIFÍ CIL»). «|» y «~» son
estrechos y nunca salen en los textos: se dibuja Í/í en su casilla, con el palo donde estaba la raya del «|» (y centrada
en la tinta del «~»), y aplicar_talk.traducciones() escribe «|» y «~» en lugar de Í/í (ASCII_I).
  - yakuza.dds (versión con tildes de trabajo/font_add_final) y yakuza_italic.dds (original): se mueve la letra.
  - gothic.bin (diálogos y subtítulos, con tabla de medidas): los registros de «|» y «~» pasan a apuntar a la casilla y
    medidas de los registros Í/í que ya se añadieron (letras_es.py).
Probado en el laboratorio (20-10): «DIFÍCIL» en el menú de dificultad sin hueco.
Entrada: trabajo/font_es_v2.par. Salida: trabajo/font_es_v5.par.   python herramientas/letras_ascii.py
"""
import os, sys, shutil, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc4, letras_es as L
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(R, 'trabajo')
PT = os.path.join(R, 'herramientas', 'partool', 'ParTool.exe')
MAPA = {'Í': '|', 'í': '~'}


def casilla(code):
    k = code - 0x20; r, c = divmod(k, 16); return r * 32, (r + 1) * 32, c * 16, (c + 1) * 16


def tinta_x(g, desde=0):
    xs = np.where((g[desde:] > 100).any(0))[0]; return int(xs.min()), int(xs.max())


def mover(g, dx):
    n = np.zeros_like(g)
    if dx >= 0: n[:, dx:] = g[:, :g.shape[1] - dx]
    else: n[:, :g.shape[1] + dx] = g[:, -dx:]
    return n


def dds_ascii(ruta_in, ruta_out, ref):
    """ref: atlas original (para las medidas de «|» y «~»)."""
    raw = bytearray(open(ruta_in, 'rb').read()); cab, dat = raw[:128], bytearray(raw[128:])
    at = bc4.decodificar(bytes(dat), 256, 512)
    for letra, sig in MAPA.items():
        y0, y1, x0, x1 = casilla(ord(letra)); g = at[y0:y1, x0:x1].copy()
        Y0, Y1, X0, X1 = casilla(ord(sig)); r = ref[Y0:Y1, X0:X1]
        if sig == '|':
            dx = tinta_x(r)[0] - tinta_x(g, 14)[0]                     # palo de la I (sin la tilde) sobre la raya
        else:
            a, b = tinta_x(r); c, d = tinta_x(g); dx = (a + b) // 2 - (c + d) // 2   # centrada en la tinta del «~»
        nuevo = mover(g, dx)
        bc4.editar_casilla(dat, 256, Y0, Y1, X0, X1, lambda reg, c, n=nuevo: (reg.__setitem__((slice(c[0], c[1]), slice(c[2], c[3])), n), reg)[1])
    os.makedirs(os.path.dirname(ruta_out), exist_ok=True); open(ruta_out, 'wb').write(bytes(cab) + bytes(dat))


def main():
    base = os.path.join(T, 'font_ascii'); shutil.rmtree(base, ignore_errors=True)
    ext = os.path.join(base, 'ext'); add = os.path.join(base, 'add', 'e')
    subprocess.run([PT, 'extract', os.path.join(T, 'font_es_v2.par'), ext], stdin=subprocess.DEVNULL, capture_output=True, check=True)
    ref = bc4.decodificar(open(os.path.join(T, 'extraido', 'font', 'e', 'yakuza.dds'), 'rb').read()[128:], 256, 512)
    ref_i = bc4.decodificar(open(os.path.join(T, 'extraido', 'font', 'e', 'yakuza_italic.dds'), 'rb').read()[128:], 256, 512)
    dds_ascii(os.path.join(ext, 'e', 'yakuza.dds'), os.path.join(add, 'yakuza.dds'), ref)
    dds_ascii(os.path.join(ext, 'e', 'yakuza_italic.dds'), os.path.join(add, 'yakuza_italic.dds'), ref_i)
    d, regs = L.leer_bin(os.path.join(ext, 'e', 'gothic.bin')); porc = {(r['code'], r['var']): r for r in regs}
    for letra, sig in MAPA.items():
        for var in (0, 1):
            fuente, dest = porc[(L.code_de(letra), var)], porc[(ord(sig), var)]
            d[dest['o'] + 8:dest['o'] + 32] = d[fuente['o'] + 8:fuente['o'] + 32]   # casilla (4 float) y medidas
    open(os.path.join(add, 'gothic.bin'), 'wb').write(d)
    out = os.path.join(T, 'font_es_v5.par')
    if os.path.exists(out): os.remove(out)
    subprocess.run([PT, 'add', os.path.join(T, 'font_es_v2.par'), os.path.join(base, 'add'), out], stdin=subprocess.DEVNULL, capture_output=True, check=True)
    print('listo', out, os.path.getsize(out))


if __name__ == '__main__': main()
