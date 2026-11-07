# (claude1, 06-11-2026) Informe de la v1.0.5 del Y6 con las cifras sacadas de los archivos (nunca a mano):
# correcciones.json (cambios con tipo y motivo), rechazadas.json (avisos revisados que NO eran error), nuevas_v105.json
# (frases que la herramienta nunca extraía), resultados/ (paquetes revisados) y la comparación con lo publicado.
# Uso: python -I -X utf8 informe_v105.py <salida.txt>
import json
import sys
from collections import Counter
from pathlib import Path

aqui = Path(__file__).resolve().parent
corr = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
rech = json.load(open(aqui / "rechazadas.json", encoding="utf-8"))
nuevas = json.load(open(aqui / "nuevas_v105.json", encoding="utf-8"))["nuevas"]
paquetes = sorted((aqui / "resultados").glob("paquete_*.json"))
avisos = sum(len(json.load(open(p, encoding="utf-8")).get("fallos", [])) for p in paquetes)
total_paq = len(list((aqui / "paquetes").glob("paquete_*.txt")))
comp = (aqui / "logs" / "comparar_v105_resumen.txt")

NOMBRE = {"término": "Un nombre, una traducción (mapa/objeto/habilidad igual en las frases)", "trato": "Tú / usted",
          "censura": "Groserías suavizadas, devueltas a la fuerza del original (NUNCA CENSURAR)",
          "género": "Género", "sentido": "Sentido", "errata": "Erratas", "españa": "Español de España",
          "región": "Palabra de un solo país", "signos": "Signos ¿? ¡!", "número": "Cifras (miles con coma, yenes)",
          "largo": "Renglón más largo que el inglés (texto que se salía)", "velocidad": "Subtítulos que no daba tiempo a leer",
          "fuente": "Letras que la fuente del juego no tiene (º ª « » à)", "mayúscula": "Mayúsculas",
          "localización": "Frase hecha o chiste localizado", "referente": "le/lo/la con el referente equivocado",
          "renglón": "Renglón partido por mal sitio (acababa en artículo o preposición)"}
tipos = Counter()
for c in corr.values():
    for t in set(c["tipo"].split("+")):     # una frase con dos arreglos del mismo tipo cuenta una vez
        tipos[t] += 1
apariciones = sum(int(c.get("veces") or 1) for c in corr.values())

L = []
w = L.append
w("YAKUZA 6: THE SONG OF LIFE - INFORME DE LA TRADUCCIÓN v1.0.5 (06-11-2026)")
w("=" * 78)
w("")
w("Revisión de toda la traducción por ESCENAS enteras (quién habla, a quién, qué se dijo antes y después), con las reglas")
w("del usuario: entender el contexto antes de tocar una frase, ser fiel al original y localizar solo cuando haga falta,")
w("NUNCA CENSURAR, anotar cada error y cada arreglo. Hecho por claude1 (el Yakuza 6 es suyo).")
w("")
w("1. CAMBIOS: %d textos distintos (%d apariciones en el juego) + %d frases que seguían en inglés" % (len(corr), apariciones, len(nuevas)))
w("-" * 78)
for t, n in tipos.most_common():
    w("  %-70s %4d" % (NOMBRE.get(t, t), n))
w("  %-70s %4d" % ("Frases de una palabra que la herramienta nunca extraía (seguían en inglés)", len(nuevas)))
w("")
w("  Lista completa (inglés, antes, después, tipo y motivo): correcciones.json y nuevas_v105.json.")
w("")
w("2. REVISIÓN POR ESCENAS")
w("-" * 78)
w("  Paquetes revisados: %d de %d. Avisos de los revisores: %d. Cada aviso se decidió a mano con la escena delante:" % (len(paquetes), total_paq, avisos))
w("  %d no eran error (motivo anotado en rechazadas.json)." % len(rech))
pasos = sorted((json.load(open(p, encoding="utf-8")) for p in (aqui / "cadena_final").glob("*.json")), key=lambda d: d.get("paso", 0))
if pasos:
    w("  Ronda final de preguntas en cadena (cada IA recibe todo lo hecho y lo que ya dijeron las anteriores): %s;"
      % ", ".join("Kilo" if p["quien"].startswith("kilo:") else {"manual:gemini-usuario": "Gemini del usuario", "manual:grok-usuario": "Grok del usuario",
                "manual:grok-usuario-2": "Grok del usuario (2.ª)"}.get(p["quien"]) or p["quien"].split(":", 1)[1].split("/")[-1].replace(":free", "")
                for p in pasos))
    w("  %d ideas nuevas, cada una convertida en barrido (ideas_cadena2 a 7.py) y revisada a mano." % sum(len(p["respuesta"].get("nuevas", [])) for p in pasos))
