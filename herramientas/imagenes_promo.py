# (Claude, 25-10-2026) 4 imágenes de presentación del mod (1920x1080) para Nexus, con capturas REALES del juego traducido.
# Mismo estilo que C:\Mods\yakuza5\herramientas\imagenes_promo.py. Uso: python imagenes_promo.py  -> C:\Mods\yakuza6\promo\
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = r"C:\Mods\yakuza6"
CAP = os.path.join(BASE, r"trabajo\capturas")
OUT = os.path.join(BASE, "promo"); os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080
ROJO = (196, 22, 28)
F = r"C:\Windows\Fonts"
def fuente(n, t): return ImageFont.truetype(os.path.join(F, n), t)

def fondo(n):
    im = Image.open(os.path.join(CAP, n)).convert("RGB")
    return im.resize((W, H), Image.LANCZOS) if im.size != (W, H) else im

def texto_sombra(d, xy, s, f, color=(255, 255, 255), sombra=6, anchor="la"):
    x, y = xy
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            d.text((x + dx, y + dy + sombra // 2), s, font=f, fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), s, font=f, fill=color, anchor=anchor)

def franja(im, titulo, sub, arriba=True):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    alto = 190
    y0 = 0 if arriba else H - alto
    d.rectangle([0, y0, W, y0 + alto], fill=(0, 0, 0, 240))
    d.rectangle([0, y0 + alto - 8 if arriba else y0, W, y0 + alto if arriba else y0 + 8], fill=ROJO + (255,))
    im = Image.alpha_composite(im.convert("RGBA"), capa)
    d = ImageDraw.Draw(im)
    texto_sombra(d, (70, y0 + 28), titulo, fuente("impact.ttf", 88))
    d.text((74, y0 + 128), sub, font=fuente("segoeuib.ttf", 38), fill=(235, 235, 235))
    return im

def sello(im, s="MOD GRATIS · PC STEAM", y=None):
    d = ImageDraw.Draw(im); f = fuente("ariblk.ttf", 30)
    w = d.textlength(s, font=f) + 50
    y = H - 90 if y is None else y
    d.rectangle([W - w - 40, y, W - 40, y + 54], fill=ROJO)
    d.text((W - 40 - w / 2, y + 27), s, font=f, fill="white", anchor="mm")
    return im

def guardar(im, n):
    p = os.path.join(OUT, n); im.convert("RGB").save(p, quality=88, optimize=True); print(p, os.path.getsize(p) // 1024, "KB")

# 1) PORTADA: menú de título en español (Steam, 1920x1080); el rótulo va debajo del menú, a la izquierda
im = fondo("steam_v10_b.png")
capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
d.rectangle([0, 540, 1060, 905], fill=(0, 0, 0, 185))
im = Image.alpha_composite(im.convert("RGBA"), capa); d = ImageDraw.Draw(im)
texto_sombra(d, (70, 548), "YAKUZA 6", fuente("impact.ttf", 150))
texto_sombra(d, (76, 712), "THE SONG OF LIFE", fuente("impact.ttf", 62), color=(230, 230, 230))
d.rectangle([70, 800, 1000, 885], fill=ROJO)
d.text((535, 842), "TRADUCCIÓN AL ESPAÑOL", font=fuente("ariblk.ttf", 52), fill="white", anchor="mm")
guardar(sello(im, "MOD GRATIS · PC STEAM · ESPAÑOL NEUTRO", y=40), "1_portada.jpg")

# 2) DIÁLOGOS: escena con subtítulo
im = franja(fondo("g3.png"), "HISTORIA Y DIÁLOGOS EN ESPAÑOL", "Más de 58.000 textos: escenas, subtítulos, misiones, minijuegos y karaoke")
guardar(sello(im), "2_dialogos.jpg")

# 3) MENÚS: elección de dificultad (franja abajo: arriba tapa «Elige una dificultad»)
im = franja(fondo("g7.png"), "MENÚS Y OPCIONES EN ESPAÑOL", "Todo el juego con tildes, ñ, ¿ y ¡", arriba=False)
guardar(sello(im, y=230), "3_menus.jpg")

# 4) IMÁGENES TRADUCIDAS: antes / después (rótulos del menú de título, textura title_press_any_button)
def blanco_sobre(pieza):
    """la hoja de comparación trae fondo verde: el brillo mínimo de cada píxel da la opacidad del texto"""
    px = pieza.convert("RGB")
    mn = Image.fromarray(np.asarray(px).min(axis=2)).point(lambda v: max(0, min(255, (v - 45) * 255 // 200)))
    out = Image.new("RGBA", px.size, (255, 255, 255, 0)); out.putalpha(mn)
    return out
hoja = Image.open(os.path.join(BASE, r"trabajo\imagenes_ui\es\title_press_any_button.png")).convert("RGB")
en, es = blanco_sobre(hoja.crop((0, 0, 500, 390))), blanco_sobre(hoja.crop((512, 0, 1012, 390)))
im = Image.new("RGB", (W, H), (14, 14, 16))
esc = 1.45
for i, (pieza, etiqueta, color) in enumerate([(en, "ORIGINAL (INGLÉS)", (90, 90, 95)), (es, "CON EL MOD", ROJO)]):
    p = pieza.resize((int(pieza.width * esc), int(pieza.height * esc)), Image.LANCZOS)
    x = 130 + i * 960; y = 380
    d = ImageDraw.Draw(im)
    d.rectangle([x - 20, y - 20, x + p.width + 20, y + p.height + 10], fill=(28, 28, 32))
    im.paste(p, (x, y), p)
    d.rectangle([x - 20, y - 90, x + p.width + 20, y - 30], fill=color)
    d.text((x + p.width / 2, y - 60), etiqueta, font=fuente("ariblk.ttf", 34), fill="white", anchor="mm")
d = ImageDraw.Draw(im)
cx, cy = W / 2 - 5, 380 + 390 * esc / 2
d.polygon([(cx - 45, cy - 18), (cx + 5, cy - 18), (cx + 5, cy - 45), (cx + 50, cy), (cx + 5, cy + 45), (cx + 5, cy + 18), (cx - 45, cy + 18)], fill=ROJO)
texto_sombra(d, (W / 2, 70), "TAMBIÉN LAS IMÁGENES CON TEXTO", fuente("impact.ttf", 92), anchor="ma")
d.text((W / 2, 185), "«Press any button», menús dibujados, carteles, minijuegos y karaoke",
       font=fuente("segoeuib.ttf", 38), fill=(220, 220, 220), anchor="ma")
guardar(sello(im), "4_imagenes.jpg")
