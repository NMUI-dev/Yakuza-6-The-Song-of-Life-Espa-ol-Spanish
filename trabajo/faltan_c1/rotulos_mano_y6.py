# -*- coding: utf-8 -*-
"""(01-11-2026, claude1) Texturas de ui.par/e del Y6 con LETRA ESTILIZADA que el kit genérico estropeaba: se rehacen a
mano, cada una con una letra parecida a la original y sin pasar del ancho del inglés (el juego enseña solo ese trozo).
  - bc_eb_s_h_chinpira: con la herramienta de rótulos del propio Y6 (herramientas/rotulos.py, la de las demás tarjetas)
  - clan_text_title «RANK UP» (serif negrita, normal + difuminada) -> «SUBES DE RANGO»
  - livechat_02 «SUCCESS / FAILED / START» (relleno de color + borde blanco; START vertical) -> «¡ÉXITO! / FALLO / INICIO»
  - mg_sumouguri_parts3 «Level Up» (normal + brillo) -> «¡Subes de nivel!»
  - mg_gym_menu «Training Menu / Comment» -> «Menú de entrenamiento / Comentario»
  - shopmenu_icon «NEW» y «SALE!» (pegatinas) -> «¡NUEVO!» / «¡OFERTA!»
  - toorina / toorina2: calles del mapa con un solo cuerpo de letra y abreviaturas de mapa si no caben
Salida: trabajo/faltan_c1/es/<ruta>.dds + revision/<nombre>.png
  python trabajo/faltan_c1/rotulos_mano_y6.py"""
import glob, json, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage
sys.path.insert(0, r'C:\Mods\yakuza5\herramientas')
import atlas_es
B = os.path.dirname(os.path.abspath(__file__)); Y = os.path.dirname(os.path.dirname(B))
U = os.path.join(B, 'ui_actual'); SAL = os.path.join(B, 'es'); REV = os.path.join(B, 'revision')
F = 'C:/Windows/Fonts/'
OCR = json.load(open(os.path.join(B, 'ocr_e.json'), encoding='utf-8'))


def caja(nombre, texto):
    """caja OCR [x0, y0, x1, y1] del primer renglón cuyo texto (sin espacios) coincide."""
    k = re.sub(r'\W', '', texto).lower()
    for l in OCR['e/texture/' + nombre + '.dds']:
        if re.sub(r'\W', '', l[4]).lower() == k: return l[:4]
    raise KeyError((nombre, texto))


def borrar(a, c, pad=6):
    """vacía (alfa 0) la tinta de la caja c (texturas con fondo transparente)."""
    x0, y0, x1, y1 = c; H, W = a.shape[:2]
    a[max(0, y0 - pad):min(H, y1 + pad), max(0, x0 - pad):min(W, x1 + pad)] = 0   # color también: si no, asoma bajo el halo


def texto_en_caja(txt, fuente, c, alto_frac=0.82, condensar_min=0.62):
    """máscara L del texto: alto de mayúsculas = alto de la caja * alto_frac; si no cabe en el ancho, se estrecha
    (hasta condensar_min) y luego se achica."""
    x0, y0, x1, y1 = c; w0, h0 = x1 - x0, y1 - y0
    f = ImageFont.truetype(fuente, 200)
    bb = f.getbbox(txt); m = Image.new('L', (bb[2] - bb[0] + 40, bb[3] - bb[1] + 40), 0)
    ImageDraw.Draw(m).text((20 - bb[0], 20 - bb[1]), txt, font=f, fill=255); m = m.crop(m.getbbox())
    hcap = f.getbbox('H')[3] - f.getbbox('H')[1]
    k = h0 * alto_frac / hcap; w, h = m.width * k, m.height * k
    if w > w0:
        s = max(condensar_min, w0 / w); w *= s
        if w > w0: k2 = w0 / w; w, h = w0, h * k2
    return m.resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)


