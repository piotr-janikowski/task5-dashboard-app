import pandas as pd
import streamlit as st

from src.anomaly_detection import (
    detect_iqr_anomalies,
    detect_zscore_anomalies,
    detect_moving_average_anomalies,
    detect_grubbs_anomaly,
)
from src.anomaly_parameters import (
    default_moving_average_window,
    max_moving_average_window,
)
from src.components import render_anomaly_metrics
from src.theme import section_header

DETECTORS = {
    "IQR": detect_iqr_anomalies,
    "Z-score": detect_zscore_anomalies,
    "Moving Average": detect_moving_average_anomalies,
    "Grubbs' test": detect_grubbs_anomaly,
}


def render_method_parameters(method: str, record_count: int) -> dict:
    if method == "IQR":
        multiplier = st.number_input("IQR multiplier", min_value=0.0, value=1.5, step=0.1)
        return {"multiplier": multiplier}
    if method == "Z-score":
        threshold = st.number_input("Z-score threshold", min_value=0.1, value=3.0, step=0.1)
        return {"threshold": threshold}
    if method == "Moving Average":
        window = st.number_input(
            "Moving average window (days)",
            min_value=1,
            max_value=max_moving_average_window(record_count),
            value=default_moving_average_window(record_count),
            step=1,
        )
        threshold_percent = st.number_input("Deviation threshold (%)", min_value=0.0, value=20.0, step=5.0)
        return {"window": int(window), "threshold_percent": threshold_percent}
    alpha = st.number_input(
        "Significance level (alpha)",
        min_value=0.001,
        max_value=0.999,
        value=0.05,
        step=0.01,
        format="%.3f",
    )
    return {"alpha": alpha}


def render_detection_tab(df: pd.DataFrame, production_columns: list) -> None:
    section_header("Anomaly Detection", "Select a series and a detection method, then adjust its parameters.")

    series_column, method_column = st.columns(2)
    with series_column:
        selected_series_name = st.selectbox("Select a mine or total production", production_columns + ["In total"])
    with method_column:
        method = st.selectbox("Detection method", list(DETECTORS))
    parameters = render_method_parameters(method, len(df))

    series = df.set_index("Date")[selected_series_name].dropna().sort_index()
    try:
        anomalies = DETECTORS[method](series, **parameters)
    except ValueError as error:
        st.error(f"Could not detect anomalies: {error}")
        st.stop()

    section_header("Detected Anomalies")
    if anomalies.empty:
        st.info("No anomalies detected with the selected method and parameters.")
        return

    render_anomaly_metrics(anomalies)
    st.dataframe(anomalies, use_container_width=True, hide_index=True)