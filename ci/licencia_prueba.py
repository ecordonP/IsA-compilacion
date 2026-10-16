# -*- coding: utf-8 -*-
"""
Instala la licencia de PRUEBA para la prueba de arranque de GitHub Actions.

La licencia está firmada con la clave privada del autor (fuera del repositorio) y se
guarda como secreto cifrado del repositorio (ISA_CI_LICENSE, en base64): no aparece en
el repositorio aunque sea público, ni se incluye en IsA.app, el .dmg o el .tar.gz.
Se crea y actualiza con publicar_compilacion.py --secreto.

Uso:  python ci/licencia_prueba.py <carpeta_destino>     (lee ISA_CI_LICENSE)
"""
import base64
import os
import sys

value = os.environ.get("ISA_CI_LICENSE", "").strip()
if not value:
    sys.exit("Falta el secreto ISA_CI_LICENSE (licencia de prueba): ejecute "
             "'python publicar_compilacion.py --secreto' en el equipo del autor.")
dest = sys.argv[1]
os.makedirs(dest, exist_ok=True)
with open(os.path.join(dest, "config.MENU"), "wb") as f:
    f.write(base64.b64decode(value))
print("Licencia de prueba instalada en", os.path.join(dest, "config.MENU"))
