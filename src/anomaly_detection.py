import numpy as np
import pandas as pd
from scipy.stats import t


def detect_iqr_anomalies(series: pd.Series, multiplier: float = 1.5) -> pd.DataFrame:
    """
    Detect anomalies using the Interquartile Range (IQR) rule.
    Values below Q1 - multiplier * IQR are drops.
    Values above Q3 + multiplier * IQR are spikes.
    """

    if multiplier < 0:
        raise ValueError("IQR multiplier must be non-negative.")

    values = pd.to_numeric(series, errors="coerce")
    valid = values.dropna()
    if valid.empty:
        return _empty_results()
    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    mask = (values < lower_bound) | (values > upper_bound)

    types = pd.Series(
        np.where(values > upper_bound, "Spike", "Drop"),
        index=values.index,
    )

    return _build_results(
        values=values,
        mask=mask,
        method="IQR",
        types=types,
        lower_bound=lower_bound,    #type: ignore
        upper_bound=upper_bound,    #type: ignore
    )


def detect_zscore_anomalies(series: pd.Series,threshold: float = 3.0) -> pd.DataFrame:
    """
    Detect anomalies using the absolute z-score.
    A value is anomalous when its absolute z-score exceeds the specified threshold.
    """
    if threshold <= 0:
        raise ValueError("Z-score threshold must be greater than zero.")
    values = pd.to_numeric(series, errors="coerce")
    valid = values.dropna()
    if len(valid) < 2:
        return _empty_results()
    mean = valid.mean()
    std = valid.std(ddof=1)
    if std == 0 or not np.isfinite(std):
        return _empty_results()

    z_scores = (values - mean) / std
    mask = z_scores.abs() > threshold
    types = pd.Series(
        np.where(z_scores > threshold, "Spike", "Drop"),
        index=values.index,
    )
    results = _build_results(
        values=values,
        mask=mask,
        method="Z-score",
        types=types,
    )
    if not results.empty:
        results["Score"] = (
        z_scores.loc[results["Date"]].abs().to_numpy()
    )

    return results


def detect_moving_average_anomalies(series: pd.Series, window: int = 7, threshold_percent: float = 20.0) -> pd.DataFrame:
    """
    Detect anomalies based on percentage deviation from a trailing moving average.
    The current observation is excluded from its reference moving average to avoid influencing its own baseline.
    """

    if not isinstance(window, int) or window < 1:
        raise ValueError("Moving average window must be a positive integer.")
    if threshold_percent < 0:
        raise ValueError("Percentage threshold must be non-negative.")

    values = pd.to_numeric(series, errors="coerce")
    moving_average = values.shift(1).rolling(
        window=window,
        min_periods=window,
    ).mean()

    denominator = moving_average.abs().replace(0, np.nan)
    deviation_percent = ((values - moving_average) / denominator) * 100
    mask = deviation_percent.abs().gt(threshold_percent).fillna(False)
    types = pd.Series(
        np.where(
            deviation_percent.fillna(0) > threshold_percent,
            "Spike",
            "Drop",
        ),
        index=values.index,
    )

    results = _build_results(
        values=values,
        mask=mask,
        method="Moving Average",
        types=types,
    )
    if not results.empty:
        result_dates = results["Date"]
        results["Reference Value"] = (moving_average.loc[result_dates].to_numpy())
        results["Deviation (%)"] = (deviation_percent.loc[result_dates].to_numpy())

    return results


def detect_grubbs_anomaly(series: pd.Series, alpha: float = 0.05) -> pd.DataFrame:
    """
    Apply the two-sided Grubbs' test to detect at most one anomaly in a sample.
    The test assumes approximately normally distributed data.
    """

    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")
    values = pd.to_numeric(series, errors="coerce")
    valid = values.dropna()
    n = len(valid)
    if n < 3:
        return _empty_results()
    mean = valid.mean()
    std = valid.std(ddof=1)
    if std == 0 or not np.isfinite(std):
        return _empty_results()
    deviations = (valid - mean).abs()
    candidate_index = deviations.idxmax()
    candidate_value = valid.loc[candidate_index]                # type: ignore
    grubbs_statistic = deviations.loc[candidate_index] / std    # type: ignore
    t_critical = t.ppf(1 - alpha / (2 * n), df=n - 2,)
    critical_value = (
        (n - 1) / np.sqrt(n)
        * np.sqrt(t_critical**2 / (n - 2 + t_critical**2))
    )

    if grubbs_statistic <= critical_value:
        return _empty_results()
    mask = pd.Series(
        values.index == candidate_index,
        index=values.index,
    )
    types = pd.Series(
        np.where(values > mean, "Spike", "Drop"),
        index=values.index,
    )
    results = _build_results(
        values=values,
        mask=mask,
        method="Grubbs",
        types=types,
    )
    if not results.empty:
        results["Score"] = grubbs_statistic
        results["Alpha"] = alpha
        results["Critical Value"] = critical_value

    return results


def detect_all_anomalies(
    series: pd.Series,
    iqr_multiplier: float = 1.5,
    zscore_threshold: float = 3.0,
    moving_average_window: int = 7,
    moving_average_threshold_percent: float = 20.0,
    grubbs_alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Run all four anomaly detection methods and combine their results.
    The same observation can appear more than once if multiple methods detect it.
    """

    results = [
        detect_iqr_anomalies(series, iqr_multiplier),
        detect_zscore_anomalies(series, zscore_threshold),
        detect_moving_average_anomalies(series, moving_average_window, moving_average_threshold_percent),
        detect_grubbs_anomaly(series, grubbs_alpha),
    ]

    non_empty = [result for result in results if not result.empty]

    if not non_empty:
        return _empty_results()

    return (
        pd.concat(non_empty, ignore_index=True)
        .sort_values(["Date", "Method"], kind="stable")
        .reset_index(drop=True)
    )


def _build_results(
    values: pd.Series,
    mask: pd.Series,
    method: str,
    types: pd.Series,
    lower_bound: float | None = None,
    upper_bound: float | None = None,
) -> pd.DataFrame:
    """Build a consistent anomaly result table."""

    mask = mask.reindex(values.index, fill_value=False).fillna(False).astype(bool)
    mask &= values.notna()

    indices = values.index[mask]

    if len(indices) == 0:
        return _empty_results()

    result = pd.DataFrame(
        {
            "Date": indices,
            "Value": values.loc[indices].to_numpy(),
            "Method": method,
            "Type": types.loc[indices].to_numpy(),
        }
    )

    if lower_bound is not None:
        result["Lower Bound"] = lower_bound
    if upper_bound is not None:
        result["Upper Bound"] = upper_bound

    return result


def _empty_results() -> pd.DataFrame:
    """Return an empty anomaly table with standard columns."""
    return pd.DataFrame(columns=["Date", "Value", "Method", "Type"])