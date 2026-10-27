from typing import Callable

import pandas as pd
import streamlit as st

from src.statistics import calculate_production_statistics
from src.theme import section_header

STATISTICS_FORMAT: dict[str, str | Callable[[object], str] | None] = {
    "Mean": "{:.2f}",
    "Standard Deviation": "{:.2f}",
    "Median": "{:.2f}",
    "Q1": "{:.2f}",
    "Q3": "{:.2f}",
    "IQR": "{:.2f}",
    "Minimum": "{:.2f}",
    "Maximum": "{:.2f}",
}


def highlight_total_row(row: pd.Series) -> list:
    style = "background-color: #EAF1FF; font-weight: 600" if row.name == "Total Production" else ""
    return [style] * len(row)


def render_statistics_tab(mines_df: pd.DataFrame) -> None:
    section_header("Production Statistics", "Statistical summary for each mine and total production.")
    statistics = calculate_production_statistics(mines_df)
    st.dataframe(
        statistics.style.format(STATISTICS_FORMAT, na_rep="-").apply(highlight_total_row, axis=1),
        use_container_width=True,
    )