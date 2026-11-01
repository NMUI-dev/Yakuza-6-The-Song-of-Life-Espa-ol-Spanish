# Lecciones para traductores (Yakuza 6, v1.0.3)

Trampas que nos encontramos traduciendo *Yakuza 6* y cómo evitarlas. La guía general (Yakuza 5, la misma familia de
juegos) está en el repositorio del Yakuza 5:
https://github.com/NMUI-dev/Yakuza-5-Remastered-Espa-ol-Spanish/blob/main/LECCIONES_PARA_TRADUCTORES.md

## Textos
- **Frases de UNA palabra** («Thanks.», «Right.», «Yeah.»): un filtro de «¿es texto o código?» que exige un espacio las
  descarta. En el Y6 se quedaron 830 subtítulos sin traducir desde la v1.0. Hay que buscar las celdas iguales al
  inglés que casan con `^[.…]*[A-Z][a-z']+[.!?…]+$` (`trabajo/faltan_c2/frases_cortas.py`).
- **Textos con salto de línea** dentro de cmn.bin (talk/hact/auth): `isprintable()` los descarta (resúmenes, avisos).
- **cmn.bin**: cada texto tiene un hueco fijo (el tamaño está en la cabecera, en múltiplos de 16) y detrás va el texto
  chino. No se puede alargar: hay que traducir con un límite de bytes (una tilde ocupa 2 bytes).
- **Contexto antes que glosario**: en el Y6 «Stand» es levantarse de un asiento y «Hit» es un golpe de béisbol. Una
  sustitución automática por el glosario oficial los habría estropeado.
- **Barrido final del juego ARMADO**, no del original: lo que de verdad lee el juego (`barrido_final.py`).

## Letra
- **Ancho por código**: la letra que se dibuja en la casilla de otra hereda SU ancho. La «í» puesta en «~» dejaba un
  hueco («Subt í tulos»); en «`» (estrecha y sin uso) queda bien. Hay que probar cada letra nueva en una frase dentro
  del juego (`herramientas/letra_i_estrecha.py`).

## Imágenes
- **Pasar OCR a TODAS las texturas en inglés**, no solo a las que difieren de las japonesas: los 13 títulos de capítulo
  del Y6 siguieron en inglés desde la v1.0 por eso (`trabajo/faltan_c1/ocr_todas_e.py`).
- Al borrar un texto sobre fondo transparente hay que borrar también el COLOR, no solo el alfa. Si no, el blanco viejo
  asoma bajo el halo nuevo y se lee el inglés de fondo.
- **Las texturas con letra estilizada** (pincel, serif con brillo, pegatinas) se rehacen a mano con una letra parecida
  (`rotulos_mano_y6.py`). Un kit genérico pone otra letra y las estropea.
- **Las PIEZAS que el juego combina** («GOOD»+«CHOICE», «TIME»+«UP») no se traducen: cada pieza tiene su hueco fijo
  en el atlas.
- **El texto nuevo no puede pasar del ancho del original**: el juego solo enseña ese trozo de la textura.
- **Comprobar el .par nuevo**: extraerlo y confirmar que solo cambian las texturas tocadas (`diff -rq` contra el
  original extraído).
- Lo que se deja en inglés se enseña en carpetas numeradas, con el motivo de cada grupo
  (`queda_ingles_imagenes.py`): letras de karaoke (canción japonesa con romaji), dardos, piezas combinadas, capturas
  diminutas, logotipos y marcas, nombres propios.