def pegar(a, m, c, color, borde=None, ancho_borde=0, difuso=0, alinear='izq', vertical=False):
    """compone la máscara m en la caja c con relleno color, borde opcional y difuminado opcional."""
    if vertical: m = m.rotate(-90, expand=True)
    x0, y0, x1, y1 = c
    x = x0 if alinear == 'izq' else (x0 + x1 - m.width) // 2
    y = (y0 + y1 - m.height) // 2
    img = Image.fromarray(a)
    capa = Image.new('L', img.size, 0); capa.paste(m, (x, y))
    if borde is not None and ancho_borde:
        b = capa.filter(ImageFilter.MaxFilter(ancho_borde * 2 + 1))
        if difuso: b = b.filter(ImageFilter.GaussianBlur(difuso))
        img.paste(Image.new('RGBA', img.size, borde + (255,)), (0, 0), b)
    elif difuso:
        capa = capa.filter(ImageFilter.GaussianBlur(difuso))
    img.paste(Image.new('RGBA', img.size, color + (255,)), (0, 0), capa)
    return np.asarray(img).copy()


def color_tinta(a, c):
    x0, y0, x1, y1 = c; z = a[y0:y1, x0:x1].reshape(-1, 4)
    z = z[z[:, 3] > 200]
    return tuple(int(v) for v in np.median(z[:, :3], 0)) if len(z) else (255, 255, 255)


def guardar(rel, a, original):
    atlas_es.TEX, atlas_es.SAL = U, SAL
    img = Image.fromarray(a); atlas_es.guardar_dds(rel[:-4], img)
    W, H = original.size; v = Image.new('RGBA', (W, H * 2), (60, 60, 80, 255)); v.alpha_composite(original); v.alpha_composite(img, (0, H))
    v.convert('RGB').save(os.path.join(REV, os.path.basename(rel)[:-4] + '.png'))


def abrir(n):
    o = Image.open(os.path.join(U, 'e/texture/' + n + '.dds')).convert('RGBA'); return o, np.asarray(o).copy()


def chinpira():
    """Tarjeta de banda: letra de pincel blanca (CaveatBrush en mayúsculas, como las demás tarjetas en español) con
    halo oscuro difuso. (rotulos.dibujar del Y6 la dejaba ilegible en esta.)"""
    sys.path.insert(0, B)
    import capitulos_y6 as C
    o, a = abrir('bc_eb_s_h_chinpira')
    c = [l[:4] for l in OCR['e/texture/bc_eb_s_h_chinpira.dds'] if 'HIROSHIMA' in l[4].upper()][0]
    borrar(a, c, pad=70)                                          # (el halo del original llega lejos)
    fuente = os.path.join(Y, 'herramientas', 'fuentes_img', 'CaveatBrush-Regular.ttf')
    m = C.linea('MATONES DE HIROSHIMA', int((c[3] - c[1]) * 0.80), min(c[2] - c[0], a.shape[1] - 60) - 30, fuente).filter(ImageFilter.MaxFilter(3))
    img = Image.fromarray(a); capa = Image.new('L', img.size, 0)
    capa.paste(m, ((c[0] + c[2] - m.width) // 2, (c[1] + c[3] - m.height) // 2))
    halo = capa.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.8))
    img.paste(Image.new('RGBA', img.size, (0, 0, 0, 255)), (0, 0), halo)
    img.paste(Image.new('RGBA', img.size, (255, 255, 255, 255)), (0, 0), C.aspero(capa, 19, amp=1.2))
    guardar('e/texture/bc_eb_s_h_chinpira.dds', np.asarray(img).copy(), o)


