import pandas as pd
import pytest

from src.data_loader import load_production_data
from src.statistics import calculate_production_statistics


@pytest.fixture(scope="module")
def production_data():
    return load_production_data()


def test_data_is_loaded(production_data):
    assert isinstance(production_data, pd.DataFrame)
    assert not production_data.empty


def test_date_column_is_valid(production_data):
    assert "Date" in production_data.columns
    assert pd.api.types.is_datetime64_any_dtype(production_data["Date"])
    assert production_data["Date"].notna().all()
    assert production_data["Date"].is_monotonic_increasing


def test_production_columns_are_numeric(production_data):
    production_columns = [
        column for column in production_data.columns
        if column != "Date"
    ]
    assert production_columns, "No mine production columns were found."
    for column in production_columns:
        assert pd.api.types.is_numeric_dtype(production_data[column]), (f"Column {column!r} is not numeric.")


def test_production_values_are_non_negative(production_data):
    production_columns = [
        column for column in production_data.columns
        if column != "Date"
    ]
    for column in production_columns:
        valid_values = production_data[column].dropna()
        assert (valid_values >= 0).all(), (f"Negative production values found in {column!r}.")


def test_statistics_cover_all_mines_and_total(production_data):
    statistics = calculate_production_statistics(production_data)
    production_columns = [
        column for column in production_data.columns
        if column != "Date"
    ]
    expected_rows = set(production_columns)
    expected_rows.add("Total Production")
    assert expected_rows.issubset(set(statistics.index))


def test_statistics_have_required_metrics(production_data):
    statistics = calculate_production_statistics(production_data)
    required_columns = {
        "Mean",
        "Standard Deviation",
        "Median",
        "Q1",
        "Q3",
        "IQR",
    }
    assert required_columns.issubset(set(statistics.columns))