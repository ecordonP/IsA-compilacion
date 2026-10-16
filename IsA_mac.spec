# -*- mode: python ; coding: utf-8 -*-
#
# Spec de macOS: un único IsA.app con el menú y los 10 módulos.
# Apple Silicon (arm64, por defecto) o Intel (ISA_TARGET_ARCH=x86_64).
#
# En Windows cada módulo es un .exe que comparte la carpeta _internal. En macOS eso no
# es posible entre .app separados, así que todos los ejecutables van en
# IsA.app/Contents/MacOS y comparten Contents/Frameworks. Menu.py lanza los módulos
# desde la carpeta de su propio ejecutable.
#
# Ofuscación: los scripts se ofuscan en Windows con `python obfuscate_mac.py`
# (pyarmor --platform darwin.arm64) en obf_mac/, y este spec sustituye en cada
# Analysis el código fuente por el ofuscado (equivale al parche que genera
# `pyarmor gen --pack`, que solo admite un Analysis).
#
# Variables de entorno opcionales:
#     ISA_TARGET_ARCH         arm64 (Apple Silicon, por defecto) o x86_64 (Intel)
#     ISA_OBF_DIR             carpeta con los scripts ofuscados (por defecto obf_mac
#                             o, en Intel, obf_mac_intel)
#     ISA_REQUIRE_PYARMOR=1   falla si no hay scripts ofuscados (lo usa la CI)
#     ISA_CODESIGN_IDENTITY   identidad "Developer ID Application: ..." para firmar
import os

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, copy_metadata

ROOT = SPECPATH
TARGET_ARCH = os.environ.get('ISA_TARGET_ARCH', 'arm64')
OBF = os.environ.get('ISA_OBF_DIR', os.path.join(ROOT, 'obf_mac' if TARGET_ARCH == 'arm64' else 'obf_mac_intel'))
RUNTIME_PKG = 'pyarmor_runtime_011681'
USE_PYARMOR = os.path.isdir(os.path.join(OBF, RUNTIME_PKG))
if os.environ.get('ISA_REQUIRE_PYARMOR') == '1' and not USE_PYARMOR:
    raise SystemExit(f'No se encuentran los scripts ofuscados en {OBF}')

CODESIGN_IDENTITY = os.environ.get('ISA_CODESIGN_IDENTITY') or None
ENTITLEMENTS = os.path.join(ROOT, 'entitlements.plist') if CODESIGN_IDENTITY else None
ICON = os.path.join(ROOT, 'IsA.ico')  # PyInstaller lo convierte a .icns con Pillow

PYREADSTAT_IMPORTS = [
    'pyreadstat._readstat_writer',
    'pyreadstat._readstat_parser',
    'pyreadstat.worker',
]
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
# rthook_mac_tk_fonts: en macOS Tk no aplica `tk scaling` a la letra; el hook la escala
# como en Windows (en pantallas grandes, como un iMac de 27", todo se veía pequeño).
COMMON_RTHOOKS = [os.path.join(ROOT, 'rthook_block_foreign_packages.py'),
                  os.path.join(ROOT, 'rthook_mac_tk_fonts.py')]

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
        datas=[(os.path.join(ROOT, f), '.') for f in ('LogoOE2.png', 'logoIsA.png', 'licencia.md')],
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
        hiddenimports=PYREADSTAT_IMPORTS + opts.get('hiddenimports', []),
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
        argv_emulation=False,
        target_arch=TARGET_ARCH,
        codesign_identity=CODESIGN_IDENTITY,
        entitlements_file=ENTITLEMENTS,
        icon=ICON,
    )
    analyses.append(a)
    exes.append(exe)

# El primer EXECUTABLE (Menu) es el CFBundleExecutable del .app
coll = COLLECT(
    *exes,
    *[a.binaries for a in analyses],
    *[a.datas for a in analyses],
    strip=False,
    upx=False,
    name='IsA',
)

app = BUNDLE(
    coll,
    name='IsA.app',
    icon=ICON,
    bundle_identifier='es.ugr.isa',
    version='1.5',
    codesign_identity=CODESIGN_IDENTITY,
    entitlements_file=ENTITLEMENTS,
    info_plist={
        'CFBundleName': 'IsA',
        'CFBundleDisplayName': 'IsA - Intelligent Statistical Assistant',
        'CFBundleShortVersionString': '1.5',
        'LSMinimumSystemVersion': '12.0',
        'NSHighResolutionCapable': True,
        # La interfaz usa fondos blancos fijos: forzar modo claro
        'NSRequiresAquaSystemAppearance': True,
    },
)
