# -*- coding: utf-8 -*-
"""(Claude Code, 20-10-2026) Traduce los rótulos de imagen (trabajo/imagenes_ui/rotulos_en.json) con un ayudante gratuito
(OpenRouter :free; reserva Gemini) siguiendo la guía y la memoria de traducción de los textos del juego ya traducidos.
Salida: trabajo/imagenes_ui/rotulos_es.json (mismo número de líneas « / » que el inglés, en MAYÚSCULAS).
"""
import json, os, re, sys, glob, urllib.request
R = 'C:/mods/yakuza6'; I = f'{R}/trabajo/imagenes_ui'
MODELOS = ['minimax/minimax-m3.1-flash:free', 'nvidia/nemotron-3-ultra-550b-a55b:free', 'google/gemma-4-31b-it:free']

def memoria():
    tm = {}
    for f in sorted(glob.glob(f'{R}/trabajo/lotes/lote_???.json')):
        es = json.load(open(f[:-5] + '_es.json', encoding='utf-8'))
        for x in json.load(open(f, encoding='utf-8')): tm.setdefault(x['en'].strip().lower(), es.get(str(x['id'])))
    return tm

def pedir(prompt):
    for m in MODELOS:
        try:
            q = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', headers={
                'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'},
                data=json.dumps({'model': m, 'temperature': 0.3, 'response_format': {'type': 'json_object'},
                                 'messages': [{'role': 'user', 'content': prompt}]}).encode())
            t = json.load(urllib.request.urlopen(q, timeout=600))['choices'][0]['message']['content']
            return json.loads(re.sub(r'^```(?:json)?|```$', '', t.strip()).strip()), m
        except Exception as e: print(m, 'falla', str(e)[:200])
    return None, None

if __name__ == '__main__':
    en = json.load(open(f'{I}/rotulos_en.json', encoding='utf-8'))
    tm = memoria()
    pistas = {}
    for v in en.values():
        for parte in [v.replace(' / ', ' ')] + v.split(' / '):
            t = tm.get(parte.lower())
            if t: pistas[parte] = t
    guia = open(f'{R}/trabajo/lotes/GUIA_TRADUCCION.md', encoding='utf-8').read()
    prompt = f"""Eres traductor de videojuegos. Traduce al español neutro latinoamericano estos RÓTULOS de imagen de Yakuza 6
(objetivos de misión, nombres de grupos de enemigos y presentaciones de jefes). Reglas: todo en MAYÚSCULAS con tildes
(Á É Í Ó Ú Ñ); objetivos en imperativo de TÚ y cortos (GO TO → VE A / VE AL; FIND → ENCUENTRA A / BUSCA; DEFEAT → DERROTA A);
los nombres propios de personas, locales y bandas que son marca (Stardust, New Serena, Snack Hourglass → BAR SNACK HOURGLASS,
Moreno, Shangri-La, Jingai Thunders, Bloody Shark, The Six Lunatics) se dejan; respeta la guía y la memoria de traducción
(términos que ya salen así en el juego). « / » separa las líneas del rótulo: devuelve EXACTAMENTE el mismo número de « / »
que el inglés, repartiendo el texto de forma equilibrada (la primera línea de las presentaciones es el NOMBRE del personaje).
Devuelve SOLO JSON {{"clave": "TRADUCCIÓN"}} con todas las claves.
# GUÍA
{guia}
# MEMORIA DE TRADUCCIÓN (inglés -> como ya está en el juego)
{json.dumps(pistas, ensure_ascii=False, indent=0)}
# RÓTULOS
{json.dumps(en, ensure_ascii=False, indent=0)}"""
    r, m = pedir(prompt)
    if r is None: sys.exit('sin respuesta')
    malos = [k for k in en if k not in r or r[k].count(' / ') != en[k].count(' / ')]
    json.dump(r, open(f'{I}/rotulos_es.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('modelo', m, 'claves', len(r), 'con problemas', malos)
