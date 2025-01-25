import os

def save_team_stats_to_parquet(team_stats, folder_name, csv_file_path):
    # Ensure the folder for saving the Parquet file exists
    save_folder = os.path.join(folder_name, 'processed_data')
    os.makedirs(save_folder, exist_ok=True)  # Create folder if it doesn't exist

    # Extracting the base filename (without extension) from the csv_file_path
    base_filename = os.path.basename(csv_file_path).replace('.csv', '.parquet')

    # Full path for saving the Parquet file
    save_path = os.path.join(save_folder, base_filename)

    # Save the dataframe as a Parquet file
    team_stats.to_parquet(save_path)

    print(f"Data saved to {save_path}")
