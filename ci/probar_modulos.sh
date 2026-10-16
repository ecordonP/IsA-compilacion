#!/usr/bin/env bash
# Prueba de arranque: abre el menú y cada módulo compilado y comprueba que siguen en
# marcha pasados unos segundos (si falta una librería o hay un error al importar, el
# programa termina enseguida). Necesita una licencia (ci/licencia_prueba.py) y, en
# Linux, una pantalla (Xvfb).
#
# Uso:  bash ci/probar_modulos.sh <carpeta_con_los_ejecutables> <config.MENU>
set -uo pipefail
DIR="$1"
export ISA_MENU_CONFIG="$2"
APPS=(Menu Datos Graficos Descriptivas Likert Tablas Comparar Fiabilidad Regresion Muestra SimpleTest)
WAIT=${ISA_TEST_WAIT:-25}
failed=()
for app in "${APPS[@]}"; do
    log="$(mktemp)"
    "$DIR/$app" --launched-from-menu > "$log" 2>&1 &
    pid=$!
    for _ in $(seq "$WAIT"); do
        sleep 1
        kill -0 "$pid" 2>/dev/null || break
    done
    if kill -0 "$pid" 2>/dev/null; then
        echo "OK     $app"
        kill "$pid" 2>/dev/null; sleep 1; kill -9 "$pid" 2>/dev/null
    else
        wait "$pid"; rc=$?
        echo "FALLO  $app (terminó con código $rc)"
        tail -n 40 "$log"
        failed+=("$app")
    fi
    rm -f "$log"
done
# El menú anota el último uso en config.MENU solo si la licencia es válida: si no se ha
# anotado, el menú se quedó en la ventana de error de licencia (no es un arranque correcto)
if ! grep -q '"estado"' "$ISA_MENU_CONFIG"; then
    echo "FALLO  Menu: la licencia de prueba no se ha aceptado (sin «estado» en config.MENU)"
    failed+=("licencia")
fi
if [ ${#failed[@]} -gt 0 ]; then
    echo "No arrancan: ${failed[*]}"
    exit 1
fi
echo "Todos los programas arrancan correctamente."
