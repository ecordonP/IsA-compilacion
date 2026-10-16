# ISA_STUB: solo importaciones de Regresion.py. Generado por publicar_compilacion.py.
# PyInstaller necesita ver qué librerías usa el programa; el programa real está
# ofuscado en obf_mac/, obf_mac_intel/ y obf_linux/.
if __name__ == "__isa_stub__":
    from collections import defaultdict
    from dataclasses import dataclass, field
    from importlib.metadata import version as _pytz_version
    from licencia import check_module_license
    from math import comb
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
    from scipy.optimize import brentq as _brentq
    from scipy.stats import f as _f
    from scipy.stats import f as _f_chow
    from scipy.stats import ncf as _ncf
    from scipy.stats import ncx2 as _ncx2, chi2 as _chi2
    from scipy.stats import shapiro, f as f_dist
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression
    from sklearn.metrics import roc_curve, auc, confusion_matrix, classification_report, cohen_kappa_score, mean_squared_error, mean_absolute_error, r2_score, brier_score_loss, log_loss
    from sklearn.model_selection import KFold, StratifiedKFold
    from sklearn.preprocessing import StandardScaler
    from statsmodels.compat import lzip
    from statsmodels.imputation.mice import MICEData
    from statsmodels.stats.diagnostic import het_breuschpagan, het_white, linear_reset
    from statsmodels.stats.multitest import multipletests
    from statsmodels.stats.outliers_influence import variance_inflation_factor, OLSInfluence
    from statsmodels.stats.stattools import jarque_bera
    from statsmodels.tools.sm_exceptions import PerfectSeparationError
    from tkinter import ttk, filedialog, messagebox, Toplevel
    from tkinter.constants import DISABLED, NORMAL
    from tkinter.scrolledtext import ScrolledText
    from ui_adapt import set_dpi_awareness, apply_tk_scaling as _base_apply_tk_scaling
    import base64
    import io
    import itertools as it
    import json
    import logging
    import math as _math
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import pandas as pd
    import pyreadstat
    import pytz as _pytz
    import seaborn as sns
    import statsmodels.api as _sm_api
    import statsmodels.api as sm
    import statsmodels.stats.diagnostic as diag
    import sys
    import tempfile
    import threading
    import tkinter as tk
    import traceback
    import warnings
