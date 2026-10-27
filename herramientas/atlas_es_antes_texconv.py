# -*- coding: utf-8 -*-
"""(Claude Code, 20-10-2026) Traduce texto dentro de los atlas de imagen de Yakuza 6 (menú principal, pausa, etc.).
Cada palabra/frase inglesa ocupa una caja del atlas; el juego recorta esa zona. Para no salirse nunca, el español se
dibuja DENTRO de la misma caja: mismo alto (calibrado con el inglés original en la misma fuente) y, si es más largo,
se estrecha en horizontal (hasta 62 %) y después se achica. Copia el color y el brillo (halo) del original.
Especificación: trabajo/imagenes_ui/atlas_es.json
  {"nombre_textura": {"fuente": "georgiaz.ttf", "items": [{"caja": [x0,y0,x1,y1], "en": "Stats", "es": "Atributos",
                       "alin": "izq|centro|der" (opcional), "efecto": "auto|brillo|nada" (opcional)}]}}
  python herramientas/atlas_es.py [nombre ...]   -> trabajo/imagenes_ui/es/<nombre>.dds (+ .png para revisar)
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(R, 'trabajo', 'extraido', 'ui', 'e', 'texture')
SAL = os.path.join(R, 'trabajo', 'imagenes_ui', 'es')
FUENTES = [os.path.join(R, 'herramientas', 'fuentes_img'), 'C:/Windows/Fonts']


def fuente(nombre, tam):
    for d in FUENTES:
        p = os.path.join(d, nombre)
        if os.path.exists(p): return ImageFont.truetype(p, tam)
    raise FileNotFoundError(nombre)


def tinta(f, t):
    """caja de tinta (anchor ls: arriba negativo) de un texto."""
    return f.getbbox(t, anchor='ls')


def calibrar(nf, en, alto_obj):
    """tamaño de letra con el que el inglés 'en' mide alto_obj px de tinta en la fuente nf."""
    tam = 40
    for _ in range(6):
        f = fuente(nf, tam); bb = tinta(f, en); h = bb[3] - bb[1]
        tam = max(6, int(round(tam * alto_obj / max(1, h))))
    return tam


def mascara(nf, t, tam, en, ancho_max):
    """Máscara L del texto t con la fuente nf al tamaño tam (se estrecha/achica si no cabe en ancho_max)."""
    f = fuente(nf, tam)
    bb_en = tinta(f, en); bb = tinta(f, t)
    img = Image.new('L', (bb[2] - bb[0] + 8, max(bb[3], bb_en[3]) - min(bb[1], bb_en[1]) + 8), 0)
    arriba = min(bb[1], bb_en[1])
    ImageDraw.Draw(img).text((4 - bb[0], 4 - arriba), t, font=f, fill=255, anchor='ls')
    base = 4 - arriba                                   # fila de la línea base dentro de img
    sup_en = base + bb_en[1]                             # fila donde empieza la tinta del inglés
    ancho = bb[2] - bb[0]
    if ancho > ancho_max:
        k = ancho_max / ancho
        if k >= 0.62: img = img.resize((max(1, int(img.width * k)), img.height), Image.LANCZOS)
        else:
            img = img.resize((max(1, int(img.width * 0.62)), img.height), Image.LANCZOS)
            k2 = ancho_max / max(1, ancho * 0.62)
            img = img.resize((max(1, int(img.width * k2)), max(1, int(img.height * k2))), Image.LANCZOS)
            base = int(base * k2); sup_en = int(sup_en * k2)
    return img, sup_en


def traducir(nombre, spec):
    orig = Image.open(os.path.join(TEX, nombre + '.dds')).convert('RGBA')
    a = np.asarray(orig).copy()
    nuevo = Image.fromarray(a)
    tams = []
    for it in spec['items']:
        x0, y0, x1, y1 = it['caja']; op = a[y0:y1, x0:x1, 3] > 200; filas = np.where(op.any(1))[0]
        alto = int(filas[-1] - filas[0] + 1) if len(filas) else (y1 - y0)
        tams.append(calibrar(it.get('fuente', spec['fuente']), it['en'], alto))
    for i, it in enumerate(spec['items']):
        grupo = [tams[j] for j, o in enumerate(spec['items']) if o.get('fuente', spec['fuente']) == it.get('fuente', spec['fuente'])
                 and abs(o['caja'][0] - it['caja'][0]) < 40]
        it['_tam'] = int(np.median(grupo)) if it.get('mediana', spec.get('mediana', True)) else tams[i]
        if it.get('tam'): it['_tam'] = int(it['tam'])   # (25-10, claude1) cuerpo fijo, como el kit de atlas
    for it in spec['items']:
        x0, y0, x1, y1 = it['caja']
        zona = a[y0:y1, x0:x1]
        op = zona[..., 3] > 200
        color = tuple(int(v) for v in np.median(zona[..., :3][op], axis=0)) if op.sum() > 10 else (255, 255, 255)
        medio = ((zona[..., 3] > 15) & (zona[..., 3] <= 200)).sum()
        efecto = it.get('efecto', 'auto')
        if efecto == 'auto': efecto = 'brillo' if medio > 1.2 * max(1, op.sum()) else 'nada'
        # alto de tinta del original: filas con alfa alto
        filas = np.where(op.any(1))[0]
        alto = int(filas[-1] - filas[0] + 1) if len(filas) else (y1 - y0)
        top = y0 + (filas[0] if len(filas) else 0)
        cols = np.where(op.any(0))[0]
        ix0 = x0 + (cols[0] if len(cols) else 0); ix1 = x0 + (cols[-1] + 1 if len(cols) else x1 - x0)
        m = 3 if efecto == 'nada' else 6
        nuevo_a = np.asarray(nuevo).copy(); nuevo_a[max(0, y0 - m):y1 + m, max(0, x0 - m):x1 + m] = 0
        nuevo = Image.fromarray(nuevo_a)
        img, sup = mascara(it.get('fuente', spec['fuente']), it['es'], it['_tam'], it['en'], it.get('ancho_max', spec.get('ancho_max', ix1 - ix0)))
        alin = it.get('alin') or spec.get('alin') or ('izq' if x0 < 12 else 'centro')
        if alin == 'izq': px = ix0
        elif alin == 'der': px = ix1 - img.width
        else: px = int(round((ix0 + ix1) / 2 - img.width / 2))
        py = top - sup
        capa = Image.new('L', orig.size, 0); capa.paste(img, (px - 4 if alin == 'izq' else px, py))
        if efecto == 'brillo':
            halo = capa.filter(ImageFilter.GaussianBlur(float(max(2, alto / 9))))
            halo = Image.fromarray(np.clip(np.asarray(halo, np.float32) * 1.7, 0, 255).astype(np.uint8))
            capa = Image.fromarray(np.maximum(np.asarray(capa), np.asarray(halo)))
        if efecto == 'borroso':                         # versión desenfocada del mismo rótulo (para el brillo del juego)
            capa = capa.filter(ImageFilter.GaussianBlur(float(max(2, alto / 10))))
            capa = Image.fromarray(np.clip(np.asarray(capa, np.float32) * 1.25, 0, 255).astype(np.uint8))
        # que nada (halo incluido) se salga de la franja de su fila: si no, aparece en el recorte de la fila vecina
        recorte = np.zeros((orig.size[1], orig.size[0]), np.uint8); recorte[max(0, y0 - 2):y1 + 2, :] = 1
        capa = Image.fromarray(np.asarray(capa) * recorte)
        color_img = Image.new('RGBA', orig.size, color + (0,)); color_img.putalpha(capa)
        nuevo.alpha_composite(color_img)
    return orig, nuevo


def guardar_dds(nombre, img):
    os.makedirs(SAL, exist_ok=True)
    o = open(os.path.join(TEX, nombre + '.dds'), 'rb').read()
    fmt = {b'DXT1': 'DXT1', b'DXT5': 'DXT5', b'DXT3': 'DXT3'}.get(o[84:88])
    ruta = os.path.join(SAL, nombre + '.dds')
    if fmt is None: raise ValueError(f'{nombre}: formato DDS no previsto {o[84:88]}')
    import io, struct
    mips = max(1, struct.unpack('<I', o[28:32])[0]); W, H = img.size; datos = b''
    for nivel in range(mips):                              # cada nivel de mipmap comprimido por separado
        im = img if nivel == 0 else img.resize((max(1, W >> nivel), max(1, H >> nivel)), Image.LANCZOS)
        if im.width < 4 or im.height < 4:                  # los bloques DXT son de 4x4: los niveles diminutos van en un bloque
            im = im.resize((max(4, im.width), max(4, im.height)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, format='DDS', pixel_format=fmt); datos += b.getvalue()[128:]
    datos = datos[:len(o) - 128]
    assert len(datos) == len(o) - 128, (nombre, len(datos), len(o) - 128)
    open(ruta, 'wb').write(o[:128] + datos)             # cabecera original (mismo tamaño, banderas y mipmaps)
    return ruta


if __name__ == '__main__':
    spec = json.load(open(os.path.join(R, 'trabajo', 'imagenes_ui', 'atlas_es.json'), encoding='utf-8'))
    for nombre in (sys.argv[1:] or list(spec)):
        orig, nuevo = traducir(nombre, spec[nombre])
        guardar_dds(nombre, nuevo)
        W, H = orig.size; v = Image.new('RGBA', (W * 2, H), (40, 90, 40, 255))
        v.alpha_composite(orig, (0, 0)); v.alpha_composite(nuevo, (W, 0)); v.convert('RGB').save(os.path.join(SAL, nombre + '.png'))
        print('ok', nombre)
