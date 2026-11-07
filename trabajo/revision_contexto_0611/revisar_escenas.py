# (claude1, 06-11-2026) Revisor gratuito por ESCENAS del Yakuza 6. Cada paquete (paquetes/paquete_NNN.txt) lleva escenas
# enteras en orden: «#id [hablante] inglés || español». El modelo lee la conversación completa y apunta solo errores
# reales de contexto. Claude verifica cada uno a mano antes de corregir nada.
#   python -I -u revisar_escenas.py NOMBRE        (varios a la vez; se reparten los paquetes con mkdir)
# Claves: GEMINI_API_KEY y OPENROUTER_API_KEY en el entorno (nunca en archivos). Cuotas: C:/mods/yakuza6/tareas/gemini/cuotas.json
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from google import genai
from google.genai import types

aqui = Path(__file__).resolve().parent
PAQ = aqui / "paquetes"
RES = aqui / "resultados"
RECL = aqui / "reclamados"
RES.mkdir(exist_ok=True)
RECL.mkdir(exist_ok=True)
QUIEN = sys.argv[1] if len(sys.argv) > 1 else "rev"
MODELOS = os.environ.get("MODELOS_REV", "gemini-3.8-flash gemini-3.7-flash gemini-3.5-flash "
                         "or:nvidia/nemotron-3-ultra-550b-a55b:free or:google/gemma-4-31b-it:free").split()
CUOTAS = Path("C:/mods/yakuza6/tareas/gemini/cuotas.json")
cli = genai.Client()


def log(*a):
    print(time.strftime("%H:%M:%S"), QUIEN, *a, flush=True)


def dia():
    return (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).strftime("%Y-%m-%d")


def cuotas():
    try:
        return json.load(open(CUOTAS, encoding="utf-8"))
    except Exception:
        return {}


def anotar(m, agotado=False):
    c = cuotas()
    d = c.setdefault(m, {}).setdefault(dia(), {"peticiones": 0})
    if agotado:
        d["agotado"] = time.strftime("%H:%M")
    else:
        d["peticiones"] += 1
    json.dump(c, open(CUOTAS, "w", encoding="utf-8"), indent=1)


def agotado(m):
    return "agotado" in cuotas().get(m, {}).get(dia(), {})


GUIA = open("C:/mods/yakuza6/trabajo/lotes/GUIA_TRADUCCION.md", encoding="utf-8").read()
FICHA = open("C:/Mods/NOTAS_AGENTES/COMUN/TRADUCCIONES/YAKUZA_PERSONAJES_Y_GENERO.md", encoding="utf-8").read()
# de la ficha, solo las reglas (sin la tabla larga de números: los nombres ya van en cada línea)
FICHA = re.sub(r"\| Kazuma Kiryu \| H \| P1098.*?\n", "| Kazuma Kiryu | H | (muchos números) |\n", FICHA)

ENCARGO = """Eres revisor profesional de la traducción al español neutro latinoamericano de Yakuza 6: The Song of Life.
Recibes ESCENAS COMPLETAS en orden. Cada línea: «#id [hablante (género H/M)] inglés || español». Sin [hablante] = cinemática
o charla: deduce quién habla por el contexto. « / » es un salto de línea. «x5» tras el id = esa MISMA traducción se usa en 5
sitios del juego (debe valer para todos).
Lee CADA ESCENA ENTERA antes de juzgar una línea, y apunta SOLO errores reales que un jugador notaría:
 1 respuesta que no encaja con la pregunta o con lo anterior
 2 tú/usted incoherente para la relación (o que cambia sin motivo dentro de la escena)
 3 frase partida en varias líneas que en español no enlaza
 4 le/lo/la/su con el referente equivocado, o género equivocado de quien habla o a quien se habla
 5 sentido cambiado o mal entendido respecto al inglés (incluye chistes y frases hechas traducidas sin sentido)
 6 errata, palabra rota o inglés colado
NO apuntes estilo, sinónimos ni gustos. NO cambies nombres, honoríficos (-san, -chan, aniki), términos del glosario ni
marcas <...>. Si la línea está bien, no la pongas. Mejor 0 fallos que uno inventado.
La propuesta: cambio MÍNIMO, mismo número de « / », mismas marcas, español neutro (sin «vosotros», sin modismos).
Además, apunta lo que sirva para el GLOSARIO de personajes: cómo se tratan (tú/usted) y cómo se llaman entre ellos.
Devuelve SOLO JSON:
{"fallos":[{"id":"141","tipo":1,"escena":"...","es":"español actual","propuesta":"...","porque":"breve, en español"}],
 "trato":[{"quien":"Kiryu","a_quien":"Haruka","trato":"tú","escena":"..."}],
 "personajes":[{"nombre":"...","genero":"H|M","quien_es":"breve","escena":"..."}]}
"""


