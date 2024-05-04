import os
import pandas as pd

def load_json_files(directory):
    # Get a list of all files with .json extension in the specified directory
    json_files = [file for file in os.listdir(directory) if file.endswith(".json")]

    # Initialize an empty list to hold individual DataFrames
    dfs = []

    # Iterate over each JSON file
    for file in json_files:
        file_path = os.path.join(directory, file)
        try:
            if file == "reddit_data.json":
                continue
            # Load JSON file into a DataFrame
            df = pd.read_json(file_path)

            # Append DataFrame to the list
            dfs.append(df)
        except Exception as e:
            print(f"Error loading file {file}: {e}")

    # Concatenate all DataFrames in the list into a single DataFrame
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    else:
        return None

if __name__ == "__main__":
    data_directory = "data"  # Specify the directory containing JSON files

    # Load all JSON files from the specified directory into a single DataFrame
    all_data_df = load_json_files(data_directory)

    if all_data_df is not None:
        # Save the combined DataFrame to a new JSON file
        output_file = "data/reddit_data.json"
        all_data_df.to_json(output_file, orient="records", lines=True)

        print(f"Combined DataFrame saved to {output_file}")
        print(f"Total number of rows in the combined DataFrame: {len(all_data_df)}")
        print(f"Posts that included stock with desired growth: {(all_data_df['Label'] == 1).sum()}")
        print(f"Posts that included stock without desired growth: {(all_data_df['Label'] == 0).sum()}")
    else:
        print("No JSON files found or error occurred during processing.")