#!/bin/bash
# (Claude Code, 19-10-2026) Reparto de la REVISIÓN de lotes (los traducidos por Gemini/MiniMax/OpenCode, lista en
# trabajo/lotes/revisar_lista.txt). Imprime el siguiente lote sin revisar y lo reserva (mkdir atómico); nada si no quedan.
#   bash herramientas/reclamar_revision.sh QUIEN
L=/c/mods/yakuza6/trabajo/lotes
for i in $(cat $L/revisar_lista.txt); do
    if mkdir "$L/revisados/$i" 2>/dev/null; then echo "$1" > "$L/revisados/$i/quien"; echo $i; exit 0; fi
done
