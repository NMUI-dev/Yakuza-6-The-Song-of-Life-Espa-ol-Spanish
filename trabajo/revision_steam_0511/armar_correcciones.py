# Arma correcciones.json con las correcciones decididas a mano (revisión de Steam, 05-11-2026, claude1).
# Cada corrección se busca por su español ACTUAL en textos.csv (no se fía del id que dio el ayudante) y se comprueba:
# un solo id, mismas etiquetas <...>, mismos saltos, bytes_max (UTF-8; í = 1 byte) y que el cambio esté donde se espera.
# Uso: python armar_correcciones.py   -> escribe correcciones.json e imprime cada una.
import csv
import json
import re
from pathlib import Path

aqui = Path(__file__).resolve().parent
# textos.csv sacado de la v1.0.3 PUBLICADA con la herramienta ya arreglada (caché con huella), sin correcciones.
TEXTOS = Path(r"C:\mods\yakuza6\entrega_v1.0.4\Herramientas para traduccion\trabajo\textos_v103_publicada.csv")

# (id esperado o None, español actual exacto, español nuevo, tipo, motivo)
DECIDIDAS = [
    ("7560", "Encantada de conocerte", "Mucho gusto", "género",
     "título de sesión del chat en vivo; no se sabe quién lo dice: forma neutra"),
    ("13656", "E-Eres bastante bueno en esto...", "E-Eres bastante buena en esto...", "género",
     "caba_sora: Kiryu (P2117) se lo dice a Sora (P1609, mujer)"),
    ("19479", "La verdad, no estoy enojado.", "La verdad, no estoy enojada.", "género",
     "main11: lo dice Kiyomi (P1869, mujer) de sí misma"),
    ("19480", "Más bien, estoy aliviado.", "Más bien, estoy aliviada.", "género",
     "main11: lo dice Kiyomi (P1869, mujer) de sí misma"),
    ("20372", "¿Estás seguro?", "¿Estás segura?", "género",
     "main13: Yuta (P1491) se lo pregunta a Haruka (P1267, mujer)"),
    (None, "¿Estás seguro? ¿No se te acabará el producto para vender?",
     "¿Estás segura? ¿No se te acabará el producto para vender?", "género",
     "sub_b23: Kiryu (P2900) se lo pregunta a Amano (P3171, mujer: «a real passionate girl»)"),
    ("14302", "¿Estás seguro?", "¿De verdad?", "género",
     "«You sure?» sale 12 veces: a hombres y en sub_a17 a una mujer (P1574): forma neutra"),
    ("18161", "Sí, estoy solo.", "Sí, lo estoy.", "sentido",
     "«Yeah, I am.» contesta a «¿estás solo?» (main07) y a «¿estás completamente seguro?» (main10): vale para las dos"),
    ("7022", "Hola, guapo.", "Hola, guapa.", "género",
     "chat en vivo: un espectador saluda a Anri-chan (mujer)"),
    ("12092", "Entonces me ofrezco a ser la primera...\nEs broma, claro.",
     "Entonces me ofrezco a ser el primero...\nEs broma, claro.", "género",
     "caba_hikaru: lo dice Kiryu (P2288) de sí mismo"),
    ("23084", "Por eso mismo siempre te digo que no\nejercas tanta presión sobre tus clientes.",
     "Por eso mismo siempre te digo que no\nejerzas tanta presión sobre tus clientes.", "ortografía",
     "«ejercas» no existe: subjuntivo de ejercer = ejerzas"),
    ("29266", "(Algo no cuadra aquí...\nTienes que ser una estafa.)", "(Algo no cuadra aquí...\nTiene que ser una estafa.)",
     "ortografía", "«It has to be a scam»: lo que tiene que ser una estafa es «esto», no «tú»"),
    # Los 19 comandos del chat en vivo que parecían cortados YA estaban bien en la v1.0.3 publicada
    # (correcciones_csv.py de claude2): el textos.csv viejo no lo reflejaba por el fallo de caché de «extraer».
]

filas = list(csv.DictReader(open(TEXTOS, encoding="utf-8-sig", newline=""), delimiter=";"))


def tam(s):
    return len(s.encode("utf-8")) - s.count("í")


def norm(s):
    return s.replace("\r\n", "\n")


salida, fallos = {}, 0
for esperado, antes, nuevo, tipo, motivo in DECIDIDAS:
    ids = [r for r in filas if norm(r["espanol"]) == antes]
    if esperado:
        ids = [r for r in ids if r["id"] == esperado] or ids
    problema = []
    if len(ids) != 1:
        problema.append("encontrados %d ids" % len(ids))
    else:
        r = ids[0]
        if re.findall(r"<[^>]*>", nuevo) != re.findall(r"<[^>]*>", antes):
            problema.append("etiquetas")
        if nuevo.count("\n") != antes.count("\n"):
            problema.append("saltos")
        if r["bytes_max"].strip() and tam(nuevo) > int(r["bytes_max"]):
            problema.append("bytes %d > %s" % (tam(nuevo), r["bytes_max"]))
        if tipo == "chat" and not re.fullmatch(r"[A-Z0-9? ]+", nuevo):
            problema.append("lo que se teclea solo admite A-Z, 0-9, ? y espacio")
        salida[r["id"]] = {"en": norm(r["ingles"]), "antes": antes, "es": nuevo, "tipo": tipo, "motivo": motivo,
                           "veces": int(r["veces"] or 1), "donde": r["donde"]}
    fallos += bool(problema)
    print(("FALLO " if problema else "OK    ") + (ids[0]["id"] if len(ids) == 1 else "?") + " | " + tipo + " | "
          + antes.replace("\n", " / ")[:45] + " -> " + nuevo.replace("\n", " / ")[:45] + ("  [" + "; ".join(problema) + "]" if problema else ""))

json.dump(salida, open(aqui / "correcciones.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\ncorrecciones.json:", len(salida), "| fallos:", fallos)
