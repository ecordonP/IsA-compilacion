# IsA (versión reducida): compilación para macOS y Linux

Este repositorio **no contiene el código fuente** de IsA – Intelligent Statistical
Assistant. Solo contiene lo necesario para compilar las versiones de macOS y Linux en
GitHub Actions:

- `obf_mac/`, `obf_mac_intel/`, `obf_linux/`: el programa **ofuscado con pyarmor** para
  macOS Apple Silicon, macOS Intel y Linux x86_64.
- Un archivo por programa (`Menu.py`, `Datos.py`...) con **solo sus líneas `import`**,
  que PyInstaller necesita para saber qué librerías incluir. No contienen el programa.
- Specs de PyInstaller, scripts de compilación, *runtime hooks* y flujos de Actions.

El código fuente está en un repositorio privado; este se actualiza desde allí con
`publicar_compilacion.py`. **No edite este repositorio a mano.**

## Compilaciones

| Flujo | Máquina | Resultado |
|---|---|---|
| Compilar macOS (Apple Silicon) | `macos-15` (M1–M5) | `IsA-macos-arm64.dmg` |
| Compilar macOS (Intel) | `macos-15-intel` | `IsA-macos-intel.dmg` |
| Compilar Linux (Ubuntu) | `ubuntu-22.04` (Ubuntu 22.04 o posterior) | `IsA-linux-x86_64.tar.gz` |

Se lanzan desde Actions → el flujo → **Run workflow**, o con una etiqueta `v*` (los tres).
Cada flujo comprueba que el menú y los 10 módulos arrancan, con una licencia de prueba
que se guarda como secreto cifrado del repositorio (`ISA_CI_LICENSE`).

## Licencia

IsA es software con licencia de uso (ver `licencia.md`). Las licencias van firmadas
digitalmente: el programa solo contiene la clave pública, que permite comprobarlas pero
no crearlas. © 2026 Eulogio Cordón Pozo, Universidad de Granada.