def rank_up():
    o, a = abrir('clan_text_title')
    cajas = [l[:4] for l in OCR['e/texture/clan_text_title.dds'] if re.sub(r'\W', '', l[4]).lower() == 'rankup']
    for i, c in enumerate(cajas[:2]):                            # (renglón normal y renglón difuminado, en orden)
        col = color_tinta(a, c); borrar(a, c)
        m = texto_en_caja('SUBES DE RANGO', F + 'georgiab.ttf', c, 0.78)
        a = pegar(a, m, c, col, difuso=2.2 if i == 1 else 0)
    guardar('e/texture/clan_text_title.dds', a, o)


def livechat():
    o, a = abrir('livechat_02')
    for en, es, rel, vert in (('SUCCESS', '¡ÉXITO!', (255, 0, 170), False), ('FAILED', 'FALLO', (20, 20, 160), False),
                              ('START', 'INICIO', (225, 30, 20), True)):
        c = caja('livechat_02', en); col = color_tinta(a, c) if not vert else rel; borrar(a, c, pad=14)
        cc = c if not vert else [c[1], c[0], c[3], c[2]]          # caja girada para medir el texto vertical
        m = texto_en_caja(es, F + 'ariblk.ttf', cc, 0.80)
        a = pegar(a, m, c, rel, borde=(255, 255, 255), ancho_borde=6, difuso=1.0, alinear='centro', vertical=vert)
    guardar('e/texture/livechat_02.dds', a, o)


def level_up():
    o, a = abrir('mg_sumouguri_parts3')
    cajas = [l[:4] for l in OCR['e/texture/mg_sumouguri_parts3.dds'] if re.sub(r'\W', '', l[4]).lower() == 'levelup']
    for i, c in enumerate(cajas):
        col = color_tinta(a, c); borrar(a, c, pad=10)
        m = texto_en_caja('¡Subes de nivel!', F + 'georgiab.ttf', c, 0.70)
        if i == 0: a = pegar(a, m, c, col, alinear='centro'); continue
        # 2.º: letra blanca con brillo suave alrededor (no un borde ancho: salía una mancha)
        img = Image.fromarray(a); capa = Image.new('L', img.size, 0)
        capa.paste(m, ((c[0] + c[2] - m.width) // 2, (c[1] + c[3] - m.height) // 2))
        brillo = capa.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.7))
        img.paste(Image.new('RGBA', img.size, (255, 255, 255, 255)), (0, 0), brillo)
        img.paste(Image.new('RGBA', img.size, (255, 255, 255, 255)), (0, 0), capa); a = np.asarray(img).copy()
    guardar('e/texture/mg_sumouguri_parts3.dds', a, o)


def gym_menu():
    o, a = abrir('mg_gym_menu')
    for en, es in (('Training Menu', 'Menú de entrenamiento'), ('Comment', 'Comentario')):
        c = caja('mg_gym_menu', en); col = color_tinta(a, c); borrar(a, c, pad=2)
        a = pegar(a, texto_en_caja(es, F + 'seguisb.ttf', c, 0.72), c, col)
    guardar('e/texture/mg_gym_menu.dds', a, o)


