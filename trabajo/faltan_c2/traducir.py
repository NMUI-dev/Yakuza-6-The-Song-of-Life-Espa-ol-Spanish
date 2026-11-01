# -*- coding: utf-8 -*-
"""(01-11, claude2) Traduce lo que queda en inglés del Yakuza 6 con Gemini (clave en GEMINI_API_KEY, 1 hilo).
Entrada: unidades.json [{id, en, max (bytes o null), donde}]. Salida: traducido.json {id: es}. Reanudable.
Cada lote lleva ejemplos de la traducción ya hecha (pares_db.json) que comparten palabras con el lote, para usar los
mismos términos. Valida etiquetas <...>, saltos de línea y bytes (í cuenta 1: en el juego se escribe «~»)."""
import json, os, re, sys, time, collections
from google import genai
from google.genai import types

D = 'C:/Mods/yakuza6/trabajo/faltan_c2'
MODELOS = os.environ.get('GEMINI_MODELOS', 'gemini-3.8-flash gemini-3.7-flash gemini-3.5-flash gemini-2.5-flash').split()
uni = json.load(open(f'{D}/unidades.json', encoding='utf-8'))
OUT = f'{D}/traducido.json'
hecho = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
pares = json.load(open(f'{D}/pares_db.json', encoding='utf-8'))
cli = genai.Client()

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def nbytes(s): return len(s.replace('í', '~').replace('Í', '|').encode('utf-8'))
def etiquetas(s): return sorted(re.findall(r'<[^>]*>', s))

def problemas(u, es):
    p = []
    if etiquetas(u['en']) != etiquetas(es): p.append('las etiquetas <...> deben quedar exactamente iguales que en el inglés')
    if u['max'] and nbytes(es) > u['max']:
        p.append(f'demasiado largo: {nbytes(es)} bytes y caben {u["max"]} (cada letra con tilde o ñ cuenta 2, la í cuenta 1): acórtalo')
    if u['en'].count('\n') and es.count('\n') > u['en'].count('\n') + 1: p.append('demasiados saltos de línea')
    lineas = es.replace('\r', '').split('\n')
    if u['en'].count('\n') and max(map(len, lineas)) > max(map(len, u['en'].replace('\r', '').split('\n'))) + 12:
        p.append('algún renglón es mucho más largo que los del inglés: reparte el texto en renglones como el inglés')
    return p

PALABRAS_COMUNES = set('the and you that this with for are was have not but what your all can just like get out about'.split())
indice = collections.defaultdict(list)
for e, s in pares.items():
    if len(e) > 160: continue
    for w in set(re.findall(r"[A-Za-z][A-Za-z'-]{3,}", e)):
        if w.lower() not in PALABRAS_COMUNES: indice[w.lower()].append(e)
def ejemplos(lote, n=40):
    c = collections.Counter()
    for u in lote:
        for w in set(re.findall(r"[A-Za-z][A-Za-z'-]{3,}", u['en'])):
            l = indice.get(w.lower(), [])
            if 0 < len(l) < 400:
                for e in l[:6]: c[e] += 1.0 / len(l) ** 0.5
    return [(e, pares[e].replace('~', 'í').replace('|', 'Í')) for e, _ in c.most_common(n)]

GUIA = """Eres el traductor al español (neutro, para América Latina y España; tuteo entre amigos, «usted» con desconocidos y
superiores como en la traducción existente) del videojuego Yakuza 6: The Song of Life. Traduce del INGLÉS cada texto.
Reglas:
- Mismos términos que la traducción ya hecha (te doy ejemplos inglés => español de ese mismo juego). Clan Tojo, Familia
  Hirose, Cuarto Presidente, patriarca, Acción Heat, Orbes de Heat, Troublr, Creador de Clanes, Club de cabaré, Chat en
  vivo, Kiryu-san (los sufijos japoneses -san, -kun, -chan, -aniki se quedan).
- Nombres propios de personas, marcas, locales con nombre propio (Club Shine, Snack Kiyomi...), títulos de canciones y
  de juegos (Out Run, Super Hang-On, Puyo Puyo), siglas técnicas (FXAA, SSAA) y códigos se dejan IGUAL.
- Si un texto no hay que traducirlo (es un nombre, ya está en español o es un identificador interno), devuélvelo IDÉNTICO.
- Etiquetas como <symbol=...>, <Sign:1,Combat>, <color=...>, </color>, ${...}: cópialas tal cual, en el lugar que toque.
- Respeta los saltos de línea (\\n): los textos se ven en recuadros; reparte el español en el mismo número de renglones
  (o como mucho uno más) y de largo parecido.
- Si un texto trae «max_bytes», la traducción NO puede pasar de esos bytes en UTF-8 (letra con tilde o ñ = 2 bytes, pero
  la í = 1). Si no cabe, resume con naturalidad sin perder lo importante (en los resúmenes de la historia, condensa).
- Textos entre paréntesis son pensamientos de Kiryu: mantenlos entre paréntesis.
Devuelve SOLO un objeto JSON {"id": "traducción"} con todos los id."""

