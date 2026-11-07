# (claude1, 06-11-2026) Paquetes extra para la revisión por contexto: textos que NO son diálogo pero hablan de personas o
# las hacen hablar (correos, misiones, subhistorias, redes sociales, chat en vivo, perfiles, pantallas de carga, mensajes).
# Van en orden de id (= orden de la tabla) y agrupados por tabla. Numera a partir del último paquete que ya exista, para no
# pisar los que los revisores ya tienen. Uso: python armar_textos.py [KB=45]
import csv
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent
TEXTOS = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv")
KB = int(sys.argv[1]) if len(sys.argv) > 1 else 45
# (06-11) tablas extra por argumento: python armar_textos.py 45 manual minigame_ pause_tutorial ...
csv.field_size_limit(10 ** 9)
TABLAS = ["pause_mail", "mission_kind", "complete", "pause_sns", "pause_profile", "loading_text", "msg |",
          "minigame_live_chat_chat_messages", "minigame_snack_common_message", "minigame_sandlot_baseball_comment_log",
          "minigame_sandlot_baseball_player", "clan_creator_mission", "player_skill | unlocked_message", "caption"]
YA = list(TABLAS)
if len(sys.argv) > 2:
    TABLAS = sys.argv[2:]

grupos = {}
for r in csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"):
    d = r["donde"].split(" + ")[0]
    t = next((t for t in TABLAS if d.startswith(t)), None)
    if len(sys.argv) > 2 and any(d.startswith(y) for y in YA):
        continue
    if not t or not r["espanol"].strip():
        continue
    marca = " x%s" % r["veces"] if r["veces"] not in ("", "1", "2") else ""
    grupos.setdefault(d, []).append("#%s%s %s || %s" % (r["id"], marca, r["ingles"].replace("\r\n", "\n").replace("\n", " / "),
                                                       r["espanol"].replace("\r\n", "\n").replace("\n", " / ")))

sal = aqui / "paquetes"
n = max(int(p.stem.split("_")[1]) for p in sal.glob("paquete_*.txt")) + 1
primero = n
act, tam = [], 0


def volcar():
    global n, act, tam
    if act:
        (sal / ("paquete_%03d.txt" % n)).write_text("\n".join(act), encoding="utf-8")
        n, act, tam = n + 1, [], 0


for d, ls in grupos.items():
    for i in range(0, len(ls), 200):
        txt = "=== ESCENA texto (no es diálogo: %s) ===\n%s\n" % (d, "\n".join(ls[i:i + 200]))
        b = len(txt.encode("utf-8"))
        if act and tam + b > KB * 1024:
            volcar()
        act.append(txt)
        tam += b
volcar()
print("tablas", len(grupos), "textos", sum(len(v) for v in grupos.values()), "paquetes nuevos", primero, "a", n - 1)
