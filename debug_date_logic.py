import pandas as pd
from datetime import datetime, timedelta


def process_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the 'Date' column in a DataFrame, handling initial date strings
    and subsequent formula strings like '=A2+1'.
    """
    if "Date" not in df.columns:
        raise ValueError("DataFrame must contain a 'Date' column.")

    processed_dates = []
    previous_date = None

    for index, row in df.iterrows():
        date_value = str(row["Date"]).strip()

        if index == 0:
            # First row contains the initial date string
            try:
                previous_date = datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"Invalid date format in the first row: {date_value}. Expected YYYY-MM-DD."
                )
            processed_dates.append(previous_date)
        else:
            # Subsequent rows contain formulas like '=A2+1'
            if date_value.startswith("="):
                # Assuming the formula is always adding 1 day to the previous date
                if previous_date is None:
                    raise ValueError("Previous date not set for formula processing.")
                previous_date += timedelta(days=1)
                processed_dates.append(previous_date)
            else:
                # If it's not a formula, try to parse it as a date
                try:
                    current_date = datetime.strptime(date_value, "%Y-%m-%d")
                    previous_date = current_date
                    processed_dates.append(current_date)
                except ValueError:
                    raise ValueError(
                        f"Unexpected value in 'Date' column at row {index}: {date_value}. Expected formula or YYYY-MM-DD."
                    )

    df["Date"] = processed_dates
    return df


if __name__ == "__main__":
    # Simulate the problematic Date column
    data = {
        "Date": ["2023-01-01", "=A2+1", "=A3+1", "=A4+1", "2023-01-08", "=A6+1"],
        "Value": [10, 20, 30, 40, 50, 60],
    }
    df = pd.DataFrame(data)

    print("Original DataFrame:")
    print(df)
    print("\n" + "=" * 30 + "\n")

    try:
        processed_df = process_date_column(df.copy())
        print("Processed DataFrame:")
        print(processed_df)
    except ValueError as e:
        print(f"Error processing dates: {e}")
