import pandas as pd
import streamlit as st


def render_anomaly_metrics(anomalies: pd.DataFrame) -> None:
    spike_count = int((anomalies["Type"] == "Spike").sum())
    drop_count = int((anomalies["Type"] == "Drop").sum())

    total_column, spike_column, drop_column = st.columns(3)
    total_column.metric("Total anomalies", len(anomalies))
    spike_column.metric("Spikes", spike_count)
    drop_column.metric("Drops", drop_count)
