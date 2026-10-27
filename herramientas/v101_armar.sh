#!/bin/bash
# (claude1, 25-10-2026) Arma la v1.0.1 del Y6 de principio a fin: atlas -> restaurar -> ui_v3/add -> bloques originales ->
# ui.par -> comprobación -> entrega_v1.0.2 -> 2 rar (traducción sin .exe / herramientas aparte) -> prueba de los rar.
set -e
cd /c/Mods/yakuza6
python -X utf8 herramientas/kit_atlas/atlas_probar.py aplicar | tail -1
python -I herramientas/v101_restaurar.py
cd trabajo
rm -rf ui_v3/add; cp -r ui_v2/add ui_v3/add
L=$( (tr -d '\r' < imagenes/v101_tocadas.txt | sed 's/^e__texture__//'; tr -d '\r' < imagenes_ui/v101_rotulos.txt
      printf '%s\n' pausemenu clear_result title_press_any_button pause_nouryoku_lvup) | sort -u)
for b in $L; do
  f=ui_v3/add/e/texture/$b.dds; [ -f $f ] || continue
  case $b in mg_gym_jump_p1|mg_gym_jump_p1_[dknpx]) cp extraido/ui/e/texture/$b.dds $f; continue;; esac   # se quedan como el original
  s=imagenes/es/e/texture/$b.dds; [ -f $s ] || s=imagenes_ui/es/$b.dds
  cp $s $f
done
cd ..
python -I herramientas/v101_bloques.py trabajo/ui_v3/add/e/texture | tail -1
W=$(cygpath -w "$PWD/trabajo")
rm -f trabajo/ui_v3/ui.par
./herramientas/partool/ParTool.exe add "$W\\original\\ui.par" "$W\\ui_v3\\add" "$W\\ui_v3\\ui.par" < /dev/null | tail -1
S=$(mktemp -d); ./herramientas/partool/ParTool.exe extract "$W\\ui_v3\\ui.par" "$(cygpath -w $S)" < /dev/null > /dev/null
ok=0; bad=0; for f in trabajo/ui_v3/add/e/texture/*.dds; do cmp -s $f "$S/e/texture/$(basename $f)" && ok=$((ok+1)) || bad=$((bad+1)); done
echo "ui.par: archivos=$(find $S -type f | wc -l) texturas_ok=$ok mal=$bad"; rm -rf "$S"; [ $bad = 0 ]
cp trabajo/ui_v3/ui.par entrega_v1.0.2/archivos/ui.par
RAR="/c/Program Files/WinRAR/Rar.exe"; rm -f rar/*v1.0.2*.rar
cd entrega_v1.0.2
"$RAR" a -r -m3 -idq "../rar/Yakuza 6 - Traduccion al espanol v1.0.2.rar" archivos AVISO.txt "INSTALAR o QUITAR.bat" instalar.ps1 LEEME.txt
"$RAR" a -r -m3 -idq "../rar/Yakuza 6 - Herramientas para traduccion v1.0.2.rar" "Herramientas para traduccion"
cd ..
for r in rar/*v1.0.2*.rar; do "$RAR" t -idq "$r" && echo "rar OK: $r"; done
echo "exe en el rar de traducción: $("$RAR" lb "rar/Yakuza 6 - Traduccion al espanol v1.0.2.rar" | grep -ci '\.exe')"
md5sum trabajo/ui_v3/ui.par
