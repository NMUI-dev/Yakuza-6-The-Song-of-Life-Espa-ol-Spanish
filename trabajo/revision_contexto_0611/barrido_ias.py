# (claude1, 06-11-2026) Comprobaciones que propusieron las IA consultadas (Gemini, Grok, OpenRouter, Kilo, GLM) y que no
# teníamos. Solo marca: se decide a mano. Uso: python barrido_ias.py [correcciones.json] > barrido_ias.txt
#  NUMERO     separador de miles distinto del que usa la mayoría del juego (50,000 frente a 50.000)
#  HONOR      honorífico del inglés (-san, -chan, -kun, -sama, aniki, kyodai, oyabun) que falta en el español
#  REGION     regionalismo fuerte de un solo país (órale, chévere, boludo...): la guía pide neutro latinoamericano
#  GUION      palabra partida con guion al final de una línea
import collections
import csv
import json
import re
import sys

csv.field_size_limit(10 ** 9)
TEXTOS = r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos.csv"
corr = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else {}
filas = list(csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"))
HONOR = re.compile(r"(?<=\w)-(san|chan|kun|sama|senpai|sensei|han|aniki)\b|\b(aniki|kyodai|oyabun|oyaji|nee-san|onii-chan)\b", re.I)
REGION = re.compile(r"\b(órale|ándale|chido|chida|güey|wey|neta|chamba|pinche|cuate|mande|chévere|bacán|bacano|boludo|pibe|"
                    r"laburo|che|guita|plata(?= (para|de|que))|cachai|parcero|parce|chamo|pana|vaina|weón|huevón|"
                    r"gonorrea|chimba|gringo|chafa|fresa|naco|padrísimo|qué padre|sale y vale|al chile)\b", re.I)
cuenta = collections.Counter()
miles = collections.Counter()


def es_de(r):
    return corr[r["id"]]["es"] if r["id"] in corr else r["espanol"]


for r in filas:
    for m in re.finditer(r"\b\d{1,3}([.,])\d{3}\b(?![.,]\d)", es_de(r)):
        miles[m.group(1)] += 1
mayoria = miles.most_common(1)[0][0] if miles else ","


def marca(tipo, r, detalle):
    cuenta[tipo] += 1
    print("%s\t%s\t%s\t%s\t%s" % (tipo, r["id"], detalle, r["ingles"].replace("\n", " / ")[:100],
                                  es_de(r).replace("\n", " / ")[:120]))


for r in filas:
    en, es = r["ingles"], es_de(r)
    if not es.strip():
        continue
    otro = "." if mayoria == "," else ","
    for m in re.finditer(r"\b\d{1,3}\%s\d{3}\b(?![.,]\d)" % otro, es):
        if not re.search(r"\d\%s\d{3}" % otro, en):
            marca("NUMERO", r, m.group(0) + " (el juego usa «%s» como separador de miles: %s)" % (mayoria, dict(miles)))
    he = collections.Counter(x.lower() for x in (a or b for a, b in HONOR.findall(en)))
    hs = collections.Counter(x.lower() for x in (a or b for a, b in HONOR.findall(es)))
    falta = he - hs
    if falta:
        marca("HONOR", r, "falta: " + " ".join(falta))
    m = REGION.search(es)
    if m:
        marca("REGION", r, m.group(0))
    m = re.search(r"\w-\n\w", es)
    if m and not re.search(r"\w-\n\w", en):
        marca("GUION", r, repr(m.group(0)))
print("separador de miles en el español:", dict(miles), "| total:", dict(cuenta))
