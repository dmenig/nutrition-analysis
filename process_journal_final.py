import pandas as pd
import json


def process_journal_final_csv(file_path, chunk_size=10000):
    print(f"Processing {file_path} in chunks of {chunk_size}...")
    relevant_columns = []
    data_structure_sample = {}
    total_rows = 0

    try:
        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
            if i == 0:
                # Identify relevant columns from the first chunk
                # We are looking for 'Date', 'Weight', and potentially 'Food'/'Sport_Formula_Final'
                # to see if we can derive calories.
                if "Date" in chunk.columns:
                    relevant_columns.append("Date")
                if "Weight" in chunk.columns:
                    relevant_columns.append("Weight")
                if "Food" in chunk.columns:
                    relevant_columns.append("Food")
                if "Sport_Formula_Final" in chunk.columns:
                    relevant_columns.append("Sport_Formula_Final")

                print(f"Identified relevant columns: {relevant_columns}")

                # Take a small sample of the data structure
                if not chunk.empty:
                    data_structure_sample = (
                        chunk[relevant_columns].head(5).to_dict(orient="records")
                    )

            total_rows += len(chunk)
            # In a real scenario, you would process the chunk here, e.g.,
            # calculate calories from 'Food' and 'Sport_Formula_Final' if needed.
            # For this task, we are just identifying columns and structure.

        print(f"Finished processing {total_rows} rows from {file_path}.")
        print(f"Sample data structure: {json.dumps(data_structure_sample, indent=2)}")
        return relevant_columns, data_structure_sample, total_rows

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return [], {}, 0


if __name__ == "__main__":
    file_path = "data/journal_final.csv"
    relevant_cols, sample_data, num_rows = process_journal_final_csv(file_path)
    print(f"\nSummary for {file_path}:")
    print(f"  Relevant Columns: {relevant_cols}")
    print(f"  Total Rows Processed: {num_rows}")
    print(f"  Sample Data: {json.dumps(sample_data, indent=2)}")
