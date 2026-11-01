# -*- coding: utf-8 -*-
"""(01-11-2026, claude1) Texturas de ui.par/e del Y6 que seguían en inglés (revisadas a ojo en hojas/), redibujadas con
el kit de páginas del Y5 (yakuza5/herramientas/paginas_es.py: borra la tinta del renglón y escribe el español con la
altura y el color medidos). Traducción: la del juego si el texto existe en los lotes del Y6 (p. ej. las calles del mapa),
si no, la de A_MANO. Lo que no está en ninguna de las dos se deja como está.
Salida: trabajo/faltan_c1/es/<ruta>.dds + revision/<nombre>.png (arriba original, abajo español)
  python trabajo/faltan_c1/imagenes_y6.py [filtro]"""
import glob, json, os, re, sys
from PIL import Image
sys.path.insert(0, r'C:\Mods\yakuza5\herramientas')
import paginas_es as P, atlas_es
from imagenes_lotes import validas, arreglar
B = os.path.dirname(os.path.abspath(__file__)); Y = os.path.dirname(os.path.dirname(B))
U = os.path.join(B, 'ui_actual'); SAL = os.path.join(B, 'es'); REV = os.path.join(B, 'revision')
OBJ = ['bc_eb_s_h_chinpira', 'clan_text_title', 'clan_win', 'livechat_02', 'mg_darts_cutin_text', 'mg_gym_start', 'mg_gym_menu',
       'mg_snack_text2_en', 'mg_snack_text_en', 'mg_sumoguri_parts3', 'shopmenu_icon', 'taiken_pause_mission', 'toorina', 'toorina2']
A_MANO = {   # inglés (OCR arreglado, en mayúsculas o como salga) -> español
    'HIROSHIMA THUGS': 'MATONES DE HIROSHIMA', 'RANK UP': 'SUBES DE RANGO', 'WIN': 'VICTORIA', 'LOSE': 'DERROTA',
    'SUCCESS': '¡ÉXITO!', 'FAILED': 'FALLO', 'START': 'INICIO', 'FINAL ROUND': 'RONDA FINAL', 'PLAYER CHANGE': 'CAMBIO DE JUGADOR',
    'REMOVE DARTS': 'RETIRA LOS DARDOS', 'TIME UP': '¡TIEMPO!', 'Training Menu': 'Menú de entrenamiento', 'Comment': 'Comentario',
    'Friendship UP': 'Amistad ARRIBA', 'Bar Patrons': 'Clientes', 'Gauge': 'Medidor', 'Topic': 'Tema', 'Details': 'Detalles',
    'Friendship': 'Amistad', 'Customer Rank': 'Rango del cliente', 'Relationships': 'Relaciones', 'Liveliness': 'Vitalidad',
    'BAD CHOICE!': '¡MALA ELECCIÓN!', 'GOOD CHOICE': 'BUENA ELECCIÓN', 'TIME': 'TIEMPO', 'EXCELLENT': 'EXCELENTE',
    'Level Up': '¡Subes de nivel!', 'NEW': '¡NUEVO!', 'SALE!': '¡OFERTA!', 'MAIN MISSION': 'MISIÓN PRINCIPAL',
    'SUB MISSION': 'MISIÓN SECUNDARIA', 'INSTANT MISSION': 'MISIÓN INSTANTÁNEA', 'Little Asia': 'Pequeña Asia',
    'W National Route 2': 'Ruta Nacional 2 Oeste', 'E National Route 2': 'Ruta Nacional 2 Este', 'W Shishido St.': 'Calle Shishido Oeste',
    'E Shishido St.': 'Calle Shishido Este', 'N Hana-no-kubo': 'Hana-no-kubo Norte', 'Senryo Ave. Entrance': 'Entrada de la Avenida Senryo'}
norm = lambda t: re.sub(r'\s+', ' ', t or '').strip()


def juego():
    """inglés -> español de los lotes del Y6 (para que las imágenes digan lo mismo que el texto del juego)."""
    d = {}
    for f in sorted(glob.glob(os.path.join(Y, 'trabajo', 'lotes', 'lote_???.json'))):
        try: es = json.load(open(f[:-5] + '_es.json', encoding='utf-8'))
        except FileNotFoundError: continue
        for x in json.load(open(f, encoding='utf-8')):
            t = es.get(str(x['id']))
            if isinstance(t, str) and t.strip(): d.setdefault(norm(x['en']), t.strip())
    return d


def main(filtro=''):
    ocr = json.load(open(os.path.join(B, 'ocr_e.json'), encoding='utf-8'))
    g = juego()
    P.origen = lambda r: os.path.join(U, r)
    atlas_es.TEX, atlas_es.SAL = U, SAL
    os.makedirs(REV, exist_ok=True)
    rutas = [r for r in ocr if os.path.basename(r)[:-4] in OBJ and filtro in r]
    informe = []
    import numpy as np
    # (el OCR pega palabras: «FINALROUND», «WNationalRoute2») -> se compara sin espacios ni signos
    nk = lambda t: re.sub(r'[\W_]', '', t or '').lower()
    dic = {nk(k): v for k, v in g.items()}; dic.update({nk(k): v for k, v in A_MANO.items()})
    for r in rutas:
        a = np.asarray(Image.open(P.origen(r)).convert('RGBA')); H, W = a.shape[:2]
        # RENGLÓN A RENGLÓN (las listas de calles se juntaban en un solo bloque y no casaban)
        hacer = []
        for l in validas(ocr[r]):
            en = arreglar(l[4]); t = dic.get(nk(en))
            informe.append(f"{os.path.basename(r):26s} {en!r:34} -> {t if t and nk(t) != nk(en) else '(igual)'!r}")
            if t and nk(t) != nk(en): hacer.append((l, t))
        if not hacer: informe.append(f'{r}: sin cambios'); continue
        limpia = P.borrar(a, [l[:4] for l, _ in hacer]); img = Image.fromarray(limpia); av = []
        for l, t in hacer:
            m, _ = P.mascara_tinta(a, l[:4])
            b = {'lineas': [l], 'caja': list(l[:4]), 'texto': l[4], 'color': P.color_tinta(a, m), 'estricto': True, 'etiqueta': True}
            debajo = [o[1] for o, _ in hacer if o[1] > l[3] and o[0] < l[2] and o[2] > l[0]]
            x = P.escribir(img, a, b, t, (min(debajo) - 2) if debajo else H - 2, W)
            if x: av.append(x)
        atlas_es.guardar_dds(r[:-4], img)
        o = Image.open(P.origen(r)).convert('RGBA'); W, H = o.size
        v = Image.new('RGBA', (W, H * 2), (60, 60, 80, 255)); v.alpha_composite(o); v.alpha_composite(img, (0, H))
        v.convert('RGB').save(os.path.join(REV, os.path.basename(r)[:-4] + '.png'))
        informe += [f'{r}: {x}' for x in av]
    open(os.path.join(B, 'imagenes_y6_informe.txt'), 'w', encoding='utf-8').write('\n'.join(informe))
    print('\n'.join(informe))


if __name__ == '__main__': main(next((a for a in sys.argv[1:] if not a.startswith('--')), ''))
