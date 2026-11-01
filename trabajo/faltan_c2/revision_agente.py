# -*- coding: utf-8 -*-
"""(01-11-2026, claude2) Correcciones de la revisión de los textos nuevos de la v1.0.3 (agente revisor + claude2):
sentido, concordancia, comillas, signos, españolismos, tú/usted del mahjong. Se aplican sobre textos.csv de la
herramienta (después de correcciones_csv.py). Si algo no cabe en su hueco lo avisa y NO lo cambia.
  python revision_agente.py <textos.csv>"""
import csv, sys
sys.stdout.reconfigure(encoding='utf-8')
# (trozo viejo, trozo nuevo): se cambia en toda fila (de la v1.0.3) que lo contenga
TROZOS = [
    ('heredar el poder', 'legar el poder'),
    ('decidió\nacabar con su vida para', 'decidió acabar\ncon la vida de Daigo para'),
    ('acabar con su vida para perpetuar', 'acabar con la vida de Daigo para perpetuar'),
    ('tras el seudónimo', 'bajo el seudónimo'),
    ('encubrimientos del asesino', 'encubrimientos que ocultaban al asesino'),
    ('al escalarse', 'al recrudecerse'),
    ('también fue disparado', 'también recibió un disparo'),
    ('fue disparado', 'recibió un disparo'),
    ('Provenía de policías', 'Provenía de una familia de policías'),
    ('la Familia Go-Ryu', 'el Clan Go-Ryu'),
    ('Penitenciaría 2 de Okinawa', 'Prisión de Okinawa 2'),
    ('la Millennium Tower', 'la Torre Millennium'),
    ('ser una ídol', 'ser una idol'),
    ('nuevos\noficiales del Clan Tojo', 'nuevos\ndirigentes del Clan Tojo'),
    ('aviso de desahucio', 'aviso de desalojo'),
    ('le convenció', 'lo convenció'),
    ('compañero de instituto', 'compañero de secundaria'),
    ('se crió', 'se crio'),
    ('ni el estado', 'ni el Estado'),
    ('¡¿Qué está pasando!?', '¡¿Qué está pasando?!'),
    ('¡¿Qué demonios haces!?', '¡¿Qué demonios haces?!'),
    ('¡Atraparé\na hasta el último', '¡Atraparé\nhasta al último'),
    ('éxito,\n tu entrenamiento', 'éxito,\ntu entrenamiento'),
    ('No lo pierdas, ¿vale?', 'No lo pierdas, ¿sí?'),
    # mahjong: tú como en el resto, tildes y ordinales
    ('Consiga ', 'Consigue '), ('Gane al menos', 'Gana al menos'), ('Pague ', 'Paga '), ('Tiene ', 'Tienes '),
    ('no ha ganado', 'no has ganado'), ('Dificil', 'Difícil'), ('(Media = ', '(Medio = '), ('(Media=', '(Medio='),
    ('1er Puesto', '1.er puesto'), ('2do Puesto', '2.º puesto'), ('3er Puesto', '3.er puesto'), ('4to Puesto', '4.º puesto'),
]
ENTERAS = {   # inglés (empieza por) -> español completo
    '"Does it matter?': '"¿Importa?\nSolo necesito algunas."',
    '"Good. Now send me photos': '"Bien. Ahora mándame fotos\nde los números de cada una."',
    '"Kiryu, you\'ve been had!': '"¡Kiryu, te engañaron!\n¡Hackearon mi cuenta el otro día!"',
    '"I\'ll see what I can do.': '"Veré qué puedo hacer.\nEse estafador no se saldrá con la suya."',
    '"Sorry, 50 grand really is a lot.': '"Perdona, 50.000 yenes es un dineral.\nTe invito un trago para compensar."',
    '"Just send them already.': '"Envíalas ya.\nTengo prisa."',
    '"Spare me the details, but it sounds': '"Ahórrame los detalles, pero parece\nque te debo un trago."',
    'Yoshida, of Yoshida Batting Center fame': '¡Yoshida, del Centro de bateo Yoshida,\nse une a los Setouchi Warriors!',
    'Gori-san, the maniacal slugging sensation': '¡Gori-san, el bateador más temible,\nse une a los Setouchi Warriors!',
    "However, I'd much rather you make a habit": 'Sin embargo, prefiero que lo conviertas\nen un hábito por tu cuenta.',
    "(I need to make sure they have enough": '(Debo asegurarme de que les alcance\npara el hospital de su hijo.)',
    'Busted.': 'Te atrapé.',
}
p = sys.argv[1]
rows = list(csv.DictReader(open(p, encoding='utf-8-sig', newline=''), delimiter=';'))
nb = lambda s: len(s.replace('í', '`').replace('Í', '|').encode())
n = 0
for r in rows:
    es = r['espanol']; en = r['ingles'].replace('\r\n', '\n')
    nuevo = es
    for k, v in ENTERAS.items():
        if en.startswith(k): nuevo = v
    if int(r['id']) >= 29000 or nuevo != es:            # trozos: solo filas nuevas de la v1.0.3 (al final del csv)
        for a, b in TROZOS:
            if a in nuevo: nuevo = nuevo.replace(a, b)
    if nuevo == es: continue
    if r['bytes_max'] and nb(nuevo) > int(r['bytes_max']):
        print('NO CABE, se deja:', r['id'], nb(nuevo), '>', r['bytes_max'], repr(nuevo[:70])); continue
    r['espanol'] = nuevo; n += 1
with open(p, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=';', quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(rows)
print(n, 'filas corregidas')
