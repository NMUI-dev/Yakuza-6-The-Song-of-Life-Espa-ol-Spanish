# (claude1, 06-11-2026) Tú/usted en el Y6, adaptado de yakuza5/trabajo/revision_contexto_0611/mezcla.py (claude2):
# dentro de un tramo seguido de la escena, el MISMO hablante (mismo número P) que trata de usted y de tú.
# Lee los paquetes de armar_escenas.py (solo las listas de habla llevan número de hablante). Salida: tu_usted.txt
import collections
import re
from pathlib import Path

aqui = Path(__file__).resolve().parent
T = re.compile(r"\b(tú|te|ti|contigo|tu|tus|tuyo|tuya|oye|mira|(?<!una )(?<!la )(?<!mi )(?<!simple )disculpa|perdona|espera|ven|dime|fíjate|cuídate|quieres|"
               r"puedes|tienes|eres|estás|sabes|has|vienes|vuelve|dijiste|hiciste|viniste)\b", re.I)
U = re.compile(r"\b(usted|disculpe|perdone|oiga|dígame|mire|espere|venga|cálmese|quiere usted|puede usted|desea|"
               r"sabe usted|cuídese|vuelva|le agradezco|lo espera|su ayuda)\b", re.I)
VENT = 8
LINEA = re.compile(r"^#(\S+)(?: x\d+)? \[(P\d+)[^\]]*\] (.*?) \|\| (.*)$")


def marca(es):
    e = re.sub(r"<[^>]*>|\{[^}]*\}|\([^)]*\)", " ", es)  # sin etiquetas ni pensamientos entre paréntesis
    return ("T" if T.search(e) else "") + ("U" if U.search(e) else "")


import json
CORR = json.load(open(aqui / "correcciones.json", encoding="utf-8"))
escenas = collections.OrderedDict()
for p in sorted(aqui.glob("paquetes/paquete_*.txt")):
    act = None
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.startswith("=== ESCENA "):
            act = escenas.setdefault(re.sub(r" \(parte \d+\)", "", l[11:-4]), [])
            continue
        m = LINEA.match(l)
        if m and act is not None and m.group(1) not in [x[0] for x in act[-6:]]:
            g = list(m.groups())
            if g[0] in CORR:  # (06-11) con las correcciones ya decididas, para ver lo que de verdad queda
                g[3] = CORR[g[0]]["es"].replace("\n", " / ")
            act.append(tuple(g))

casos, n = [], 0
with open(aqui / "tu_usted.txt", "w", encoding="utf-8") as o:
    for nombre, L in escenas.items():
        mk = [marca(x[3]) for x in L]
        idx = set()
        for i, x in enumerate(L):
            if mk[i] != "U":
                continue
            for k in range(max(0, i - VENT), min(len(L), i + VENT + 1)):
                if k != i and L[k][1] == x[1] and mk[k] == "T":
                    idx.update([i, k])
        if not idx:
            continue
        n += 1
        o.write("### %s\n" % nombre)
        lo, hi = max(0, min(idx) - 3), min(len(L), max(idx) + 4)
        for k in range(lo, hi):
            y = L[k]
            o.write(("%s#%s [%s] %s || %s\n" % (">> " if k in idx else "   ", y[0], y[1], y[2], y[3])))
        casos.append((nombre, len(idx)))
print("escenas con mezcla", n, "| líneas marcadas", sum(c for _, c in casos))
