#!/bin/bash
# (Claude Code, 19-10-2026) Trabajador OpenCode: reclama lotes libres uno a uno y los traduce hasta que no queden.
#   bash herramientas/trabajador_opencode.sh NOMBRE     (máximo 2-3 a la vez por la cuota gratuita)
Y=/c/mods/yakuza6; Q=$1
export XDG_DATA_HOME=C:/mods/yakuza6/tareas/opencode/datos_$Q
mkdir -p "$Y/tareas/opencode/datos_$Q"
fallos=0
while true; do
    N=$(bash $Y/herramientas/reclamar_lote.sh "opencode_$Q"); [ -z "$N" ] && { echo "$(date +%T) sin lotes libres: fin"; exit 0; }
    T=$Y/tareas/opencode/lote_${N}_$Q.txt
    sed "s/NNN/$N/g" $Y/tareas/opencode/plantilla.txt > $T
    echo "$(date +%T) lote $N: empiezo"
    # vigilante de arranque/cuota (copia del de crash4-coop, trabajando en trabajo/lotes)
    bash $Y/herramientas/opencode_ejecutar.sh "$T"
    if python $Y/herramientas/validar_lote.py $N >/dev/null 2>&1; then echo "$(date +%T) lote $N: OK"; fallos=0
    else echo "$(date +%T) lote $N: FALLÓ (se libera)"; rm -rf "$Y/trabajo/lotes/reclamados/$N"; fallos=$((fallos+1))
         [ $fallos -ge 4 ] && { echo "3 fallos seguidos: paro"; exit 1; }; fi
done
