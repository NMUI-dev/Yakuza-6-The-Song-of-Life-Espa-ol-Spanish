# Cómo compilar la traducción de Yakuza 6 desde el código

Esto es para quien quiera **rehacer o revisar** la traducción. **Para jugar no hace falta:** descarga el zip de
[Releases](https://github.com/NMUI-dev/Yakuza-6-The-Song-of-Life-Espa-ol-Spanish/releases/latest), descomprímelo y
abre `INSTALAR o QUITAR.bat`.

## Lo que necesitas

- Windows 10/11 y *Yakuza 6: The Song of Life* de Steam (versión en inglés, la actual de Steam).
- [Git para Windows](https://git-scm.com/download/win) (trae **Git Bash**, donde se escriben los comandos de abajo).
- Todo lo demás lo baja **`PREPARAR TODO.bat`** (paso 2).

## 1. Descargar el código

Ponlo en `C:\Mods\yakuza6`: algunos scripts tienen esa carpeta escrita dentro. En Git Bash:

```bash
mkdir -p /c/Mods && cd /c/Mods
git clone https://github.com/NMUI-dev/Yakuza-6-The-Song-of-Life-Espa-ol-Spanish.git yakuza6
cd yakuza6
```

(Sin Git: botón verde **Code → Download ZIP** y descomprímelo como `C:\Mods\yakuza6`.)

## 2. Descargar todo lo necesario de una vez

Doble clic en **`PREPARAR TODO.bat`**. Hace esto solo, comprobando la SHA-256 de cada archivo:

| Qué | De dónde | Dónde lo deja |
|---|---|---|
| Python 3.12 (si no lo tienes, te pregunta si lo instala con winget) | python.org | el sistema |
| Paquetes de Python: numpy; y si dices que sí, los de imágenes (pillow, opencv, rapidocr, simple-lama-inpainting; unos 3 GB) | PyPI | el sistema |
| ParTool 1.3.4 (Kaplas80) | GitHub de ParManager | `herramientas/partool/` |
| reARMP (Ret-HZ, GPL-2.0) | copia incluida en `entrega/.../programas/reARMP` | `herramientas/reARMP/` |
| texconv may2026 (Microsoft DirectXTex, MIT) | GitHub de DirectXTex | `herramientas/kit_atlas/texconv/` |
| 16 fuentes (Bangers, Oswald, Permanent Marker...) | Google Fonts | `herramientas/fuentes_img/` |

Puedes abrirlo las veces que quieras: lo que ya está bien no se vuelve a bajar. Con
`PREPARAR TODO.bat -SoloTexto` instala solo lo necesario para el texto (sin los 3 GB de imágenes).

## 3. Copiar y desempaquetar los archivos del juego

Nunca se toca la carpeta de Steam: se trabaja con copias. Cambia `GAME` por la carpeta de tu juego:

```bash
GAME="/c/Program Files (x86)/Steam/steamapps/common/Yakuza 6 - The Song of Life"
mkdir -p trabajo/original trabajo/extraido
cp -r "$GAME/data/db/e" trabajo/original/db_e
cp "$GAME/data/talk.par" "$GAME/data/ui.par" "$GAME/data/font.par" trabajo/original/
W=$(cygpath -w "$PWD/trabajo")
for p in talk ui font; do herramientas/partool/ParTool.exe extract -r "$W\\original\\$p.par" "$W\\extraido\\$p" < /dev/null; done
mkdir -p trabajo/armp_json
for f in trabajo/original/db_e/*.bin; do python herramientas/reARMP/reARMP.py "$f" && mv "$f.json" trabajo/armp_json/; done
python herramientas/armp_textos.py trabajo/armp_json trabajo/db_e_ingles.csv
python herramientas/sacar_talk.py
```

(`sound_label.bin` y `ui_layer_text.bin` no se convierten: no hacen falta.)

## 4. Texto

```bash
python herramientas/aplicar_db.py trabajo/v5/db_e                                  # las 187 tablas traducidas
python herramientas/aplicar_talk.py trabajo/original/talk.par trabajo/v5/talk.par   # talk.par rehecho capa a capa
```

La traducción está en `trabajo/lotes/lote_NNN_es.json`. `herramientas/validar_lote.py` revisa cada lote (etiquetas,
saltos de línea, límite de bytes y letras que la fuente puede dibujar).

## 5. Fuente

```bash
python herramientas/letras_es.py trabajo/extraido/font/e trabajo/font_add_final/e trabajo/lotes   # añade á é í ó ú ü ñ ¿ ¡
python herramientas/letras_ascii.py                                                               # -> trabajo/font_es_v5.par
```

## 6. Texturas con texto (`ui.par`)

Necesita los paquetes de imágenes del paso 2.

```bash
python herramientas/rotulos_aplicar.py          # rótulos de misiones y enemigos
python herramientas/atlas_es.py                 # menú de título y de pausa
bash herramientas/v101_armar.sh                 # el resto de atlas -> trabajo/ui_v3/ui.par
```

`v101_armar.sh` también copia el resultado a `entrega_v1.0.2/archivos/` y, si tienes WinRAR, crea los archivos de la
versión.

## 7. Armar el mod

Copia junto a los archivos de `entrega/`, dentro de una carpeta `archivos/`:

| Origen | Destino |
|---|---|
| `trabajo/v5/db_e` | `archivos/db_e` |
| `trabajo/v5/talk.par` | `archivos/talk.par` |
| `trabajo/font_es_v5.par` | `archivos/font.par` |
| `trabajo/ui_v3/ui.par` | `archivos/ui.par` |

Esa carpeta es el mod: `INSTALAR o QUITAR.bat` lo instala en el juego (guarda antes los originales) y lo quita.
