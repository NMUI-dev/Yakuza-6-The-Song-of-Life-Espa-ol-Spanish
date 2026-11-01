# -*- coding: utf-8 -*-
"""(01-11-2026, claude2) Correcciones a mano sobre textos.csv de la herramienta (después de «extraer» y antes de
«aplicar»): frases que no cabían en su hueco más pequeño (mismo sentido con menos palabras, regla del usuario) y lo que
se teclea en el Chat en vivo (que no quede cortado a medias).
  python correcciones_csv.py <textos.csv>"""
import csv, sys
sys.stdout.reconfigure(encoding='utf-8')
POR_INGLES = {
    "(I'm hungry. Maybe I should go\ngrab something at a restaurant.)": '(Tengo hambre. Quizás debería ir\na comer a un restaurante.)',
    "(So he wants sushi, huh...\nI guess I should buy some when I have time.)": '(Así que quiere sushi...\nCompraré un poco cuando pueda.)',
    "(I'll need to keep finding players for the Warriors\nif I want to help the team really succeed.)": '(Tengo que buscar más jugadores\npara que los Warriors triunfen.)',
    "(No, Haruto's too young to stand up\non his own, let alone talk on the phone.)": '(No, Haruto es muy chico para pararse\nsolo, y menos hablar por teléfono.)',
    "(Is this the father of the kid Taichi hurt?\nI'm pretty sure his name is Ishigaki.)": '(¿Será el padre del chico al que Taichi hirió?\nCreo que se llama Ishigaki.)',
    "(I need to make sure they have enough\nto cover their son's hospital bills.)": '(Debo asegurarme de que tengan lo\njusto para el hospital de su hijo.)',
    "(More importantly, I can't let\nTaichi end up in debt!)": '(¡Y sobre todo, no puedo dejar\nque Taichi acabe endeudado!)',
    "(This thing is pretty impressive.\nIt's hard to believe it's just a phone app.)": '(Esto es impresionante. Cuesta\ncreer que sea una app de celular.)',
    "(Hiji's totally in control of the conversation.\nShe's really a special piece of technology.)": '(Hiji controla toda la conversación.\nEs una tecnología muy especial.)',
    "That was perfect, Kiryu-san!\nYou must be in excellent shape!": '¡Eso fue perfecto, Kiryu-san!\n¡Estás en excelente forma!',
    "Things really didn't go so well, huh?\nRelax, recharge, and try harder next time!": 'Las cosas no salieron muy bien, ¿eh?\n¡Descansa, recupérate y esfuérzate más!',
    "(Bars... You walk in to share a drink and a laugh,\nbut sometimes you walk out with a story...)": '(Los bares... Entras a compartir un trago\ny unas risas, y sales con una historia...)',
    "(Stories that turn strangers into family.\nI like this little family. I'll never forget them.)": '(Historias que hacen familia a extraños.\nMe gusta esta familia. No la olvidaré.)',
}
CHAT = {'IM IN LOVE': 'ME ENAMORE', 'STRIP?': 'TE DESNUDAS?', 'PAY ATTENTION': 'PRESTA ATENCION', 'GOOD?': 'TE GUSTA?',
    'STRIP FOR US': 'DESNUDATE YA', 'ME TOO': 'YO TAMBIEN', 'ALONE TIME': 'A SOLAS', 'HOW EXACTLY?': 'COMO EXACTO?',
    'CANT WAIT': 'QUE GANAS', 'YOU MEAN IT?': 'EN SERIO?', 'TRY SMILING': 'SONRIE', 'NEVERMIND': 'OLVIDALO', 'NICE': 'GENIAL',
    'LEGS PLEASE': 'PIERNAS YA', 'A BIG FAT ONE': 'UNA ENORME', 'JUST FOR US': 'SOLO NUESTRO', 'YOU LOOK HOT': 'TE VES SEXY',
    'OKAY': 'BIEN', 'IVE NOTICED': 'YA ME FIJE', 'MARRY ME': 'CASATE CONMIGO', 'I WONDER...': 'ME PREGUNTO...'}
# red de seguridad: si una fila quedó sin español pero el traductor de la v1.0.3 la tradujo, se pone esa
import json, re
D = 'C:/Mods/yakuza6/trabajo/faltan_c2'
_u = {u['id']: u for u in json.load(open(f'{D}/unidades.json', encoding='utf-8'))}
_t = json.load(open(f'{D}/traducido.json', encoding='utf-8')); _t.update(json.load(open(f'{D}/correcciones.json', encoding='utf-8')))
V103 = {}
for i, es in _t.items():
    en = _u[int(i)]['en']
    if es != en: V103[en.replace(chr(13) + chr(10), chr(10))] = re.sub(r'^Los (eventos|acontecimientos|hechos) de Yakuza', 'Los sucesos de Yakuza', es)
p = sys.argv[1]
rows = list(csv.DictReader(open(p, encoding='utf-8-sig', newline=''), delimiter=';'))
nb = lambda s: len(s.replace('í', '`').replace('Í', '|').encode())
n = 0
for r in rows:
    en = r['ingles'].replace('\r\n', '\n')
    if en in POR_INGLES: r['espanol'] = POR_INGLES[en]; n += 1
    elif 'input_character' in r['donde'] and en in CHAT: r['espanol'] = CHAT[en]; n += 1
    elif not r['espanol'].strip() and en in V103: r['espanol'] = V103[en]; n += 1; print('rellenado:', repr(en[:60]))
    if r['bytes_max'] and r['espanol'].strip() and nb(r['espanol'].replace('\r\n', '\n')) > int(r['bytes_max']):
        print('NO CABE:', r['id'], repr(r['espanol']))
with open(p, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=';', quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(rows)
print(n, 'correcciones')
