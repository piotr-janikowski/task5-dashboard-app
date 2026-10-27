import pandas as pd

from src.anomaly_summary import generate_all_anomalies
from src.pdf_report import generate_pdf_report
from src.statistics import calculate_production_statistics


def test_pdf_report_is_generated_with_statistics_and_anomalies():
    df = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=12),
            "Mine A": [10, 11, 10, 12, 11, 10, 12, 11, 10, 12, 11, 40],
            "Mine B": [5, 6, 5, 6, 5, 6, 5, 6, 5, 6, 5, 2],
        }
    )
    statistics = calculate_production_statistics(df)
    anomalies = generate_all_anomalies(df, moving_average_window=3)

    pdf_bytes = generate_pdf_report(
        df=df,
        statistics=statistics,
        anomalies=anomalies,
        parameters={
            "iqr_multiplier": 1.5,
            "zscore_threshold": 3.0,
            "moving_average_window": 3,
            "moving_average_threshold_percent": 20.0,
            "grubbs_alpha": 0.05,
        },
        trendline_degree=1,
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000
