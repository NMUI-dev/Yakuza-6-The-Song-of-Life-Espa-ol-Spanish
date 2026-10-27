# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) Letras españolas para la fuente del Yakuza 6 (font.par: <idioma>/gothic.dds + gothic.bin).

La fuente no trae á é í ó ú ü ñ ¿ ¡ (ni mayúsculas). Se montan con piezas de la PROPIA fuente (misma letra del juego):
letra base + tilde «´», diéresis «¨» o «~»; ¿ y ¡ son ? y ! girados. Cada una se dibuja en la casilla de un kanji que el
texto inglés nunca usa (KANJI_LIBRES) y se recalculan sus 6 medidas (en píxeles de la casilla de 39x39:
[izquierda, ancho de tinta, derecha, arriba, alto, abajo]). La estructura del .bin no cambia (mismos códigos, mismo orden).
La traducción escribe esos kanji en lugar de las letras (MAPA: letra -> kanji).

gothic.bin: cabecera 0x30, registros de 32 bytes: código (bytes UTF-8 como entero), variante (0/1: las dos letras del
juego), 4 float (y0/4096, x0/8192, y1/4096, x1/8192) y 8 bytes de medidas. gothic.dds: BC4 8192x4096 (herramientas/bc4.py).
"""
import os, struct, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc4

LETRAS = 'áéíóúüñÁÉÍÓÚÜÑ¿¡'
UMBRAL = 100           # tinta (igual que las medidas originales)

def leer_bin(ruta):
    d = bytearray(open(ruta, 'rb').read()); n = struct.unpack_from('<I', d, 0x10)[0]
    regs = []
    for i in range(n):
        o = 0x30 + i * 32; code, var = struct.unpack_from('<II', d, o); f = struct.unpack_from('<4f', d, o + 8)
        regs.append({'i': i, 'o': o, 'code': code, 'var': var, 'y0': round(f[0] * 4096), 'x0': round(f[1] * 8192),
                     'y1': round(f[2] * 4096), 'x1': round(f[3] * 8192), 'med': list(d[o + 24:o + 32])})
    return d, regs

def char_de(code):
    b = code.to_bytes((code.bit_length() + 7) // 8 or 1, 'big')
    try: return b.decode('utf-8')
    except UnicodeDecodeError: return None

def code_de(ch): return int.from_bytes(ch.encode('utf-8'), 'big')

def kanji_libres(regs, n, evitar=()):
    """Los ÚLTIMOS kanji del bloque CJK unificado (U+4E00-U+9FFF) que tiene la fuente y que NO salen en ningún texto del
    juego (evitar: p. ej. 龍 sale 1.522 veces en las tablas timeline)."""
    cj = sorted({r['code'] for r in regs if '一' <= (char_de(r['code']) or ' ') <= '鿿'})
    cj = [char_de(c) for c in cj if char_de(c) not in evitar]
    return cj[-n:]

def medidas(cel):
    ys, xs = np.where(cel > UMBRAL)
    if len(xs) == 0: return [0, 0, 39, 0, 0, 39, 0, 0]
    l, r, t, b = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    return [l, r - l + 1, 39 - (r + 1), t, b - t + 1, 39 - (b + 1), 0, 0]

def tinta(cel):
    ys, xs = np.where(cel > 10)
    return cel[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def escalar(img, sy, sx=1.0):
    from PIL import Image
    h, w = img.shape
    return np.asarray(Image.fromarray(img).resize((max(1, round(w * sx)), max(1, round(h * sy))), Image.LANCZOS))

def pegar(cel, pieza, y, x):
    h, w = pieza.shape; y = max(0, y); x = max(0, min(39 - w, x))
    zona = cel[y:y + h, x:x + w]; p = pieza[:zona.shape[0], :zona.shape[1]]
    cel[y:y + p.shape[0], x:x + p.shape[1]] = np.maximum(zona, p)

def sin_punto(cel):
    """i sin el punto: borra lo que esté por encima del primer hueco vacío desde abajo."""
    c = cel.copy(); filas = (c > UMBRAL).any(1); ys = np.where(filas)[0]
    abajo = ys.max(); y = abajo
    while y > 0 and filas[y]: y -= 1                # sube por el palo
    c[:y + 1] = 0
    return c

def montar(atlas, regs):
    porc = {(r['code'], r['var']): r for r in regs}
    def cel(ch, var):
        r = porc[(code_de(ch), var)]; return atlas[r['y0']:r['y1'], r['x0']:r['x1']].astype(np.uint8).copy()
    out = {}
    for var in (0, 1):
        acento = tinta(cel('´', var)); dier = tinta(cel('¨', var)); tilde = tinta(cel('~', var))
        if tilde.shape[0] > 6: tilde = escalar(tilde, 6 / tilde.shape[0], 0.85)
        for ch in LETRAS:
            if ch in '¿¡':
                base = cel('?' if ch == '¿' else '!', var)[::-1, ::-1].copy()
                t = tinta(base); m = medidas(cel('?' if ch == '¿' else '!', var))
                c = np.zeros((39, 39), np.uint8); top = 39 - t.shape[0] - 1      # baja por debajo de la línea, como en español
                pegar(c, t, top, m[0]); out[(ch, var)] = c; continue
            plano = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n',
                     'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U', 'Ñ': 'N'}[ch]
            pieza = dier if ch in 'üÜ' else tilde if ch in 'ñÑ' else acento
            b = cel(plano, var)
            if plano == 'i': b = sin_punto(b)
            mb = medidas(b); c = np.zeros((39, 39), np.uint8)
            if ch.isupper():
                # mayúscula: se achata para dejar sitio a la tilde dentro de la casilla (la línea base no se mueve)
                t = tinta(b); hueco = pieza.shape[0] + 2; alto = (mb[3] + mb[4]) - hueco - 1
                t2 = escalar(t, alto / t.shape[0]); pegar(c, t2, (mb[3] + mb[4]) - t2.shape[0], mb[0])
                ytilde = 0
            else:
                c = b.copy(); ytilde = max(0, mb[3] - pieza.shape[0] - 2)
            mc = medidas(c); xc = mc[0] + mc[1] // 2 - pieza.shape[1] // 2
            pegar(c, pieza, ytilde, xc)
            out[(ch, var)] = c
    return out

def aplicar(dds_in, bin_in, dds_out, bin_out, informe=None, evitar=()):
    raw = open(dds_in, 'rb').read(); cab = raw[:128]
    atlas = bc4.decodificar(raw[128:], 8192, 4096).copy()
    d, regs = leer_bin(bin_in)
    libres = kanji_libres(regs, len(LETRAS), evitar); mapa = dict(zip(LETRAS, libres))
    glifos = montar(atlas, regs)
    porc = {(r['code'], r['var']): r for r in regs}
    tocadas = set()
    for (ch, var), c in glifos.items():
        r = porc[(code_de(mapa[ch]), var)]
        atlas[r['y0']:r['y1'], r['x0']:r['x1']] = c
        d[r['o'] + 24:r['o'] + 32] = bytes(medidas(c))
        tocadas.add((r['y0'] // 4, r['y1'] // 4 + 1, r['x0'] // 4, r['x1'] // 4 + 1))
    # recodificar SOLO los bloques 4x4 de las casillas tocadas (el resto del atlas queda byte a byte igual)
    blq = bytearray(raw[128:]); bw = 8192 // 4
    for by0, by1, bx0, bx1 in tocadas:
        enc = bc4.codificar_bloques(atlas[by0 * 4:by1 * 4, bx0 * 4:bx1 * 4])
        for j in range(by1 - by0):
            o = ((by0 + j) * bw + bx0) * 8; blq[o:o + (bx1 - bx0) * 8] = enc[j].tobytes()
    open(dds_out, 'wb').write(cab + bytes(blq)); open(bin_out, 'wb').write(bytes(d))
    if informe is not None: informe.update(mapa)
    return mapa, glifos

if __name__ == '__main__':
    # uso: letras_es.py <carpeta fuente e> <salida> <carpetas/archivos de texto del juego para descartar kanji usados...>
    e = sys.argv[1]; s = sys.argv[2]; os.makedirs(s, exist_ok=True)
    usados = set()
    for ruta in sys.argv[3:]:
        arch = [os.path.join(ruta, n) for n in os.listdir(ruta)] if os.path.isdir(ruta) else [ruta]
        for a in arch:
            if a.endswith(('.json', '.csv')): usados |= set(open(a, encoding='utf-8', errors='replace').read())
    mapa, _ = aplicar(os.path.join(e, 'gothic.dds'), os.path.join(e, 'gothic.bin'), os.path.join(s, 'gothic.dds'),
                      os.path.join(s, 'gothic.bin'), evitar=usados)
    import json
    json.dump(mapa, open(os.path.join(s, 'mapa_letras.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(mapa)


def insertar_codigos(dds_in, bin_in, dds_out, bin_out, evitar=()):
    """(19-10, tras ver que el texto se escribe en UTF-8 real) Variante limpia: AÑADE registros nuevos con los códigos
    reales (á = 0xC3A1...) en orden, dibujados en casillas de kanji que el juego no usa. El número de registros (cabecera
    0x10) sube y el archivo mantiene su tamaño (hay 138.688 bytes de ceros al final). Así el mismo texto en español sirve
    para las dos letras del juego (yakuza.dds de menús/subtítulos y gothic)."""
    raw = open(dds_in, 'rb').read(); cab = raw[:128]
    atlas = bc4.decodificar(raw[128:], 8192, 4096).copy()
    d, regs = leer_bin(bin_in); n = len(regs)
    libres = kanji_libres(regs, len(LETRAS), evitar); casilla = dict(zip(LETRAS, libres))
    glifos = montar(atlas, regs)
    porc = {(r['code'], r['var']): r for r in regs}
    nuevos = []; tocadas = set()
    for (ch, var), c in glifos.items():
        r = porc[(code_de(casilla[ch]), var)]
        atlas[r['y0']:r['y1'], r['x0']:r['x1']] = c
        tocadas.add((r['y0'] // 4, r['y1'] // 4 + 1, r['x0'] // 4, r['x1'] // 4 + 1))
        reg = bytearray(d[r['o']:r['o'] + 32])
        struct.pack_into('<II', reg, 0, code_de(ch), var); reg[24:32] = bytes(medidas(c))
        nuevos.append((code_de(ch), var, bytes(reg)))
    todos = [(r['code'], r['var'], bytes(d[r['o']:r['o'] + 32])) for r in regs] + nuevos
    todos.sort(key=lambda t: (t[0], t[1]))
    fin = 0x30 + len(todos) * 32
    assert all(b == 0 for b in d[0x30 + n * 32:fin]), 'no hay sitio libre al final del .bin'
    for i, (_, _, b) in enumerate(todos): d[0x30 + i * 32:0x30 + (i + 1) * 32] = b
    struct.pack_into('<I', d, 0x10, len(todos))
    blq = bytearray(raw[128:]); bw = 8192 // 4
    for by0, by1, bx0, bx1 in tocadas:
        enc = bc4.codificar_bloques(atlas[by0 * 4:by1 * 4, bx0 * 4:bx1 * 4])
        for j in range(by1 - by0):
            o = ((by0 + j) * bw + bx0) * 8; blq[o:o + (bx1 - bx0) * 8] = enc[j].tobytes()
    open(dds_out, 'wb').write(cab + bytes(blq)); open(bin_out, 'wb').write(bytes(d))
    return casilla
