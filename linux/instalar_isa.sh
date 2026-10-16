#!/bin/bash
# Añade IsA al menú de aplicaciones del usuario (no necesita permisos de administrador).
# Uso: descomprima IsA-linux-x86_64.tar.gz donde quiera conservarlo y ejecute
#      ./instalar_isa.sh   desde la carpeta IsA.
# Para quitarlo del menú:  ./instalar_isa.sh --desinstalar
set -e
DIR="$(cd "$(dirname "$0")" && pwd -P)"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP="$APPS/isa.desktop"
if [ "${1:-}" = "--desinstalar" ]; then
  rm -f "$DESKTOP"
  echo "IsA se ha quitado del menú (la carpeta $DIR no se ha borrado)."
  exit 0
fi
mkdir -p "$APPS"
cat > "$DESKTOP" <<DESKTOP_ENTRY
[Desktop Entry]
Type=Application
Name=IsA
Comment=Intelligent Statistical Assistant
Exec="$DIR/Menu"
Path=$DIR
Icon=$DIR/isa.png
Categories=Science;Education;Math;
Terminal=false
DESKTOP_ENTRY
chmod +x "$DESKTOP" "$DIR/Menu"
command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" 2>/dev/null || true
echo "IsA añadido al menú de aplicaciones. También puede abrirlo con: $DIR/Menu"
