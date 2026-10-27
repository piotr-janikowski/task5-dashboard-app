import pandas as pd
import streamlit as st

from src.data_loader import load_production_data
from src.state import reset_all_anomalies_state, reset_chart_state
from src.theme import (
    ICON_END,
    ICON_MINES,
    ICON_RECORDS,
    ICON_START,
    inject_theme,
    render_kpi_cards,
    render_page_header,
    render_source_pill,
)


def configure_page() -> None:
    st.set_page_config(
        page_title="Mine Production Analytics",
        page_icon="⛏️",
        layout="wide",
    )
    inject_theme()
    render_page_header("Mine Production Analytics", "Daily production monitoring and anomaly detection")


def load_data_or_stop() -> pd.DataFrame:
    try:
        return load_production_data()
    except Exception as error:
        st.error(f"Could not load production data: {error}")
        st.stop()


def render_refresh_bar() -> None:
    caption_column, button_column = st.columns([5, 1], vertical_alignment="center")
    with caption_column:
        render_source_pill("Data source: Google Sheets")
    with button_column:
        if st.button("Refresh data", use_container_width=True):
            reset_all_anomalies_state()
            reset_chart_state()
            st.cache_data.clear()
            st.rerun()


def get_production_columns(df: pd.DataFrame) -> list:
    return [column for column in df.columns if column != "Date"]


def add_total_column(df: pd.DataFrame, production_columns: list) -> None:
    df["In total"] = df[production_columns].sum(axis=1, min_count=1)


def render_overview(df: pd.DataFrame, production_columns: list) -> None:
    start_date = df["Date"].min().strftime("%Y-%m-%d")
    end_date = df["Date"].max().strftime("%Y-%m-%d")

    render_kpi_cards([
        (ICON_RECORDS, "Daily records", len(df)),
        (ICON_MINES, "Number of mines", len(production_columns)),
        (ICON_START, "Start date", start_date),
        (ICON_END, "End date", end_date),
    ])

    with st.expander("Daily Production Data"):
        df_display = df[["Date", "In total"] + production_columns]
        st.dataframe(df_display, use_container_width=True, hide_index=True)