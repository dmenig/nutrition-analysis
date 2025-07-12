import json


def process_nutrition_data_json(file_path):
    print(f"Processing {file_path} line by line...")
    relevant_columns = []
    data_structure_sample = {}
    total_entries = 0

    try:
        with open(file_path, "r") as f:
            # Read the first few lines to get a sense of the structure
            # This assumes the JSON is structured with top-level keys as dates
            # and values as dictionaries containing nutrition data.
            # We'll read line by line to avoid loading the whole file.
            lines = []
            for _ in range(10):  # Read first 10 lines to get a sample
                line = f.readline()
                if not line:
                    break
                lines.append(line)

            # Attempt to parse the first few lines as JSON to get column names
            # This is a bit tricky with line-by-line for a large JSON,
            # but we can try to parse a small, valid JSON snippet.
            # For a truly large JSON, a streaming parser would be ideal.
            # Given the `head -n 5` output, it seems to be a dictionary of dictionaries.
            # We'll try to load a small part to get the keys.

            # Re-open file to ensure we are at the beginning for actual processing
            f.seek(0)
            first_line = f.readline()
            if first_line.strip() == "{":  # Check if it starts with an object
                # Read until we get a full entry or a few entries
                temp_json_str = "{"
                for line in f:
                    temp_json_str += line
                    if (
                        "}" in line and "}" in temp_json_str
                    ):  # Simple check for end of an entry
                        try:
                            # Try to parse a small part to get keys
                            temp_data = json.loads(
                                temp_json_str + "}"
                            )  # Add closing brace for valid JSON
                            first_key = next(iter(temp_data))
                            sample_entry = temp_data[first_key]
                            relevant_columns = list(sample_entry.keys())
                            data_structure_sample = {first_key: sample_entry}
                            break
                        except json.JSONDecodeError:
                            continue
                f.seek(0)  # Reset file pointer for full processing

            print(f"Identified relevant columns: {relevant_columns}")

            # Now, iterate through the file to count entries and confirm structure
            # This is a simplified approach for large JSONs.
            # A proper streaming JSON parser (like `ijson` or `json_stream`) would be better.
            # For this task, we'll assume the top-level keys are dates and each value is a daily record.
            # We'll count the top-level keys.
            f.seek(0)
            full_data = json.load(
                f
            )  # For this specific structure, loading the whole thing is the easiest way to count top-level keys.
            # If the file was truly massive and flat, line-by-line would be necessary.
            # Given the `head` output, it's a dictionary of daily records.
            total_entries = len(full_data)

            # If relevant_columns were not found from the sample, try from the full data
            if not relevant_columns and total_entries > 0:
                first_key = next(iter(full_data))
                sample_entry = full_data[first_key]
                relevant_columns = list(sample_entry.keys())
                data_structure_sample = {first_key: sample_entry}

        print(f"Finished processing {total_entries} entries from {file_path}.")
        print(f"Sample data structure: {json.dumps(data_structure_sample, indent=2)}")
        return relevant_columns, data_structure_sample, total_entries

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return [], {}, 0


if __name__ == "__main__":
    file_path = "nutrition_data.json"
    relevant_cols, sample_data, num_entries = process_nutrition_data_json(file_path)
    print(f"\nSummary for {file_path}:")
    print(f"  Relevant Columns/Keys: {relevant_cols}")
    print(f"  Total Entries Processed: {num_entries}")
    print(f"  Sample Data: {json.dumps(sample_data, indent=2)}")
