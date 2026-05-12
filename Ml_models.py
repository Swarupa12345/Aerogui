# ml_backend.py
# DO NOT EDIT — imported by app.py via function calling
# Functions: load_ml_models, run_ml_evaluation,
#            plot_pred_vs_actual, plot_residuals,
#            plot_feature_importance, plot_clcd_alpha,
#            draw_figure

import os
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# ── File paths — edit if your filenames differ ────────────────
CL_MODEL_PATH  = 'cl_xgb.model'
CD_MODEL_PATH  = 'cd_xgb.model'
XCP_MODEL_PATH = 'xcp_xgb.model'
SCALER_PATH    = 'feature_scaler.pkl'

# Must match your CSV column names exactly
FEATURES = [
    'nose length', 'body_length', 'wing LE', 'root chord', 'tip chord',
    'semi-span',   'root th',     'tip th',  'wing sweep', 'tail LE',
    'root chord.1','tip chord.1', 'semi-span.1','root th.1','tip th.1',
    'MACH', 'ALPHA', 'ALT',
]

# ── Canvas handle store ───────────────────────────────────────
_handles = {}


# =============================================================
# 1. LOAD MODELS
# =============================================================
def load_ml_models():
    """
    Called once at app startup.
    Returns (scaler, cl_model, cd_model, xcp_model).
    Raises FileNotFoundError with a clear message if any file missing.
    """
    for path in [SCALER_PATH, CL_MODEL_PATH, CD_MODEL_PATH, XCP_MODEL_PATH]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f'Required file not found: {path}\n'
                f'Make sure all .model and .pkl files are in the same folder as app.py'
            )

    scaler = joblib.load(SCALER_PATH)

    def _load(p):
        m = xgb.XGBRegressor()
        m.load_model(p)
        return m

    return scaler, _load(CL_MODEL_PATH), _load(CD_MODEL_PATH), _load(XCP_MODEL_PATH)


# =============================================================
# 2. RUN EVALUATION  (called when Select & Run is clicked)
# =============================================================
def run_ml_evaluation(csv_path, scaler, cl_model, cd_model, xcp_model):
    """
    Loads CSV → scales inputs → predicts → computes metrics.
    Returns dict with metrics_rows, df, feature_cols.
    """
    df = pd.read_csv(csv_path)
    df = df.apply(pd.to_numeric, errors='coerce')

    # check all feature columns exist
    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        raise ValueError(
            f'CSV is missing these columns:\n  {missing}\n\n'
            f'Columns found in CSV:\n  {list(df.columns)}'
        )

    feature_cols = [f for f in FEATURES if f in df.columns]
    X_scaled = scaler.transform(df[feature_cols].values)

    # predictions
    df['CL_pred']  = cl_model.predict(X_scaled)
    df['CD_pred']  = cd_model.predict(X_scaled)
    df['XCP_pred'] = xcp_model.predict(X_scaled)

    # metrics  (only if actual columns exist)
    metrics_rows = []
    for actual_col, pred_col, label in [
        ('CL',     'CL_pred',  'CL'),
        ('CD',     'CD_pred',  'CD'),
        ('X-C.P.', 'XCP_pred', 'XCP'),
    ]:
        if actual_col in df.columns:
            act  = df[actual_col].dropna()
            pred = df[pred_col].loc[act.index]
            mae  = mean_absolute_error(act, pred)
            rmse = np.sqrt(mean_squared_error(act, pred))
            r2   = r2_score(act, pred)
            pct  = (mae / max(abs(act).mean(), 1e-9)) * 100
            metrics_rows.append([
                label,
                f'{mae:.5f}',
                f'{rmse:.5f}',
                f'{r2:.5f}',
                f'{pct:.2f}%',
            ])

    return {
        'metrics_rows': metrics_rows,
        'df':           df,
        'feature_cols': feature_cols,
    }


# =============================================================
# 3. PLOTS — each returns a matplotlib Figure
# =============================================================

def plot_pred_vs_actual(df):
    """Scatter: Predicted vs Actual for CL and CD."""
    sns.set_style('whitegrid')
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    fig.suptitle('Predicted vs Actual', fontsize=13, fontweight='bold')

    for ax, (actual_col, pred_col, label, color) in zip(axes, [
        ('CL',     'CL_pred', 'CL', 'steelblue'),
        ('CD',     'CD_pred', 'CD', 'darkorange'),
    ]):
        if actual_col not in df.columns:
            ax.text(0.5, 0.5, f'No actual {actual_col} in CSV',
                    ha='center', va='center', transform=ax.transAxes)
            continue
        act  = df[actual_col].dropna().values
        pred = df[pred_col].loc[df[actual_col].dropna().index].values
        ax.scatter(act, pred, color=color, alpha=0.5,
                   edgecolors='k', linewidths=0.3, s=18)
        mn, mx = min(act.min(), pred.min()), max(act.max(), pred.max())
        ax.plot([mn, mx], [mn, mx], 'r--', lw=1.8, label='Perfect fit')
        ax.set_xlabel(f'Actual {label}',    fontsize=10)
        ax.set_ylabel(f'Predicted {label}', fontsize=10)
        ax.set_title(f'{label}: Predicted vs Actual', fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.4)
    fig.tight_layout()
    return fig


