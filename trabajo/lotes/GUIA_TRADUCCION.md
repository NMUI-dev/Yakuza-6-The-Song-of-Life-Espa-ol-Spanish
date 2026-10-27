# Guía de traducción — Yakuza 6: The Song of Life (inglés oficial → español)

Proyecto del usuario (Claude Code, 19-10-2026). Se traduce desde el INGLÉS OFICIAL del juego (decisión del usuario).

## Formato de trabajo
- Entrada: `lote_NNN.json` = lista de `{"id", "en", "ctx", "max"}`. `ctx` = tabla y columna del juego donde sale el texto
  (pista de contexto: `msg`/`ui_text`/`option` = menús; `item` = objetos; `mission_kind` = misiones; `sound_auth*`,
  `auth|…cinema_telop` = subtítulos de escenas; `talk` = diálogos de subhistorias/minijuegos; `minigame_*` = minijuegos;
  `pause_mail` = correos del móvil; `manual` = manual; `player_skill` = habilidades; `clan_creator_*` = Creador de Clanes).
- Salida: `lote_NNN_es.json` = objeto `{"id": "traducción"}` con TODOS los id del lote (claves como texto).
- Validar SIEMPRE: `python C:/mods/yakuza6/herramientas/validar_lote.py NNN` → tiene que decir OK.

## Reglas técnicas (las comprueba el validador)
1. Copiar EXACTAS todas las marcas: `${nombre}`, `<color=xxx>` … `</color>`, `<symbol=xxx>`, `<Sign:2>`, `%d`, `%s`.
   Pueden cambiar de sitio dentro de la frase si el español lo pide, pero no se traducen ni se tocan.
2. Mismo número de saltos de línea (`\n`) que el inglés. Repartir el texto para que los renglones queden parecidos.
3. `max` (solo `talk`): el texto en UTF-8 no puede pasar de esos bytes (á é í ó ú ñ ü ¿ ¡ cuentan 2). Si no cabe, abreviar.
4. `\` delante de cifras es el símbolo del yen (`\5,000`): se deja igual. Los números se dejan como están (5,000).
5. Solo caracteres de Latin-1 (español completo: á é í ó ú ü ñ Á É Í Ó Ú Ü Ñ ¿ ¡). Nada de emojis ni comillas raras.
   Usar SOLO comillas inglesas "…" (nada de « »); puntos suspensivos como "..." (como el original).
6. Respetar espacios al principio/fin y el espacio japonés ancho (`　`) si el original lo tiene.
7. Siglas cortas de minijuegos (SS, LF, CF, HR, BB, DH, SUB) y términos de mahjong (Pon, Chi, Kan, Riichi, Tsumo, Ron,
   Dora, Ura-Dora, Han, Fu, Mangan, Haneman, Baiman, Yakuman...) se dejan en inglés/japonés como en el original.

## Estilo
- Español NEUTRO latinoamericano (el usuario es de Latinoamérica). Nada de «vosotros», «coger», «ordenador», «vale».
  Al jugador se le habla de TÚ. Botones: «Presiona», no «Pulsa». «Celular»/«teléfono» para el móvil del juego.
- Menús e interfaz: cortos, como el original (el espacio es limitado). Mayúsculas igual que el original (títulos en
  MAYÚSCULAS se quedan en MAYÚSCULAS; «Title Case» inglés → solo la primera palabra con mayúscula, salvo nombres propios).
- Diálogos: naturales, con la personalidad de cada uno (Kiryu seco y serio; Majima excéntrico; los matones vulgares). Las
  groserías con la misma fuerza que el inglés, en registro neutro (maldito, carajo, idiota, desgraciado, imbécil...).
- Honoríficos japoneses se dejan: -san, -chan, -kun, -sama, -nee, Aniki, Oyaji, Mama (de un bar).
- Nada de explicaciones ni notas dentro del texto. Si una línea es solo un nombre propio o una onomatopeya, se deja o se adapta.
- Coherencia: mismo término siempre. Las decisiones nuevas se apuntan en `glosario_vivo.md` (una línea: inglés → español).

## Glosario fijo
Personajes (no se traducen): Kazuma Kiryu, Haruka Sawamura, Haruto, Yuta Usami, Tsuyoshi Nagumo, Toru Hirose,
Daigo Dojima, Goro Majima, Taiga Saejima, Shun Akiyama, Makoto Date, Kiyomi, Joji Kazama, Jo Amon, Masaru Sera, Big Bro → «Aniki».
Lugares (se dejan): Kamurocho, Onomichi, Jingaicho, Hiroshima, Okinawa, Sunshine Orphanage → orfanato Sunshine, Snack Bar
Ange → bar Ange (snack), Little Asia → Little Asia, Millennium Tower → Torre Millennium, Theater Square → Plaza del Teatro,
Pink Street → Calle Pink, Showa Street → Calle Showa, Tenkaichi Street → Calle Tenkaichi, Nakamichi Street → Calle Nakamichi.
Organizaciones: Tojo Clan → Clan Tojo; Yomei Alliance → Alianza Yomei; Hirose Family → Familia Hirose; Saio Triad → Tríada
Saio; Jingweon Mafia → mafia Jingweon; Omi Alliance → Alianza Omi; JUSTIS → JUSTIS; Kiryu Clan → Clan Kiryu.
Juego: Heat → Heat; Heat Action → Acción Heat; Heat Gauge → barra de Heat; Extreme Heat Mode → Modo Heat Extremo;
EXP → EXP; Health → Vida; Strength → Fuerza; Agility → Agilidad; Charisma → Carisma; Technique → Técnica; Spirit/Soul →
Espíritu; Toughness → Aguante; Skill → Habilidad; Equipment/Gear → Equipo; Inventory → Inventario; Item → Objeto;
Key Items → Objetos clave; Substory → Subhistoria; Main Story → Historia principal; Mission → Misión; Reward → Recompensa;
Completion List → Lista de logros (del juego); Save Data → Datos guardados; Autosave → Autoguardado; Difficulty → Dificultad
(Easy → Fácil, Normal → Normal, Hard → Difícil, Legend → Leyenda); Settings → Opciones; Controls → Controles.
Minijuegos: Clan Creator → Creador de Clanes; Cabaret Club → Club de cabaré; hostess → anfitriona; Live Chat → Chat en vivo;
Spearfishing → Pesca submarina; Sandlot Baseball → Béisbol de barrio; Batting Center → Centro de bateo; Gym → Gimnasio;
Cat Café → Café de gatos; Karaoke → Karaoke; Darts → Dardos; Mahjong → Mahjong; Troublr → Troublr; Snack bar → bar snack.
Dinero: yen (no «yenes» en menús: «10,000 yen»; en diálogo «yenes» está bien).

## Español NEUTRO LATINO (pedido del usuario, 19-10-2026)
Nada de España (vosotros, coche, móvil, ordenador, vale, tío, chaval, crío, gafas, zumo, piso, conducir, aparcar, enfadarse,
cabrear, pillar, coger, joder, coño, hostia, gilipollas) ni jerga marcada de un solo país (ahorita, chido, güey, neta,
pinche, órale, che, boludo, pibe, laburo, chévere, parcero, vos). Usar: auto, celular, computadora, está bien/de acuerdo,
amigo, muchacho/niño, lentes, jugo, departamento, manejar, estacionar, enojarse, agarrar/atrapar, tomar, maldición/carajo/
demonios, imbécil. Barrido: python -X utf8 herramientas/buscar_fallos.py
