import pandas as pd


def calculate_production_statistics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate descriptive statistics for each mine and for total daily production.
        Input: A DataFrame with a 'Date' column and one numeric column for each mine.
        Returns: A DataFrame containing: observation count, mean, standard deviation, median, Q1, Q3, IQR, minimum, and maximum production.
    """
    if "Date" not in df.columns:
        raise ValueError("The DataFrame must contain a 'Date' column.")
    
    production_columns = [
        column for column in df.columns
        if column != "Date"
    ]
    if not production_columns:
        raise ValueError("No mine production columns were found.")

    production = df[production_columns].apply(pd.to_numeric, errors="coerce")
    production["Total Production"] = production.sum(axis=1,min_count=1)

    rows = []
    for column in production.columns:
        values = production[column].dropna()
        if values.empty:
            rows.append(
                {
                    "Mine": column,
                    "Available Days": 0,
                    "Mean": float("nan"),
                    "Standard Deviation": float("nan"),
                    "Median": float("nan"),
                    "Q1": float("nan"),
                    "Q3": float("nan"),
                    "IQR": float("nan"),
                    "Minimum": float("nan"),
                    "Maximum": float("nan"),
                }
            )
            continue
        
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        rows.append(
            {
                "Mine": column,
                "Available Days": len(values),
                "Mean": values.mean(),
                "Standard Deviation": values.std(),
                "Median": values.median(),
                "Q1": q1,
                "Q3": q3,
                "IQR": q3 - q1,
                "Minimum": values.min(),
                "Maximum": values.max(),
            }
        )

    return pd.DataFrame(rows).set_index("Mine")