# Ideas acumuladas (pregunta en cadena, 06-11-2026 22:27)

1. **Contracciones «al» y «del»: «a el» / «de el» sueltos** (kilo:kilo/kilo-auto/free, prioridad alta)
   - Por qué: En español «a el» y «de el» son incorrectos; deben ser «al» y «del». Un jugador las lee al instante como error ortográfico en menús, objetos y diálogos (ej. «menú de el objeto», «ir a el mercado»).
   - Cómo detectarlo: Programático: buscar con expresiones regulares "\\bde el \\b", "\\ba el \\b", "de el\\.", "a el\\." en todo el paquete de textos; revisar a ojo los casos donde «el» abre sustantivo tras preposición.
2. **Concordancia pronombre-verbo: «usted» con verbo de «tú» o viceversa** (kilo:kilo/kilo-auto/free, prioridad alta)
   - Por qué: «¿Cómo estás usted?» o «usted tienes» suenan a error grave de gramática para cualquier hispanohablante y rompen la inmersión en menús y diálogos de personajes mayores o jerárquicos.
   - Cómo detectarlo: Programático: lista de formas verbales propias de tú (estás, tienes, eres, quieres, vas...) y de usted (está, tiene, es, quiere, va...); marcar cualquier línea donde un pronombre «tú/usted» contiguo coincida con forma del otro. Revisar a ojo los matches.
3. **Negativa calcada del inglés: «no nadie», «no nada»** (kilo:kilo/kilo-auto/free, prioridad media)
   - Por qué: En español «no nadie» y «no nada» son incorrectos (se dice «nadie», «nada», o «no a nadie»). Un jugador nativo lo detecta inmediatamente como texto calcado y mal revisado.
   - Cómo detectarlo: Programático: buscar «no nadie», «no nada», «no ninguno», «no ningún» en diálogos y menús. Revisar a ojo cada match para corregir a «nadie/nada» o reestructurar.
4. **Voz propia de cada personaje (idiolecto): todos suenan igual y neutro** (kilo:kilo/kilo-auto/free, prioridad media)
   - Por qué: Si un matón callejero, una hostess de cabaret y un miembro del clan yakuza hablan con el mismo español neutro plano, el jugador pierde la distinción de personajes que sí tiene el inglés. Afecta especialmente a Majima y a los enemigos de combate.
   - Cómo detectarlo: A ojo: agrupar líneas por personaje y leer seguido las de cada uno (Majima, matones, hostesses, Nishiki, principales) comprobando que conserven registros y marcas propias en español; sin repetir lo ya revisado de dialecto Kansai ni honoríficos.
