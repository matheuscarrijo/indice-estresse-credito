import pandas as pd


# ── Expanding window (no lookahead) ──────────────────────────────────────────

def expanding_minmax(series: pd.Series) -> pd.Series:
    """Min-max normalization using expanding window — no lookahead.

    At each t, anchors are min/max of series[0:t+1]. Returns NaN where
    min == max (all values identical; 0/0 is indeterminate). Clip guards
    against floating-point rounding slightly outside [0, 1].
    """
    mn = series.expanding().min()
    mx = series.expanding().max()
    return ((series - mn) / (mx - mn)).clip(0.0, 1.0)



def expanding_percentile_rank(series: pd.Series) -> pd.Series:
    """Empirical CDF evaluated at each point using expanding window — no lookahead.

    Returns the fraction of observations in [0, t] that are <= series[t].
    Minimum value is 1/n (current always counts against itself).
    """
    return series.expanding().apply(lambda x: (x <= x[-1]).mean(), raw=True)


# ── Rolling window (no lookahead) ─────────────────────────────────────────────

def rolling_minmax(series: pd.Series, window: int = 60) -> pd.Series:
    """Min-max normalization using rolling window of `window` months — no lookahead."""
    mn = series.rolling(window, min_periods=window).min()
    mx = series.rolling(window, min_periods=window).max()
    return ((series - mn) / (mx - mn)).clip(0.0, 1.0)



def rolling_percentile_rank(series: pd.Series, window: int = 60) -> pd.Series:
    """Empirical CDF evaluated at each point using rolling window — no lookahead.

    Returns the fraction of observations in [t-window+1, t] that are <= series[t].
    """
    return series.rolling(window, min_periods=window).apply(
        lambda x: (x <= x[-1]).mean(), raw=True
    )
