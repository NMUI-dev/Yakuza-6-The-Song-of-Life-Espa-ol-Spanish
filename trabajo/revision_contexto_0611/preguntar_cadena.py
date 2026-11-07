# (claude1, 06-11-2026) Pregunta EN CADENA a todas las IA qué falta revisar (regla del usuario): cada IA recibe todo lo
# hecho (pregunta_cadena_base.md), las ideas propias de Claude y la lista ORDENADA de lo que ya propusieron las anteriores,
# y solo debe aportar lo NUEVO. Todo queda escrito en cadena/: paso_NN_<modelo>.json y lista_acumulada.md.
# Se puede añadir a mano lo que respondan Gemini o Grok del usuario: cadena/manual_NN_<nombre>.json (mismo formato).
#   python -I -u preguntar_cadena.py
import json
import os
import re
import time
import urllib.request
from pathlib import Path

aqui = Path(__file__).resolve().parent
# (06-11) ronda final: CADENA=cadena_final BASE=pregunta_cadena_final.md python -I -u preguntar_cadena.py
sal = aqui / os.environ.get("CADENA", "cadena")
sal.mkdir(exist_ok=True)
BASE = (aqui / os.environ.get("BASE", "pregunta_cadena_base.md")).read_text(encoding="utf-8")
# 06-11 18:40: Gemini al final (sin cuota hoy; si falla, se vuelve a lanzar mañana y recibe todo lo anterior).
ORDEN = ["or:nvidia/nemotron-3-ultra-550b-a55b:free", "kilo:kilo/kilo-auto/free", "or:nvidia/nemotron-3.5-super-vl:free",
         "or:recursive/flint-v1.0:free", "or:xingchen-agi/xing4.0-29b-a4b:free", "or:dots-studio/dots-3-note-preview:free",
         "or:nvidia/nemotron-3.5-lightning:free", "or:google/gemma-4-31b-it:free",
         "gemini:gemini-3.8-flash", "gemini:gemini-3.7-flash", "gemini:gemini-3.5-flash"]
CUOTAS = Path("C:/mods/yakuza6/tareas/gemini/cuotas.json")


def sin_cuota(quien):
    # mismo registro que revisar_escenas.py (día = UTC-7, cuando Google reinicia la cuota)
    import datetime
    dia = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=7)).strftime("%Y-%m-%d")
    try:
        c = json.load(open(CUOTAS, encoding="utf-8"))
    except Exception:
        return False
    clave = quien.split(":", 1)[1] if quien.startswith("gemini:") else quien
    return "agotado" in c.get(clave, {}).get(dia, {})


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def limpiar(t):
    t = re.sub(r"^```(?:json)?|```$", "", t.strip()).strip()
    m = re.search(r"\{.*\}", t, re.S)
    return json.loads(m.group(0) if m else t)


def preguntar(quien, texto):
    tipo, m = quien.split(":", 1)
    if tipo == "or":
        q = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", headers={
            "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"},
            data=json.dumps({"model": m, "temperature": 0.5, "messages": [{"role": "user", "content": texto}]}).encode())
        return limpiar(json.load(urllib.request.urlopen(q, timeout=900))["choices"][0]["message"]["content"])
    if tipo == "kilo":
        # la pregunta va en un archivo: por la línea de comandos de cmd se rompen « » | < > y las comillas
        import subprocess
        f = sal / "pregunta_kilo.md"
        f.write_text(texto, encoding="utf-8")
        orden = "Lee el archivo %s y responde exactamente a lo que pide, SOLO con el JSON. No ejecutes comandos ni edites nada." % f
        p = subprocess.run(["cmd", "/c", "kilo", "run", "-m", m, orden], cwd=str(sal), capture_output=True, timeout=1800,
                           encoding="utf-8", errors="replace")
        (sal / "kilo_salida.txt").write_text(p.stdout + "\n--- stderr\n" + p.stderr, encoding="utf-8")
        return limpiar(re.sub(r"\x1b\[[0-9;]*m", "", p.stdout))
    from google import genai
    from google.genai import types
    cli = genai.Client()   # (07-11) en una línea aparte: si no, «client has been closed» (aviso de claude2)
    r = cli.models.generate_content(model=m, contents=texto, config=types.GenerateContentConfig(
        response_mime_type="application/json", temperature=0.5, http_options=types.HttpOptions(timeout=900000)))
    return limpiar(r.text)


def acumuladas():
    ideas = []
    for f in sorted(sal.glob("*.json")):
        d = json.load(open(f, encoding="utf-8"))
        for x in d.get("respuesta", {}).get("nuevas", []):
            ideas.append((d["quien"], x))
    return ideas


def escribir_lista(ideas):
    with open(sal / "lista_acumulada.md", "w", encoding="utf-8") as o:
        o.write("# Ideas acumuladas (pregunta en cadena, %s)\n\n" % time.strftime("%d-%m-%Y %H:%M"))
        for n, (q, x) in enumerate(ideas, 1):
            o.write("%d. **%s** (%s, prioridad %s)\n   - Por qué: %s\n   - Cómo detectarlo: %s\n" % (
                n, x.get("aspecto", ""), q, x.get("prioridad", "?"), x.get("por_que", ""), x.get("como_detectar", "")))


hechos = {json.load(open(f, encoding="utf-8"))["quien"] for f in sal.glob("*.json")}
for quien in ORDEN:
    if quien in hechos:
        continue
    if sin_cuota(quien):
        log(quien, "sin cuota hoy: se pregunta en la próxima vuelta")
        continue
    ideas = acumuladas()
    previas = "\n".join("- %s: %s" % (x.get("aspecto", ""), x.get("como_detectar", "")[:160]) for _, x in ideas) or "(ninguna todavía)"
    texto = BASE + "\n\nIDEAS QUE YA DIERON OTRAS IA ANTES QUE TÚ (tampoco las repitas):\n" + previas + \
        "\n\nResponde SOLO JSON: {\"nuevas\":[{\"aspecto\":\"...\",\"por_que\":\"...\",\"como_detectar\":\"...\"," \
        "\"prioridad\":\"alta|media|baja\"}]}. Si de verdad no queda nada nuevo, devuelve {\"nuevas\":[]}."
    for intento in range(3):
        try:
            r = preguntar(quien, texto)
            n = len(list(sal.glob("*.json"))) + 1
            json.dump({"quien": quien, "paso": n, "pregunta": texto, "respuesta": r},
                      open(sal / ("paso_%02d_%s.json" % (n, re.sub(r"\W+", "_", quien))), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            log(quien, "aportó", len(r.get("nuevas", [])), "ideas nuevas")
            escribir_lista(acumuladas())
            break
        except Exception as e:
            log(quien, "error", str(e)[:150])
            time.sleep(60)
escribir_lista(acumuladas())
log("fin de la cadena:", len(acumuladas()), "ideas en cadena/lista_acumulada.md")
