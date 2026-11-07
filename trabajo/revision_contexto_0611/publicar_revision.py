# (claude1, 06-11-2026) Copia las herramientas de la revisión por escenas a una carpeta «revision» de las herramientas
# públicas, cambiando las rutas de este PC por rutas relativas a la carpeta «Herramientas para traduccion».
# Uso: python publicar_revision.py "<carpeta Herramientas para traduccion>"
import re
import shutil
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
herr = Path(sys.argv[1])
dest = herr / "revision"
dest.mkdir(exist_ok=True)

RUTAS = '''# Rutas de la revisión, relativas a la carpeta «Herramientas para traduccion» (la de herramienta_traduccion.py).
from pathlib import Path

HERR = Path(__file__).resolve().parent.parent
TEXTOS = HERR / "trabajo" / "textos.csv"            # lo saca «EXTRAER textos.bat»
ARMP = HERR / "trabajo" / "en" / "db_json"           # tablas inglesas en JSON (también las saca EXTRAER)
TALK_EN = HERR / "trabajo" / "en" / "talk_todo"      # talk.par inglés extraído (también lo saca EXTRAER)
TALK_INDICE = HERR / "datos" / "talk_indice.csv"
HABLANTES = HERR / "datos" / "hablantes_y6.json"     # número de hablante -> nombre y género
GUIA = HERR / "datos" / "GUIA_TRADUCCION.md"
FICHA = HERR / "datos" / "PERSONAJES_Y_GENERO.md"
CUOTAS = Path(__file__).resolve().parent / "cuotas.json"
'''
(dest / "rutas.py").write_text(RUTAS, encoding="utf-8")

CAMBIOS = [
    (r'TEXTOS = Path\(r"[^"]+"\)', "TEXTOS = R.TEXTOS"),
    (r'TEXTOS = r"[^"]+"', "TEXTOS = R.TEXTOS"),
    (r'ARMP = T / "armp_json"', "ARMP = R.ARMP"),
    (r'T = Path\(r"C:\\mods\\yakuza6\\trabajo"\)\n', ""),
    (r'hab = json.load\(open\(T / "revision_steam_0511" / "hablantes_y6.json", encoding="utf-8"\)\)',
     'hab = json.load(open(R.HABLANTES, encoding="utf-8"))'),
    (r'CUOTAS = Path\("[^"]+"\)', "CUOTAS = R.CUOTAS"),
    (r'open\("C:/mods/yakuza6/trabajo/lotes/GUIA_TRADUCCION.md"', "open(R.GUIA"),
    (r'open\("C:/Mods/NOTAS_AGENTES/COMUN/TRADUCCIONES/YAKUZA_PERSONAJES_Y_GENERO.md"', "open(R.FICHA"),
]
ARCHIVOS = ["armar_escenas.py", "armar_textos.py", "revisar_escenas.py", "ver.py", "decidir.py", "pendientes.py",
            "correcciones_v105.py", "barrido_fijo.py", "terminos_dobles.py", "tu_usted.py"]
for n in ARCHIVOS:
    s = (aqui / n).read_text(encoding="utf-8")
    for a, b in CAMBIOS:
        s = re.sub(a, lambda m: b, s)
    if "R." in s:
        s = re.sub(r"(\nimport [^\n]+\n)", r"\1import rutas as R\n", s, count=1) if "\nimport " in s else "import rutas as R\n" + s
        s = s.replace("import rutas as R\n", "import sys as _s; _s.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))\nimport rutas as R\n", 1)
    for viejo in ("C:\\mods", "C:/mods", "C:\\Mods", "C:/Mods"):
        if viejo in s and n != "armar_escenas.py":
            print("OJO: queda una ruta de este PC en", n)
    (dest / ("correcciones.py" if n == "correcciones_v105.py" else n)).write_text(s, encoding="utf-8")

# las charlas de talk.par: en la versión pública salen del índice de la herramienta (no de talk_ingles.csv)
p = dest / "armar_escenas.py"
s = p.read_text(encoding="utf-8")
viejo = s[s.index("# 3) charlas de talk.par"):s.index("# paquetes:")]
nuevo = '''# 3) charlas de talk.par (por escena, en orden de offset), leídas del talk.par inglés que extrae la herramienta
talk = OrderedDict()
for r in csv.DictReader(open(R.TALK_INDICE, encoding="utf-8-sig", newline=""), delimiter=";"):
    talk.setdefault(r["escena"].replace("\\\\", "/"), []).append(int(r["offset"]))
for esc, offs in talk.items():
    datos = open(R.TALK_EN / esc / "cmn.par" / "cmn.bin", "rb").read()
    ls = [linea(datos[o:datos.index(0, o)].decode("utf-8")) for o in sorted(offs)]
    ls = [x for x in ls if x]
    if ls:
        escenas["charla " + esc] = ls

'''
s = s.replace(viejo, nuevo)
p.write_text(s, encoding="utf-8")
for n in ("poner_correcciones.py",):
    s = (aqui.parent / "revision_steam_0511" / n).read_text(encoding="utf-8")
    (dest / n).write_text(s, encoding="utf-8")
shutil.copy(aqui.parent / "revision_steam_0511" / "hablantes_y6.json", herr / "datos" / "hablantes_y6.json")
shutil.copy(Path(r"C:\mods\yakuza6\trabajo\lotes\GUIA_TRADUCCION.md"), herr / "datos" / "GUIA_TRADUCCION.md")
print("copiadas en", dest, sorted(x.name for x in dest.iterdir()))
