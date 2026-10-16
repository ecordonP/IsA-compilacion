# rthook_bokeh_no_notebook.py
# Neutraliza cualquier intentona de usar el backend de cuaderno de Bokeh dentro de un ejecutable

import sys

def _noop(*args, **kwargs):
    return None

try:
    # 1) Parche directo en bokeh.io.output
    import bokeh.io.output as _bokeh_output
    _bokeh_output.output_notebook = _noop
except Exception:
    pass

try:
    # 2) Evitar que bokeh.io.notebook ejecute hooks de notebook/Jupyter
    import bokeh.io.notebook as _bokeh_nb
    _bokeh_nb.run_notebook_hook = _noop
    _bokeh_nb.load_notebook = _noop
    _bokeh_nb.publish_display_data = _noop  # por si lo alcanzan
except Exception:
    pass
