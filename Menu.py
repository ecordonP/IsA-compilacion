# ISA_STUB: solo importaciones de Menu.py. Generado por publicar_compilacion.py.
# PyInstaller necesita ver qué librerías usa el programa; el programa real está
# ofuscado en obf_mac/, obf_mac_intel/ y obf_linux/.
if __name__ == "__isa_stub__":
    from PIL import Image, ImageTk
    from datetime import date
    from dateutil.relativedelta import relativedelta
    from licencia import CONFIG_ENV_VAR, LAUNCH_FLAG, CONTACT_MESSAGE, LicenciaError, check_machine, get_base_dir, machine_code, normalize_machine_code, record_last_run, verify_license_document, config_path, is_app_allowed, read_config, validate_dates
    from tkinter import messagebox, filedialog, ttk
    from ui_adapt import set_dpi_awareness, fit_image_size, apply_tk_scaling as _base_apply_tk_scaling
    import ctypes
    import json
    import os
    import re
    import shutil
    import subprocess
    import sys
    import tempfile
    import tkinter as tk