5. **Punto y signos dentro de comillas cerradas (norma española)** (kilo:kilo/kilo-auto/free, prioridad media)
   - Por qué: En español el punto va fuera de las comillas a menos que pertenezca a lo citado; calcar el inglés (punto dentro) se ve en menús, diálogos y correos y resulta noticeable para lectores hispanohablantes.
   - Cómo detectarlo: Programático: buscar comillas cerradas seguidas de punto o signo («.»", "¡!", "¿?" dentro del par de comillas) y revisar si el signo pertenece a la cita; corregir al estilo español.
6. **Género inconsistente de préstamos («el katana», «la sushi»)** (kilo:kilo/kilo-auto/free, prioridad media)
   - Por qué: Palabras japonesas o inglesas sin género fijo en español reciben artículo distinto según el traductor («el/la katana», «el/la sushi», «el/la bento»). El jugador nota la inconsistencia entre menús, objetos y diálogos.
   - Cómo detectarlo: Programático: tabular préstamos (katana, sushi, bento, yakuza, clan...) y marcar líneas donde su artículo no coincida con la entrada de la tabla; revisar a ojo el resto de sustantivos prestados sin género claro.
7. **Orden de palabras calcado del inglés (adjetivo y sustantivo, SVO rígido)** (kilo:kilo/kilo-auto/free, prioridad baja)
   - Por qué: Estructuras con adjetivos siempre antes del sustantivo por calque del inglés suenan a traducción automática y restan naturalidad a diálogos y descripciones de objetos.
   - Cómo detectarlo: A ojo: leer descripciones de objetos, misiones y diálogos comprobando que el orden de adjetivos y sustantivos suene natural en español latino, no calco del inglés.
8. **Renderizado de glifos y ligaduras tipográficas (ñ, ¿, ¡, ç, ª, º)** (or:xingchen-agi/xing4.0-29b-a4b:free, prioridad alta)
   - Por qué: Si la fuente del juego carece de glifos para caracteres españoles especiales, el texto aparecerá en blanco, deforme o sin tilde, destruyendo la immersion visual en cinemáticas, diálogos y menús. Un jugador lo notará al ver letras vacías o figuras estilizadas incorrectas.
   - Cómo detectarlo: Inspeccionar los archivos de fuentes (.ttf/.otf) del paquete del juego para verificar la presencia de glifos para ñ, ¿, ¡, ç, ª, º. Probar renderizar las cadenas problemáticas en un visor de fuentes tipográficas.
9. **Expansión visual de texto en interfaz (solapamiento de elementos)** (or:xingchen-agi/xing4.0-29b-a4b:free, prioridad alta)
   - Por qué: Aunque el límite de bytes se cumpla, el español ocupa más espacio que el inglés. Si un texto de botón se expande, puede solaparse con el texto de otro botón o desbordarse de su bounding box, cortándose el texto o mostrando espacios fantasmas. Un jugador notará texto cortado o botones superpuestos.
   - Cómo detectarlo: Usar scripts Python/JS para calcular el ancho de la fuente española (usando librerías como `wcwidth`) y compararlo con el ancho de la bounding box del UI element en la pantalla, identificando desbordamientos even cuando los bytes son suficientes.
10. **Código-switching en UI y tooltips (inglés colado en textos en español)** (or:xingchen-agi/xing4.0-29b-a4b:free, prioridad alta)
   - Por qué: Mixturas como 'Press START' o 'HP:' dentro de textos en español neutro rompen la coherencia y el tono del juego, haciendo que la interfaz parezca traducida por amateurs. Destruye la immersion del jugador.
   - Cómo detectarlo: Buscar patrones de inglés colado (mayúsculas inusuales, verbos ingleses como 'Press', términos de Steam como 'Achievement', unidades como 'HP') en todos los textos, excluyendo las excepciones justificadas (nombres propios, códigos técnicos, nombres de canciones).
11. **Pluralización inconsistentes de nombres propios (Kiryu -> Kiryu vs Los Kiryu)** (or:xingchen-agi/xing4.0-29b-a4b:free, prioridad media)
   - Por qué: En el japonés, los nombres son invariantes plural. En español, añadir 'Los' a 'Kiryu' suena forzado o incorrecto dependiendo del contexto (personaje individual vs clan). La inconsistencia es audible y visual para el jugador.
   - Cómo detectarlo: Tabular todos los nombres propios de personajes y NPCs. Marcar si se añade 'Los' inconsistentemente o se omite en contextos donde el plural es gramaticalmente correcto en español neutro.
12. **Errores de aspecto verbal en cadenas dinámicas (${...})** (or:xingchen-agi/xing4.0-29b-a4b:free, prioridad media)
   - Por qué: Cambios temporales (pretérito perfecto vs pretérito indefinido) pueden distorsionar el significado en español, como 'Ha matado' vs 'Mató', alterando la percepción del estado del personaje o la línea temporal de la historia.
   - Cómo detectarlo: Revisar manualmente cada `${...}` variable donde el verbo cambia de tiempo. Comparar la conjugación española con la estructura inglesa original para asegurar que el aspecto verbal se preserve.
13. **Transliteración inconsistente de palabras japonesas (Yakuza, Ryuzaki)** (or:xingchen-agi/xing4.0-29b-a4b:free, prioridad media)
   - Por qué: Palabras como 'Yakuza' o 'Ryuzaki' pueden escribirse de formas raras o inconsistentes (Yakuza, Yakuzá, Yakuça), confundiendo al jugador que busca el significado o la identidad del personaje en menús o diálogos.
   - Cómo detectarlo: Crear una tabla de concordancia de transliteraciones aceptadas (ej. 'Ryuzaki', no 'Ryuziaki') y escanear todo el texto en busca de variaciones no estándar que no estén en el glosario oficial.
