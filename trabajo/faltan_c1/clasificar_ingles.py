# -*- coding: utf-8 -*-
"""(01-11-2026, claude1) Qué texturas de ui/e (v1.0.3 en curso) siguen con TEXTO EN INGLÉS según el OCR (ocr_e.json).
Una línea cuenta como inglés si tiene palabras inglesas y no españolas, o rótulos en Mayúsculas de 2+ palabras sin
tildes. Agrupa por prefijo de nombre para revisar por familias. Escribe ingles_e.json {ruta: [líneas]} + resumen.
  python trabajo/faltan_c1/clasificar_ingles.py"""
import collections, json, os, re
B = os.path.dirname(os.path.abspath(__file__))
EN = set("""the you and of to is it that this with for be have do not what your my we he she they on in at was are i i'm
can will would could should all any some one no yes get got just me him her them our there here who how why when where
which up out into over from by about press button select back next start exit quit continue game new load save data
option options settings menu item items money yen win lose lost won round score total points point time best record
level rank stage clear complete completed mission missions skill skills ability abilities equip equipment use buy sell
shop price free bonus hit miss great good perfect excellent cool nice ready go stop pause retry try again player enemy
attack defense guard health life power speed tutorial how play rules controls control camera move confirm cancel left
right up down hold release push pull open close name chapter part story friend friends call mail map people""".split())
ES = set("""de la el que y en los las un una por con es se su al lo del para como más pero sus le ya o este sí porque esta
son entre cuando muy sin sobre también me hasta hay donde quien desde todo nos durante uno les ni contra otros ese eso
ante ellos esto antes algunos qué unos yo otro otras otra él tanto esa estos mucho nada muchos poco ella estar estas algo
nosotros mi mis tú te ti tu tus pulsa botón seleccionar volver salir continuar partida nueva cargar guardar opciones
ajustes dinero ganar perder ronda puntos tiempo nivel misión habilidad equipo usar comprar vender tienda precio jugar
reglas controles cámara mover confirmar cancelar izquierda derecha arriba abajo mantener soltar abrir cerrar capítulo""".split())
PAL = re.compile(r"[A-Za-z][A-Za-z']*")


def ingles(t):
    if len(t.strip()) < 3 or re.search('[áéíóúñ¿¡ÁÉÍÓÚÑ]', t): return False
    w = PAL.findall(t)
    if not w: return False
    lw = [x.lower() for x in w]
    en = sum(x in EN for x in lw); es = sum(x in ES for x in lw)
    if es >= en and es: return False
    if en: return True
    return len(w) >= 2 and all(x[0].isupper() for x in w) and len(''.join(w)) >= 6


def main():
    o = json.load(open(os.path.join(B, 'ocr_e.json'), encoding='utf-8'))
    res = {}
    for r, ls in o.items():
        malas = [l for l in ls if l[5] >= 0.6 and ingles(l[4])]
        if malas: res[r] = [l[4] for l in malas]
    json.dump(res, open(os.path.join(B, 'ingles_e.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    fam = collections.defaultdict(list)
    for r in res:
        n = os.path.basename(r)[:-4]
        k = re.sub(r'[_\-]?\d+[a-z]?$', '', n); k = '_'.join(k.split('_')[:3])
        fam[k].append(r)
    print('texturas con texto inglés:', len(res), 'de', len(o), '| familias:', len(fam))
    for k, v in sorted(fam.items(), key=lambda x: -len(x[1])):
        print(f'{len(v):4d}  {k:34s} ej: {res[v[0]][:3]}')


if __name__ == '__main__': main()
