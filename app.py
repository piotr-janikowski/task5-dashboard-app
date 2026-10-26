import streamlit as st
from src.data_loader import load_production_data
from src.statistics import calculate_production_statistics


st.set_page_config(
    page_title="Mine Production Analytics",
    page_icon="⛏️",
    layout="wide",
)

st.title("⛏️ Mine Production Analytics")
st.caption("Daily production monitoring and anomaly detection")

try:
    df = load_production_data()
except Exception as error:
    st.error(f"Could not load production data: {error}")
    st.stop()

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()
with col2:
    st.caption("Data source: Google Sheets")

production_columns = [column for column in df.columns if column != "Date"]
total_records = len(df)
mine_count = len(production_columns)
start_date = df["Date"].min().strftime("%Y-%m-%d")
end_date = df["Date"].max().strftime("%Y-%m-%d")

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Daily records", total_records)
metric2.metric("Number of mines", mine_count)
metric3.metric("Start date", start_date)
metric4.metric("End date", end_date)

st.divider()
st.subheader("Daily Production Data")
production_columns = [
    column for column in df.columns
    if column != "Date"
]
df_display = df.copy()
df_display.insert(1, "In total", df_display[production_columns].sum(axis=1, min_count=1))
st.dataframe(df_display, use_container_width=True, hide_index=True)


st.subheader("Production Statistics")
statistics = calculate_production_statistics(df)
st.dataframe(statistics.style.format(
    {
        "Mean": "{:.2f}",
        "Standard Deviation": "{:.2f}",
        "Median": "{:.2f}",
        "Q1": "{:.2f}",
        "Q3": "{:.2f}",
        "IQR": "{:.2f}",
        "Minimum": "{:.2f}",
        "Maximum": "{:.2f}",
    },
    na_rep="-"
    ), 
    use_container_width=True,
)