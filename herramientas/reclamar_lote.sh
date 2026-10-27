#!/bin/bash
# (Claude Code, 19-10-2026) Reparto de lotes entre varios traductores a la vez (Fable y OpenCode).
# Imprime el siguiente lote libre (NNN) y lo deja reservado con mkdir (atómico); nada si no quedan.
#   bash herramientas/reclamar_lote.sh QUIEN
L=/c/mods/yakuza6/trabajo/lotes
for i in $(seq -f "%03g" 0 116); do
    [ -f "$L/lote_${i}_es.json" ] && python /c/mods/yakuza6/herramientas/validar_lote.py $i >/dev/null 2>&1 && continue
    if mkdir "$L/reclamados/$i" 2>/dev/null; then echo "$1" > "$L/reclamados/$i/quien"; echo $i; exit 0; fi
done
