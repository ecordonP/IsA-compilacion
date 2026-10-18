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

# Licencia incluida en la carpeta IsA (config.MENU): se instala donde la busca el menú
# (~/.config/IsA, como licencia.get_config_dir) si aún no hay ninguna instalada.
CFG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/IsA"
if [ -f "$DIR/config.MENU" ]; then
  if [ -f "$CFG_DIR/config.MENU" ]; then
    echo "Ya hay una licencia instalada en $CFG_DIR; no se ha cambiado."
    echo "Para usar la de esta carpeta, ábrala desde IsA con «Instalar licencia...»."
  else
    mkdir -p "$CFG_DIR"
    cp "$DIR/config.MENU" "$CFG_DIR/config.MENU"
    echo "Licencia instalada en $CFG_DIR."
  fi
fi
