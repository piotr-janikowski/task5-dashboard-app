import pandas as pd
import streamlit as st

from src.anomaly_parameters import calculate_all_anomalies, default_anomaly_parameters
from src.pdf_report import generate_pdf_report
from src.statistics import calculate_production_statistics
from src.theme import card, section_header


def render_report_section(mines_df: pd.DataFrame) -> None:
    with card("export"):
        text_column, button_column = st.columns([4, 1], vertical_alignment="center")
        with text_column:
            section_header(
                "Export analysis",
                "Generate a report containing production statistics, charts with anomaly markers, "
                "individual anomaly details, and the parameters used for detection.",
            )
        with button_column:
            generate_report = st.button("Generate PDF report", type="primary", use_container_width=True)

    if not generate_report:
        return

    report_parameters = st.session_state.get("all_anomalies_parameters")
    report_anomalies = st.session_state.get("all_anomalies_data")

    if report_parameters is None:
        report_parameters = default_anomaly_parameters(len(mines_df))

    if report_anomalies is None:
        with st.spinner("Detecting anomalies and preparing the report..."):
            report_anomalies = calculate_all_anomalies(mines_df, report_parameters)

    try:
        with st.spinner("Creating PDF report..."):
            pdf_bytes = generate_pdf_report(
                df=mines_df,
                statistics=calculate_production_statistics(mines_df),
                anomalies=report_anomalies,
                parameters=report_parameters,
                trendline_degree=int(st.session_state.get("chart_trendline_degree", 1)),
            )
        st.download_button(
            label="Download Mine Production Analytics Report.pdf",
            data=pdf_bytes,
            file_name="mine_production_analytics_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.success("The PDF report is ready to download.")
    except Exception as error:
        st.error(f"Could not generate the PDF report: {error}")