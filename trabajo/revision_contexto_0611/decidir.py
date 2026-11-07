# (claude1, 06-11-2026) Apunta decisiones tomadas a mano sobre los avisos de los revisores (con la escena delante, ver.py).
#   python decidir.py si ID "trozo actual" "trozo nuevo" TIPO "motivo"   -> decididas_escenas.json (las usa correcciones_v105.py)
#   python decidir.py no ID "por qué no"                                -> rechazadas.json (para las cifras del informe)
# Tipos: respuesta, trato, partida, referente, género, sentido, localización, errata, españa, término
import json
import sys
from pathlib import Path

aqui = Path(__file__).resolve().parent


def cargar(n):
    p = aqui / n
    return json.load(open(p, encoding="utf-8")) if p.exists() else []


def guardar(n, d):
    json.dump(d, open(aqui / n, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


modo = sys.argv[1]
if modo == "si":
    _, _, idt, viejo, nuevo, tipo, motivo = sys.argv
    d = [x for x in cargar("decididas_escenas.json") if not (x[0] == idt and x[1] == viejo)]
    d.append([idt, viejo.replace(" / ", "\n"), nuevo.replace(" / ", "\n"), tipo, motivo])  # « / » = salto, como en ver.py
    guardar("decididas_escenas.json", d)
    print("si", idt, len(d))
else:
    _, _, idt, motivo = sys.argv
    d = [x for x in cargar("rechazadas.json") if x[0] != idt]
    d.append([idt, motivo])
    guardar("rechazadas.json", d)
    print("no", idt, len(d))
