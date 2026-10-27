import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.anomaly_detection import (
    detect_iqr_anomalies,
    detect_zscore_anomalies,
    detect_moving_average_anomalies,
    detect_grubbs_anomaly,
)
from src.theme import (
    DROP_COLOR,
    SPIKE_COLOR,
    apply_chart_theme,
    card,
    section_header,
    series_color,
)


def render_production_chart(
    df: pd.DataFrame,
    production_columns: list[str],
) -> None:
    """Render an interactive production chart with collapsible settings panels."""

    section_header(
        "Production Chart & Trend Analysis",
        "Daily production per mine with trendlines and detected anomalies.",
    )

    if df.empty or not production_columns:
        st.info("No production data is available for the chart.")
        return

    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    for column in production_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["Date"]).sort_values("Date")
    if data.empty:
        st.info("No valid dates are available for the chart.")
        return
    data["In total"] = data[production_columns].sum(axis=1, min_count=1)

    if "chart_active_panel" not in st.session_state:
        st.session_state.chart_active_panel = "chart"
    if "chart_anomaly_source" not in st.session_state:
        st.session_state.chart_anomaly_source = "default"

    panel_col1, panel_col2, panel_col3 = st.columns(3)
    panels = [
        ("chart", "Chart settings"),
        ("filters", "Anomaly filters"),
        ("parameters", "Anomaly parameters"),
    ]
    for column, (panel_key, label) in zip(
        [panel_col1, panel_col2, panel_col3],
        panels,
    ):
        with column:
            active = st.session_state.chart_active_panel == panel_key

            if st.button(
                label,
                key=f"chart_panel_button_{panel_key}",
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                st.session_state.chart_active_panel = (
                    None if active else panel_key
                )
                st.rerun()

    st.session_state.setdefault("chart_iqr_multiplier", 1.5)
    st.session_state.setdefault("chart_zscore_threshold", 3.0)
    st.session_state.setdefault("chart_moving_average_window", min(7, max(1, len(data) - 1)))
    st.session_state.setdefault("chart_moving_average_threshold", 20.0)
    st.session_state.setdefault("chart_grubbs_alpha", 0.05)
    for parameter_key in [
        "chart_iqr_multiplier",
        "chart_zscore_threshold",
        "chart_moving_average_window",
        "chart_moving_average_threshold",
        "chart_grubbs_alpha",
    ]:
        st.session_state[parameter_key] = st.session_state[parameter_key]
    st.session_state.chart_moving_average_window = min(
        int(st.session_state.chart_moving_average_window),
        max(1, len(data) - 1),
    )

    default_parameters = {
        "iqr_multiplier": st.session_state.chart_iqr_multiplier,
        "zscore_threshold": st.session_state.chart_zscore_threshold,
        "moving_average_window": int(st.session_state.chart_moving_average_window),
        "moving_average_threshold_percent": st.session_state.chart_moving_average_threshold,
        "grubbs_alpha": st.session_state.chart_grubbs_alpha,
    }

    mine_options = production_columns + ["In total"]
    default_mines = mine_options
    default_methods = ["IQR", "Z-score", "Moving Average", "Grubbs"]
    default_types = ["Spike", "Drop"]

    st.session_state.setdefault("chart_selected_mines", default_mines)
    st.session_state.setdefault("chart_date_range", (
        data["Date"].min().date(),
        data["Date"].max().date(),
    ))
    st.session_state.setdefault("chart_type", "Line chart")
    st.session_state.setdefault("chart_trendline_degree", 1)
    st.session_state.setdefault("chart_show_trendline", True)
    st.session_state.setdefault("chart_show_production", True)
    st.session_state.setdefault("chart_show_anomalies", True)
    st.session_state.setdefault("chart_selected_methods", default_methods)
    st.session_state.setdefault("chart_selected_types", default_types)

    available_start = data["Date"].min().date()
    available_end = data["Date"].max().date()
    saved_range = st.session_state.chart_date_range
    if isinstance(saved_range, (tuple, list)) and any(
        not available_start <= day <= available_end for day in saved_range
    ):
        st.session_state.chart_date_range = (available_start, available_end)

    saved_mines = st.session_state.chart_selected_mines
    valid_mines = [mine for mine in saved_mines if mine in mine_options]
    st.session_state.chart_selected_mines = (
        valid_mines if valid_mines or not saved_mines else default_mines
    )

    for setting_key in [
        "chart_selected_mines",
        "chart_date_range",
        "chart_type",
        "chart_trendline_degree",
        "chart_show_trendline",
        "chart_show_production",
        "chart_show_anomalies",
        "chart_selected_methods",
        "chart_selected_types",
    ]:
        st.session_state[setting_key] = st.session_state[setting_key]

    if st.session_state.chart_active_panel == "chart":
        with card("chart-settings"):
            section_header("Chart settings", "Configure what data to display in the chart.")

            st.multiselect(
                "Select mines and total production",
                options=mine_options,
                key="chart_selected_mines",
            )
            date_min = data["Date"].min().date()
            date_max = data["Date"].max().date()
            date_column, type_column, degree_column = st.columns(3)
            with date_column:
                st.date_input(
                    "Date range",
                    value=(
                        st.session_state.chart_date_range
                        if isinstance(st.session_state.chart_date_range, (tuple, list))
                        else (date_min, date_max)
                    ),
                    min_value=date_min,
                    max_value=date_max,
                    key="chart_date_range",
                )
            with type_column:
                st.selectbox(
                    "Chart type",
                    options=["Line chart", "Bar chart", "Stacked bar chart"],
                    key="chart_type",
                )
            with degree_column:
                st.selectbox(
                    "Trendline polynomial degree",
                    options=[1, 2, 3, 4],
                    key="chart_trendline_degree",
                    help="Higher degrees can follow short-term changes more closely and may overfit the data.",
                )
            trendline_column, production_column, anomalies_column = st.columns(3)
            with trendline_column:
                st.toggle("Show trendline", key="chart_show_trendline")
            with production_column:
                st.toggle("Show production data", key="chart_show_production")
            with anomalies_column:
                st.toggle("Show anomalies", key="chart_show_anomalies")

    if st.session_state.chart_active_panel == "filters":
        with card("chart-filters"):
            section_header("Anomaly filters", "Choose which detection methods and anomaly types appear on the chart.")
            methods_column, types_column = st.columns(2)
            with methods_column:
                st.multiselect("Detection methods", options=default_methods, key="chart_selected_methods")
            with types_column:
                st.multiselect("Anomaly types", options=default_types, key="chart_selected_types")

    if st.session_state.chart_active_panel == "parameters":
        with card("chart-parameters"):
            section_header("Anomaly parameters", "Select the source of anomaly results shown on the chart.")
            apply_col, reset_col = st.columns(2)
            with apply_col:
                if st.button(
                    "Add parameters from Anomaly Summary",
                    key="chart_apply_summary_parameters",
                    use_container_width=True,
                ):
                    summary_results = st.session_state.get("all_anomalies_data")
                    if (st.session_state.get("show_all_anomalies", False) and summary_results is not None):
                        st.session_state.chart_anomaly_source = "summary"
                        st.rerun()
                    else:
                        st.warning("Create the Anomaly Summary table first to use its anomaly results.")

            with reset_col:
                if st.button("Reset parameters", key="chart_reset_parameters", use_container_width=True):
                    st.session_state.chart_anomaly_source = "default"
                    st.session_state.chart_iqr_multiplier = 1.5
                    st.session_state.chart_zscore_threshold = 3.0
                    st.session_state.chart_moving_average_window = min(7, max(1, len(data) - 1))
                    st.session_state.chart_moving_average_threshold = 20.0
                    st.session_state.chart_grubbs_alpha = 0.05
                    st.rerun()

            if st.session_state.chart_anomaly_source == "summary":
                st.caption("Using the anomaly results currently stored in Anomaly Summary.")
            else:
                st.caption("Using the detection parameters set below.")

            summary_source = st.session_state.chart_anomaly_source == "summary"
            left_column, right_column = st.columns(2)
            with left_column:
                st.number_input("IQR multiplier", min_value=0.0, step=0.1, key="chart_iqr_multiplier", disabled=summary_source)
                st.number_input("Z-score threshold", min_value=0.1, step=0.1, key="chart_zscore_threshold", disabled=summary_source)
                st.number_input("Moving average window (days)", min_value=1, max_value=max(1, len(data) - 1), step=1, key="chart_moving_average_window", disabled=summary_source)
            with right_column:
                st.number_input("Moving average deviation threshold (%)", min_value=0.0, step=5.0, key="chart_moving_average_threshold", disabled=summary_source)
                st.number_input("Grubbs significance level (alpha)", min_value=0.001, max_value=0.999, step=0.01, format="%.3f", key="chart_grubbs_alpha", disabled=summary_source)


    selected_mines = st.session_state.chart_selected_mines
    selected_methods = st.session_state.chart_selected_methods
    selected_types = st.session_state.chart_selected_types
    date_range = st.session_state.chart_date_range
    chart_type = st.session_state.chart_type
    show_production = st.session_state.chart_show_production
    show_anomalies = st.session_state.chart_show_anomalies
    show_trendline = st.session_state.chart_show_trendline
    trendline_degree = int(st.session_state.chart_trendline_degree)

    if not selected_mines:
        st.info("Select at least one mine or total production series.")
        return
    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        st.info("Select both a start date and an end date.")
        return

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    if start_date > end_date:
        st.warning("The start date must not be after the end date.")
        return

    chart_data = data[
(data["Date"] >= start_date) & (data["Date"] <= end_date)
    ].copy()

    if chart_data.empty:
        st.info("No production data is available for the selected date range.")
        return

    if st.session_state.chart_anomaly_source == "summary":
        summary_results = st.session_state.get("all_anomalies_data")
        if summary_results is None:
            all_anomalies = pd.DataFrame(
                columns=["Date", "Value", "Method", "Type", "Mine"]
            )
        else:
            all_anomalies = summary_results.copy()
            all_anomalies["Mine"] = all_anomalies["Mine"].replace(
                {"Total Production": "In total"}
            )
    else:
        anomaly_frames = []
        for mine in selected_mines:
            series = data.set_index("Date")[mine].dropna().sort_index()
            if series.empty:
                continue

            detectors = {
                "IQR": lambda: detect_iqr_anomalies(
                    series, multiplier=default_parameters["iqr_multiplier"]
                ),
                "Z-score": lambda: detect_zscore_anomalies(
                    series, threshold=default_parameters["zscore_threshold"]
                ),
                "Moving Average": lambda: detect_moving_average_anomalies(
                    series,
                    window=default_parameters["moving_average_window"],
                    threshold_percent=default_parameters[
                        "moving_average_threshold_percent"
                    ],
                ),
                "Grubbs": lambda: detect_grubbs_anomaly(
                    series, alpha=default_parameters["grubbs_alpha"]
                ),
            }

            for method_name in selected_methods:
                result = detectors[method_name]()
                if result.empty:
                    continue
                result = result.copy()
                result["Mine"] = mine
                anomaly_frames.append(result)

        if anomaly_frames:
            all_anomalies = pd.concat(
                anomaly_frames, ignore_index=True, sort=False
            )
        else:
            all_anomalies = pd.DataFrame(
                columns=["Date", "Value", "Method", "Type", "Mine"]
            )

    if not all_anomalies.empty:
        all_anomalies["Date"] = pd.to_datetime(
            all_anomalies["Date"], errors="coerce"
        )
        all_anomalies = all_anomalies[
            all_anomalies["Date"].between(start_date, end_date)
            & all_anomalies["Mine"].isin(selected_mines)
            & all_anomalies["Method"].isin(selected_methods)
            & all_anomalies["Type"].isin(selected_types)
        ].copy()


    fig = go.Figure()

    if chart_type == "Stacked bar chart":
        for mine in selected_mines:
            if mine == "In total":
                continue
            if show_production:
                fig.add_trace(
                    go.Bar(
                        x=chart_data["Date"],
                        y=chart_data[mine],
                        name=mine,
                        marker_color=series_color(mine, mine_options),
                    )
                )
        fig.update_layout(barmode="stack")
    else:
        for mine in selected_mines:
            if show_production:
                if chart_type == "Line chart":
                    fig.add_trace(
                        go.Scatter(
                            x=chart_data["Date"],
                            y=chart_data[mine],
                            mode="lines+markers",
                            name=mine,
                            line={
                                "color": series_color(mine, mine_options),
                                "width": 3 if mine == "In total" else 2,
                            },
                            marker={"size": 5},
                        )
                    )
                else:
                    fig.add_trace(
                        go.Bar(
                            x=chart_data["Date"],
                            y=chart_data[mine],
                            name=mine,
                            marker_color=series_color(mine, mine_options),
                        )
                    )

    if show_trendline and chart_type != "Stacked bar chart":
        for mine in selected_mines:
            if mine == "In total":
                trend_values = chart_data[production_columns].sum(axis=1, min_count=1)
            else:
                trend_values = pd.to_numeric(chart_data[mine], errors="coerce")

            valid = trend_values.notna()
            x_values = np.arange(len(chart_data), dtype=float)
            x_valid = x_values[valid.to_numpy()]
            y_valid = trend_values.loc[valid].to_numpy(dtype=float)

            if len(y_valid) <= trendline_degree:
                continue

            x_center = x_valid.mean()
            x_scale = max(float(np.ptp(x_valid)), 1.0)
            x_scaled = (x_valid - x_center) / x_scale
            coefficients = np.polyfit(x_scaled, y_valid, trendline_degree)
            trend_y = np.polyval(coefficients, (x_values - x_center) / x_scale)

            fig.add_trace(
                go.Scatter(
                    x=chart_data["Date"],
                    y=trend_y,
                    mode="lines",
                    name=f"{mine} — Trendline (degree {trendline_degree})",
                    line={
                        "dash": "dash",
                        "width": 1.5,
                        "color": series_color(mine, mine_options),
                    },
                )
            )

    if show_anomalies and not all_anomalies.empty:
        for (mine, method_name, anomaly_type), group in all_anomalies.groupby(
            ["Mine", "Method", "Type"]
        ):
            fig.add_trace(
                go.Scatter(
                    x=group["Date"],
                    y=group["Value"],
                    mode="markers",
                    name=f"{mine} — {method_name} — {anomaly_type}",
                    marker={
                        "symbol": "x" if anomaly_type == "Drop" else "diamond",
                        "size": 11,
                        "color": DROP_COLOR if anomaly_type == "Drop" else SPIKE_COLOR,
                        "line": (
                            {"width": 2, "color": DROP_COLOR}
                            if anomaly_type == "Drop"
                            else {"width": 1, "color": "#FFFFFF"}
                        ),
                    },
                    customdata=np.column_stack([group["Method"], group["Type"]]),
                    hovertemplate=(
                        "Date: %{x|%Y-%m-%d}<br>"
                        "Production: %{y:.2f}<br>"
                        "Method: %{customdata[0]}<br>"
                        "Type: %{customdata[1]}<extra></extra>"
                    ),
                )
            )

    title_mines = ", ".join(selected_mines)
    fig.update_layout(
        title=f"Daily Production and Anomalies — {title_mines}",
        xaxis_title="Date",
        yaxis_title="Production",
        hovermode="x unified",
        legend_title="Production series / anomalies",
        template="plotly_white",
        height=650,
    )
    apply_chart_theme(fig)

    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

    st.caption(
        "Anomalies are shown using the selected anomaly source. "
        "The date filter controls which observations are displayed."
    )

    if chart_type == "Stacked bar chart" and show_trendline:
        st.info("Trendlines are disabled for stacked bar charts. Select a line or regular bar chart to display a trendline.")

    if chart_type == "Stacked bar chart" and "In total" in selected_mines:
        st.info(
            "Total Production is not added as a separate stacked series, "
            "because it already includes the production of all mines."
        )