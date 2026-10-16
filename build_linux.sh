#!/usr/bin/env bash
# Compila IsA para Linux (x86_64, Ubuntu 22.04 o posterior) y genera
# dist/IsA-linux-x86_64.tar.gz (carpeta IsA + instalar_isa.sh).
#
# Los scripts ofuscados se generan antes en Windows con `python obfuscate_mac.py`
# (la licencia de pyarmor no admite CI) y se suben en obf_linux/.
#
# Requisitos: Linux x86_64 y Python 3.11 con requirements-mac.txt instalado.
# Variable opcional: ISA_SKIP_PYARMOR=1 compila sin ofuscar (solo para depurar).
set -euo pipefail
cd "$(dirname "$0")"

if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
    echo "Este script debe ejecutarse en Linux x86_64." >&2
    exit 1
fi

APPS=(Menu Datos Graficos Descriptivas Likert Tablas Comparar Fiabilidad Regresion Muestra SimpleTest)

rm -rf build dist

if [[ "${ISA_SKIP_PYARMOR:-0}" != "1" ]]; then
    # En el repositorio público de compilación no hay fuentes: la comprobación se hizo al publicar
    if [[ -f obfuscate_mac.py ]]; then
        echo "==> Comprobando scripts ofuscados (obf_linux/)"
        python obfuscate_mac.py --check linux
    fi
    export ISA_OBF_DIR="$PWD/obf_linux"
    export ISA_REQUIRE_PYARMOR=1
else
    export ISA_OBF_DIR="$PWD/build/no-obf"
fi

echo "==> Compilando IsA con PyInstaller"
pyinstaller --noconfirm --clean IsA_linux.spec

APP="dist/IsA"
for name in "${APPS[@]}"; do
    test -x "$APP/$name" || { echo "Falta el ejecutable $name" >&2; exit 1; }
done

echo "==> Creando IsA-linux-x86_64.tar.gz"
python - "$PWD/IsA.ico" "$APP/isa.png" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1])
im.size = sorted(im.info.get("sizes", [im.size]))[-1]
im.convert("RGBA").resize((256, 256), Image.LANCZOS).save(sys.argv[2])
PY
cp linux/instalar_isa.sh "$APP/instalar_isa.sh"
cp "linux/LEEME_LINUX.txt" "$APP/LEEME.txt"
chmod +x "$APP/instalar_isa.sh"
tar -C dist -czf dist/IsA-linux-x86_64.tar.gz IsA
echo "==> Listo: dist/IsA y dist/IsA-linux-x86_64.tar.gz"
