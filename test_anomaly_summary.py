from src.data_loader import load_production_data
from src.anomaly_summary import generate_all_anomalies


def main():
    print("Loading production data...")
    df = load_production_data()

    print(f"Loaded rows: {len(df)}")
    print(f"Loaded mines: {len(df.columns) - 1}")

    print("\nGenerating anomalies for all mines...")
    anomalies = generate_all_anomalies(df)

    print(f"\nTotal detected anomalies: {len(anomalies)}")

    if anomalies.empty:
        print("No anomalies detected.")
        return

    print("\nAnomalies by method:")
    print(anomalies["Method"].value_counts().to_string())

    print("\nAnomalies by type:")
    print(anomalies["Type"].value_counts().to_string())

    print("\nAnomalies by mine:")
    print(anomalies["Mine"].value_counts().to_string())

    print("\nFirst 20 anomalies:")
    print(anomalies.head(20).to_string(index=False))

    print("\nOutput columns:")
    print(anomalies.columns.tolist())


if __name__ == "__main__":
    main()