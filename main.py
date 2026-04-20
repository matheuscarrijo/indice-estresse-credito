from pathlib import Path

from src.build_index import (
    NORM_METHODS_EXPANDING,
    NORM_METHODS_ROLLING,
    ROLL_WINDOW,
    build_components,
    build_index,
)
from src.load_data import load_raw_series
from src.plot import plot_all

DATA_OUT = Path("outputs/data")


def main() -> None:
    Path("outputs/data").mkdir(parents=True, exist_ok=True)

    print("Carregando dados do BCB...")
    raw = load_raw_series()
    raw.to_csv(DATA_OUT / "series_raw.csv")

    print("Construindo componentes (C, I, Q)...")
    components = build_components(raw)
    components.to_csv(DATA_OUT / "components_raw.csv")
    start = components.index[0].strftime("%b-%Y")
    end   = components.index[-1].strftime("%b-%Y")
    print(f"  Período: {start} a {end} ({len(components)} observações)")

    print("Construindo índice — janela expansiva...")
    index_expanding = build_index(components, NORM_METHODS_EXPANDING)
    index_expanding.loc[index_expanding.index < "2014-01-01"] = float("nan")
    index_expanding.to_csv(DATA_OUT / "index_expanding.csv")

    print(f"Construindo índice — janela móvel {ROLL_WINDOW}m...")
    index_rolling = build_index(components, NORM_METHODS_ROLLING)
    index_rolling.to_csv(DATA_OUT / "index_rolling.csv")

    plot_all(components, index_expanding, index_rolling)
    _print_summary(index_expanding, index_rolling)


def _print_summary(index_expanding, index_rolling) -> None:
    labels = {
        "minmax":     "Min-Max",
        "percentile": "Rank Percentil",
    }
    windows = [
        ("Janela expansiva",             index_expanding),
        (f"Janela móvel ({ROLL_WINDOW}m)", index_rolling),
    ]
    for win_label, df in windows:
        last_date = df.dropna().index[-1].strftime("%b-%Y")
        print(f"\n{win_label} — último dado: {last_date}")
        print(f"  {'Método':<22} {'Atual':>8} {'Média':>8} {'Desvpad':>8} {'Mín':>8} {'Máx':>8}")
        print("  " + "-" * 62)
        for method, label in labels.items():
            s = df[f"index_{method}"].dropna()
            print(
                f"  {label:<22} {s.iloc[-1]:8.3f} {s.mean():8.3f}"
                f" {s.std():8.3f} {s.min():8.3f} {s.max():8.3f}"
            )
    print("\nOutputs salvos em:")
    print("  outputs/data/             — series_raw.csv, components_raw.csv,")
    print("                              index_expanding.csv, index_rolling.csv")
    print("  outputs/figures/general/  — 2 figuras (PNG)")
    print("  outputs/figures/expanding/ — 8 figuras (PNG)")
    print("  outputs/figures/rolling/   — 8 figuras (PNG)")


if __name__ == "__main__":
    main()
