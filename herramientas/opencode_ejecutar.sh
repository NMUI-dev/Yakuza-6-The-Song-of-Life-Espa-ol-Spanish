#!/bin/bash
# (Claude Code, 17-10-2026; copia para Yakuza 6 19-10) Lanza una tarea de OpenCode y la vigila: a veces se cuelga al arrancar («init») sin hacer nada.
# Si en 120 s no ha empezado a trabajar (no aparece «loop session» en su log), lo mata y lo reintenta (hasta 3 veces).
#   opencode_ejecutar.sh herramientas/opencode_tareas/tareaN.txt
R=/c/mods/yakuza6/trabajo/lotes
# XDG_DATA_HOME lo pone trabajador_opencode.sh (una carpeta por agente)
# (18-10) con 8 agentes a la vez se agotó la cuota gratuita («Rate limit exceeded»): MÁXIMO 2-3 a la vez, y si un
# modelo se queda sin cuota se prueba el siguiente de la lista.
MODELOS=${OPENCODE_MODELO:-"opencode/glm-5.3-flash-free opencode/big-pickle opencode/nemotron-3-ultra-free"}   # (19-10) deepseek-flash se corta tras el primer ls
TAREA=$1
SALIDA=${TAREA%.txt}_salida.txt
LOGDIR=$(echo "$XDG_DATA_HOME" | sed "s|^C:|/c|")/opencode/log
cd $R
for MODELO in $MODELOS; do
for intento in 1 2 3; do
    antes=$(cat "$LOGDIR"/*.log 2>/dev/null | grep -c "loop session")
    opencode run -m "$MODELO" "$(cat "$TAREA")" > "$SALIDA" 2>&1 &
    pid=$!
    arranco=0
    for s in $(seq 1 24); do
        sleep 5
        ahora=$(cat "$LOGDIR"/*.log 2>/dev/null | grep -c "loop session")
        if [ "$ahora" -gt "$antes" ]; then arranco=1; break; fi
        kill -0 $pid 2>/dev/null || break
    done
    if [ $arranco = 1 ]; then
        echo "intento $intento: trabajando"
        # (18-10) vigilar mientras trabaja: si la última línea del log es «Rate limit» y el log lleva 90 s sin
        # cambiar, el modelo se quedó sin cuota a mitad: se corta y se pasa al siguiente modelo
        rl=0
        while kill -0 $pid 2>/dev/null; do
            sleep 15
            f=$(ls -t "$LOGDIR"/*.log 2>/dev/null | head -1)
            if [ -n "$f" ] && tail -1 "$f" | grep -q "Rate limit" && [ $(( $(date +%s) - $(stat -c %Y "$f") )) -gt 90 ]; then rl=1; kill $pid 2>/dev/null; break; fi
        done
        wait $pid 2>/dev/null; rc=$?
        if [ $rl = 1 ]; then echo "intento $intento: $MODELO sin cuota a mitad (Rate limit); paso al siguiente modelo"; continue 2; fi
        if grep -q "Rate limit exceeded" "$SALIDA" && [ ! -s "${TAREA%.txt}_INFORME.md" ]; then
            echo "intento $intento: $MODELO sin cuota (Rate limit); paso al siguiente modelo"; continue 2
        fi
        echo "terminado (código $rc, modelo $MODELO)"; exit 0
    fi
    echo "intento $intento: colgado al arrancar, se reintenta"
    kill $pid 2>/dev/null   # (solo el suyo: el otro agente puede estar trabajando a la vez)
    sleep 3
done
done
echo "OpenCode no arrancó o todos los modelos sin cuota"; exit 1
