# -*- coding: utf-8 -*-
"""(01-11-2026, claude1) Títulos de capítulo del Y6 (ui.par e/texture/chapter_NN.dds, 1024x1024): en la v1.0 se quedaron
en INGLÉS (título + «CHAPTER N»). Arriba va el título japonés y «第N章» (se dejan); desde y=540 todo se vacía y se
escribe el español del juego (lote 025 «Capítulo N: título»; final = «FINAL / LOS IMPERDONABLES») con letra de pincel
blanca, renglones centrados como el original y «CAPÍTULO N» a la izquierda (x 111, y 924-987).
Salida: trabajo/faltan_c1/es/e/texture/chapter_NN.dds + revision/*.png
  python trabajo/faltan_c1/capitulos_y6.py [--prueba-fuentes]"""
import glob, json, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B = os.path.dirname(os.path.abspath(__file__)); Y = os.path.dirname(os.path.dirname(B))
U = os.path.join(B, 'ui_actual'); SAL = os.path.join(B, 'es'); REV = os.path.join(B, 'revision')
FUENTES = os.path.join(Y, 'herramientas', 'fuentes_img')
FUENTE = os.path.join(FUENTES, 'Bangers-Regular.ttf')     # (la más parecida al original; con aspereza de pincel)
Y0 = 540                                       # desde aquí hacia abajo solo hay inglés
TITULO = (556, 843)                            # alto que ocupan 1-2 renglones del título
CAP = (111, 924, 987)                          # x, arriba, abajo de «CHAPTER N»


def titulos():
    L = os.path.join(Y, 'trabajo', 'lotes')
    out = {}
    for f in sorted(glob.glob(L + '/lote_???.json')):
        try: es = json.load(open(f[:-5] + '_es.json', encoding='utf-8'))
        except FileNotFoundError: continue
        for x in json.load(open(f, encoding='utf-8')):
            m = re.fullmatch(r'Chapter (\d+): .+', x['en'].strip())
            t = es.get(str(x['id']), '')
            if m and t.startswith('Capítulo'): out[int(m.group(1))] = t.split(':', 1)[1].strip()
            if x['en'].strip() == 'Finale: The Unforgiven': out[13] = t.split(':', 1)[1].strip()
    return out


def renglones(texto, f, ancho):
    pal = texto.upper().split(); r = ['']
    for p in pal:
        if f.getlength((r[-1] + ' ' + p).strip()) <= ancho: r[-1] = (r[-1] + ' ' + p).strip()
        else: r.append(p)
    return r


ALTO_RENGLON, ALTO_CAP, ESTRECHO = 118, 60, 0.95     # alto de la tinta del original (131 con trazos) y de «CHAPTER N»


def linea(texto, alto, ancho_max, fuente):
    """Máscara de un renglón de pincel: se dibuja grande, se recorta a la tinta y se escala al alto pedido (como
    rotulos._texto del Y5: el espacio de la letra de pincel es estrecho, se duplica)."""
    import unicodedata
    f = ImageFont.truetype(fuente, 220); t = texto.upper().replace(' ', '  ')
    bb = f.getbbox(t); m = Image.new('L', (bb[2] - bb[0] + 80, bb[3] - bb[1] + 80), 0)
    ImageDraw.Draw(m).text((40 - bb[0], 40 - bb[1]), t, font=f, fill=255); m = m.crop(m.getbbox())
    # el alto se mide SIN tildes ni virgulilla (si no, «CONSPIRACIÓN» o «ENGAÑO» salían más chicos)
    llano = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    bl = f.getbbox(llano); hl = Image.new('L', (bl[2] - bl[0] + 80, bl[3] - bl[1] + 80), 0)
    ImageDraw.Draw(hl).text((40 - bl[0], 40 - bl[1]), llano, font=f, fill=255); hl = hl.crop(hl.getbbox()).height
    k = alto / hl; w = int(m.width * k * ESTRECHO)
    if w > ancho_max: k *= ancho_max / w; w = ancho_max          # no cabe: más chico (nunca aplastado)
    return m.resize((max(1, w), max(1, int(m.height * k))), Image.LANCZOS)


