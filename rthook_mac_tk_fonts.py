# -*- coding: utf-8 -*-
"""
Runtime hook de PyInstaller (solo macOS): tamaño de letra igual que en Windows.

Los módulos de IsA calculan una escala según la pantalla y la aplican con
`tk scaling`; las letras se indican en puntos. En Windows y Linux Tk convierte los
puntos a píxeles multiplicando por `tk scaling`, así que la letra crece con la
escala. En macOS, en cambio, Tk pasa los puntos directamente a Cocoa (1 punto =
1 píxel lógico) e ignora `tk scaling`: la geometría (root.dp) se escalaba pero la
letra no, y en pantallas grandes (iMac 27") todo se veía pequeño.

Este hook reproduce en macOS el cálculo de Windows sin tocar el código de los
módulos (que llegan ofuscados):
  - Al crear Tk, fija `tk scaling` = 96/72, como Windows a 100 % (96 ppp), para
    que la escala calculada con winfo_fpixels('1i') sea la misma.
  - Cada tamaño de letra positivo (en puntos) se multiplica por el `tk scaling`
    vigente al usarlo; los negativos (en píxeles) se pasan a positivos, porque en
    macOS 1 punto = 1 píxel lógico. Las fuentes con nombre (TkDefaultFont...) no
    se tocan: ya tienen el tamaño estándar de macOS.
"""
import sys

if sys.platform == "darwin":
    import tkinter
    import tkinter.font as _tkfont
    from tkinter import ttk as _ttk

    _WINDOWS_SCALING = 96.0 / 72.0

    def _current_scaling(widget=None):
        try:
            w = widget if widget is not None else tkinter._default_root
            return float(w.tk.call("tk", "scaling")) if w is not None else _WINDOWS_SCALING
        except Exception:
            return _WINDOWS_SCALING

    def _scale_size(size, k):
        try:
            n = float(size)
        except (TypeError, ValueError):
            return size
        if n < 0:
            return int(round(-n))
        if n == 0:
            return size
        return max(1, int(round(n * k)))

    def _scale_font(value, k, tk_obj=None):
        """Devuelve la descripción de fuente con el tamaño ajustado (si lo tiene)."""
        if isinstance(value, _tkfont.Font) or value is None or value == "":
            return value
        if isinstance(value, (tuple, list)):
            items = list(value)
        elif isinstance(value, str):
            try:
                items = list((tk_obj or tkinter._default_root.tk).splitlist(value))
            except Exception:
                return value
        else:
            return value
        if len(items) >= 2 and str(items[0]).startswith("-"):
            # Forma «-family X -size N ...»
            for i in range(0, len(items) - 1, 2):
                if items[i] == "-size":
                    items[i + 1] = _scale_size(items[i + 1], k)
            return tuple(items)
        if len(items) >= 2:
            new_size = _scale_size(items[1], k)
            if new_size is items[1]:
                return value
            items[1] = new_size
            return tuple(items)
        return value   # fuente con nombre o solo la familia

    # --- Tk: tk scaling inicial como Windows a 100 % --------------------------------
    _orig_tk_init = tkinter.Tk.__init__

    def _tk_init(self, *args, **kwargs):
        _orig_tk_init(self, *args, **kwargs)
        try:
            self.tk.call("tk", "scaling", _WINDOWS_SCALING)
        except Exception:
            pass

    tkinter.Tk.__init__ = _tk_init

    # --- Opciones de widgets (creación, configure, tag_configure, create_text...) ---
    _orig_options = tkinter.Misc._options

    def _options(self, cnf, kw=None):
        def fix(d):
            if d and isinstance(d, dict) and "font" in d:
                d = dict(d)
                d["font"] = _scale_font(d["font"], _current_scaling(self), self.tk)
            return d
        return _orig_options(self, fix(cnf), fix(kw))

    tkinter.Misc._options = _options

    # --- Base de datos de opciones: root.option_add("*Font", "{Segoe UI} 16") -------
    _orig_option_add = tkinter.Misc.option_add

    def _option_add(self, pattern, value, priority=None):
        if str(pattern).lower().endswith("font"):
            value = _scale_font(value, _current_scaling(self), self.tk)
            if isinstance(value, tuple):
                value = tkinter._join(value) if hasattr(tkinter, "_join") else " ".join(
                    "{%s}" % v if " " in str(v) else str(v) for v in value)
        return _orig_option_add(self, pattern, value, priority)

    tkinter.Misc.option_add = _option_add

    # --- Estilos ttk: style.configure("TButton", font=("Segoe UI", 14)) -------------
    _orig_style_configure = _ttk.Style.configure

    def _style_configure(self, style, query_opt=None, **kw):
        if "font" in kw:
            kw["font"] = _scale_font(kw["font"], _current_scaling(self.master), self.tk)
        return _orig_style_configure(self, style, query_opt, **kw)

    _ttk.Style.configure = _style_configure

    # --- tkinter.font.Font(size=12) y Font.configure(size=12) -----------------------
    _orig_font_init = _tkfont.Font.__init__

    def _font_init(self, root=None, font=None, name=None, exists=False, **options):
        k = _current_scaling(root)
        if "size" in options:
            options["size"] = _scale_size(options["size"], k)
        if font is not None:
            font = _scale_font(font, k)
        _orig_font_init(self, root, font, name, exists, **options)

    _tkfont.Font.__init__ = _font_init

    _orig_font_configure = _tkfont.Font.configure

    def _font_configure(self, **options):
        if "size" in options:
            options["size"] = _scale_size(options["size"], _current_scaling())
        return _orig_font_configure(self, **options)

    _tkfont.Font.configure = _font_configure
    _tkfont.Font.config = _font_configure
