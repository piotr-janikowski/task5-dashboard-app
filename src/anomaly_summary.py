import pandas as pd

from src.anomaly_detection import (
    detect_iqr_anomalies,
    detect_zscore_anomalies,
    detect_moving_average_anomalies,
    detect_grubbs_anomaly,
)


def generate_all_anomalies(
    df: pd.DataFrame,
    iqr_multiplier: float = 1.5,
    zscore_threshold: float = 3.0,
    moving_average_window: int = 7,
    moving_average_threshold_percent: float = 20.0,
    grubbs_alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Detect anomalies for every mine and total production.
    Each detection method is applied independently to every production series. Results are combined into one table.
    """

    if "Date" not in df.columns:
        raise ValueError("Input data must contain a 'Date' column.")

    production_columns = [
        column for column in df.columns
        if column != "Date"
    ]
    if not production_columns:
        raise ValueError("Input data must contain production columns.")

    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"]).sort_values("Date")

    for column in production_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["Total Production"] = data[production_columns].sum(axis=1, min_count=1)

    series_columns = production_columns + ["Total Production"]
    all_results = []


    for column in series_columns:
        series = (data.set_index("Date")[column].dropna().sort_index())

        if series.empty:
            continue
        method_results = [
            detect_iqr_anomalies(series, multiplier=iqr_multiplier),
            detect_zscore_anomalies(series, threshold=zscore_threshold),
            detect_moving_average_anomalies(series, window=moving_average_window, threshold_percent=moving_average_threshold_percent),
            detect_grubbs_anomaly(series, alpha=grubbs_alpha),
        ]

        for result in method_results:
            if result.empty:
                continue
            result = result.copy()
            result.insert(1, "Mine", column)
            all_results.append(result)

    if not all_results:
        return pd.DataFrame(columns=["Date", "Mine", "Value", "Method", "Type"])
    anomalies = pd.concat(all_results, ignore_index=True, sort=False)

    return anomalies.sort_values(["Date", "Mine", "Method"], kind="stable").reset_index(drop=True)