def openrouter(m, prompt):
    import urllib.request
    q = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', headers={
        'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'},
        data=json.dumps({'model': m, 'temperature': 0.3, 'response_format': {'type': 'json_object'},
                         'messages': [{'role': 'user', 'content': prompt}]}).encode())
    try: t = json.load(urllib.request.urlopen(q, timeout=240))['choices'][0]['message']['content']
    except urllib.error.HTTPError as e: raise Exception(f'{e.code} {e.read()[:200]}')
    return json.loads(re.sub(r'^```(?:json)?|```$', '', t.strip()).strip())

def pedir(lote, extra=''):
    datos = {str(u['id']): ({'texto': u['en'], 'max_bytes': u['max']} if u['max'] else {'texto': u['en']}) for u in lote}
    ej = '\n'.join(f'{e!r} => {s!r}' for e, s in ejemplos(lote))
    prompt = f'{GUIA}\n\nEJEMPLOS de la traducción existente:\n{ej}\n\n{extra}TEXTOS:\n{json.dumps(datos, ensure_ascii=False, indent=0)}'
    for m in MODELOS:
        for intento in range(int(os.environ.get('INTENTOS', '6'))):
            try:
                if m.startswith('or:'): return openrouter(m[3:], prompt), m
                r = cli.models.generate_content(model=m, contents=prompt, config=types.GenerateContentConfig(
                    response_mime_type='application/json', temperature=0.3))
                return json.loads(r.text), m
            except Exception as ex:
                s = str(ex)
                q = re.findall(r"quotaId': '([^']*)", s)
                log('  error', m, s[:60], q)
                if '404' in s: break
                if '429' in s and (not q or any('PerDay' in x for x in q)): break      # cuota del día: otro modelo
                time.sleep(65 if '429' in s else 20)                                  # por minuto o saturado: esperar
    raise SystemExit('sin modelos')

def main():
    tam = int(os.environ.get('LOTE', '30'))
    falta = [u for u in uni if str(u['id']) not in hecho]
    falta.sort(key=lambda u: u['donde'])
    log(f'{len(falta)} por traducir de {len(uni)}')
    i = 0
    while i < len(falta):
        lote = []; car = 0
        while i < len(falta) and len(lote) < tam and car < 6000:
            lote.append(falta[i]); car += len(falta[i]['en']); i += 1
        r, m = pedir(lote)
        for ronda in range(3):
            malos = []
            for u in lote:
                es = r.get(str(u['id']))
                if not isinstance(es, str) or not es.strip(): malos.append((u, ['falta la traducción'])); continue
                es = es.replace('\r\n', '\n')
                if '\r\n' in u['en']: es = es.replace('\n', '\r\n')
                p = problemas(u, es)
                if p: malos.append((u, p))
                else: hecho[str(u['id'])] = es
            if not malos: break
            log(f'  ronda {ronda + 1}: {len(malos)} con problemas')
            extra = 'CORRIGE estos (tu versión anterior y el problema):\n' + '\n'.join(
                f'{u["id"]}: {r.get(str(u["id"]))!r} -> {"; ".join(p)}' for u, p in malos) + '\n\n'
            r2, m = pedir([u for u, _ in malos], extra); r.update(r2); lote = [u for u, _ in malos]
        json.dump(hecho, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        log(f'{len(hecho)}/{len(uni)} ({m})')

if __name__ == '__main__': main()
