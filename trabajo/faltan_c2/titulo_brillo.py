# -*- coding: utf-8 -*-
"""(01-11-2026, claude2) Pantalla de título: «PRESIONA UN BOTÓN» se dibuja con dos filas de la textura
title_press_any_button.dds (fina + gruesa con brillo) encima una de otra. En el inglés las dos miden lo mismo; en la
nuestra la gruesa era más ancha y asomaba un «ÓN» fantasma a la derecha. Se estrecha la fila gruesa al ancho de la fina.
  python titulo_brillo.py <ui extraído (carpeta con e/texture)> <salida .dds>"""
import os, struct, subprocess, sys, tempfile
import numpy as np
from PIL import Image
U, SAL = sys.argv[1:3]
TC = 'C:/Mods/yakuza6/herramientas/kit_atlas/texconv/texconv.exe'
src = os.path.join(U, 'e', 'texture', 'title_press_any_button.dds')
im = Image.open(src).convert('RGBA'); a = np.array(im)
def caja(y0, y1):
    ys, xs = np.where(a[y0:y1, :, 3] > 30); return xs.min(), xs.max()
f0, f1 = caja(0, 31); g0, g1 = caja(31, 66)
print('fina', f0, f1, 'gruesa', g0, g1)
ys = np.where(a[31:66, :, 3] > 30)[0]; t0, t1 = 31 + ys.min(), 31 + ys.max()
fila = im.crop((g0 - 2, t0 - 2, g1 + 3, t1 + 3))
nuevo_ancho = (f1 + 2) - (f0 - 2) + 1
# también de alto: como el inglés (tinta de y=34 a 61), para que el acento no toque la fila de arriba
fila = fila.resize((nuevo_ancho, (61 - 34 + 1) + 4), Image.LANCZOS)
salida = im.copy(); salida.paste((0, 0, 0, 0), (0, 31, im.width, 66))
salida.alpha_composite(fila, (f0 - 2, 34 - 2))
mips = struct.unpack_from('<I', open(src, 'rb').read(), 0x1C)[0] or 1
with tempfile.TemporaryDirectory() as t:
    png = os.path.join(t, 'title_press_any_button.png'); salida.save(png)
    subprocess.run([TC, '-nologo', '-y', '-f', 'BC3_UNORM', '-m', str(mips), '-o', t, png], check=True, capture_output=True)
    os.makedirs(os.path.dirname(SAL), exist_ok=True)
    os.replace(os.path.join(t, 'title_press_any_button.dds'), SAL)
b = np.array(Image.open(SAL).convert('RGBA')); a = b
print('nueva gruesa', caja(31, 66), 'mips', mips)
bg = Image.new('RGBA', (512, 70), (40, 40, 40, 255)); bg.alpha_composite(Image.open(SAL).convert('RGBA').crop((0, 0, 512, 70)))
bg.convert('RGB').save(SAL[:-4] + '_vista.png')
