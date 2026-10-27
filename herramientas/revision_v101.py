"""(claude1, 25-10-2026) Revisión de las imágenes del Yakuza 6 v1.0 (pedido del usuario vía claude2).
Solo LEE ui_v2 y extraido; todo lo que escribe va a trabajo/imagenes/revision_v101/.
  python -I -u herramientas/revision_v101.py png     -> PNG original/español de las 302 DDS entregadas
  python -I -u herramientas/revision_v101.py ocr     -> OCR (RapidOCR) del español: palabras inglesas que quedan
  python -I -u herramientas/revision_v101.py vision  -> revisor de visión gratis (gemma4 local; OpenRouter gemma-4 de reserva)
  python -I -u herramientas/revision_v101.py hojas   -> hojas de parejas (original | español) de las marcadas, de 8 en 8
"""
import os, sys, json, subprocess, base64, time, re, urllib.request
from PIL import Image

Y6 = r'C:\Mods\yakuza6'
T = os.path.join(Y6, 'trabajo')
ES_RAIZ = os.path.join(T, 'ui_v2', 'add')
OR_RAIZ = os.path.join(T, 'extraido', 'ui')
SAL = os.path.join(T, 'imagenes', 'revision_v101')
TEXCONV = os.path.join(Y6, 'herramientas', 'kit_atlas', 'texconv', 'texconv.exe')
os.makedirs(SAL, exist_ok=True)


def lista():
    r = []
    for d, _, fs in os.walk(ES_RAIZ):
        for f in fs:
            if f.lower().endswith('.dds'):
                rel = os.path.relpath(os.path.join(d, f), ES_RAIZ)
                r.append(rel)
    return sorted(r)


def clave(rel):
    return rel.replace('\\', '__').replace('/', '__')[:-4]


def png():
    falta = []
    for sub in ('or', 'es'):
        os.makedirs(os.path.join(SAL, sub), exist_ok=True)
    for rel in lista():
        k = clave(rel)
        for sub, raiz in (('es', ES_RAIZ), ('or', OR_RAIZ)):
            dst = os.path.join(SAL, sub, k + '.png')
            if os.path.exists(dst):
                continue
            src = os.path.join(raiz, rel)
            if not os.path.exists(src):
                falta.append((sub, rel)); continue
            tmp = os.path.join(SAL, 'tmp'); os.makedirs(tmp, exist_ok=True)
            subprocess.run([TEXCONV, '-nologo', '-y', '-ft', 'png', '-m', '1', '-o', tmp, src], capture_output=True)
            p = os.path.join(tmp, os.path.basename(src)[:-4] + '.png')
            if os.path.exists(p):
                os.replace(p, dst)
            else:
                falta.append((sub, rel))
    json.dump(falta, open(os.path.join(SAL, 'png_fallos.json'), 'w'), indent=0)
    print('dds', len(lista()), 'fallos', len(falta))


# palabras inglesas frecuentes en los menús que en español no existen (la OCR las lee aunque la letra sea pequeña)
INGLES = set('''the and of to you your with for from press select back cancel confirm start exit yes no on off
game new load save data settings options next previous level points score time total best win lose loser winner
round player players stage clear failed get got item items money rank ranking record records hit miss great good
perfect bad bonus mode easy normal hard play stop pause resume continue quit menu help rules rule how controls
move button buttons left right up down hold release tap'''.split())


