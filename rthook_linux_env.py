# -*- coding: utf-8 -*-
"""
Runtime hook de PyInstaller (solo Linux): el arranque de PyInstaller añade la carpeta
_internal a LD_LIBRARY_PATH. Los programas del sistema que lanza IsA (navegador web,
xdg-open...) la heredarían y cargarían bibliotecas del paquete en lugar de las del
sistema, lo que puede hacerlos fallar en distribuciones más nuevas. Se restablece el
valor original; los módulos de IsA que lanza el menú no se ven afectados, porque el
arranque de cada uno vuelve a fijar su propia ruta.
"""
import os
import sys

if sys.platform.startswith("linux") and getattr(sys, "frozen", False):
    _orig = os.environ.pop("LD_LIBRARY_PATH_ORIG", None)
    if _orig:
        os.environ["LD_LIBRARY_PATH"] = _orig
    else:
        os.environ.pop("LD_LIBRARY_PATH", None)
