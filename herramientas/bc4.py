# -*- coding: utf-8 -*-
"""(Claude Code, 19-10-2026) BC4 (ATI1, un canal) para el atlas de letras del Yakuza 6: decodificar y codificar con numpy."""
import numpy as np

def _paleta(e0, e1):
    e0 = e0.astype(np.float32); e1 = e1.astype(np.float32)
    p = np.zeros(e0.shape + (8,), np.float32)
    p[..., 0] = e0; p[..., 1] = e1
    may = e0 > e1
    for i in range(1, 7):     # e0 > e1: 6 intermedios
        p[..., i + 1] = np.where(may, ((7 - i) * e0 + i * e1) / 7, p[..., i + 1])
    for i in range(1, 5):     # e0 <= e1: 4 intermedios + 0 y 255
        p[..., i + 1] = np.where(may, p[..., i + 1], ((5 - i) * e0 + i * e1) / 5)
    p[..., 6] = np.where(may, p[..., 6], 0); p[..., 7] = np.where(may, p[..., 7], 255)
    return p

def decodificar(datos, ancho, alto):
    bw, bh = ancho // 4, alto // 4
    b = np.frombuffer(datos, np.uint8, bw * bh * 8).reshape(bh, bw, 8)
    pal = _paleta(b[..., 0], b[..., 1])
    bits = np.zeros((bh, bw), np.uint64)
    for i in range(6): bits |= b[..., 2 + i].astype(np.uint64) << np.uint64(8 * i)
    idx = np.stack([(bits >> np.uint64(3 * k)) & np.uint64(7) for k in range(16)], -1).astype(np.int64)
    px = np.take_along_axis(pal, idx, -1)                       # (bh, bw, 16)
    return np.round(px).astype(np.uint8).reshape(bh, bw, 4, 4).transpose(0, 2, 1, 3).reshape(alto, ancho)

def codificar_bloques(img):
    """img (h, w) múltiplo de 4 -> bytes BC4 (modo e0 > e1, 8 niveles)."""
    h, w = img.shape
    t = img.reshape(h // 4, 4, w // 4, 4).transpose(0, 2, 1, 3).reshape(h // 4, w // 4, 16).astype(np.float32)
    mx = t.max(-1); mn = t.min(-1)
    e0 = mx.astype(np.uint8); e1 = mn.astype(np.uint8)
    plano = e0 == e1
    e0 = np.where(plano & (e0 < 255), e0 + 1, e0); e1 = np.where(plano & (e0 == e1), e1 - 1, e1)   # e0 > e1 siempre
    pal = _paleta(e0, e1)
    idx = np.abs(t[..., :, None] - pal[..., None, :]).argmin(-1).astype(np.uint64)
    bits = np.zeros(idx.shape[:2], np.uint64)
    for k in range(16): bits |= idx[..., k] << np.uint64(3 * k)
    out = np.zeros(idx.shape[:2] + (8,), np.uint8); out[..., 0] = e0; out[..., 1] = e1
    for i in range(6): out[..., 2 + i] = ((bits >> np.uint64(8 * i)) & np.uint64(255)).astype(np.uint8)
    return out

def editar_casilla(datos, ancho, y0, y1, x0, x1, funcion):
    """Edita solo los bloques 4x4 que cubren [y0:y1, x0:x1] de un BC4 en memoria (bytearray sin cabecera).
    funcion(region) recibe la región decodificada (alineada a bloques) y la casilla relativa; devuelve la región nueva."""
    bw = ancho // 4; by0, by1, bx0, bx1 = y0 // 4, (y1 + 3) // 4, x0 // 4, (x1 + 3) // 4
    filas = b''.join(bytes(datos[((by0 + j) * bw + bx0) * 8:((by0 + j) * bw + bx1) * 8]) for j in range(by1 - by0))
    reg = decodificar(filas, (bx1 - bx0) * 4, (by1 - by0) * 4).copy()
    reg = funcion(reg, (y0 - by0 * 4, y1 - by0 * 4, x0 - bx0 * 4, x1 - bx0 * 4))
    enc = codificar_bloques(reg)
    for j in range(by1 - by0):
        o = ((by0 + j) * bw + bx0) * 8; datos[o:o + (bx1 - bx0) * 8] = enc[j].tobytes()