def openrouter(m, prompt):
    q = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", headers={
        "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"},
        data=json.dumps({"model": m, "temperature": 0.2, "response_format": {"type": "json_object"},
                         "messages": [{"role": "user", "content": prompt}]}).encode())
    try:
        t = json.load(urllib.request.urlopen(q, timeout=900))["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        raise Exception("%s %s" % (e.code, e.read()[:200]))
    t = re.sub(r"^```(?:json)?|```$", "", t.strip()).strip()
    return json.loads(t)


def kilo(m, prompt):
    # (06-11) Kilo CLI: cuota aparte de Gemini y OpenRouter. La pregunta va en un archivo (por cmd se rompen « » | < >);
    # sin --auto (Claude Code lo bloquea): Kilo solo lee el archivo y contesta.
    import subprocess
    f = aqui / "logs" / ("kilo_%s.md" % QUIEN)
    f.write_text(prompt, encoding="utf-8")
    orden = "Lee el archivo %s y haz exactamente lo que pide. Responde SOLO con el JSON. No ejecutes comandos ni edites nada." % f
    p = subprocess.run(["cmd", "/c", "kilo", "run", "-m", m, orden], cwd=str(aqui / "logs"), capture_output=True,
                       timeout=2400, encoding="utf-8", errors="replace")
    t = re.sub(r"\x1b\[[0-9;]*m", "", p.stdout)
    (aqui / "logs" / ("kilo_%s_salida.txt" % QUIEN)).write_text(t + "\n--- stderr\n" + p.stderr, encoding="utf-8")
    if "rate limit" in (t + p.stderr).lower() or "429" in p.stderr:
        raise Exception("429 kilo")
    i, j = t.find("{"), t.rfind("}")
    return json.loads(t[i:j + 1])


def pedir(prompt):
    for m in MODELOS:
        if agotado(m):
            continue
        for intento in range(4):
            try:
                if m.startswith("kilo:"):
                    r = kilo(m[5:], prompt)
                elif m.startswith("or:"):
                    r = openrouter(m[3:], prompt)
                else:
                    r = cli.models.generate_content(model=m, contents=prompt, config=types.GenerateContentConfig(
                        response_mime_type="application/json", temperature=0.2,
                        http_options=types.HttpOptions(timeout=900000)))
                    r = json.loads(r.text)
                anotar(m)
                return r, m
            except Exception as e:
                s = str(e)
                if "429" in s or "RESOURCE_EXHAUSTED" in s:
                    if "PerDay" in s or "per day" in s.lower() or intento == 3:
                        anotar(m, agotado=True)
                        log(m, "sin cuota")
                        break
                    time.sleep(60)
                    continue
                if "404" in s or "not found" in s.lower():
                    anotar(m, agotado=True)
                    log(m, "no existe")
                    break
                log(m, "error", s[:160])
                time.sleep(30 if "503" in s else 10)
    return None, None


def valido(r):
    return isinstance(r, dict) and isinstance(r.get("fallos", []), list)


MAXP = int(sys.argv[2]) if len(sys.argv) > 2 else 999
hechos = 0
while hechos < MAXP:
    libres = [p for p in sorted(PAQ.glob("paquete_*.txt")) if not (RES / (p.stem + ".json")).exists()]
    mio = None
    for p in libres:
        try:
            (RECL / p.stem).mkdir()
            mio = p
            break
        except FileExistsError:
            continue
    if not mio:
        log("fin: no quedan paquetes libres")
        break
    if all(agotado(m) for m in MODELOS):
        log("todos los modelos sin cuota: espero al reinicio diario")
        (RECL / mio.stem).rmdir()
        time.sleep(1800)
        continue
    texto = mio.read_text(encoding="utf-8")
    prompt = ENCARGO + "\n=== GUÍA DE TRADUCCIÓN ===\n" + GUIA + "\n=== FICHA DE PERSONAJES Y REGLAS ===\n" + FICHA + \
        "\n=== ESCENAS A REVISAR ===\n" + texto
    t0 = time.time()
    r, m = pedir(prompt)
    if not valido(r):
        log(mio.stem, "sin respuesta válida; lo suelto")
        (RECL / mio.stem).rmdir()
        time.sleep(120)
        continue
    r["_modelo"], r["_segundos"] = m, int(time.time() - t0)
    json.dump(r, open(RES / (mio.stem + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hechos += 1
    log(mio.stem, m, "fallos", len(r.get("fallos", [])), "trato", len(r.get("trato", [])), "en", r["_segundos"], "s")
