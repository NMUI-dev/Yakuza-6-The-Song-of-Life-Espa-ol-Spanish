# -*- coding: utf-8 -*-
"""(01-11-2026, claude1) OCR (RapidOCR, sin conexión) de TODAS las texturas de ui.par/e de la v1.0.3 en curso
(ui_actual = entrega_v1.0.3/archivos/ui.par extraído), no solo las distintas del japonés (trampa del Y5: las que no
tienen versión ja o son iguales se saltaban). Con transparencia se lee sobre negro y sobre blanco. Retoma si se corta.
Salida: trabajo/faltan_c1/ocr_e.json  {ruta relativa a ui_actual: [[x0, y0, x1, y1, texto, confianza], ...]}
  python -u trabajo/faltan_c1/ocr_todas_e.py"""
import os, json, glob
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
B = os.path.dirname(os.path.abspath(__file__)); U = os.path.join(B, 'ui_actual'); SAL = os.path.join(B, 'ocr_e.json')


def leer(ocr, p):
    im = Image.open(p).convert('RGBA')
    if im.width < 32 or im.height < 16: return []
    mejor = []
    for fondo in ((0, 0, 0, 255), (255, 255, 255, 255)):
        b = Image.new('RGBA', im.size, fondo); b.alpha_composite(im)
        r, _ = ocr(np.asarray(b.convert('RGB')))
        lineas = [[int(min(q[0] for q in c)), int(min(q[1] for q in c)), int(max(q[0] for q in c)), int(max(q[1] for q in c)), t, round(float(s), 3)]
                  for c, t, s in (r or [])]
        if sum(len(l[4]) * l[5] for l in lineas) > sum(len(l[4]) * l[5] for l in mejor): mejor = lineas
        if im.getextrema()[3][0] == 255: break
    return mejor


def main():
    rutas = sorted(os.path.relpath(p, U).replace(os.sep, '/') for p in glob.glob(os.path.join(U, 'e', '**', '*.dds'), recursive=True))
    hecho = json.load(open(SAL, encoding='utf-8')) if os.path.exists(SAL) else {}
    ocr = RapidOCR()
    for i, r in enumerate(rutas):
        if r in hecho: continue
        try: hecho[r] = leer(ocr, os.path.join(U, r))
        except Exception as e: hecho[r] = [[0, 0, 0, 0, 'ERROR ' + str(e)[:80], 0]]
        if i % 100 == 0:
            json.dump(hecho, open(SAL, 'w', encoding='utf-8'), ensure_ascii=False); print(i, len(rutas), flush=True)
    json.dump(hecho, open(SAL, 'w', encoding='utf-8'), ensure_ascii=False); print('fin', len(hecho))


if __name__ == '__main__': main()
