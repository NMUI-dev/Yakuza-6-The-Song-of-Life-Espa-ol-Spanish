# -*- coding: utf-8 -*-
"""(claude1, 21-10-2026, copiado del Y5) Lee con OCR (RapidOCR, sin conexión) el texto inglés de las texturas de ui.par
con texto (trabajo/ui_e_distintas.txt), salvo las ya hechas por programa (trabajo/imagenes_ui/es y su atlas_es.json).
Las texturas con transparencia se leen sobre negro y sobre blanco (se queda la lectura más segura).
Salida: trabajo/imagenes/ocr.json  {ruta: [[x0, y0, x1, y1, texto, confianza], ...]}. Retoma si se corta.
  python -u herramientas/kit_atlas/ocr_imagenes.py
"""
import os, json, time
import numpy as np
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # (claude1, Y6) kit en herramientas/kit_atlas
T = os.path.join(R, 'trabajo')
SAL = os.path.join(T, 'imagenes', 'ocr.json')


def origen(ruta):
    return os.path.join(T, 'extraido', 'ui', ruta)


def hechas_programa():
    """Nombres (sin extensión, minúsculas) que claude2 ya hizo por programa en imagenes_ui."""
    u = os.path.join(T, 'imagenes_ui')
    h = {os.path.splitext(f)[0].lower() for f in os.listdir(os.path.join(u, 'es'))}
    return h | {k.lower() for k in json.load(open(os.path.join(u, 'atlas_es.json'), encoding='utf-8'))}


def lista():
    h = hechas_programa()
    return [l.strip() for l in open(os.path.join(T, 'ui_e_distintas.txt'), encoding='utf-8')
            if l.strip() and os.path.splitext(os.path.basename(l.strip()))[0].lower() not in h]


def leer(ocr, ruta):
    im = Image.open(origen(ruta)).convert('RGBA')
    mejor = []
    for fondo in ((0, 0, 0, 255), (255, 255, 255, 255)):
        b = Image.new('RGBA', im.size, fondo); b.alpha_composite(im)
        r, _ = ocr(np.asarray(b.convert('RGB')))
        lineas = [[int(min(p[0] for p in c)), int(min(p[1] for p in c)), int(max(p[0] for p in c)), int(max(p[1] for p in c)), t, round(float(s), 3)]
                  for c, t, s in (r or [])]
        if sum(len(l[4]) * l[5] for l in lineas) > sum(len(l[4]) * l[5] for l in mejor): mejor = lineas
        if im.getextrema()[3][0] == 255: break           # opaca: con una lectura basta
    return mejor


def main():
    from rapidocr_onnxruntime import RapidOCR
    hecho = json.load(open(SAL, encoding='utf-8')) if os.path.exists(SAL) else {}
    ls = lista(); ocr = RapidOCR(); t0 = time.time()
    for i, ruta in enumerate(ls):
        if ruta in hecho: continue
        try: hecho[ruta] = leer(ocr, ruta)
        except Exception as e: hecho[ruta] = []; print('ERROR', ruta, e)
        if i % 20 == 0:
            json.dump(hecho, open(SAL, 'w', encoding='utf-8'), ensure_ascii=False)
            print(f'{len(hecho)}/{len(ls)}  {time.time() - t0:.0f} s', flush=True)
    json.dump(hecho, open(SAL, 'w', encoding='utf-8'), ensure_ascii=False)
    print('fin', len(hecho))


if __name__ == '__main__': main()
