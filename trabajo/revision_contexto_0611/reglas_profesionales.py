# (claude1, 06-11-2026) Reglas de traductores profesionales que aún no medíamos (fuentes en
# NOTAS_AGENTES/COMUN/TRADUCCIONES/REGLAS_PROFESIONALES.md: guía de subtítulos de Netflix para español latino, guía de
# estilo de Microsoft para español neutro, lista de fallos de localización de Inlingo). Solo MARCA candidatos sobre lo
# publicado (v1.0.4) + correcciones.json; cada uno se decide a mano con la escena delante (ver.py / decidir.py).
# Uso: python -I reglas_profesionales.py [máx. ejemplos por regla=15]  -> reglas_profesionales.txt
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

aqui = Path(__file__).resolve().parent
TEXTOS = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
csv.field_size_limit(10 ** 9)
maxi = int(sys.argv[1]) if len(sys.argv) > 1 else 15
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))

filas = []
for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"):
    es = corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]
    filas.append((r["id"], r["donde"], r["ingles"], es))

ETQ = re.compile(r"<[^>]*>|\$\{[^}]*\}|%[sdif]|\{\d+\}")
PAL = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")

# palabras que en el texto aparecen en minúscula muchas veces = palabras comunes (no nombres propios)
minus = Counter()
for _, _, _, es in filas:
    for w in PAL.findall(ETQ.sub(" ", es)):
        if w.islower():
            minus[w] += 1

hallado = defaultdict(list)


def marca(regla, idt, donde, en, es, nota=""):
    hallado[regla].append("#%s [%s] %s || %s%s" % (idt, donde.split("|")[0].strip(), en.replace("\n", " / ")[:90],
                                                    es.replace("\n", " / ")[:110], ("  <- " + nota) if nota else ""))


MESES = r"Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre"
DIAS = r"Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo"
IDIOMAS = r"Inglés|Japonés|Chino|Coreano|Español|Francés|Alemán|Italiano|Ruso|Japonesa|Coreana|Estadounidense"
MEDIO = re.compile(r"(?<=[a-záéíóúñ,] )(%s|%s|%s)\b" % (MESES, DIAS, IDIOMAS))
UNIDADES = re.compile(r"\b(?:feet|foot|ft|inch(?:es)?|pounds?|lbs?|miles?|mph|yards?|ounces?|oz|gallons?|°F|Fahrenheit)\b")
CENSURA = re.compile(r"\b[A-Za-z]\*{2,}|\b[A-Za-z]-{2,}\b|\*{3,}")
SR = re.compile(r"\b(Sr|Sra|Srta)\.(?!\s+[A-ZÁÉÍÓÚ])")
PUNTO_TRAS = re.compile(r"[?!]\.(?!\.)")
COMPUESTO = re.compile(r"\b(?:he|has|ha|hemos|han)\s+(?:\w+(?:ado|ido|cho|sto|to|rto))\b", re.I)
CUATRO = re.compile(r"(?<!\.)\.{4,}|\.\s\.\s\.|…")

for idt, donde, en, es in filas:
    if not es.strip() or es == en:
        continue
    lim = ETQ.sub(" ", es)
    pal_en = PAL.findall(ETQ.sub(" ", en))
    pal_es = PAL.findall(lim)
    # 1 Mayúsculas de título del inglés copiadas (en español solo la primera palabra y los nombres propios)
    # solo títulos: inglés sin signos de frase y con todas sus palabras largas en mayúscula; en español, palabras comunes
    # con mayúscula que no van detrás de un signo de frase
    if 2 <= len(pal_en) <= 7 and not re.search(r"[.?!,]", en) and all(w[0].isupper() for w in pal_en if len(w) > 3) \
            and "\n" not in es and not es.isupper():
        malas = [m.group(0) for m in PAL.finditer(lim) if m.start() > 0 and m.group(0)[0].isupper()
                 and not m.group(0).isupper() and not re.search(r"[.?!¿¡:\-\"(]\s*$", lim[:m.start()])
                 and minus[m.group(0).lower()] >= 5]
        if malas:
            marca("1 mayúsculas de título en inglés", idt, donde, en, es, ", ".join(malas))
    # 2 meses, días e idiomas con mayúscula en medio de frase
    m = MEDIO.search(lim)
    if m:
        marca("2 mes/día/idioma con mayúscula", idt, donde, en, es, m.group(1))
    # 3 unidades inglesas sin pasar a métrico (salvo que la cifra importe para la historia)
    if UNIDADES.search(en):
        marca("3 unidades inglesas", idt, donde, en, es, UNIDADES.search(en).group(0))
    # 4 groserías censuradas en el original (inicial + puntos: «hijo de p...»)
    if CENSURA.search(en):
        marca("4 censura del original", idt, donde, en, es, CENSURA.search(en).group(0))
    # 5 «Sr.» abreviado sin nombre detrás
    if SR.search(lim):
        marca("5 Sr./Sra. sin nombre", idt, donde, en, es)
    # 6 punto después de ? o !
    if PUNTO_TRAS.search(lim):
        marca("6 punto tras ? o !", idt, donde, en, es)
    # 7 puntos suspensivos raros (4 o más, con espacios, o el carácter … si la fuente no lo tiene)
    if CUATRO.search(lim):
        marca("7 puntos suspensivos raros", idt, donde, en, es, CUATRO.search(lim).group(0))
    # 8 pretérito perfecto compuesto (en Latinoamérica se prefiere el simple: «ya comiste», no «ya has comido»)
    for m in COMPUESTO.finditer(lim):
        hallado["_compuesto"].append(m.group(0).lower())
        if re.search(r"\b(?:ya|hoy|esta mañana|esta noche|acab|recién|just|already)\b", lim + " " + en, re.I):
            marca("8 perfecto compuesto en pasado reciente", idt, donde, en, es, m.group(0))
            break

with open(aqui / "reglas_profesionales.txt", "w", encoding="utf-8") as o:
    for regla in sorted(k for k in hallado if not k.startswith("_")):
        v = hallado[regla]
        o.write("== %s: %d\n" % (regla, len(v)))
        for x in v[:maxi]:
            o.write("  " + x + "\n")
    c = Counter(hallado["_compuesto"])
    o.write("== perfecto compuesto en total: %d (más usados: %s)\n" % (sum(c.values()), ", ".join(
        "%s %d" % kv for kv in c.most_common(12))))
for regla in sorted(hallado):
    print(regla, len(hallado[regla]))
