import pandas as pd

from src.anomaly_summary import generate_all_anomalies

PARAMETER_WIDGET_KEYS = [
    "all_iqr_multiplier",
    "all_zscore_threshold",
    "all_moving_average_window",
    "all_moving_average_threshold",
    "all_grubbs_alpha",
]


def max_moving_average_window(record_count: int) -> int:
    return max(1, record_count - 1)


def default_moving_average_window(record_count: int) -> int:
    return min(7, max_moving_average_window(record_count))


def default_anomaly_parameters(record_count: int) -> dict:
    return {
        "iqr_multiplier": 1.5,
        "zscore_threshold": 3.0,
        "moving_average_window": default_moving_average_window(record_count),
        "moving_average_threshold_percent": 20.0,
        "grubbs_alpha": 0.05,
    }


def calculate_all_anomalies(df: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    return generate_all_anomalies(df, **parameters)
