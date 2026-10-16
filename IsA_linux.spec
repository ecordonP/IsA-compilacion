# -*- mode: python ; coding: utf-8 -*-
#
# Spec de Linux (x86_64, Ubuntu 22.04 o posterior): carpeta IsA con el menú y los 10
# módulos, que comparten la carpeta _internal (como en Windows).
#
# Ofuscación: los scripts se ofuscan en Windows con `python obfuscate_mac.py`
# (pyarmor --platform linux.x86_64) en obf_linux/, y este spec sustituye en cada
# Analysis el código fuente por el ofuscado.
#
# Variables de entorno opcionales:
#     ISA_OBF_DIR             carpeta con los scripts ofuscados (por defecto obf_linux)
#     ISA_REQUIRE_PYARMOR=1   falla si no hay scripts ofuscados (lo usa la CI)
import os

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, copy_metadata

ROOT = SPECPATH
OBF = os.environ.get('ISA_OBF_DIR', os.path.join(ROOT, 'obf_linux'))
RUNTIME_PKG = 'pyarmor_runtime_011681'
USE_PYARMOR = os.path.isdir(os.path.join(OBF, RUNTIME_PKG))
if os.environ.get('ISA_REQUIRE_PYARMOR') == '1' and not USE_PYARMOR:
    raise SystemExit(f'No se encuentran los scripts ofuscados en {OBF}')


PYREADSTAT_IMPORTS = [
    'pyreadstat._readstat_writer',
    'pyreadstat._readstat_parser',
    'pyreadstat.worker',
]
# El arranque de PyInstaller (pyi_rth_pkgres) carga pkg_resources, que necesita jaraco y
# backports.tarfile. Se incluyen en cada programa: si no, rthook_block_foreign_packages los
# trata como paquetes ajenos de la carpeta compartida y el programa no arranca.
PKG_RESOURCES_IMPORTS = ['jaraco.text', 'jaraco.context', 'jaraco.functools', 'backports.tarfile']
# Linux: PIL.ImageTk carga PIL._tkinter_finder de forma dinámica (PyInstaller no lo ve) y sin
# él falla «invalid command name PyImagingPhoto» en los módulos con imágenes (Likert, Muestra)
PKG_RESOURCES_IMPORTS += ['PIL._tkinter_finder']
BOKEH_IMPORTS = [
    'bokeh.resources',
    'bokeh.util',
    'bokeh._version',
    'bokeh.settings',
    'bokeh.core.templates',
    'bokeh.core.property.bases',
    'bokeh.core.property.container',
    'bokeh.core.property.singletons',
    'bokeh.core.property.descriptors',
    'bokeh.core.property.struct',
]
# Con todos los módulos en un mismo paquete, evita que un módulo importe como
# namespace package vacío una librería que solo incluye otro (ver el propio hook).
# rthook_linux_env: los programas del sistema que se lanzan no heredan _internal
COMMON_RTHOOKS = [os.path.join(ROOT, 'rthook_block_foreign_packages.py'),
                  os.path.join(ROOT, 'rthook_linux_env.py')]

# --- Regresion: diagnostic.py de statsmodels como dato (igual que en Windows) ---
import statsmodels.stats.diagnostic as _sm_diagnostic
_regresion_datas = (
    copy_metadata('bokeh') + copy_metadata('IPython') + copy_metadata('pyreadstat')
    + collect_data_files('bokeh') + collect_data_files('IPython')
    + [(os.path.abspath(_sm_diagnostic.__file__), 'statsmodels/stats')]
)

