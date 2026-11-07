# (claude1, 06-11-2026) Pregunta a TODAS las IA gratuitas disponibles qué más revisar (pedido del usuario: «pregúntale a
# todas las IA y así sacamos la mayor cantidad de errores o faltas»). La pregunta, con todo lo ya hecho, está en
# pregunta_revision.md. Guarda cada respuesta en preguntas/<modelo>.json y no repite las que ya respondieron.
# Gemini sin cuota: reintenta cada 30 min hasta que vuelva (reinicio diario de Google). Claves solo en el entorno.
#   python -I -u preguntar_ias.py
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

aqui = Path(__file__).resolve().parent
sal = aqui / "preguntas"
sal.mkdir(exist_ok=True)
PREGUNTA = (aqui / "pregunta_revision.md").read_text(encoding="utf-8")
GEMINI = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-4-argon"]
OPENROUTER = ["nvidia/nemotron-3-ultra-550b-a55b:free", "google/gemma-4-31b-it:free", "google/gemma-4-26b-a4b-it:free",
              "nvidia/nemotron-3.5-super-vl:free", "dots-studio/dots-3-note-preview:free", "xingchen-agi/xing4.0-29b-a4b:free",
              "recursive/flint-v1.0:free", "nvidia/nemotron-3.5-lightning:free"]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def limpiar(t):
    t = re.sub(r"^```(?:json)?|```$", "", t.strip()).strip()
    m = re.search(r"\{.*\}", t, re.S)
    return json.loads(m.group(0) if m else t)


def openrouter(m):
    q = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", headers={
        "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"},
        data=json.dumps({"model": m, "temperature": 0.4, "messages": [{"role": "user", "content": PREGUNTA}]}).encode())
    return limpiar(json.load(urllib.request.urlopen(q, timeout=600))["choices"][0]["message"]["content"])


def gemini(m):
    from google import genai
    from google.genai import types
    r = genai.Client().models.generate_content(model=m, contents=PREGUNTA, config=types.GenerateContentConfig(
        response_mime_type="application/json", temperature=0.4, http_options=types.HttpOptions(timeout=600000)))
    return limpiar(r.text)


def hecho(m):
    return (sal / (m.replace("/", "_").replace(":", "_") + ".json")).exists()


def guardar(m, r):
    json.dump({"modelo": m, "respuesta": r}, open(sal / (m.replace("/", "_").replace(":", "_") + ".json"), "w",
                                                 encoding="utf-8"), ensure_ascii=False, indent=1)
    log(m, "respondió:", len(r.get("faltan", [])), "aspectos")


for m in OPENROUTER:
    if hecho(m):
        continue
    for intento in range(3):
        try:
            guardar(m, openrouter(m))
            break
        except Exception as e:
            log(m, "error", str(e)[:150])
            time.sleep(30)

while not any(hecho(m) for m in GEMINI):
    for m in GEMINI:
        try:
            guardar(m, gemini(m))
            break
        except Exception as e:
            log(m, "sin respuesta:", str(e)[:100])
    else:
        log("Gemini sin cuota: reintento en 30 min")
        time.sleep(1800)
log("fin")
