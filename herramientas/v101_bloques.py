"""(claude1, 25-10-2026) Al guardar una textura editada, el compresor DXT de Pillow recomprime TODA la imagen y estropea los
detalles finos que no se tocaron (números verdes de los dardos, ceros con acentos fantasma...). Este paso devuelve, en el
nivel 0, los bloques 4x4 ORIGINALES (comprimidos tal cual) donde la imagen no cambió de verdad.
  python -I herramientas/v101_bloques.py <carpeta_con_dds_editadas>     (compara con trabajo/extraido/ui/e/texture)
"""
import os, sys, struct, subprocess, tempfile
import numpy as np
from PIL import Image

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(R, 'trabajo', 'extraido', 'ui', 'e', 'texture')
TC = os.path.join(R, 'herramientas', 'kit_atlas', 'texconv', 'texconv.exe')
MARGEN = 12   # px alrededor de cada casilla editada (halo, brillo, borrado LaMa)
import json
HECHOS = os.path.join(R, 'trabajo', 'imagenes', 'atlas_hechos'); UI = os.path.join(R, 'trabajo', 'imagenes_ui', 'atlas_es.json')


def zonas(nombre):
    """casillas que el redibujado pudo tocar; None = no se sabe (no se restaura nada en esa textura)."""
    p = os.path.join(HECHOS, 'e__texture__' + nombre + '.json')
    if os.path.exists(p): its = json.load(open(p, encoding='utf-8'))['items']
    else:
        u = json.load(open(UI, encoding='utf-8'))
        if nombre not in u: return None
        its = u[nombre]['items']
    return [it['caja'] for it in its if not it.get('dejar') or it.get('solo_borrar')]   # todo lo que se pudo redibujar o borrar


def png(ruta, tmp):
    subprocess.run([TC, '-nologo', '-y', '-ft', 'png', '-m', '1', '-o', tmp, ruta], capture_output=True)
    return np.asarray(Image.open(os.path.join(tmp, os.path.basename(ruta)[:-4] + '.png')).convert('RGBA')).astype(int)


def main(carpeta):
    tot = 0
    for f in sorted(os.listdir(carpeta)):
        if not f.endswith('.dds'): continue
        nuevo, orig = os.path.join(carpeta, f), os.path.join(ORIG, f)
        ob = open(orig, 'rb').read(); nb = bytearray(open(nuevo, 'rb').read())
        if ob == bytes(nb) or len(ob) != len(nb) or ob[84:88] not in (b'DXT1', b'DXT3', b'DXT5'): continue
        bs = 8 if ob[84:88] == b'DXT1' else 16
        H, W = struct.unpack('<II', ob[12:20])
        z = zonas(f[:-4])
        if z is None: print(f, 'sin especificación: se deja'); continue
        tocado = np.zeros((H, W), bool)
        for x0, y0, x1, y1 in z: tocado[max(0, y0 - MARGEN):y1 + MARGEN, max(0, x0 - MARGEN):x1 + MARGEN] = True
        # (25-10) el español puede salir de su casilla (las casillas son del OCR, no del juego): también es «tocado» todo lo
        # que cambió de verdad respecto al original, con 12 px alrededor (halos y capas borrosas)
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            a, b = png(orig, t1), png(nuevo, t2)
        import cv2
        fuerte = (np.abs(a - b).max(2) > 60).astype(np.uint8)
        tocado |= cv2.dilate(fuerte, np.ones((25, 25), np.uint8)).astype(bool)
        fila = (W + 3) // 4; n = 0
        for by in range(H // 4):
            for bx in range(W // 4):
                if not tocado[by*4:by*4+4, bx*4:bx*4+4].any():
                    k = 128 + (by * fila + bx) * bs
                    if nb[k:k+bs] != ob[k:k+bs]: nb[k:k+bs] = ob[k:k+bs]; n += 1
        open(nuevo, 'wb').write(bytes(nb)); tot += n
        print(f, 'bloques originales devueltos:', n)
    print('total', tot)


if __name__ == '__main__':
    main(sys.argv[1])
