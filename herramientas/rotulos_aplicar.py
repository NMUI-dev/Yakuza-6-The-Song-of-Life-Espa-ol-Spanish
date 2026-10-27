# -*- coding: utf-8 -*-
"""(Claude Code, 20-10-2026) Genera los rótulos de pincel en español (trabajo/imagenes_ui/rotulos_es.json, líneas
separadas por « / ») -> trabajo/imagenes_ui/es/<nombre>.dds + hoja de revisión rotulos_revision_NN.png.
Si el español es idéntico al inglés (nombres) no se toca la textura."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('ROT_FUENTE', 'CaveatBrush-Regular.ttf'); os.environ.setdefault('ROT_ESTRECHO', '0.95'); os.environ.setdefault('ROT_GROSOR', '5')
import rotulos, atlas_es
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); I = os.path.join(R, 'trabajo', 'imagenes_ui')
en = json.load(open(os.path.join(I, 'rotulos_en.json'), encoding='utf-8'))
es = json.load(open(os.path.join(I, 'rotulos_es.json'), encoding='utf-8'))
hechos = []; fallos = []
for k in (sys.argv[1:] or list(en)):
    if es.get(k, en[k]).strip() == en[k].strip(): continue
    o = Image.open(os.path.join(atlas_es.TEX, k + '.dds')).convert('RGBA')
    try: n = rotulos.dibujar(o, [x.strip() for x in es[k].split(' / ')], semilla=len(k))
    except ValueError as e: fallos.append((k, str(e))); continue
    atlas_es.guardar_dds(k, n); hechos.append((k, o, n))
print('hechos', len(hechos), 'fallos', fallos)
for p in range(0, len(hechos), 12):
    hoja = Image.new('RGB', (2 * 512, 128 * 12), (60, 60, 60))
    for i, (k, o, n) in enumerate(hechos[p:p + 12]):
        for j, im in enumerate((o, n)):
            b = Image.new('RGBA', im.size, (90, 90, 90, 255)); b.alpha_composite(im); b = b.convert('RGB'); b.thumbnail((512, 128))
            hoja.paste(b, (j * 512, i * 128))
    hoja.save(os.path.join(I, f'rotulos_revision_{p // 12:02d}.png'))
