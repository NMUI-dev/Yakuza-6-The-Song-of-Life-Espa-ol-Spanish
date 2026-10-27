"""(claude1, 25-10-2026) Arreglos de la revisión v1.0.1 sobre los atlas (trabajo/imagenes/atlas_hechos/*.json).
Copia previa intacta en atlas_hechos_v1.0/. Cada arreglo: (patrón de nombre, índice o texto inglés, cambios).
  python -I herramientas/v101_editar.py        aplica todos los cambios (idempotente) y lista las texturas tocadas
"""
import os, json, glob, fnmatch

H = r'C:\Mods\yakuza6\trabajo\imagenes\atlas_hechos'
QUITAR = object()

# (patrón, selector, cambios). selector: int = índice; str = valor de «en». Cambio con valor QUITAR borra la clave.
ARREGLOS = [
    ('clan_card_base', 'NEW', {'dejar': QUITAR}),
    ('mg_snack_p2_2*', 'Next', {'dejar': QUITAR, 'caja': [243, 198, 282, 218], 'es': 'Seguir', 'efecto': 'nada', 'color': [255, 255, 255], 'fuente': 'segoeuib.ttf', 'fondo': 'lama', 'alin': 'izq'}),
    ('mg_snack_p2_2*', '* Bar Patrons', {'es': '  Clientes del bar', 'alin': 'izq'}),
    ('base_ball_cutin', 'Play', {'es': '¡A', 'dejar': QUITAR}),
    ('base_ball_cutin', 'Ball!', {'es': 'jugar!', 'dejar': QUITAR}),
    ('base_ball_cutin', 'Play Ball!', {'es': '¡A jugar!', 'dejar': QUITAR}),
    ('base_ball_cutin', 'LEVEL UP', {'es': 'SUBES DE NIVEL'}),
    ('mg_karaoke_menu01', 'ON OFF', {'es': 'SÍ  NO', 'dejar': QUITAR}),
    ('mg_karaoke_menu01', 'Play', {'ancho_max': 42}),
    ('ibukuro', 'BONUS', {'es': 'EXTRA', 'dejar': QUITAR}),
    ('mg_kyaba_p3_1', "What's your favorite", {'es': '¿Cuál es tu comida', 'tam': 20}),
    ('mg_kyaba_p3_1', 'NUEVO', {'caja': [126, 154, 250, 186], 'en': 'food?', 'es': 'favorita?', 'fuente': 'courbd.ttf', 'efecto': 'nada', 'alin': 'izq', 'fondo': 'lama', 'color': [235, 235, 235], 'ancho_max': 124, 'tam': 20}),
    ('karaoke_cube', 'NO', {'es': 'SIN'}),
    ('karaoke_cube', 'CHANGE', {'es': 'CAMBIOS'}),
    ('karaoke_cube', 'UP', {'es': 'SUBE'}),
    ('karaoke_cube', 'DOWN', {'es': 'BAJA'}),
    ('karaoke_cube', 'UP!!', {'es': '¡¡SUBE!!'}),
    ('karaoke_cube', 'DOWN!!', {'es': '¡¡BAJA!!'}),
    ('karaoke_cube', 'STAY!!', {'es': '¡¡IGUAL!!'}),
    ('clan_bg', 'LEVEL UP', {'es': 'SUBES DE NIVEL'}),
    ('mg_clan_menu_p05_1*', 'LEVEL UP', {'es': 'SUBES DE NIVEL'}),
    ('mg_clan_menu_p07_1', 'PLAYER', {'es': 'RANGO DEL'}),
    ('mg_clan_menu_p07_1', 'NEXT RANK', {'caja': [32, 94, 168, 122]}),
    ('mg_clan_menu_p07_1', 'RANK', {'es': 'JUGADOR'}),
    ('mg_darts_01_p02', '5/10 ROUND SCORE', {'dejar': True}),
    ('mg_darts_01_p02', 'DART SCORES', {'es': 'PUNT. DARDOS', 'dejar': QUITAR, 'efecto': 'nada', 'color': [235, 235, 235]}),
    ('mg_darts_cricket_p02', '5/ 5 ROUND SCORE', {'dejar': True}),
    ('mg_karaoke_result_bg', 'Song :', {'es': 'Canción :'}),
    ('mg_darts_anm_result_logo', 'ROUND', {'es': '¡FIN DE'}),
    ('mg_darts_anm_result_logo', 'OVER!', {'es': 'RONDA!'}),
    ('mg_darts_anm_result_logo', 'GOOD!', {'es': '¡BIEN!'}),
    ('mg_darts_anm_result_logo', 'FANTASTIC!', {'mediana': False}),
    ('mg_mahjong_cutin', 'DRAW', {'fuente': 'PermanentMarker-Regular.ttf'}),
    ('taiken_caution_right', 'YEBIS is a registered trademark of', {'es': '*YEBIS es una marca registrada de'}),
    ('mg_clan_menu_p03', 'Lieu', {'es': 'Tenie', 'dejar': QUITAR}),
    # gimnasio: título bajo el gancho dorado -> mismo alto que el inglés (x16-63, y11-21) y borrado limpio
    ('mg_gym_rowing*', 0, {'en': 'Seated Rowing', 'caja': [15, 9, 112, 23], 'alto': 8, 'alin': 'izq', 'fondo': 'lama', 'mediana': False}),
    ('mg_gym_pulldown_p*', 0, {'en': 'Lat Pulldowns', 'caja': [15, 9, 112, 23], 'alto': 8, 'alin': 'izq', 'fondo': 'lama', 'mediana': False}),
    ('mg_gym_squat_p*', 0, {'en': 'Squats', 'caja': [15, 9, 112, 23], 'alto': 8, 'alin': 'izq', 'fondo': 'lama', 'mediana': False}),
    ('mg_gym_benchpress*', 0, {'caja': [15, 9, 112, 23], 'alto': 7, 'alin': 'izq', 'fondo': 'lama', 'mediana': False, 'color': [196, 156, 44]}),
    ('mg_gym_deadlift_*', 0, {'caja': [15, 9, 112, 23], 'alto': 8, 'alin': 'izq', 'fondo': 'lama', 'mediana': False}),
    ('mg_gym_jump_p1', 0, {'en': 'Squat Jumps', 'dejar': True}),
    ('mg_gym_jump_p1_[dknpx]', 0, {'en': 'Squat Jumps', 'dejar': True}),
    ('mg_gym_jump_p1_2*', 'GREAT', {'dejar': True}),
    ('mg_gym_jump_p1_2*', 'NUEVO', {'caja': [12, 7, 110, 16], 'en': 'Squat Jumps', 'es': 'Sentadillas con salto', 'fuente': 'tahomabd.ttf', 'efecto': 'nada', 'alto': 4, 'alin': 'izq', 'fondo': 'lama', 'mediana': False, 'color': [214, 172, 42]}),
    ('mg_gym_rowing', 'NUEVO', {'caja': [66, 218, 98, 230], 'en': 'Hold Down', 'es': 'Mantén', 'fuente': 'tahomabd.ttf', 'efecto': 'nada', 'alin': 'izq', 'fondo': 'lama', 'mediana': False, 'color': [235, 235, 235]}),
    ('livechat_00', 'FAIL', {'dejar': True}),
    ('mg_sumoguri_text', 'Emperor', {'caja': [29, 609, 991, 743], 'es': 'Calamar emperador', 'alin': 'centro'}),
    ('mg_sumoguri_text', 'Squid', {'es': ''}),
    ('mg_sumoguri_text', 'Delicious', {'caja': [21, 771, 1011, 872], 'es': 'Pulpo delicioso', 'alin': 'centro'}),
    ('mg_sumoguri_text', 'Octopus', {'es': ''}),
    ('mg_sumoguri_text', 'Bloody Shark', {'es': 'Tiburón sangriento', 'dejar': QUITAR}),
    ('mg_clan_menu_p05_2', 'Lv. 5', {'mediana': False, 'alto': 15, 'color': [235, 225, 200], 'alin': 'der'}),
    ('mg_clan_menu_p04_2', 'Lv. 1', {'mediana': False, 'alto': 15, 'color': [235, 225, 200], 'alin': 'der'}),
    ('mg_clan_menu_p05_2', 'Skill', {'caja': [58, 195, 118, 217], 'alto': 9, 'fondo': 'lama', 'mediana': False}),
    ('mg_clan_menu_p04_2', 'Skill', {'caja': [69, 191, 129, 214], 'alto': 9, 'fondo': 'lama', 'mediana': False}),
    ('mg_clan_menu_p04_2', 'Ultimate Dropkick', {'es': 'Patada voladora definitiva', 'caja': [156, 192, 270, 213], 'alin': 'izq', 'mediana': False}),
    ('mg_clan_menu_p05_2', 'Ultimate Dropkick', {'es': 'Patada voladora definitiva', 'caja': [146, 195, 260, 217], 'alin': 'izq', 'mediana': False}),
    ('mg_clan_menu_p0[45]_2', 'Health', {'alto': 9, 'mediana': False, 'margen': 0}),
    ('mg_clan_menu_p0[45]_2', 'Attack', {'alto': 9, 'mediana': False, 'margen': 0}),
    ('mg_clan_menu_p0[45]_2', 'Defense', {'alto': 9, 'mediana': False, 'margen': 0}),
    ('mg_clan_menu_p0[45]_2', 'Influence', {'alto': 9, 'mediana': False, 'margen': 0}),
    ('batting_logo', 'HOME RUN', {'fuente': 'segoeuiz.ttf'}),
    ('batting_logo', 'SINGLE', {'fuente': 'segoeuiz.ttf'}),
    ('batting_logo', 'DOUBLE', {'fuente': 'segoeuiz.ttf'}),
    ('gameover_parts', 0, {'fuente': 'PermanentMarker-Regular.ttf'}),
    ('gameover_parts', 1, {'fuente': 'PermanentMarker-Regular.ttf', 'efecto': 'borroso', 'radio': 5}),
    ('clan_win_cutiin', 3, {'efecto': 'brillo'}),
    ('icon_talk_mg', 'SPEC', {'mediana': 'todos', 'tam': 17}),
    ('icon_talk_mg', 'Legend', {'efecto': 'nada'}),
    ('icon_talk_mg', 6, {'efecto': 'nada'}),
    ('tutorial_pic_mission', 'CLEAR', {'caja': [60, 142, 205, 170], 'efecto': 'nada', 'color': [255, 238, 200], 'alin': 'izq', 'fondo': 'lama'}),
    ('clan_menu_text', 'SPEC', {'mediana': 'todos', 'tam': 36, 'alin': 'izq', 'ceñido': True}),
    ('mg_karaoke_menu', 'Live', {'ancho_max': 62}),
    ('mg_karaoke_menu', 'High Scores', {'es': 'Récords'}),
    ('mg_karaoke_menu', 'Movies', {'mediana': False}),
    ('clan_menu_text', 0, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 1, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 2, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 3, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 4, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 5, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 6, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 7, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 8, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 9, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 10, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 11, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 12, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 13, {'alin': 'izq', 'sangria': 2}),
    ('clan_menu_text', 14, {'alin': 'izq', 'sangria': 2}),
    ('mg_snack_text2', 22, {'efecto': 'nada'}),
    ('mg_karaoke_jacket', 'Song Number', {'fuente': 'segoeui.ttf', 'color': [205, 205, 205], 'efecto': 'nada'}),
    ('adv_geihinkan', 'Lockers', {'alin': 'centro', 'ancho_max': 165}),
    ('adv_vending', 'Atk', {'es': 'Atq.'}),
    ('adv_vending', 'Def', {'es': 'Def.'}),
    ('btl_tutorial_11_weapon*', 'Grab', {'alin': 'der', 'ancho_max': 72}),
    ('mg_clan_btl_p06_1*', 'DEPLOYED', {'mediana': False, 'ancho_max': 80}),
    ('mg_clan_menu_p04_1*', 'Strike Team', {'efecto': 'nada', 'color': [255, 255, 255]}),
    ('mg_clan_menu_p07_2', 1, {'caja': [38, 66, 140, 88], 'es': '  Fuerza de defensa', 'alin': 'izq', 'mediana': False}),
    ('mg_clan_menu_p07_2', 'Kiryu Clan Org Chart', {'alin': 'der', 'ancho_max': 125}),
    ('adv_geihinkan', 'Lockers', {'es': 'Vestidor'}),
    ('mg_clan_btl_p0[23]*', 'AREA 1', {'dejar': True}),
    ('mg_clan_menu_p02_2_d', 'BREAK', {'dejar': True}),
    ('ui_karaoke_tonight', 'SPEC', {'mediana': 'todos'}),
    ('mg_caba_status', 'NUEVO', {'caja': [6, 280, 98, 320], 'en': 'New!', 'es': '¡Nuevo!', 'fuente': 'times.ttf', 'efecto': 'estilo', 'alin': 'izq', 'mediana': False}),
    ('mg_caba_status', 'SCORE', {'es': 'PTS.'}),
    ('mg_karaoke_menu01', 'Default', {'efecto': 'nada', 'color': [215, 25, 25], 'fondo': 'lama', 'mediana': False, 'alto': 11}),
    ('mg_clan_menu_p04_1*', 1, {'dejar': True}),
    ('mg_clan_menu_p05_1*', 'Results', {'ancho_max': 41, 'mediana': False}),
]


