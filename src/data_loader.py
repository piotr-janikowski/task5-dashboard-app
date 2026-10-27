import requests
import pandas as pd
import streamlit as st

SPREADSHEET_ID = "1FTkIlAqUrMlHkkESgFCqJqKZKmcNiBQCxD6FPZUhm_A"
SHEET_NAME = "Visualisation"

@st.cache_data(ttl=300)
def load_production_data() -> pd.DataFrame:
    """
    Download data from the public Google Sheet using the Google Sheets API.
    Returns DataFrame with one date column and one column for each mine.
    """
    api_key = st.secrets["GOOGLE_SHEETS_API_KEY"]

    url = ("https://sheets.googleapis.com/v4/spreadsheets/"f"{SPREADSHEET_ID}/values/{SHEET_NAME}")

    response = requests.get(url, params={"key": api_key}, timeout=30,)
    response.raise_for_status()

    values = response.json().get("values", [])

    if len(values) < 2:
        raise ValueError(f"The '{SHEET_NAME}' sheet does not contain enough data.")

    headers = values[0]
    rows = values[1:]

    rows = [
        row + [""] * (len(headers) - len(row))
        for row in rows
    ]

    df = pd.DataFrame(rows, columns=headers)

    if "Date" not in df.columns:
        raise ValueError("The 'Date' column was not found.")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for column in df.columns:
        if column != "Date":
            df[column] = pd.to_numeric(
                df[column]
                .astype("string")
                .str.replace(",", ".", regex=False)
                .str.strip(),errors="coerce",
                )

    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    return df