"""(claude1, 25-10-2026) Devuelve trozos del ORIGINAL que el redibujado dañó (números que no se traducen).
Se ejecuta DESPUÉS de atlas_probar.py aplicar.  python -I herramientas/v101_restaurar.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kit_atlas'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atlas_es
from PIL import Image

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(R, 'trabajo', 'extraido', 'ui', 'e', 'texture')
ES = os.path.join(R, 'trabajo', 'imagenes', 'es', 'e', 'texture')
# textura: [zonas x0, y0, x1, y1] que vuelven al original
ZONAS = {
    'mg_darts_cricket_p02': [(396, 48, 484, 104)],   # TRIPLE 16 / TRIPLE 15 (no se traducen)
}
for n, zs in ZONAS.items():
    o = Image.open(os.path.join(ORIG, n + '.dds')).convert('RGBA')
    e = Image.open(os.path.join(ES, n + '.dds')).convert('RGBA')
    for z in zs:
        e.paste(o.crop(z), z[:2])
    atlas_es.SAL = ES; atlas_es.TEX = ORIG
    ruta = atlas_es.guardar_dds(n, e)
    # (25-10) el compresor de Pillow estropea los números finos: en el nivel 0 se copian TAL CUAL los bloques DXT originales
    import struct
    ob = open(os.path.join(ORIG, n + '.dds'), 'rb').read(); nb = bytearray(open(ruta, 'rb').read())
    W = struct.unpack('<I', ob[16:20])[0]; bs = 8 if ob[84:88] == b'DXT1' else 16; fila = (W + 3) // 4
    for x0, y0, x1, y1 in zs:
        for by in range(y0 // 4, (y1 + 3) // 4):
            for bx in range(x0 // 4, (x1 + 3) // 4):
                k = 128 + (by * fila + bx) * bs; nb[k:k + bs] = ob[k:k + bs]
    open(ruta, 'wb').write(bytes(nb))
    print('restaurado', n, zs)
