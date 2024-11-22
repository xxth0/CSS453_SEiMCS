import os
import pandas as pd

# Specify the folder containing CSV files and the output folder
input_folder_path = '/Users/roblu/Desktop/Cyber_Crime/RawMD'  # Folder path for the input CSV files
output_folder_path = '/Users/roblu/Desktop/Cyber_Crime/KWextracted'  # Folder path for the output text files

# Ensure the output folder exists
os.makedirs(output_folder_path, exist_ok=True)

# Specify the columns you want to extract
columns_to_extract = ['PID', 'Name', 'Gender', 'Type', 'Allergies', 'Region', 'Diagnosis']

# Loop through each file in the input folder
for filename in os.listdir(input_folder_path):
    if filename.endswith('.csv'):
        csv_file_path = os.path.join(input_folder_path, filename)
        output_txt_file_path = os.path.join(output_folder_path, f"{os.path.splitext(filename)[0]}.txt")

        # Read the CSV file
        try:
            df = pd.read_csv(csv_file_path)
        except pd.errors.ParserError:
            print(f"Error reading file '{filename}'. It might be in a raw format or lack headers.")
            continue  # Skip this file and move to the next one

        # Rename 'Patient ID' to 'PID' if it exists
        if 'Patient ID' in df.columns:
            df = df.rename(columns={'Patient ID': 'PID'})

        # Check if specified columns are present in the CSV
        missing_columns = [col for col in columns_to_extract if col not in df.columns]
        if missing_columns:
            print(f"Columns not found in '{filename}': {missing_columns}")
            continue  # Skip this file if required columns are missing

        # Extract the specified columns
        extracted_data = df[columns_to_extract]

        # Write the extracted data to a text file in a readable format
        with open(output_txt_file_path, 'w') as f:
            for index, row in extracted_data.iterrows():
                for col in columns_to_extract:
                    f.write(f"{col}: {row[col]}\n")
                f.write("\n")  # Separate each entry with a newline

        print(f"Data successfully extracted from '{filename}' to '{output_txt_file_path}'")
