import streamlit as st

from src.detection_tab import render_detection_tab
from src.overview import (
    add_total_column,
    configure_page,
    get_production_columns,
    load_data_or_stop,
    render_overview,
    render_refresh_bar,
)
from src.production_chart import render_production_chart
from src.report_section import render_report_section
from src.statistics_tab import render_statistics_tab
from src.summary_tab import render_summary_tab

configure_page()

df = load_data_or_stop()
render_refresh_bar()

production_columns = get_production_columns(df)
add_total_column(df, production_columns)
mines_df = df[["Date"] + production_columns]

render_overview(df, production_columns)
render_production_chart(df=df, production_columns=production_columns)

statistics_tab, detection_tab, summary_tab = st.tabs([
    "Production Statistics",
    "Anomaly Detection",
    "Anomaly Summary",
])

with statistics_tab:
    render_statistics_tab(mines_df)

with detection_tab:
    render_detection_tab(df, production_columns)

with summary_tab:
    render_summary_tab(mines_df)

render_report_section(mines_df)
