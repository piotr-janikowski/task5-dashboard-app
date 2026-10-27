from src.data_loader import load_production_data

df = load_production_data()

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- FIRST 15 ROWS ---")
print(df.head(15).to_string(index=False))

print("\n--- NON-EMPTY VALUES PER MINE ---")
for column in df.columns:
    if column != "Date":
        print(f"{column}: {df[column].notna().sum()}")

print("\n--- ROWS WITH AT LEAST ONE PRODUCTION VALUE ---")
production_columns = [column for column in df.columns if column != "Date"]

print(
    df[production_columns]
    .notna()
    .any(axis=1)
    .sum()
)

print("\n--- MISSING VALUES BY DATE ---")
print(
    df.loc[
        df[production_columns].isna().all(axis=1),
        ["Date"],
    ].to_string(index=False)
)