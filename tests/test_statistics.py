
import pandas as pd
import pytest

from src.statistics import calculate_production_statistics


def test_statistics_include_mines_and_total_production_without_double_counting():
    df = pd.DataFrame(
        {
            "Date": pd.date_range("2025-01-01", periods=3),
            "Mine A": [10, 20, 30],
            "Mine B": [1, 2, 3],
        }
    )

    result = calculate_production_statistics(df)

    assert set(result.index) == {"Mine A", "Mine B", "Total Production"}
    assert result.loc["Total Production", "Mean"] == pytest.approx(22)
    assert result.loc["Total Production", "Median"] == pytest.approx(22)
    assert result.loc["Total Production", "IQR"] == pytest.approx(11)


def test_statistics_ignore_missing_values_but_preserve_available_days_count():
    df = pd.DataFrame(
        {
            "Date": pd.date_range("2025-01-01", periods=3),
            "Mine A": [10, None, 30],
        }
    )

    result = calculate_production_statistics(df)

    assert result.loc["Mine A", "Available Days"] == 2
    assert result.loc["Mine A", "Mean"] == pytest.approx(20)
    assert result.loc["Total Production", "Available Days"] == 2


def test_statistics_validate_required_columns():
    with pytest.raises(ValueError, match="Date"):
        calculate_production_statistics(pd.DataFrame({"Mine A": [1, 2]}))
    with pytest.raises(ValueError, match="production columns"):
        calculate_production_statistics(pd.DataFrame({"Date": pd.date_range("2025-01-01", periods=2)}))
