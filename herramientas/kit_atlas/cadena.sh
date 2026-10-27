#!/bin/bash
# (claude1, Y6) Cadena automática: tandas de 15 con paginas_auto.py (solo gratuitos/locales) hasta que no quede nada.
cd /c/mods/yakuza6
export PYTHONIOENCODING=utf-8
while true; do
  n=$(python herramientas/kit_atlas/paginas_auto.py 15 2>&1 | tee -a tareas/y6_auto.log | grep -c "ACEPTADO\|^FIN")
  grep -q "^FIN 0 aceptados, 0 quedan" <(tail -1 tareas/y6_auto.log) && break
  [ "$n" -eq 0 ] && break
done
echo "CADENA FIN $(date +%H:%M)" >> tareas/y6_auto.log