def tienda():
    """Pegatinas: «NEW» = letra marrón inclinada sobre círculo amarillo; «SALE!» = letra blanca inclinada sobre círculo
    rojo con aro blanco. Se borra la letra rellenando con el fondo (inpaint) y se escribe el español con la misma
    inclinación y color."""
    import cv2
    o, a = abrir('shopmenu_icon')
    for en, es, color, angulo, es_letra in (
            ('NEW', '¡NUEVO!', (95, 50, 20), 18, lambda z: (z[..., 0] < 150) & (z[..., 2] < 90)),
            ('SALE!', '¡OFERTA!', (255, 255, 255), 14, lambda z: z[..., :3].min(-1) > 200)):
        c = caja('shopmenu_icon', en); x0, y0, x1, y1 = c
        zz = a[y0:y1, x0:x1]; m = es_letra(zz.astype(int)) & (zz[..., 3] > 100)
        if en == 'SALE!':                                       # el aro blanco de la pegatina no es letra
            yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
            m &= ((yy - m.shape[0] / 2) / (m.shape[0] / 2)) ** 2 + ((xx - m.shape[1] / 2) / (m.shape[1] / 2)) ** 2 < 0.62
        mk = cv2.dilate(m.astype(np.uint8) * 255, np.ones((3, 3), np.uint8), iterations=2)
        zz[..., :3] = cv2.inpaint(np.ascontiguousarray(zz[..., :3]), mk, 5, cv2.INPAINT_TELEA)
        w, h = x1 - x0, y1 - y0
        mt = texto_en_caja(es, F + 'ariblk.ttf', [0, 0, int(w * 0.92), int(h * 0.42)], 0.95).rotate(angulo, expand=True, resample=Image.BICUBIC)
        img = Image.fromarray(a); capa = Image.new('L', img.size, 0)
        capa.paste(mt, (x0 + (w - mt.width) // 2, y0 + (h - mt.height) // 2))
        img.paste(Image.new('RGBA', img.size, color + (255,)), (0, 0), capa); a = np.asarray(img).copy()
    guardar('e/texture/shopmenu_icon.dds', a, o)


ABREV = [('Entrada de la Avenida', 'Entrada Av.'), ('Entrada de la Calle', 'Entrada C.'), ('Avenida', 'Av.'), ('Bulevar', 'Blvd.'),
         ('Callejón', 'Cjón.'), ('Escalinata del Santuario', 'Escalinata Sant.'), ('Callejón del Santuario', 'Cjón. Sant.'),
         ('Calle Torre Millennium', 'C. Torre Millennium'), ('Distrito Comercial', 'Distr. Comercial')]


def mapa(nombre, trad):
    o, a = abrir(nombre); orig = a.copy()
    ls = [l for l in OCR['e/texture/' + nombre + '.dds'] if l[5] > 0.5]
    nk = lambda t: re.sub(r'[\W_]', '', t).lower()
    altos = sorted(l[3] - l[1] for l in ls); h = altos[len(altos) // 2]
    f = ImageFont.truetype(F + 'seguisb.ttf', 100); hcap = f.getbbox('H')[3] - f.getbbox('H')[1]
    tam = 100 * h * 0.62 / hcap
    for l in ls:
        es = trad.get(nk(l[4]))
        if not es: continue
        c = l[:4]; col = color_tinta(orig, c); borrar(a, c, pad=2)
        ancho = c[2] - c[0]
        fu = ImageFont.truetype(F + 'seguisb.ttf', int(round(tam)))
        t = es
        for viejo, nuevo in ABREV:                                   # abreviaturas solo si hacen falta
            if fu.getlength(t) <= ancho * 1.35: break
            t = t.replace(viejo, nuevo)
        bb = fu.getbbox(t); m = Image.new('L', (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), 0)
        ImageDraw.Draw(m).text((2 - bb[0], 2 - bb[1]), t, font=fu, fill=255)
        if m.width > ancho: m = m.resize((ancho, m.height), Image.LANCZOS)    # estrechar lo que falte
        img = Image.fromarray(a); capa = Image.new('L', img.size, 0)
        capa.paste(m, (c[0], c[3] - m.height + 1)); img.paste(Image.new('RGBA', img.size, col + (255,)), (0, 0), capa)
        a = np.asarray(img).copy()
    guardar('e/texture/' + nombre + '.dds', a, o)


def main():
    os.makedirs(REV, exist_ok=True)
    sys.path.insert(0, B)
    import imagenes_y6 as I
    g = I.juego(); nk = lambda t: re.sub(r'[\W_]', '', t).lower()
    trad = {nk(k): v for k, v in g.items()}; trad.update({nk(k): v for k, v in I.A_MANO.items()})
    for fn in (chinpira, rank_up, livechat, level_up, gym_menu, tienda): fn(); print('ok', fn.__name__)
    for n in ('toorina', 'toorina2'): mapa(n, trad); print('ok', n)


if __name__ == '__main__': main()
