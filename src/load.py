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


def save_team_stats_to_csv(team_stats, folder_name, csv_file_path):
    # Ensure the folder for saving the CSV file exists
    save_folder = os.path.join(folder_name, 'processed_csv_data')
    os.makedirs(save_folder, exist_ok=True)  # Create folder if it doesn't exist

    # Convert specified columns to integers
    columns_to_convert = ['ExpectedPoints_Prob', 'ExpectedPoints_xG', 'xG_Scored', 'xG_Conceded']
    for col in columns_to_convert:
        if col in team_stats.columns:
            team_stats[col] = team_stats[col].astype(int)

    # Extracting the base filename (without extension) from the csv_file_path
    base_filename = os.path.basename(csv_file_path).replace('.csv', '_processed.csv')

    # Full path for saving the CSV file
    save_path = os.path.join(save_folder, base_filename)

    # Save the dataframe as a CSV file
    team_stats.to_csv(save_path, index=False)

    print(f"Data saved to {save_path}")