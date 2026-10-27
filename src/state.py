import streamlit as st

from src.anomaly_parameters import PARAMETER_WIDGET_KEYS


def init_all_anomalies_state() -> None:
    if "show_all_anomalies" not in st.session_state:
        st.session_state.show_all_anomalies = False
    if "all_anomalies_data" not in st.session_state:
        st.session_state.all_anomalies_data = None
    if "all_anomalies_parameters" not in st.session_state:
        st.session_state.all_anomalies_parameters = None


def reset_all_anomalies_state() -> None:
    st.session_state.show_all_anomalies = False
    st.session_state.all_anomalies_data = None
    st.session_state.all_anomalies_parameters = None


def reset_chart_state() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("chart_"):
            st.session_state.pop(key, None)


def clear_parameter_widgets() -> None:
    for key in PARAMETER_WIDGET_KEYS:
        st.session_state.pop(key, None)