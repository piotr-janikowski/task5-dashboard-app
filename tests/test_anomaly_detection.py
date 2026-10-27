import pandas as pd
import pytest

from src.anomaly_detection import (
    detect_iqr_anomalies,
    detect_zscore_anomalies,
    detect_moving_average_anomalies,
    detect_grubbs_anomaly,
    detect_all_anomalies,
)

REQUIRED_COLUMNS = {"Date", "Value", "Method", "Type"}
VALID_METHODS = {"IQR", "Z-score", "Moving Average", "Grubbs"}


@pytest.fixture(scope="module")
def series():
    dates = pd.date_range("2099-01-01", periods=20, freq="D")
    production = [
        100, 102, 98, 101, 99,
        103, 97, 100, 102, 98,
        101, 99, 103, 97, 100,
        500, 102, 101, 20, 99,
    ]
    return pd.Series(production, index=dates, name="Test Mine")


@pytest.fixture(scope="module")
def iqr_results(series):
    return detect_iqr_anomalies(series)


@pytest.fixture(scope="module")
def zscore_results(series):
    return detect_zscore_anomalies(series)


@pytest.fixture(scope="module")
def moving_average_results(series):
    return detect_moving_average_anomalies(series, window=5, threshold_percent=20)


@pytest.fixture(scope="module")
def grubbs_results(series):
    return detect_grubbs_anomaly(series)


@pytest.fixture(scope="module")
def all_results(series):
    return detect_all_anomalies(
        series,
        iqr_multiplier=1.5,
        zscore_threshold=2.0,
        moving_average_window=5,
        moving_average_threshold_percent=20,
        grubbs_alpha=0.05,
    )


def validate_result(name, result, series, expected_method=None):
    assert isinstance(result, pd.DataFrame), f"{name}: result is not a DataFrame."

    if result.empty:
        return

    assert REQUIRED_COLUMNS.issubset(result.columns), (
        f"{name}: missing columns {REQUIRED_COLUMNS - set(result.columns)}."
    )
    assert result["Date"].isin(series.index).all(), f"{name}: invalid dates."
    assert result["Value"].notna().all(), f"{name}: Value contains NaN."
    assert result["Method"].isin(VALID_METHODS).all(), f"{name}: unknown method name."
    assert result["Type"].isin(["Spike", "Drop"]).all(), f"{name}: invalid Type."

    if expected_method is not None:
        assert (result["Method"] == expected_method).all(), (f"{name}: unexpected method in results.")


def test_iqr(iqr_results, series):
    validate_result("IQR", iqr_results, series, expected_method="IQR")
    assert not iqr_results.empty, "IQR did not detect any anomalies."
    assert set(iqr_results["Type"]) == {"Spike", "Drop"}, ("IQR did not correctly identify both spikes and drops.")


def test_zscore(zscore_results, series):
    validate_result("Z-score", zscore_results, series, expected_method="Z-score")
    assert not zscore_results.empty, "Z-score did not detect any anomalies."


def test_moving_average(moving_average_results, series):
    validate_result("Moving Average", moving_average_results, series, expected_method="Moving Average")
    assert not moving_average_results.empty, ("Moving Average did not detect any anomalies.")
    assert set(moving_average_results["Type"]) == {"Spike", "Drop"}, ("Moving Average did not correctly identify both spikes and drops.")


def test_grubbs(grubbs_results, series):
    validate_result("Grubbs", grubbs_results, series, expected_method="Grubbs")
    assert not grubbs_results.empty, "Grubbs did not detect any anomalies."
    assert len(grubbs_results) == 1, "Grubbs should detect at most one anomaly."
    assert grubbs_results.iloc[0]["Type"] == "Spike", "Grubbs should flag 500 as a spike."


def test_all_methods_combined(all_results, series):
    validate_result("All methods combined", all_results, series)
    assert set(all_results["Method"]) == VALID_METHODS, (f"Not all methods detected anomalies: {set(all_results['Method'])}")

def test_empty_or_non_numeric_series_returns_standard_empty_result():
    series = pd.Series([None, "not-a-number", float("nan")])

    result = detect_iqr_anomalies(series)

    assert result.empty
    assert list(result.columns) == ["Date", "Value", "Method", "Type"]


def test_constant_series_does_not_create_zscore_or_grubbs_anomalies():
    series = pd.Series([10, 10, 10, 10], index=pd.date_range("2025-01-01", periods=4))

    assert detect_zscore_anomalies(series).empty
    assert detect_grubbs_anomaly(series).empty


def test_moving_average_does_not_flag_values_when_reference_average_is_zero():
    series = pd.Series(
        [0, 0, 0, 100],
        index=pd.date_range("2025-01-01", periods=4),
    )

    result = detect_moving_average_anomalies(
        series,
        window=3,
        threshold_percent=20,
    )

    # Percentage deviation from a zero baseline is undefined, not infinite.
    assert result.empty


def test_detection_methods_reject_invalid_parameters():
    series = pd.Series([1, 2, 3, 4])

    with pytest.raises(ValueError):
        detect_iqr_anomalies(series, multiplier=-0.1)
    with pytest.raises(ValueError):
        detect_zscore_anomalies(series, threshold=0)
    with pytest.raises(ValueError):
        detect_moving_average_anomalies(series, window=0)
    with pytest.raises(ValueError):
        detect_moving_average_anomalies(series, threshold_percent=-1)
    with pytest.raises(ValueError):
        detect_grubbs_anomaly(series, alpha=1)
