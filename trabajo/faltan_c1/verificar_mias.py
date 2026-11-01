# OCR de MIS texturas nuevas (es/) para ver si queda algo en inglés
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ocr_todas_e import leer
from clasificar_ingles import ingles
from rapidocr_onnxruntime import RapidOCR
B = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(B, 'es')
ocr = RapidOCR()
for dp, _, fs in os.walk(E):
    for f in sorted(fs):
        p = os.path.join(dp, f); ls = leer(ocr, p)
        malas = [l[4] for l in ls if l[5] >= 0.6 and ingles(l[4])]
        print(f'{f:28s}', 'EN INGLÉS: ' + ' | '.join(malas) if malas else 'ok', '| leído:', ' / '.join(l[4] for l in ls)[:110])
