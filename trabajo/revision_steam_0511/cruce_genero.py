# Segunda pasada de género (Y6): con el género de cada hablante (recortes/hablantes.json + correcciones manuales de
# GENERO_EXTRA), busca en las listas de habla frases donde quien habla se describe con un adjetivo del otro género
# («estoy segura» dicho por un hombre) o le habla así a quien tiene al lado («¿estás lista?» a un hombre).
# Solo marca candidatos: se deciden a mano. Uso: python cruce_genero.py > cruce_genero.txt
import csv
import glob
import json
import re
from pathlib import Path

aqui = Path(__file__).resolve().parent
ARMP = Path(r"C:\mods\yakuza6\trabajo\armp_json")
TEXTOS = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos_v103_publicada.csv")

genero = {}
for p, v in json.load(open(aqui / "recortes" / "hablantes.json", encoding="utf-8")).items():
    gs = {str(h.get("genero", "")).strip().upper()[:1] for h in v} - {""}
    if len(gs) == 1:
        genero[int(p.lstrip("Pp"))] = gs.pop()
genero[1679] = "H"

es_de = {}
for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"):
    es_de.setdefault(r["ingles"].replace("\r\n", "\n").strip(), (r["id"], r["espanol"].replace("\r\n", "\n")))

RAICES = ("segur list cansad preocupad sol enojad aliviad equivocad content emocionad nervios enamorad sorprendid "
          "ocupad encantad agradecid avergonzad convencid perdid asustad celos hart dispuest borrach llen molest "
          "confundid decepcionad impresionad orgullos tranquil curios honrad obligad interesad aburrid ansios "
          "agotad emborrachad excitad relajad acostumbrad apenad halagad sincer dormid despiert solit prepara").split()
ADJ = r"(?:muy |tan |bastante |un poco |algo |re |súper |super)?(" + "|".join(RAICES) + r")(o|a|os|as)\b"
YO = re.compile(r"\b(?:estoy|soy|estaba|estaré|estuve|me siento|me sentí|me quedé|quedé|me pongo|me puse|ando)\s+" + ADJ, re.I)
TU = re.compile(r"\b(?:estás|eres|estabas|estarás|te sientes|te ves|pareces|andas)\s+" + ADJ, re.I)


def contrario(g, fin):
    return (g == "H" and fin.startswith("a")) or (g == "M" and fin.startswith("o"))


n = 0
for f in sorted(glob.glob(str(ARMP / "sound_auth_subtitles_speech_list_*.bin.json"))):
    t = json.load(open(f, encoding="utf-8"))
    filas = [t.get(str(i), {}).get("", {}) for i in range(t["ROW_COUNT"])]
    filas = [(x.get("1"), x["4"].replace("\r\n", "\n").strip()) for x in filas if isinstance(x.get("4"), str)]
    escena = Path(f).name[len("sound_auth_subtitles_speech_list_"):-len(".bin.json")]
    for i, (quien, en) in enumerate(filas):
        if en not in es_de:
            continue
        idt, es = es_de[en]
        marcas = []
        g = genero.get(quien)
        for m in YO.finditer(es):
            if g and contrario(g, m.group(2)):
                marcas.append("habla %s y dice «%s»" % (g, m.group(0)))
        otros = [q for q, _ in filas[max(0, i - 2): i + 3] if q != quien]
        go = {genero.get(q) for q in otros} - {None}
        for m in TU.finditer(es):
            if len(go) == 1 and contrario(next(iter(go)), m.group(2)):
                marcas.append("le habla a %s y dice «%s»" % (next(iter(go)), m.group(0)))
        if marcas:
            n += 1
            print("### %s | %s | P%s | %s" % (idt, escena, quien, "; ".join(marcas)))
            for q, e in filas[max(0, i - 3): i + 3]:
                print("   %s[P%s] %s" % (">> " if e == en else "", q, e.replace("\n", " / ")[:120]))
print("candidatos:", n, "| hablantes con género:", len(genero))
