#!/usr/bin/env bash
# Compila IsA.app para macOS y genera IsA-macos-<arquitectura>.dmg: arm64 (Apple
# Silicon) o x86_64 (Intel), según el Mac en que se ejecute.
#
# Los scripts ofuscados se generan antes en Windows con `python obfuscate_mac.py`
# (la licencia de pyarmor no admite CI) y se suben en obf_mac/. Aquí solo se
# comprueba que están al día y se compila con PyInstaller.
#
# Requisitos: macOS (arm64 o x86_64) y Python 3.11 con requirements-mac.txt instalado.
#
# Variables de entorno opcionales:
#   ISA_CODESIGN_IDENTITY   "Developer ID Application: Nombre (TEAMID)"; sin ella se
#                           firma ad hoc (válido solo para pruebas internas)
#   ISA_SKIP_PYARMOR=1      compila sin ofuscar (solo para depurar)
set -euo pipefail

cd "$(dirname "$0")"

ARCH="$(uname -m)"
case "$ARCH" in
    arm64)  OBF_TARGET=mac;       DMG_NAME=IsA-macos-arm64.dmg ;;
    x86_64) OBF_TARGET=mac_intel; DMG_NAME=IsA-macos-intel.dmg ;;
    *) echo "Arquitectura no admitida: $ARCH" >&2; exit 1 ;;
esac
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Este script debe ejecutarse en macOS." >&2
    exit 1
fi
export ISA_TARGET_ARCH="$ARCH"

APPS=(Menu Datos Graficos Descriptivas Likert Tablas Comparar Fiabilidad Regresion Muestra SimpleTest)

rm -rf build dist

if [[ "${ISA_SKIP_PYARMOR:-0}" != "1" ]]; then
    # En el repositorio público de compilación no hay fuentes: la comprobación se hizo al publicar
    if [[ -f obfuscate_mac.py ]]; then
        echo "==> Comprobando scripts ofuscados ($OBF_TARGET)"
        python obfuscate_mac.py --check "$OBF_TARGET"
    fi
    if [[ "$ARCH" == "arm64" ]]; then export ISA_OBF_DIR="$PWD/obf_mac"; else export ISA_OBF_DIR="$PWD/obf_mac_intel"; fi
    export ISA_REQUIRE_PYARMOR=1
else
    export ISA_OBF_DIR="$PWD/build/no-obf"
fi

echo "==> Compilando IsA.app con PyInstaller"
pyinstaller --noconfirm --clean IsA_mac.spec

APP="dist/IsA.app"
for name in "${APPS[@]}"; do
    test -x "$APP/Contents/MacOS/$name" || { echo "Falta el ejecutable $name" >&2; exit 1; }
done

if [[ -n "${ISA_CODESIGN_IDENTITY:-}" ]]; then
    echo "==> Verificando firma"
    codesign --verify --deep --strict --verbose=2 "$APP"
fi

echo "==> Creando DMG"
STAGE="build/dmg"
rm -rf "$STAGE" && mkdir -p "$STAGE"
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
cp "mac/Instrucciones de instalación.html" "$STAGE/"
hdiutil create -volname "IsA" -srcfolder "$STAGE" -ov -format UDZO "dist/$DMG_NAME"

if [[ -n "${ISA_CODESIGN_IDENTITY:-}" ]]; then
    codesign --force --sign "$ISA_CODESIGN_IDENTITY" "dist/$DMG_NAME"
fi

echo "==> Listo: dist/IsA.app y dist/$DMG_NAME"
