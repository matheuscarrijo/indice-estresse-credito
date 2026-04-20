from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

FIGURES_DIR = Path("outputs/figures")

KEY_EVENTS = {
    "Pandemia\nCOVID-19": pd.Timestamp("2020-03-01"),
    "Programa\nDesenrola": pd.Timestamp("2023-06-01"),
}

NORM_LABELS = {
    "minmax":     "Min-Max",
    "percentile": "Rank Percentil",
}

NORM_COLORS = {
    "minmax":     "#1f77b4",
    "percentile": "#2ca02c",
}

COMP_LABELS = {
    "C": "Comprometimento de Renda",
    "I": "Inadimplência (90+ dias)",
    "Q": "Qualidade do Crédito",
}

COMP_COLORS = {
    "C": "#1f77b4",
    "I": "#d62728",
    "Q": "#9467bd",
}

WINDOW_LABELS = {
    "expanding": "Janela Expansiva",
    "rolling":   "Janela Móvel 60m",
}


# ── helpers ──────────────────────────────────────────────────────────────────

def _style_ax(ax, ylabel: str = None, ylim: tuple = None) -> None:
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(True, axis="y", alpha=0.3, linestyle="--", linewidth=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    if ylim:
        ax.set_ylim(*ylim)


def _add_events(ax) -> None:
    for label, date in KEY_EVENTS.items():
        ax.axvline(date, color="grey", linestyle="--", linewidth=0.9, alpha=0.6)
        ax.text(
            date, 0.97, label,
            transform=ax.get_xaxis_transform(),
            fontsize=6.5, color="#555555",
            ha="center", va="top", linespacing=1.3,
        )


# ── figure builders ───────────────────────────────────────────────────────────

def _plot_index_comparison(index_df: pd.DataFrame, window_key: str) -> None:
    """One figure overlaying the two normalization methods for a given window type."""
    fig, ax = plt.subplots(figsize=(12, 5))

    for method, label in NORM_LABELS.items():
        ax.plot(
            index_df.index, index_df[f"index_{method}"],
            label=label, color=NORM_COLORS[method], linewidth=1.8,
        )

    _style_ax(ax, ylabel="Índice [0 – 1]", ylim=(0, 1.05))
    _add_events(ax)
    ax.legend(loc="lower left", framealpha=0.9, fontsize=9, edgecolor="#cccccc")
    ax.set_title(
        f"Índice de Desconforto de Crédito — {WINDOW_LABELS[window_key]}",
        fontsize=12, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    _save(fig, f"index_comparison.png", subdir=window_key)


def plot_components_raw(components: pd.DataFrame) -> None:
    """Figure — raw (unnormalized) components."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    configs = [
        ("C", components["C"],         "% da renda"),
        ("I", components["I"],         "%"),
        ("Q", components["Q"] * 100,   "%"),
    ]

    for ax, (comp, series, unit) in zip(axes, configs):
        ax.plot(series.index, series.values, color=COMP_COLORS[comp], linewidth=1.5)
        _style_ax(ax, ylabel=unit)
        _add_events(ax)
        ax.set_title(COMP_LABELS[comp], fontsize=10, fontweight="bold")

    fig.suptitle(
        "Componentes do Índice — Valores Brutos (não normalizados)",
        fontsize=12, fontweight="bold", y=1.01,
    )
    fig.tight_layout()
    _save(fig, "components_raw.png", subdir="general")


def _plot_components_normalized(
    index_df: pd.DataFrame, method: str, window_key: str
) -> None:
    """Three-panel figure with each normalized component for a given method and window."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)

    for ax, comp in zip(axes, ["C", "I", "Q"]):
        ax.plot(
            index_df.index, index_df[f"{comp}_{method}"],
            color=COMP_COLORS[comp], linewidth=1.5,
        )
        _style_ax(
            ax,
            ylabel="[0 – 1]" if comp == "C" else None,
            ylim=(-0.02, 1.05),
        )
        _add_events(ax)
        ax.set_title(COMP_LABELS[comp], fontsize=10, fontweight="bold")

    fig.suptitle(
        f"Componentes Normalizados — {NORM_LABELS[method]} — {WINDOW_LABELS[window_key]}",
        fontsize=12, fontweight="bold", y=1.01,
    )
    fig.tight_layout()
    _save(fig, f"components_{method}.png", subdir=window_key)


def _plot_index_single(
    index_df: pd.DataFrame, method: str, window_key: str
) -> None:
    """Single-method index figure for a given window type."""
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        index_df.index, index_df[f"index_{method}"],
        color=NORM_COLORS[method], linewidth=1.8,
    )

    _style_ax(ax, ylabel="Índice [0 – 1]", ylim=(0, 1.05))
    _add_events(ax)
    ax.set_title(
        f"Índice de Desconforto de Crédito — {NORM_LABELS[method]} — {WINDOW_LABELS[window_key]}",
        fontsize=12, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    _save(fig, f"index_{method}.png", subdir=window_key)


# ── base-100 figures ──────────────────────────────────────────────────────────

def _rebase100(s: pd.Series) -> pd.Series:
    """Rebase a series so that the first non-NaN value equals 100."""
    first_valid = s.dropna().iloc[0]
    return (s / first_valid) * 100


def plot_components_base100(components: pd.DataFrame) -> None:
    """Single-panel figure with C, I, Q rebased to 100 at the start of the sample."""
    fig, ax = plt.subplots(figsize=(12, 5))

    for comp in ["C", "I", "Q"]:
        rebased = _rebase100(components[comp])
        ax.plot(
            rebased.index, rebased.values,
            label=COMP_LABELS[comp], color=COMP_COLORS[comp], linewidth=1.5,
        )

    ax.axhline(100, color="grey", linestyle=":", linewidth=0.8, alpha=0.6)
    base_date = components.index[0].strftime("%b-%Y")
    _style_ax(ax, ylabel=f"Base 100 = {base_date}")
    _add_events(ax)
    ax.legend(loc="lower left", framealpha=0.9, fontsize=9, edgecolor="#cccccc")
    ax.set_title(
        f"Componentes do Índice — Evolução Base 100 ({base_date})",
        fontsize=12, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    _save(fig, "components_base100.png", subdir="general")


def _plot_index_comparison_base100(
    index_df: pd.DataFrame, window_key: str
) -> None:
    """Overlay both normalisation methods rebased to 100."""
    fig, ax = plt.subplots(figsize=(12, 5))

    for method, label in NORM_LABELS.items():
        rebased = _rebase100(index_df[f"index_{method}"])
        ax.plot(
            rebased.index, rebased.values,
            label=label, color=NORM_COLORS[method], linewidth=1.8,
        )

    ax.axhline(100, color="grey", linestyle=":", linewidth=0.8, alpha=0.6)
    base_date = index_df[f"index_minmax"].dropna().index[0].strftime("%b-%Y")
    _style_ax(ax, ylabel=f"Base 100 = {base_date}")
    _add_events(ax)
    ax.legend(loc="lower left", framealpha=0.9, fontsize=9, edgecolor="#cccccc")
    ax.set_title(
        f"Índice de Desconforto de Crédito — Base 100 — {WINDOW_LABELS[window_key]}",
        fontsize=12, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    _save(fig, "index_comparison_base100.png", subdir=window_key)


def _plot_index_single_base100(
    index_df: pd.DataFrame, method: str, window_key: str
) -> None:
    """Single-method index rebased to 100."""
    fig, ax = plt.subplots(figsize=(12, 5))

    rebased = _rebase100(index_df[f"index_{method}"])
    ax.plot(
        rebased.index, rebased.values,
        color=NORM_COLORS[method], linewidth=1.8,
    )

    ax.axhline(100, color="grey", linestyle=":", linewidth=0.8, alpha=0.6)
    base_date = index_df[f"index_{method}"].dropna().index[0].strftime("%b-%Y")
    _style_ax(ax, ylabel=f"Base 100 = {base_date}")
    _add_events(ax)
    ax.set_title(
        f"Índice de Desconforto de Crédito — {NORM_LABELS[method]} — Base 100 — {WINDOW_LABELS[window_key]}",
        fontsize=12, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    _save(fig, f"index_{method}_base100.png", subdir=window_key)


def _save(fig, filename: str, subdir: str = "") -> None:
    target_dir = FIGURES_DIR / subdir if subdir else FIGURES_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {subdir}/{filename}" if subdir else f"  {filename}")


# ── entry point ───────────────────────────────────────────────────────────────

def plot_all(
    components: pd.DataFrame,
    index_expanding: pd.DataFrame,
    index_rolling: pd.DataFrame,
) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans"})

    print("Salvando figuras em outputs/figures/:")

    # Componentes brutos → general/
    plot_components_raw(components)
    plot_components_base100(components)

    # Janela expansiva → expanding/
    _plot_index_comparison(index_expanding, "expanding")
    for method in ["minmax", "percentile"]:
        _plot_components_normalized(index_expanding, method, "expanding")
    for method in ["minmax", "percentile"]:
        _plot_index_single(index_expanding, method, "expanding")
    _plot_index_comparison_base100(index_expanding, "expanding")
    for method in ["minmax", "percentile"]:
        _plot_index_single_base100(index_expanding, method, "expanding")

    # Janela móvel 60m → rolling/
    _plot_index_comparison(index_rolling, "rolling")
    for method in ["minmax", "percentile"]:
        _plot_components_normalized(index_rolling, method, "rolling")
    for method in ["minmax", "percentile"]:
        _plot_index_single(index_rolling, method, "rolling")
    _plot_index_comparison_base100(index_rolling, "rolling")
    for method in ["minmax", "percentile"]:
        _plot_index_single_base100(index_rolling, method, "rolling")