def main():
    tocadas = set()
    for pat, sel, cambios in ARREGLOS:
        fs = [f for f in glob.glob(os.path.join(H, 'e__texture__*.json'))
              if fnmatch.fnmatch(os.path.basename(f)[12:-5], pat)]
        if not fs:
            print('SIN TEXTURA', pat); continue
        for f in fs:
            d = json.load(open(f, encoding='utf-8'))
            its = d['items']
            if sel == 'SPEC':   # claves de toda la textura
                d.update(cambios); json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); tocadas.add(os.path.basename(f)[:-5]); continue
            if sel == 'NUEVO':   # añade un rótulo que el borrador no vio (si no está ya)
                ya = [it for it in its if it.get('en') == cambios['en']]
                if ya: ya[0].update(cambios)
                else: its.append(dict(cambios))
                json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); tocadas.add(os.path.basename(f)[:-5]); continue
            idx = ([sel] if sel < len(its) else []) if isinstance(sel, int) else [i for i, it in enumerate(its) if it.get('en') == sel]
            if not idx:
                print('SIN RÓTULO', os.path.basename(f), sel); continue
            for i in idx:
                for k, v in cambios.items():
                    if v is QUITAR: its[i].pop(k, None)
                    else: its[i][k] = v
            json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            tocadas.add(os.path.basename(f)[:-5])
    open(os.path.join(os.path.dirname(H), 'v101_tocadas.txt'), 'w').write('\n'.join(sorted(tocadas)) + '\n')
    print('tocadas', len(tocadas))


if __name__ == '__main__':
    main()