def plot_residuals(df):
    """Residual plot: Actual − Predicted vs Predicted."""
    sns.set_style('whitegrid')
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    fig.suptitle('Residual Plots', fontsize=13, fontweight='bold')

    for ax, (actual_col, pred_col, label) in zip(axes, [
        ('CL', 'CL_pred', 'CL'),
        ('CD', 'CD_pred', 'CD'),
    ]):
        if actual_col not in df.columns:
            ax.text(0.5, 0.5, f'No actual {actual_col} in CSV',
                    ha='center', va='center', transform=ax.transAxes)
            continue
        act  = df[actual_col].dropna().values
        pred = df[pred_col].loc[df[actual_col].dropna().index].values
        res  = act - pred
        ax.scatter(pred, res, color='darkorange', alpha=0.5,
                   edgecolors='k', linewidths=0.3, s=18)
        ax.axhline(0, color='red', linestyle='--', lw=1.8)
        ax.set_xlabel(f'Predicted {label}',          fontsize=10)
        ax.set_ylabel('Residual  (Actual − Pred)',    fontsize=10)
        ax.set_title(f'{label}  Residual Plot',       fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.4)
    fig.tight_layout()
    return fig


def plot_feature_importance(cl_model, cd_model, feature_cols):
    """Horizontal bar: top-10 feature importances for CL and CD models."""
    sns.set_style('whitegrid')
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Feature Importance  (XGBoost)', fontsize=13, fontweight='bold')

    for ax, (model, label) in zip(axes, [
        (cl_model, 'CL Model'),
        (cd_model, 'CD Model'),
    ]):
        imp = model.feature_importances_
        idx = np.argsort(imp)[::-1][:10]
        names = [feature_cols[i] for i in idx][::-1]
        vals  = imp[idx][::-1]
        ax.barh(names, vals, color='teal', edgecolor='black', linewidth=0.4)
        ax.set_title(f'{label}', fontweight='bold')
        ax.set_xlabel('Importance Score', fontsize=10)
        ax.grid(True, axis='x', linestyle='--', alpha=0.4)
    fig.tight_layout()
    return fig


def plot_clcd_alpha(df):
    """
    CL/CD vs Alpha — Actual (tab:blue/circle) vs Predicted (tab:pink/square).
    Exact style from cl_cd_alpha.py — one subplot per Mach×Alt combo.
    """
    sns.set_style('whitegrid')

    if 'ALPHA' not in df.columns:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.text(0.5, 0.5, 'No ALPHA column in CSV',
                ha='center', va='center', transform=ax.transAxes)
        return fig

    # compute ratios
    if 'CL' in df.columns and 'CD' in df.columns:
        df['CL_CD_actual'] = df['CL'] / df['CD']
    df['CL_CD_pred'] = df['CL_pred'] / df['CD_pred']

    # group by Mach×Alt (up to 4 subplots)
    combos = []
    if 'MACH' in df.columns and 'ALT' in df.columns:
        combos = (
            df.groupby(['MACH', 'ALT'])
              .size()
              .reset_index()[['MACH', 'ALT']]
              .values.tolist()
        )[:4]
    if not combos:
        combos = [None]

    n   = len(combos)
    fig, axes = plt.subplots(1, n, figsize=(9 * n, 5), squeeze=False)
    fig.suptitle('CL/CD vs Alpha — Actual vs Predicted',
                 fontsize=13, fontweight='bold')

    for i, combo in enumerate(combos):
        ax = axes[0][i]
        if combo is None:
            sub   = df.sort_values('ALPHA')
            title = 'All data'
        else:
            mach, alt = combo
            mask  = (
                np.isclose(df['MACH'], mach) &
                (df['ALT'] == alt)
            )
            sub   = df.loc[mask].sort_values('ALPHA')
            title = f'Mach={mach}, Alt={int(alt)} m'

        if sub.empty:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            continue

        if 'CL_CD_actual' in sub.columns:
            sns.lineplot(data=sub, x='ALPHA', y='CL_CD_actual',
                         label='Actual', color='tab:blue',
                         marker='o', linestyle='-',
                         errorbar=None, ax=ax)

        sns.lineplot(data=sub, x='ALPHA', y='CL_CD_pred',
                     label='Predicted', color='tab:pink',
                     marker='s', linestyle='-',
                     errorbar=None, ax=ax)

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('Incidence Angle α (°)', fontsize=10)
        ax.set_ylabel('CL/CD Ratio',           fontsize=10)
        ax.legend(title='Series', fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.4)

    fig.tight_layout()
    return fig


# =============================================================
# 4. DRAW FIGURE ONTO GUI CANVAS
# =============================================================
def draw_figure(canvas_elem, fig, key):
    """
    Renders a matplotlib figure onto a PySimpleGUI Canvas element.
    Replaces any previously drawn figure safely.
    """
    global _handles
    if key in _handles:
        try:
            _handles[key].get_tk_widget().destroy()
        except Exception:
            pass
    agg = FigureCanvasTkAgg(fig, canvas_elem.TKCanvas)
    agg.draw()
    agg.get_tk_widget().pack(fill='both', expand=True)
    _handles[key] = agg
    plt.close(fig)