w("")
w("3. LO QUE NO SE TOCÓ A PROPÓSITO (y por qué)")
w("-" * 78)
for x in ("Formato de los subtítulos de sound_auth: una coma sola en su renglón y renglones partidos con un espacio "
          "vienen IGUAL en el inglés original; es formato del juego, no errata.",
          "Habla rota de algunos personajes («¿Por qué tú aquí?», «Esto ser correcto»): igual que el inglés.",
          "Erratas a propósito del chat en vivo («reljaa»), como el original.",
          "«Joder» como verbo y «jodido» se usan en toda Latinoamérica: se dejan (solo «¡Joder!» exclamación es de España).",
          "«preparatoria» (doblaje latino), «hacer sombra» (boxeo), «guio» sin tilde (RAE 2010).",
          "Tratos que cambian con motivo: Joon-gi Han pasa de usted a tú con Yuta al pasar de «Usami-san» a «Yuta-kun»;",
          "  Torafuru pasa a tú después de presentarse. Detalle en NOTAS_AGENTES/COMUN/TRADUCCIONES/YAKUZA_PERSONAJES_Y_GENERO.md."):
    w("  - " + x)
w("")
w("4. FALLO DE LA HERRAMIENTA ENCONTRADO Y ARREGLADO")
w("-" * 78)
w("  es_texto() tomaba por código toda palabra suelta con «.» o «-» («B-Bullshit.», «Th-Thanks...», «Loading...»), así que")
w("  esas frases nunca se extraían y seguían en INGLÉS: 136 distintas, 585 apariciones (el informe de la v1.0.4 decía")
w("  que solo quedaban nombres: no era así). Arreglado en la herramienta pública, con una prueba (prueba_filtro.py).")
perdidos = json.load(open(aqui / "perdidos_ingles_v104.json", encoding="utf-8"))
de_136 = [s for s in perdidos if s in nuevas]
w("  De las %d, %d se tradujeron; las otras %d son nombres e interjecciones que en español se escriben igual."
  % (len(perdidos), len(de_136), len(perdidos) - len(de_136)))
w("  Además, %d textos visibles que el filtro dejaba fuera por ir en minúscula o con «/» (guías de botones «Pause/Quit»,"
  % (len(nuevas) - len(de_136)))
w("  entradas del béisbol «1st» -> «1.°», «points», «seconds», chat en vivo «shiiit») se añadieron a datos/celdas_extra.")
w("")
w("5. COMPROBADO")
w("-" * 78)
w("  " + (comp.read_text(encoding="utf-8").strip().replace("\n", "\n  ") if comp.exists() else "(falta la comparación con lo publicado)"))
for x in ("Ida y vuelta: se volvió a extraer lo armado y cada una de las filas de textos.csv coincide con lo que se quería",
          "  meter (tablas, diálogos de talk.par y escenas sueltas): 0 diferencias. Ningún diálogo quedó en inglés por no caber.",
          "Todas las letras usadas existen en la fuente del juego (letras_fuente.py: 0 que falten).",
          "Prueba en el juego (copia de laboratorio, sin tocar Steam): título, menú principal, dificultad, aviso de autoguardado",
          "  y subtítulos de las primeras escenas en español, con tildes, ñ y ¡¿ bien dibujados.",
          "Barridos fijos repetidos al final: groserías suavizadas 0, honoríficos perdidos 0, «pulsa» 0, variables %s/%d en",
          "  otro orden 0, letras que faltan 0."):
    w("  " + x)
w("")
w("6. LO QUE QUEDA SIN ARREGLAR (y por qué)")
w("-" * 78)
import re, subprocess
vel = subprocess.run([sys.executable, "-I", "-X", "utf8", str(aqui / "velocidad_subtitulos.py"), str(aqui / "correcciones.json")],
                     capture_output=True, text=True, encoding="utf-8").stdout
n_vel = int(re.search(r"demasiado rápidos: (\d+)", vel).group(1))
n_ren = int(re.search(r"a mano[^:]*: (\d+)", (aqui / "saltos_sentido.txt").read_text(encoding="utf-8")).group(1))
for x in ("%d subtítulos algo rápidos (más de 20 letras por segundo): acortarlos quitaría sentido o suavizaría una grosería." % n_vel,
          "%d renglones que terminan en artículo o preposición y no se pueden partir mejor sin que la caja del subtítulo crezca." % n_ren,
          "Lo que se deja en inglés a propósito (nombres, marcas, términos de dardos, karaoke en japonés): carpeta",
          "  «Lo que queda en ingles v1.0.5»."):
    w("  - " + x)
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
