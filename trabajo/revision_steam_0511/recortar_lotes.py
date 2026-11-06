# Prepara los lotes de revisión de género para los ayudantes: deja solo unas líneas de escena
# alrededor de cada frase, en texto compacto, y los reparte en N partes.
# Uso: python recortar_lotes.py [partes=6] [lineas_alrededor=4]
import glob
import json
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
partes = int(sys.argv[1]) if len(sys.argv) > 1 else 6
radio = int(sys.argv[2]) if len(sys.argv) > 2 else 4

lotes = sorted(glob.glob(str(aqui / "lotes" / "lote_[0-9][0-9][0-9].json")))
items = []
for f in lotes:
    for it in json.load(open(f, encoding="utf-8")):
        it["lote"] = Path(f).stem
        items.append(it)


def recorte(it):
    ctx = it.get("ctx") or []
    marca = next((i for i, l in enumerate(ctx) if l.startswith(">>")), None)
    if marca is None:
        return ctx[: radio * 2 + 1]
    return ctx[max(0, marca - radio): marca + radio + 1]


salida = aqui / "recortes"
salida.mkdir(exist_ok=True)
for viejo in salida.glob("parte_*.txt"):
    viejo.unlink()

# Reparte por escenas enteras, para que cada ayudante vea seguidas las frases de una misma escena.
por_parte = (len(items) + partes - 1) // partes
for p in range(partes):
    trozo = items[p * por_parte:(p + 1) * por_parte]
    lineas = []
    for it in trozo:
        lineas.append("### id %s | %s | escena %s | veces %s" % (it["id"], it["lote"], it.get("escena", ""), it.get("veces", "")))
        if not any(l.startswith(">>") for l in it.get("ctx") or []):
            lineas.append(">> " + it["en"] + " || " + it["es"])
        for l in recorte(it):
            lineas.append(l if l.startswith(">>") else "   " + l[:400])
        lineas.append("")
    (salida / ("parte_%d.txt" % (p + 1))).write_text("\n".join(lineas), encoding="utf-8")
    print("parte_%d.txt: %d frases, %d KB" % (p + 1, len(trozo), len("\n".join(lineas).encode()) // 1024))
print("total", len(items), "frases de", len(lotes), "lotes")
