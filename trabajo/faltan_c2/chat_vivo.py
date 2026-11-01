# -*- coding: utf-8 -*-
"""(01-11, claude2) Chat en vivo: «input_character» (lo que se teclea, en MAYÚSCULAS sin tildes) sale del mensaje ya en
español; «button» (un botón por letra) se estira al nuevo largo con el mismo dibujo que el inglés.
Escribe db_extra.json {tabla: {ruta: valor}} que usa aplicar.py."""
import json, os, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Mods/yakuza6/trabajo/faltan_c2'
T = 'minigame_live_chat_chat_commands'
en = json.load(open(f'C:/Mods/yakuza6/trabajo/armp_json/{T}.bin.json', encoding='utf-8'))
es = json.load(open(f'{D}/es_json/{T}.bin.json', encoding='utf-8'))
uni = {u['id']: u for u in json.load(open(f'{D}/unidades.json', encoding='utf-8'))}
nuevo = {uni[int(i)]['en']: s for i, s in json.load(open(f'{D}/traducido.json', encoding='utf-8')).items()}

def teclear(frase, largo):
    s = unicodedata.normalize('NFD', frase.replace('~', 'í').replace('|', 'Í'))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').upper()
    s = re.sub(r"[^A-Z0-9? ]", ' ', s); palabras = s.split()
    out = ''
    for p in palabras:
        cand = (out + ' ' + p).strip()
        if len(cand) > largo + 3 and out: break
        out = cand
    return out.rstrip() or s.strip()[:largo]

# mensajes de una palabra que el extractor tomó por códigos (llevan punto y no espacio): a mano (01-11, claude2)
SUELTOS = {'...Alone.': '...Solo.', 'Absolutely.': 'Totalmente.', 'Aroused.': 'Excitado.', 'Definitely.': 'Sin duda.',
    'Ecstasy.': 'Éxtasis.', 'Gladly.': 'Con gusto.', 'Gotcha.': 'Entendido.', 'Jackpot.': '¡Premio!', 'Legs.': 'Piernas.',
    'Likewise.': 'Igualmente.', 'Okay.': 'De acuerdo.', 'Perfection...': 'Perfección...', 'Pleasure.': 'Placer.',
    'Relax.': 'Relájate.', 'Sex.': 'Sexo.', 'Spectacular...': 'Espectacular...', 'Strip.': 'Desnúdate.',
    'Strip...': 'Desnúdate...', 'Yeah.': 'Sí.', 'Yes...': 'Sí...', 'Yup.': 'Ajá.'}
A_JUEGO = str.maketrans({'Í': '|', 'í': '`'})
extra = {}; n = 0
for i, fila in en.items():
    if not isinstance(fila, dict): continue
    for k, v in fila.items():
        if not (isinstance(v, dict) and v.get('input_character')): continue
        msg = es[i][k]['chat_message']
        if msg == v['chat_message']: msg = nuevo.get(v['chat_message'], msg)
        if msg == v['chat_message'] and msg in SUELTOS:
            msg = SUELTOS[msg]; extra[f'{i}/{k}/chat_message'] = msg.translate(A_JUEGO)
        if msg == v['chat_message']: print('SE DEJA:', msg); continue
        inp = teclear(msg, len(v['input_character']))
        b = v['button']; btn = ''.join(b[int(j * len(b) / len(inp))] for j in range(len(inp)))
        extra[f'{i}/{k}/input_character'] = inp; extra[f'{i}/{k}/button'] = btn; n += 1
        if len(inp) > len(b):      # más letras que en inglés: el mismo tiempo por letra
            extra[f'{i}/{k}/limit_time'] = round(v['limit_time'] * len(inp) / len(b) * 4) / 4
        if n <= 12: print(v['input_character'], '->', inp, '|', b, '->', btn, '|', msg)
json.dump({T: extra}, open(f'{D}/db_extra.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(n, 'filas')
