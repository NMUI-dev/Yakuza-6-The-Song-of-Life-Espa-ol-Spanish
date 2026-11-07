# (claude1, 06-11-2026) Correcciones decididas a mano para la v1.0.5 del Y6 (revisión por ESCENAS + barridos fijos).
# Cada una es un cambio de TROZO dentro del español actual de textos.csv v1.0.4 (lo publicado). Comprueba: que el trozo
# esté (una vez), mismas etiquetas <...>, mismos saltos, bytes_max (UTF-8; í = 1 byte, como en la herramienta).
# Escribe correcciones.json (mismo formato que revision_steam_0511) e imprime cada una.
# Uso: python correcciones_v105.py
import csv
import json
import re
from pathlib import Path

aqui = Path(__file__).resolve().parent
TEXTOS = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
csv.field_size_limit(10 ** 9)

# Términos con dos traducciones: el nombre de la tabla (mapa, objeto, habilidad) manda; las frases que lo citan se igualan.
# (término inglés que debe salir en la frase, trozo español actual, trozo nuevo, motivo)
TERMINOS = [
    ("Little Asia", "Little Asia", "Pequeña Asia", "el mapa y el glosario aprobado (01-11) dicen «Pequeña Asia»"),
    ("LITTLE ASIA", "LITTLE ASIA", "PEQUEÑA ASIA", "aviso de misión (caption) de los rótulos rehechos; el usuario confirmó «Pequeña Asia» (06-11)"),
    ("Navy Apartments", "Departamentos Navy", "Apartamentos Navy", "el mapa dice «Apartamentos Navy»"),
    ("Gindaco Highball Tavern", "Gindaco Highball Tavern", "Taberna Gindaco Highball", "nombre de la tienda en el mapa"),
    ("Fuji Soba", "Completa Fuji Soba", "Completa Soba Fuji", "nombre de la tienda en el mapa"),
    ("Fuji Soba", "menú de Fuji Soba", "menú de Soba Fuji", "nombre de la tienda en el mapa"),
    ("Oyster Shack", "Oyster Shack", "Puesto de ostras", "nombre de la tienda en el mapa"),
    ("Otafuku Pawn Shop", "Casa de empeño Otafuku", "Empeños Otafuku", "objetivo de misión: debe coincidir con el mapa"),
    ("Napolitan", "Un Napolitan", "Un napolitano", "el objeto se llama «Napolitano»"),
    ("Napolitan", "un Napolitan", "un napolitano", "el objeto se llama «Napolitano»"),
    ("Sandwich Set", "Surtido de sándwich", "Combo de sándwich", "el plato se llama «Combo de sándwich»"),
    ("Wild Fried Chicken", "Wild Fried Chicken", "Pollo frito Wild", "nombre del objeto"),
    ("Nagasaki Champon", "Nagasaki Champon", "Champon de Nagasaki", "nombre del objeto"),
    ("Jim Beam Highball", "Jim Beam Highball", "Highball Jim Beam", "nombre del objeto"),
    ("Samurai", "Derrota a Samurai", "Derrota a Samurái", "el rival se llama «Samurái»"),
    ("Social Skills Lv.", "Don de gentes Nv.", "Habilidades sociales Nv.", "la habilidad se llama «Habilidades sociales»"),
    ("Forkball", ">Forkball<", ">Bola de tenedor<", "el lanzamiento se llama «Bola de tenedor» en el centro de bateo"),
    ("Morning Glory Photo", "«Foto de Morning Glory»", '"Foto del orfanato Morning Glory"', "nombre del objeto; comillas rectas: la fuente no tiene « »"),
    ("Morning Glory Waistband", "«Faja de Morning Glory»", '"Faja del Morning Glory"', "nombre del objeto; comillas rectas: la fuente no tiene « »"),
]

# Una a una: (id, trozo actual, trozo nuevo, tipo, motivo)
UNA = [
    ("160", "Y un cuerno no tardarás.", "¡Sí, cómo no! Seguro que no tardas.", "localización",
     "«Like hell you won't» contesta a «no tardaré»: «y un cuerno» es de España y queda raro; se localiza la ironía"),
    ("201", "un poco poco convencional", "un poco fuera de lo común", "errata", "palabra repetida «poco poco»"),
]