# (nombre del ejecutable = nombre en APPS de Menu.py, script, opciones de Analysis)
TARGETS = [
    ('Menu', 'Menu.py', dict(
        datas=[(os.path.join(ROOT, f), '.') for f in ('LogoOE2.png', 'logoIsA.png', 'licencia.md', 'IsA.ico')],
    )),
    ('Datos', 'Datos.py', dict(
        excludes=[
            'torch', 'torchvision', 'torchaudio', 'transformers', 'tokenizers',
            'safetensors', 'onnxruntime', 'tensorflow', 'keras', 'jax', 'jaxlib',
            'numba', 'llvmlite',
            'av', 'cv2', 'yt_dlp', 'mutagen', 'brotli', 'curl_cffi', 'websockets',
            'pyarrow', 'dask', 'polars',
            'IPython', 'jupyter', 'jupyter_client', 'jupyter_core', 'notebook',
            'ipykernel', 'sphinx', 'pytest',
            'bokeh', 'plotly', 'sympy',
        ],
    )),
    ('Graficos', 'Graficos.py', dict()),
    ('Descriptivas', 'Descriptivas.py', dict()),
    ('Likert', 'Likert.py', dict(hiddenimports=BOKEH_IMPORTS)),
    ('Tablas', 'Tablas.py', dict()),
    ('Comparar', 'Comparar.py', dict(hiddenimports=BOKEH_IMPORTS)),
    ('Fiabilidad', 'Fiabilidad.py', dict(
        hiddenimports=BOKEH_IMPORTS,
        binaries=collect_dynamic_libs('pyreadstat'),
    )),
    ('Regresion', 'Regresion.py', dict(
        datas=_regresion_datas,
        binaries=collect_dynamic_libs('pyreadstat'),
        runtime_hooks=[os.path.join(ROOT, 'rthook_bokeh_no_notebook.py')],
        excludes=['statsmodels.stats.diagnostic'],
    )),
    ('Muestra', 'Muestra.py', dict(
        hiddenimports=BOKEH_IMPORTS,
        binaries=collect_dynamic_libs('pyreadstat'),
    )),
    ('SimpleTest', 'SimpleTest.py', dict()),
]


def apply_pyarmor_patch(a):
    """Sustituye scripts y módulos locales del Analysis por su versión ofuscada."""
    if not USE_PYARMOR:
        return

    if hasattr(a.pure, '_code_cache'):
        code_cache = a.pure._code_cache
    else:
        from PyInstaller.config import CONF
        code_cache = CONF['code_cache'].get(id(a.pure))

    src = os.path.normcase(ROOT)

    def obfuscated(path):
        if path and os.path.normcase(path).startswith(src + os.sep):
            candidate = os.path.join(OBF, path[len(src) + 1:])
            if os.path.exists(candidate):
                return candidate
        return None

    count = 0
    for i, (name, path, typecode) in enumerate(a.scripts):
        x = obfuscated(path)
        if x:
            a.scripts[i] = (name, x, typecode)
            count += 1
    if count == 0:
        raise RuntimeError('No se encontró ningún script ofuscado para ' + a.scripts[-1][0])

    for i, (name, path, typecode) in enumerate(a.pure):
        x = obfuscated(path)
        if x:
            if code_cache is not None:
                code_cache.pop(name, None)
            a.pure[i] = (name, x, typecode)

    a.pure.append((RUNTIME_PKG, os.path.join(OBF, RUNTIME_PKG, '__init__.py'), 'PYMODULE'))
    ext = os.path.join(RUNTIME_PKG, 'pyarmor_runtime.so')
    a.binaries.append((ext, os.path.join(OBF, ext), 'EXTENSION'))


analyses = []
exes = []
for name, script, opts in TARGETS:
    a = Analysis(
        [os.path.join(ROOT, script)],
        pathex=[ROOT],
        binaries=opts.get('binaries', []),
        datas=opts.get('datas', []),
        hiddenimports=PYREADSTAT_IMPORTS + PKG_RESOURCES_IMPORTS + opts.get('hiddenimports', []),
        hookspath=[],
        hooksconfig={},
        runtime_hooks=COMMON_RTHOOKS + opts.get('runtime_hooks', []),
        excludes=opts.get('excludes', []),
        noarchive=False,
        optimize=0,
    )
    apply_pyarmor_patch(a)
    pyz = PYZ(a.pure)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
    )
    analyses.append(a)
    exes.append(exe)

coll = COLLECT(
    *exes,
    *[a.binaries for a in analyses],
    *[a.datas for a in analyses],
    strip=False,
    upx=False,
    name='IsA',
)