def ocr():
    from rapidocr_onnxruntime import RapidOCR
    eng = RapidOCR()
    out_p = os.path.join(SAL, 'ocr_es.json')
    res = json.load(open(out_p, encoding='utf-8')) if os.path.exists(out_p) else {}
    for rel in lista():
        k = clave(rel)
        if k in res:
            continue
        p = os.path.join(SAL, 'es', k + '.png')
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGBA')
        fondo = Image.new('RGBA', im.size, (0, 0, 0, 255)); fondo.alpha_composite(im)
        tmp = os.path.join(SAL, 'tmp_ocr.png'); fondo.convert('RGB').save(tmp)
        r, _ = eng(tmp)
        textos = [x[1] for x in (r or [])]
        ing = sorted({w for t in textos for w in re.findall(r'[A-Za-z]+', t) if w.lower() in INGLES})
        res[k] = {'textos': textos, 'ingles': ing}
        json.dump(res, open(out_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    n = sum(1 for v in res.values() if v['ingles'])
    print('ocr', len(res), 'con inglés', n)


PROMPT = ('Two images of the same video game UI texture: LEFT = original (English/Japanese), RIGHT = Spanish translation. '
          'Check ONLY the RIGHT one for: English text left untranslated (except proper names/brands), text cut off or '
          'overflowing its box, overlapping/garbled letters, two different fonts mixed in one line, wrong Spanish words, '
          'Spanish text that does not match the meaning of the original. Answer ONLY JSON: '
          '{"ok": true|false, "problemas": ["short description in Spanish", ...]}')


def pareja(k, maxw=1024):
    a = Image.open(os.path.join(SAL, 'or', k + '.png')).convert('RGBA')
    b = Image.open(os.path.join(SAL, 'es', k + '.png')).convert('RGBA')
    w, h = a.size[0] + b.size[0] + 16, max(a.size[1], b.size[1])
    c = Image.new('RGBA', (w, h), (40, 40, 40, 255))
    for x0, im in ((0, a), (a.size[0] + 16, b)):
        f = Image.new('RGBA', im.size, (0, 0, 0, 255)); f.alpha_composite(im); c.paste(f, (x0, 0))
    if w > maxw:
        c = c.resize((maxw, max(1, int(h * maxw / w))), Image.LANCZOS)
    return c.convert('RGB')


def vision_local(img_b64):
    body = json.dumps({'model': 'gemma4:12b', 'stream': False, 'format': 'json',
                       'messages': [{'role': 'user', 'content': PROMPT, 'images': [img_b64]}]}).encode()
    rq = urllib.request.Request('http://127.0.0.1:11434/api/chat', body, {'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(rq, timeout=300).read())['message']['content']


def vision():
    out_p = os.path.join(SAL, 'vision.json')
    res = json.load(open(out_p, encoding='utf-8')) if os.path.exists(out_p) else {}
    for rel in lista():
        k = clave(rel)
        if k in res or not os.path.exists(os.path.join(SAL, 'es', k + '.png')) or not os.path.exists(os.path.join(SAL, 'or', k + '.png')):
            continue
        tmp = os.path.join(SAL, 'tmp_par.jpg'); pareja(k).save(tmp, quality=90)
        b64 = base64.b64encode(open(tmp, 'rb').read()).decode()
        try:
            txt = vision_local(b64)
            m = re.search(r'\{.*\}', txt, re.S); v = json.loads(m.group(0)) if m else {'ok': None, 'crudo': txt}
        except Exception as e:
            v = {'ok': None, 'error': str(e)[:200]}
        res[k] = v
        json.dump(res, open(out_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(k, v.get('ok'), '; '.join(v.get('problemas', []))[:150], flush=True)
    print('vision', len(res), 'marcadas', sum(1 for v in res.values() if v.get('ok') is not True))


def hojas():
    ocr_r = json.load(open(os.path.join(SAL, 'ocr_es.json'), encoding='utf-8')) if os.path.exists(os.path.join(SAL, 'ocr_es.json')) else {}
    vis = json.load(open(os.path.join(SAL, 'vision.json'), encoding='utf-8')) if os.path.exists(os.path.join(SAL, 'vision.json')) else {}
    marc = [k for k in sorted(set(ocr_r) | set(vis)) if (ocr_r.get(k, {}).get('ingles')) or vis.get(k, {}).get('ok') is not True]
    os.makedirs(os.path.join(SAL, 'hojas'), exist_ok=True)
    ind = []
    for i in range(0, len(marc), 8):
        grupo = marc[i:i + 8]; ims = [pareja(k, 900) for k in grupo]
        H = sum(im.size[1] + 24 for im in ims); W = max(im.size[0] for im in ims)
        hoja = Image.new('RGB', (W, H), (20, 20, 20)); y = 0
        from PIL import ImageDraw
        d = ImageDraw.Draw(hoja)
        for k, im in zip(grupo, ims):
            d.text((4, y + 4), k, fill=(255, 255, 0)); hoja.paste(im, (0, y + 24)); y += im.size[1] + 24
        n = 'hoja_%02d.png' % (i // 8); hoja.save(os.path.join(SAL, 'hojas', n)); ind.append([n, grupo])
    json.dump(ind, open(os.path.join(SAL, 'hojas', 'indice.json'), 'w'), indent=0)
    print('marcadas', len(marc), 'hojas', len(ind))


if __name__ == '__main__':
    {'png': png, 'ocr': ocr, 'vision': vision, 'hojas': hojas}[sys.argv[1]]()
