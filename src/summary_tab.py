import pandas as pd
import streamlit as st

from src.anomaly_parameters import (
    calculate_all_anomalies,
    default_anomaly_parameters,
    default_moving_average_window,
    max_moving_average_window,
)
from src.components import render_anomaly_metrics
from src.theme import section_header
from src.state import (
    clear_parameter_widgets,
    init_all_anomalies_state,
    reset_all_anomalies_state,
)


def get_all_anomalies_parameters() -> dict:
    return {
        "iqr_multiplier": st.session_state.all_iqr_multiplier,
        "zscore_threshold": st.session_state.all_zscore_threshold,
        "moving_average_window": int(st.session_state.all_moving_average_window),
        "moving_average_threshold_percent": st.session_state.all_moving_average_threshold,
        "grubbs_alpha": st.session_state.all_grubbs_alpha,
    }


def render_parameter_inputs(record_count: int) -> None:
    section_header(
        "Detection Parameters",
        "Adjust any parameter and click Recalculate anomalies to run the analysis again. These settings do not affect the individual mine analysis above.",
    )

    left_column, right_column = st.columns(2)
    with left_column:
        st.number_input("IQR multiplier", min_value=0.0, value=1.5, step=0.1, key="all_iqr_multiplier")
        st.number_input("Z-score threshold", min_value=0.1, value=3.0, step=0.1, key="all_zscore_threshold")
        st.number_input("Moving average window (days)", min_value=1, max_value=max_moving_average_window(record_count), value=default_moving_average_window(record_count), step=1, key="all_moving_average_window")
    with right_column:
        st.number_input("Moving average deviation threshold (%)", min_value=0.0, value=20.0, step=5.0, key="all_moving_average_threshold")
        st.number_input("Grubbs significance level (alpha)", min_value=0.001, max_value=0.999, value=0.05, step=0.01, format="%.3f", key="all_grubbs_alpha")


def render_action_buttons(mines_df: pd.DataFrame) -> None:
    recalculate_column, delete_column = st.columns(2)
    with recalculate_column:
        if st.button("Recalculate anomalies", use_container_width=True):
            parameters = get_all_anomalies_parameters()
            with st.spinner("Recalculating anomalies..."):
                try:
                    st.session_state.all_anomalies_data = calculate_all_anomalies(mines_df, parameters)
                    st.session_state.all_anomalies_parameters = parameters
                except (ValueError, TypeError) as error:
                    st.error(f"Could not recalculate anomalies: {error}")
    with delete_column:
        if st.button("Delete anomalies table", use_container_width=True):
            reset_all_anomalies_state()
            clear_parameter_widgets()
            st.rerun()


def render_filtered_anomalies(all_anomalies: pd.DataFrame) -> None:
    render_anomaly_metrics(all_anomalies)

    mine_column, method_column, type_column = st.columns(3)
    with mine_column:
        mine_options = sorted(all_anomalies["Mine"].unique().tolist())
        selected_mines = st.multiselect("Filter by mine", options=mine_options, default=mine_options, key="all_anomalies_mine_filter")
    with method_column:
        method_options = sorted(all_anomalies["Method"].unique().tolist())
        selected_methods = st.multiselect("Filter by method", options=method_options, default=method_options, key="all_anomalies_method_filter")
    with type_column:
        selected_types = st.multiselect("Filter by anomaly type", options=["Spike", "Drop"], default=["Spike", "Drop"], key="all_anomalies_type_filter")

    filtered_anomalies = all_anomalies[
        all_anomalies["Mine"].isin(selected_mines)
        & all_anomalies["Method"].isin(selected_methods)
        & all_anomalies["Type"].isin(selected_types)
    ].copy()

    st.caption(f"Showing {len(filtered_anomalies)} of {len(all_anomalies)} detected anomalies.")
    st.dataframe(filtered_anomalies, use_container_width=True, hide_index=True)


def render_summary_tab(mines_df: pd.DataFrame) -> None:
    section_header("All Mines - Anomaly Summary", "Run every detection method on every mine and review the results in one table.")
    init_all_anomalies_state()

    if st.button("Create all anomalies table", use_container_width=True):
        default_parameters = default_anomaly_parameters(len(mines_df))
        with st.spinner("Analysing all mines and detection methods..."):
            try:
                st.session_state.all_anomalies_data = calculate_all_anomalies(mines_df, default_parameters)
                st.session_state.all_anomalies_parameters = default_parameters
                st.session_state.show_all_anomalies = True
            except (ValueError, TypeError) as error:
                st.error(f"Could not generate anomalies table: {error}")

    if st.session_state.show_all_anomalies:
        render_parameter_inputs(len(mines_df))
        render_action_buttons(mines_df)

        all_anomalies = st.session_state.all_anomalies_data
        section_header("All Detected Anomalies")
        if all_anomalies is None or all_anomalies.empty:
            st.info("No anomalies were detected with the current parameters. Try adjusting the detection thresholds and recalculating.")
        else:
            render_filtered_anomalies(all_anomalies)

        if st.session_state.all_anomalies_parameters is not None:
            with st.expander("Parameters used for these results"):
                st.json(st.session_state.all_anomalies_parameters)