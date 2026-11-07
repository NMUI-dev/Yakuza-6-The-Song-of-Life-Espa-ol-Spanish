# (claude1, 06-11-2026) Comprobaciones de forma sobre TODO el español (lista propia de lo que faltaba revisar):
#  VARIABLE  marcas ${...}, %s/%d, {0}, <Sign:...>, <symbol...>, <color...> distintas del inglés (el juego pondría basura)
#  SIGNOS    ¿ sin ? o ? sin ¿ (y lo mismo con ¡ !) dentro de una frase (las frases pueden ocupar varias líneas)
#  ESPACIOS  dobles (que el inglés no tiene) o espacio antes de , . ? !
#  FINAL     el inglés acaba en ? o ! y el español no: suele ser tono o sentido cambiado
#  MAYUS     el inglés empieza en mayúscula y el español en minúscula
#  LES       «le» con complemento plural («le hicieron a mis hombres» -> les)
#  LARGO     una línea del español más larga que la línea inglesa más larga de esa MISMA tabla (riesgo de no caber)
# Solo marca: se decide a mano. Uso: python barrido_extra.py [textos.csv] > barrido_extra.txt
import collections
import csv
import re
import sys

csv.field_size_limit(10 ** 9)
TEXTOS = sys.argv[1] if len(sys.argv) > 1 else r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv"
VAR = re.compile(r"\$\{[^}]*\}|%[sdif]|\{\d+\}|<Sign:[^>]*>|<symbol=[^>]*>|<color[^>]*>|</color>|<font_kind[^>]*>|</font_kind>")
ETQ = re.compile(r"<[^>]*>")
# (06-11) «lo que le hicieron a mis hombres»: «le» con complemento plural debe ser «les» (4 casos reales en el Y6)
# (06-11) «¿Quién demonios son estos tipos?»: con verbo plural va «quiénes» (3 casos reales)
QUIEN_PLURAL = re.compile(r"¿¡?Qui[eé]n\b(\s+\w+){0,2}\s+(son|eran|serán|fueron)\s+(estos|esos|aquellos|ustedes|ellos|ellas)\b", re.I)
LE_PLURAL = re.compile(r"\ble\s+(\w+\s+){1,4}?a\s+(los|las|mis|tus|sus|nuestros|nuestras|ustedes|ellos|ellas|todos|todas)\b", re.I)
SALTO = "\n"
cuenta = collections.Counter()
filas = list(csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"))


def lineas(s):
    return ETQ.sub("", s.replace("\r\n", SALTO)).split(SALTO)


max_tabla = collections.Counter()
for r in filas:
    t = r["donde"].split(" | ")[0]
    max_tabla[t] = max(max_tabla[t], max(len(x) for x in lineas(r["ingles"])))


def marca(tipo, r, detalle):
    cuenta[tipo] += 1
    print("%s\t%s\t%s\t%s\t%s" % (tipo, r["id"], detalle, r["ingles"].replace(SALTO, " / ")[:110],
                                  r["espanol"].replace(SALTO, " / ")[:130]))


for r in filas:
    en, es = r["ingles"].replace("\r\n", SALTO), r["espanol"].replace("\r\n", SALTO)
    if not es.strip():
        continue
    if sorted(VAR.findall(en)) != sorted(VAR.findall(es)):
        marca("VARIABLE", r, " ".join(sorted(set(VAR.findall(en)) ^ set(VAR.findall(es))))[:80])
    plano = ETQ.sub("X", es).replace(SALTO, " ")
    if plano.upper() == plano:      # comandos del chat en vivo (MAYÚSCULAS sin signos de apertura, a propósito)
        plano = ""
    for frase in re.split(r"(?<=[!?])\s+(?=[¿¡A-ZÁÉÍÓÚÑ])|(?<=[^.]\.)\s+(?=[¿¡A-ZÁÉÍÓÚÑ])", plano):
        if frase.count("¿") > frase.count("?") or (frase.count("?") > frase.count("¿") and not re.match(r"^[!?)\s]", frase)):
            marca("SIGNOS", r, "¿?: " + frase[:60])
            break
        if frase.count("¡") > frase.count("!") or (frase.count("!") > frase.count("¡") and not re.match(r"^[!?)\s]", frase)):
            marca("SIGNOS", r, "¡!: " + frase[:60])
            break
    es_x, en_x = ETQ.sub("X", es), ETQ.sub("X", en)
    if re.search(r"(?<=\S)  +(?=\S)", es_x) and not re.search(r"(?<=\S)  +(?=\S)", en_x):
        marca("ESPACIOS", r, "doble espacio")
    elif re.search(r"\w ([,.?!])(?!\.)", es_x) and not re.search(r"\w ([,.?!])", en_x):
        marca("ESPACIOS", r, "espacio antes de signo")
    fe = re.sub(r"[\s)\]\"»”']+$", "", ETQ.sub("", en))[-1:]
    fs = re.sub(r"[\s)\]\"»”']+$", "", ETQ.sub("", es))[-1:]
    if fe and fe in "?!" and fs not in "?!" and len(en) > 3:
        marca("FINAL", r, "inglés acaba en %s, español en %s" % (fe, fs or "nada"))
    if re.match(r"^[A-Z]", en) and re.match(r"^[a-zñáéíóú]", es) and not re.match(r"^(iPhone|e-|eh|ah|oh|mm)", es):
        marca("MAYUS", r, "empieza en minúscula")
    m = LE_PLURAL.search(es.replace(SALTO, " "))
    if m:
        marca("LES", r, "«le» con complemento plural: " + m.group(0)[:60])
    m = QUIEN_PLURAL.search(es.replace(SALTO, " "))
    if m:
        marca("QUIEN", r, "«quién» con verbo plural: " + m.group(0)[:60])
    t = r["donde"].split(" | ")[0]
    ls = max(len(x) for x in lineas(es))
    if r["donde"].startswith(("sound_auth", "auth", "talk")) and ls > max_tabla[t]:
        marca("LARGO", r, "línea de %d letras (la más larga del inglés en esa tabla: %d)" % (ls, max_tabla[t]))
print("total:", dict(cuenta))
