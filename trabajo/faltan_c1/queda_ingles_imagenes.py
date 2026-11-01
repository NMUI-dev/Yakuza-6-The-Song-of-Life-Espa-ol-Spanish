# -*- coding: utf-8 -*-
"""(01-11-2026, claude1) Carpeta «1 Imagenes (png)» de lo que se queda en inglés en el Y6 (ui.par/e), numerada por grupo
y con el motivo, para que claude2 la meta en «Lo que queda en ingles v1.0.3». Sale de ingles_e.json (OCR) menos lo
traducido (es/). Escribe trabajo/faltan_c1/queda_ingles/1 Imagenes (png)/NN grupo/*.png + LEEME_imagenes.txt
  python trabajo/faltan_c1/queda_ingles_imagenes.py"""
import json, os, re, shutil
from PIL import Image
B = os.path.dirname(os.path.abspath(__file__)); U = os.path.join(B, 'ui_actual')
OUT = os.path.join(B, 'queda_ingles', '1 Imagenes (png)')
GRUPOS = [   # (carpeta, motivo, patrón del nombre)
    ('01 Letras del karaoke (cancion en japones)', 'Son la letra de la canción en japonés con su romaji; las palabras inglesas son parte de la canción.', r'^karaoke_song_lyric'),
    ('02 Dardos (marcadores y animaciones)', 'Términos de dardos que la saga oficial deja en inglés; animaciones letra a letra y marcadores llenos de etiquetas diminutas.', r'darts'),
    ('03 Piezas que el juego combina', 'Palabras sueltas que el juego une («GOOD»+«CHOICE», «TIME»+«UP», «WIN/LOSE»): cada pieza tiene su hueco fijo y en español no caben.', r'^(mg_snack_text|mg_gym_start|clan_win$)'),
    ('04 Capturas de ejemplo', 'Capturas de pantalla de los minijuegos (ayuda/menú) con texto diminuto.', r'^(mg_.*_p\d|mg_.*_p$|mg_clan_menu|mg_mahjong|mg_karaoke_p|mg_karaoke_result|mg_tera|mg_gym_jump|mg_gym_bench|mg_kyaba|mg_livechat_p|mg_snack_p|mg_sumoguri_p|mg_space|mg_hang)'),
    ('05 Logotipos, marcas y textos legales', 'Logotipos del juego y de SEGA, productos y marcas reales, portadas del karaoke (título de canción) y avisos legales.', r'^(firstload|system_logo|title_menu_logo|title_menu_sub|kokuchi|ui_item_(sn|drinkkora|drinkposeidon|mantaicard|prepaid|muscle|memoango|meishi|bromide)|ui_food|ui_karaoke|otr_)'),
    ('06 Nombres propios', 'Nombres de grupos y personajes (The Six Lunatics, Jingai Thunders).', r'^bc_'),
    ('07 Iconos y rotulos pequenos', 'Iconos con una palabra (NEW, CLEAR, ITEM, MENU), teclas del teclado y términos de béisbol (STRIKE, OUT, FOUL, como HOME RUN).', r'.'),
    ('08 Version de prueba (demo)', 'Texturas taiken_* de la versión de prueba del juego.', r'^taiken'),
]


def main():
    r = json.load(open(os.path.join(B, 'ingles_e.json'), encoding='utf-8'))
    hechas = {p.replace(os.sep, '/')[len(os.path.join(B, 'es')) + 1:] for p in
              [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(B, 'es')) for f in fs]}
    shutil.rmtree(OUT, ignore_errors=True)
    por = {g[0]: [] for g in GRUPOS}
    for k in sorted(r):
        if k in hechas or '/chapter_' in k: continue
        n = os.path.basename(k)[:-4]
        if n.startswith('ac_m_') or re.match(r'^(clan_area_cutin|clan_win_cutiin|clear_result_bg|adv_geihinkan|pause_nouryoku|pausemenu|mg_caba_status|mg_sumoguri_text)', n):
            continue                                          # ya están en español (el OCR las marcó sin tildes)
        if n.startswith('bc_') and not any(re.search('LUNATICS|THUNDERS', t, re.I) for t in r[k]):
            continue                                          # tarjetas ya en español o solo con el nombre del personaje
        g = next(g for g in ([x for x in GRUPOS if x[0].startswith('08')] + GRUPOS) if re.search(g[2], n))
        por[g[0]].append(k)
    lineas = ['IMÁGENES DEL YAKUZA 6 QUE SE QUEDAN EN INGLÉS (v1.0.3), por grupo:', '']
    total = 0
    for g, motivo, _ in GRUPOS:
        ks = por[g]
        if not ks: continue
        d = os.path.join(OUT, g); os.makedirs(d, exist_ok=True)
        for k in ks:
            im = Image.open(os.path.join(U, k)).convert('RGBA'); bg = Image.new('RGBA', im.size, (40, 40, 40, 255)); bg.alpha_composite(im)
            bg.convert('RGB').save(os.path.join(d, os.path.basename(k)[:-4] + '.png'))
        lineas += [f'{g} ({len(ks)}): {motivo}']; total += len(ks)
    lineas += ['', f'Total: {total}. Traducidas en la v1.0.3: los 13 títulos de capítulo, Matones de Hiroshima, Subes de rango,',
               '¡Éxito!/Fallo/Inicio (chat en vivo), ¡Subes de nivel!, menú del gimnasio, ¡Nuevo!/¡Oferta! y las calles del mapa.']
    open(os.path.join(B, 'queda_ingles', 'LEEME_imagenes.txt'), 'w', encoding='utf-8-sig', newline='\r\n').write('\n'.join(lineas) + '\n')
    print('\n'.join(lineas))


if __name__ == '__main__': main()