filas = {r["id"]: r for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";")}


def tam(s):
    return len(s.encode("utf-8")) - s.count("í")


def norm(s):
    return s.replace("\r\n", "\n")


pedidas = []  # (id, viejo, nuevo, tipo, motivo)
for en, viejo, nuevo, motivo in TERMINOS:
    for r in filas.values():
        if en in r["ingles"] and viejo in norm(r["espanol"]):
            pedidas.append((r["id"], viejo, nuevo, "término", motivo))
pedidas += UNA
EXTRA = aqui / "decididas_escenas.json"   # las de la revisión por escenas, verificadas a mano: [[id, viejo, nuevo, tipo, motivo]]
if EXTRA.exists():
    pedidas += [tuple(x) for x in json.load(open(EXTRA, encoding="utf-8"))]

salida, fallos = {}, 0
for idt, viejo, nuevo, tipo, motivo in pedidas:
    r = filas.get(idt)
    problema = []
    if not r:
        problema.append("no existe el id")
    else:
        base = salida[idt]["es"] if idt in salida else norm(r["espanol"])
        vacia = viejo == "" and base == ""   # frase que estaba vacía (salía en inglés): se traduce entera
        ref = norm(r["ingles"]) if vacia else base  # con qué se comparan etiquetas y saltos
        if not vacia and base.count(viejo) != 1:
            problema.append("el trozo sale %d veces" % base.count(viejo))
        else:
            nueva = nuevo if vacia else base.replace(viejo, nuevo)
            base = ref
            if re.findall(r"<[^>]*>", nueva) != re.findall(r"<[^>]*>", base):
                problema.append("etiquetas")
            # «largo»: un subtítulo de una línea que no cabía puede pasar a dos (un espacio pasa a salto: mismos bytes)
            if nueva.count("\n") != base.count("\n") and not (tipo == "largo" and nueva.count("\n") == base.count("\n") + 1):
                problema.append("saltos")
            if r["bytes_max"].strip() and tam(nueva) > int(r["bytes_max"]):
                problema.append("bytes %d > %s" % (tam(nueva), r["bytes_max"]))
            if not problema:
                prev = salida.get(idt)
                salida[idt] = {"en": norm(r["ingles"]), "antes": prev["antes"] if prev else norm(r["espanol"]), "es": nueva,
                               "tipo": tipo if not prev else prev["tipo"] + "+" + tipo,
                               "motivo": motivo if not prev else prev["motivo"] + "; " + motivo,
                               "veces": int(r["veces"] or 1), "donde": r["donde"]}
    fallos += bool(problema)
    print(("FALLO " if problema else "OK    ") + idt + " | " + tipo + " | " + viejo[:40] + " -> " + nuevo[:40]
          + ("  [" + "; ".join(problema) + "]" if problema else ""))

# Separador de miles: el juego (y el inglés) usa la coma en la mayoría de textos («50,000 yenes»); los que usan punto
# («10.000 Pts») se igualan. Mismo número de bytes: las tablas alineadas con espacios no se descuadran.
MILES = re.compile(r"\b(\d{1,3})\.(\d{3})\b(?![.,]\d)")
for idt, r in filas.items():
    base = salida[idt]["es"] if idt in salida else norm(r["espanol"])
    if MILES.search(base) and not MILES.search(norm(r["ingles"])):
        nueva = MILES.sub(r"\1,\2", base)
        prev = salida.get(idt)
        salida[idt] = {"en": norm(r["ingles"]), "antes": prev["antes"] if prev else norm(r["espanol"]), "es": nueva,
                       "tipo": (prev["tipo"] + "+" if prev else "") + "número",
                       "motivo": (prev["motivo"] + "; " if prev else "") + "separador de miles con coma, como el resto del juego",
                       "veces": int(r["veces"] or 1), "donde": r["donde"]}
        print("OK    " + idt + " | número | miles con punto -> coma")

json.dump(salida, open(aqui / "correcciones.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
por_tipo = {}
for c in salida.values():
    por_tipo[c["tipo"]] = por_tipo.get(c["tipo"], 0) + 1
print("\ncorrecciones.json:", len(salida), "frases | fallos:", fallos, "| por tipo:", por_tipo)
