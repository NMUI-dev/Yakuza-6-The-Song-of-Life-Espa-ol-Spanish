# Yakuza 6: The Song of Life — Spanish translation (source)

## Para jugar / To play

**No descargues el código (botón verde «Code»): no trae la traducción lista.** Descarga el zip de la última versión en **[Releases](https://github.com/NMUI-dev/Yakuza-6-The-Song-of-Life-Espa-ol-Spanish/releases/latest)** (`Yakuza.6.-.Traduccion.al.espanol.v1.0.5.zip`), descomprímelo en una carpeta, haz doble clic en **`INSTALAR o QUITAR.bat`** y escribe `1` (instalar). El instalador encuentra el juego de Steam solo y guarda una copia de los archivos originales para poder quitarla. Lee el `LEEME.txt` del zip.

*Do not download the source (green «Code» button): it does not contain the ready translation.* Get the zip from **[Releases](https://github.com/NMUI-dev/Yakuza-6-The-Song-of-Life-Espa-ol-Spanish/releases/latest)**, unzip it into a folder, double-click **`INSTALAR o QUITAR.bat`** and type `1` (install). The installer finds the Steam game by itself and backs up the original files so it can be removed.

**¿Quieres corregir esta traducción, pasarla a otro idioma o traducir otro Yakuza?** Usa las **[herramientas y la guía paso a paso](https://github.com/NMUI-dev/Yakuza-6-Herramientas-de-traduccion)**, con ParTool y reARMP incluidos.

**Para compilarla tú mismo:** guía paso a paso en español en **[COMPILAR.md](COMPILAR.md)**. **`PREPARAR TODO.bat`** descarga de una vez todo lo necesario (Python, ParTool, reARMP, texconv y las fuentes), comprobando cada archivo.

The rest of this page is the source code, for people who want to rebuild or check the mod.

Source code and translation data for the fan-made Spanish (Latin American neutral) translation of
*Yakuza 6: The Song of Life* (Steam, PC). Release v1.0.5.

**This repository contains no game files.** Everything here is our own scripts, the translated text and the
specifications used to redraw in-image text. To build the mod you need your own copy of the game from Steam.

## What the released mod contains

The release zip only replaces files inside the game's `data` folder:

| File | What it is | Built from |
|---|---|---|
| `data/db/e/*.bin` (187 tables) | Menus, items, missions, subtitles, manual (ARMP tables) | `herramientas/aplicar_db.py` + `trabajo/lotes/*_es.json` |
| `data/talk.par` | Substory / minigame dialogue | `herramientas/aplicar_talk.py` + `trabajo/lotes/*_es.json` |
| `data/font.par` | Font with Spanish letters added | `herramientas/letras_es.py`, `herramientas/letras_ascii.py` |
| `data/ui.par` | UI textures with English text redrawn in Spanish | `herramientas/kit_atlas/*`, `herramientas/rotulos*.py`, `herramientas/v101_*.py` + `trabajo/imagenes*/` specs; v1.0.3 chapter cards, map and signs: `trabajo/faltan_c1/*.py` |
| `data/hact/`, `data/auth/` (v1.0.3) | Cutscene subtitles (cmn.bin) | `herramienta_traduccion.py` + `datos/cmn_indice_v103.csv` of the [translation tools](https://github.com/NMUI-dev/Yakuza-6-Herramientas-de-traduccion) |

The installer (`entrega/instalar.ps1`, started by `entrega/INSTALAR o QUITAR.bat`) is a plain PowerShell script: it
finds the game through Steam's `libraryfolders.vdf`, backs up the original files and copies the translated ones;
option 2 restores the backup. It downloads nothing and runs nothing else.

The translation tools (`herramienta_traduccion.py extraer|aplicar`) and the step-by-step guide are in a
[separate repository](https://github.com/NMUI-dev/Yakuza-6-Herramientas-de-traduccion), which includes ParTool and reARMP.

## v1.0.5

- Whole-translation review scene by scene (`trabajo/revision_contexto_0611/`): `armar_escenas.py` puts every cutscene,
  speech list and talk in order with who speaks; free AI reviewers (`revisar_escenas.py`) flagged 398 possible errors and
  each one was decided by hand with the scene in front (`decididas_escenas.json` = fixed, `rechazadas.json` = not an error,
  with the reason). 677 fixes in `correcciones.json` (built by `correcciones_v105.py`, which checks tags, line breaks and
  byte limits): line breaks, terms, tú/usted, numbers, profanity restored to the original strength, gender, meaning.
- Tool fix (tools repository): one-word lines with "." or "-" ("B-Bullshit.", "Th-Thanks...") were taken for internal codes
  and never extracted, so 136 lines stayed in English; plus 34 visible cells in lower case or with "/". 53 texts translated
  (`nuevas_v105.json`).
- Built with `armar_v105.py` (extract with the fixed tool, put the fixes by their English text, apply, compare cell by cell
  with the published v1.0.4: only the intended cells change). A second extract of the build matches every row.

## v1.0.4

- Review after a Steam comment ("sometimes the gender is wrong"): `trabajo/revision_steam_0511/`. The 3,158 lines that
  describe a person were checked with the scene in front, speaker by speaker (`hablantes_y6.json`: 356 speaker ids with
  name and gender; the same character has a different id in each scene). `cruce_genero.py` cross-checks every scene.
- 12 fixes in `correcciones.json` (9 gender, 1 meaning, 2 typos). `chat_vivo.py` now strips `<...>` tags from what is typed
  in Live Chat (a `<font_kind>` tag had been typed as "FONT KIND" before the v1.0.3 manual fixes).
- Translation tool fix: `extraer` reused its working copies even when the translation had changed, so `textos.csv` could
  come from an older build. Each copy now stores the MD5 of its source. `comparar_tablas.py` checks, cell by cell, that
  only the intended fixes change against the published build.
- Built from v1.0.3 with the public tool: `poner_correcciones.py <tools>/trabajo/textos.csv`, then
  `herramienta_traduccion.py aplicar`.

## v1.0.3

- Texts still left in English are translated (`trabajo/faltan_c2/`: `cmn_scan.py` finds them in cmn.bin, `traducir.py`,
  `aplicar.py`, `chat_vivo.py`, `frases_cortas.py` for one-word lines, `terminos_saga.py` for the series' official
  Latin American terms, `correcciones_csv.py` / `revision_agente.py` for the review, `barrido_final.py` for the final
  sweep of the BUILT game).
- The narrow "i" (`herramientas/letra_i_estrecha.py`): the accented i drawn in another glyph's cell inherited its width.
- Images (`trabajo/faltan_c1/`): OCR of ALL 2,858 English UI textures (`ocr_todas_e.py`, `clasificar_ingles.py`), the
  13 chapter title cards (`capitulos_y6.py`), stylised signs and map street names (`rotulos_mano_y6.py`), and the list
  of what stays in English and why (`queda_ingles_imagenes.py`).
- Lessons for other translators: [LECCIONES_PARA_TRADUCTORES.md](LECCIONES_PARA_TRADUCTORES.md).

## Repository layout

```
herramientas/          our build scripts (Python 3 + a few bash scripts)
  kit_atlas/           texture text-replacement kit (OCR, erase, draw Spanish text, DDS save)
trabajo/lotes/         the translation: lote_NNN.json (English source) + lote_NNN_es.json (Spanish), indice.json
trabajo/clases_grupos.json   which table columns are player-visible text (TEXTO) vs internal ids (ID, never touched)
trabajo/imagenes/atlas_hechos/*.json   per-texture specs: box, English text, Spanish text, font, size, colours
trabajo/imagenes_ui/*.json   specs for title/pause/mission banners (atlas_es.json, rotulos_es.json)
entrega/               installer, exactly as shipped
terceros/reARMP/       reARMP (Ret-HZ, GPL-2.0), copied to herramientas/reARMP by PREPARAR TODO.bat
trabajo/revision_contexto_0611/ v1.0.5 review: scene-by-scene review, fixes and their reasons, build and checks
trabajo/revision_steam_0511/   v1.0.4 review: fixes, speakers and their gender, review scripts
```

## Requirements

- Windows 10/11, *Yakuza 6: The Song of Life* from Steam (English version, current Steam build).
- Python 3.12 with: `pip install numpy pillow opencv-python rapidocr-onnxruntime simple-lama-inpainting`
  (OCR and LaMa are only needed to regenerate textures; the text build only needs the standard library + numpy).
- Git Bash (for the `.sh` scripts).
- Third-party tools (not included, download them into these folders):
  - **ParTool** (ParManager by Kaplas80) — `herramientas/partool/ParTool.exe`
    <https://github.com/Kaplas80/ParManager/releases/download/v1.3.4/v1.3.4-windows-x64.zip>
    (SHA-256 of ParTool.exe: `b798027a243229c04741e491abb1f92ae4cc7a379c0cba31b81446f9be4e5b3f`)
  - **reARMP** (Ret-HZ, GPL-2.0) — `herramientas/reARMP/reARMP.py` <https://github.com/Ret-HZ/reARMP>
    (a copy with its LICENSE is in `terceros/reARMP/`)
  - **texconv** (Microsoft DirectXTex, MIT) — `herramientas/kit_atlas/texconv/texconv.exe`
    <https://github.com/microsoft/DirectXTex/releases>
  - Fonts for redrawn textures (Google Fonts, OFL/Apache) — `herramientas/fuentes_img/`:
    Bangers, Caveat Brush, Fjalla One, Gochi Hand, Kalam Bold, Knewave, Lilita One, Marck Script, Nanum Brush Script,
    Oswald, Permanent Marker, Rock Salt, Rubik Dirt, Sedgwick Ave Display, Shojumaru, Yuji Syuku
    (<https://fonts.google.com>). Some specs also use standard Windows fonts from `C:\Windows\Fonts`.

## How to build

Clone the repository to `C:\Mods\yakuza6` (a few scripts have that working folder hard-coded) and run all
commands from there in Git Bash. `GAME` is your game folder, e.g.
`GAME="/d/SteamLibrary/steamapps/common/Yakuza 6 - The Song of Life"`.

### 1. Copy and unpack the original files (never edit the Steam folder directly)

```bash
mkdir -p trabajo/original trabajo/extraido
cp -r "$GAME/data/db/e" trabajo/original/db_e
cp "$GAME/data/talk.par" "$GAME/data/ui.par" "$GAME/data/font.par" trabajo/original/
W=$(cygpath -w "$PWD/trabajo")
for p in talk ui font; do herramientas/partool/ParTool.exe extract -r "$W\\original\\$p.par" "$W\\extraido\\$p" < /dev/null; done
# ARMP tables -> JSON (sound_label.bin and ui_layer_text.bin do not export; they are not needed)
mkdir -p trabajo/armp_json
for f in trabajo/original/db_e/*.bin; do python herramientas/reARMP/reARMP.py "$f" && mv "$f.json" trabajo/armp_json/; done
python herramientas/armp_textos.py trabajo/armp_json trabajo/db_e_ingles.csv
python herramientas/sacar_talk.py       # -> trabajo/talk_ingles.csv
```

(`armp_textos.py`, `sacar_talk.py`, `clasificar_grupos.py` and `preparar_lotes.py` are how the English text was
extracted and split into the batches in `trabajo/lotes`; the batches are already in the repo.)

### 2. Text

```bash
python herramientas/aplicar_db.py trabajo/v5/db_e                                  # 187 translated ARMP tables
python herramientas/aplicar_talk.py trabajo/original/talk.par trabajo/v5/talk.par   # talk.par rebuilt layer by layer
```

`aplicar_db.py` changes only cells of TEXTO columns whose English has a translation and repacks them with reARMP.
`aplicar_talk.py` writes each Spanish line over the English one inside every `cmn.bin` (never past its byte slot) and
repacks `cmn.bin -> cmn.par -> scene.par -> talk.par` with ParTool. `herramientas/validar_lote.py` checks every batch
(tags, line breaks, byte limits, characters the font can draw).

### 3. Font

```bash
python herramientas/letras_es.py trabajo/extraido/font/e trabajo/font_add_final/e trabajo/lotes   # adds á é í ó ú ü ñ ¿ ¡ to gothic
python herramientas/letras_ascii.py                                                               # Í/í in the "|"/"~" cells -> trabajo/font_es_v5.par
```

`letras_es.py` builds the Spanish letters from pieces of the game's own font (base letter + accent) in unused kanji
cells and recomputes their metrics, without changing the file structure. In the menu font (`yakuza.dds`, Latin-1 grid
that already has most accents) only two cells were redrawn by hand: `¿` (the original cell had a `/`) and Í/í
(moved to the `|`/`~` cells by `letras_ascii.py`, see its header). The intermediate `font_es_v2.par` is
`trabajo/original/font.par` with `trabajo/font_add_final` added by `ParTool add`.

### 4. UI textures (`ui.par`)

```bash
python herramientas/rotulos_aplicar.py          # brush-style mission/enemy banners from trabajo/imagenes_ui/rotulos_es.json
python herramientas/atlas_es.py                 # title / pause menu atlases from trabajo/imagenes_ui/atlas_es.json
bash herramientas/v101_armar.sh                 # all atlases from trabajo/imagenes/atlas_hechos/*.json -> trabajo/ui_v3/ui.par
```

Each texture spec lists the English text box, the Spanish text, font, size and colours. The scripts erase the English
text (transparent pixels, or LaMa inpainting on opaque backgrounds), draw the Spanish text, and save the DDS with the
original header and mipmaps (`v101_bloques.py` keeps the original DXT blocks outside the edited boxes).
`v101_armar.sh` also copies the result to `entrega_v1.0.2/archivos/` and makes the release archives (WinRAR); the
paths at its top assume the working folder `C:\Mods\yakuza6`.

### 5. Package

Put `trabajo/v5/db_e` → `archivos/db_e`, `trabajo/v5/talk.par` → `archivos/talk.par`, `trabajo/font_es_v5.par` →
`archivos/font.par` and `trabajo/ui_v3/ui.par` → `archivos/ui.par` next to the files in `entrega/`. That folder is the
released mod.

## Testing

We tested in a separate copy of the game so the Steam install was never modified until the end, then installed with
the installer on the Steam copy and played. That test setup is not part of this repository.

## Credits and licenses

- Our scripts, installer and translation data: MIT (see `LICENSE`). The game, its text and its assets belong to SEGA;
  this is an unofficial fan translation and is not affiliated with SEGA.
- ParTool / ParManager — Kaplas80 (see its repository for the license). reARMP — Ret-HZ (GPL-2.0). texconv — Microsoft (MIT). Fonts — their authors
  (SIL OFL / Apache 2.0).
- Translation made with AI assistance (Claude by Anthropic, Google Gemini and free OpenRouter models) and reviewed.