def aspero(m, semilla=1, amp=1.6):
    """Pincel seco como el original: borde ondulado (desplazamiento con ruido suave) y vetas horizontales finas."""
    from scipy import ndimage
    r = np.random.default_rng(semilla); a = np.asarray(m, np.float32) / 255; h, w = a.shape
    def suave(sy, sx):
        n = r.random((max(2, h // sy), max(2, w // sx))).astype(np.float32)
        return np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255 - 0.5
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = ndimage.map_coordinates(a, [yy + suave(6, 6) * 2 * amp, xx + suave(6, 6) * 2 * amp], order=1)
    vetas = np.clip((suave(3, 40) + 0.5 - 0.90) * 6, 0, 1)        # rayas de cerdas (pocas)
    a = a * (1 - 0.6 * vetas)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def dibujar(img, texto, cap, fuente=FUENTE):
    a = np.asarray(img).copy(); a[Y0:, :, 3] = 0; img = Image.fromarray(a)
    capa = Image.new('L', img.size, 0)
    # título en 1 o 2 renglones (corte por palabras lo más parejo posible), centrados en el alto del original
    pal = texto.upper().split()
    if len(pal) == 1 or len(texto) <= 14: r = [texto]
    else:
        cortes = [(' '.join(pal[:i]), ' '.join(pal[i:])) for i in range(1, len(pal))]
        r = list(min(cortes, key=lambda c: abs(len(c[0]) - len(c[1]))))
    ms = [linea(x, ALTO_RENGLON, 900, fuente) for x in r]
    sep = 30; total = sum(m.height for m in ms) + sep * (len(ms) - 1)
    y = TITULO[0] + ((TITULO[1] - TITULO[0]) - total) // 2
    for m in ms:
        capa.paste(m, ((1024 - m.width) // 2, y), m); y += m.height + sep
    mc = linea(cap, ALTO_CAP, 600, fuente); capa.paste(mc, (CAP[0], CAP[1]), mc)
    capa = capa.filter(ImageFilter.MaxFilter(3))                 # (trazo del original, más grueso)
    capa = aspero(capa, semilla=len(texto))
    blanco = Image.new('RGBA', img.size, (255, 255, 255, 255)); img.paste(blanco, (0, 0), capa)
    return img


def guardar_dds(rel, img):
    """Como atlas_es.guardar_dds del Y5: mismo formato y cabecera que el original (texconv para BC*)."""
    sys.path.insert(0, r'C:\Mods\yakuza5\herramientas')
    import atlas_es
    atlas_es.TEX, atlas_es.SAL = U, SAL
    return atlas_es.guardar_dds(rel[:-4], img)


def main():
    os.makedirs(REV, exist_ok=True)
    tt = titulos(); print('títulos', len(tt), tt)
    if '--prueba-fuentes' in sys.argv:
        o = Image.open(os.path.join(U, 'e/texture/chapter_01.dds')).convert('RGBA'); hojas = []
        for fn in ('Bangers-Regular.ttf',):
            im = dibujar(o.copy(), 'THE PRICE OF FREEDOM', 'CHAPTER 1', os.path.join(FUENTES, fn))
            bg = Image.new('RGBA', im.size, (60, 60, 60, 255)); bg.alpha_composite(im); hojas.append(bg.convert('RGB').crop((0, 520, 1024, 1024)).resize((512, 252)))
        bg = Image.new('RGBA', o.size, (60, 60, 60, 255)); bg.alpha_composite(o); hojas.insert(0, bg.convert('RGB').crop((0, 520, 1024, 1024)).resize((512, 252)))
        m = Image.new('RGB', (1024, 252 * 3))
        for i, h in enumerate(hojas): m.paste(h, ((i % 2) * 512, (i // 2) * 252))
        m.save(os.path.join(REV, 'prueba_fuentes.png')); return
    for n in range(1, 14):
        rel = f'e/texture/chapter_{n:02d}.dds'
        o = Image.open(os.path.join(U, rel)).convert('RGBA')
        cap = 'FINAL' if n == 13 else f'CAPÍTULO {n}'
        img = dibujar(o.copy(), tt[n], cap)
        guardar_dds(rel, img)
        bg = Image.new('RGBA', img.size, (60, 60, 60, 255)); bg.alpha_composite(img)
        bg.convert('RGB').resize((512, 512)).save(os.path.join(REV, f'chapter_{n:02d}.png'))
        print(rel, tt[n])


if __name__ == '__main__': main()
