# hojas de contacto de las texturas con inglés (sin capítulos ni letras del karaoke), para decidir a ojo qué se traduce
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
B = os.path.dirname(os.path.abspath(__file__)); U = os.path.join(B, 'ui_actual'); H = os.path.join(B, 'hojas'); os.makedirs(H, exist_ok=True)
r = json.load(open(os.path.join(B, 'ingles_e.json'), encoding='utf-8'))
ks = [k for k in sorted(r) if 'karaoke_song_lyric' not in k and '/chapter_' not in k]
f = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
CW, CH, COL = 330, 200, 4
for h in range(0, len(ks), COL * 5):
    lote = ks[h:h + COL * 5]; m = Image.new('RGB', (CW * COL, CH * ((len(lote) + COL - 1) // COL)), (20, 20, 20)); d = ImageDraw.Draw(m)
    for i, k in enumerate(lote):
        im = Image.open(os.path.join(U, k)).convert('RGBA'); bg = Image.new('RGBA', im.size, (70, 70, 90, 255)); bg.alpha_composite(im)
        t = bg.convert('RGB'); t.thumbnail((CW - 6, CH - 34)); x, y = (i % COL) * CW, (i // COL) * CH
        m.paste(t, (x + 3, y + 3)); d.text((x + 3, y + CH - 30), f'{h + i}: ' + os.path.basename(k)[:40], fill=(255, 255, 0), font=f)
        d.text((x + 3, y + CH - 15), ' | '.join(r[k])[:46], fill=(150, 255, 150), font=f)
    m.save(os.path.join(H, f'hoja_{h // (COL * 5):02d}.png'))
json.dump(ks, open(os.path.join(H, 'indice.json'), 'w', encoding='utf-8'), indent=0)
print(len(ks), 'texturas en', (len(ks) + COL * 5 - 1) // (COL * 5), 'hojas')
