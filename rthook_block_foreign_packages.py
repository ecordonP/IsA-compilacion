# Runtime hook de PyInstaller para ejecutables que comparten carpeta _internal.
#
# En C:\IsA varios módulos (Menu, Datos, Bayesiano...) comparten _internal. Si
# este ejecutable no incluye un paquete (p. ej. pyarrow) pero otro módulo dejó en
# _internal una carpeta con sus binarios, Python la importa como "namespace
# package" vacío. Las librerías que prueban "try: import pyarrow" creen entonces
# que está instalado y fallan (p. ej. pandas: "module 'pyarrow' has no attribute
# '__version__'").
#
# Este hook hace que esas carpetas ajenas se traten como paquetes no instalados
# (ModuleNotFoundError), igual que si el ejecutable estuviera en su propia carpeta.
import os
import sys
from importlib.machinery import PathFinder


def _bundled_names():
    """Nombres de módulos/paquetes incluidos en el PYZ de este ejecutable."""
    try:
        import pyimod02_importers
        return pyimod02_importers.pyz_archive.toc
    except Exception:
        return {}


class _BlockForeignNamespacePackages:
    def __init__(self, base_dir):
        self.base_dir = os.path.normcase(os.path.abspath(base_dir))

    def _inside_bundle(self, location):
        location = os.path.normcase(os.path.abspath(location))
        return location == self.base_dir or location.startswith(self.base_dir + os.sep)

    def find_spec(self, fullname, path=None, target=None):
        if path is not None or "." in fullname:
            return None  # solo paquetes de primer nivel
        if fullname in _bundled_names():
            return None  # incluido en este ejecutable (también namespace packages legítimos)
        spec = PathFinder.find_spec(fullname, sys.path)
        if spec is None or spec.loader is not None or not spec.submodule_search_locations:
            return None  # módulo normal (o no encontrado): comportamiento estándar
        locations = list(spec.submodule_search_locations)
        if locations and all(self._inside_bundle(loc) for loc in locations):
            raise ModuleNotFoundError(f"No module named '{fullname}'", name=fullname)
        return None


_base = getattr(sys, "_MEIPASS", None)
if _base:
    sys.meta_path.insert(0, _BlockForeignNamespacePackages(_base))
