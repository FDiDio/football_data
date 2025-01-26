import argparse
import os
import pandas as pd
import json
from extract import download_and_extract_zip
from transform import calculate_xg, calculate_expected_points_poisson, aggregate_team_stats, calculate_points, calculate_form, calculate_expected_points
from load import save_team_stats_to_parquet
from predict import predict_match_with_suggestions

# Load configuration from the config.json file
def load_config(config_path='config.json'):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config

def process_file(season_year, specific_file, home_team, away_team, config):
    print(f"Starting process for season {season_year} and file {specific_file}...")

    # Construct URL using the base URL from config
    url = config["base_url"].format(season_year=season_year)
    folder_name = f"{season_year[:2]}_{season_year[2:]}"
    
    # Extract phase
    print(f"Extracting data from {url}...")
    extracted_files = download_and_extract_zip(url, folder_name)
    extracted_files = os.listdir(folder_name)

    # Construct file path using file format from config
    formatted_file_name = config["file_format"].format(season_year=season_year, file_name=specific_file)
    if formatted_file_name in extracted_files:
        print(f"Processing specific file: {formatted_file_name}...")
        csv_file_path = os.path.join(folder_name, formatted_file_name)

        try:
            # Read the CSV file
            df = pd.read_csv(csv_file_path)
            
            # Transform phase
            df = calculate_xg(df)

            # Calculate expected points using Poisson probabilities
            df[['Home_xP_Poisson', 'Away_xP_Poisson']] = df.apply(
                lambda row: pd.Series(calculate_expected_points_poisson(row['Home_xG_scored'], row['Away_xG_scored'])),
                axis=1
            )

            # Step 1: Calculate points for each match
            df[['HomePoints', 'AwayPoints']] = df.apply(calculate_points, axis=1)

            # Step 2: Calculate xG for all matches
            df = calculate_xg(df)
            df = calculate_expected_points(df)
            # Step 3: Calculate team stats (including Rank)
            team_stats = aggregate_team_stats(df)

            # Step 4: Calculate Form
            form_data = calculate_form(df)


            # Step 5: Merge Form into team_stats
            team_stats = team_stats.merge(form_data, on='Team', how='left')

            # Print the ranking dataset
            print("\n=== Team Rankings ===")
            print(team_stats.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False]))
        
            # Predict match result if teams are provided
            if home_team and away_team:
                predicted_home_goals, predicted_away_goals, suggestions = predict_match_with_suggestions(team_stats, home_team, away_team)
                print(f"\nPredicted result: {home_team} {predicted_home_goals} - {predicted_away_goals} {away_team}")
                print("Top 3 likely results:")
                for home, away, prob in suggestions:
                    print(f"{home}-{away} ({prob:.2f}% chance)")

            # Load phase
            print(f"\nSaving processed data for {csv_file_path} to Parquet...")
            save_team_stats_to_parquet(team_stats, folder_name, csv_file_path)

        except Exception as e:
            print(f"Error while processing {csv_file_path}: {e}")
    else:
        print(f"Error: {formatted_file_name} not found in extracted files.")

def main(season_year, specific_file=None, home_team=None, away_team=None):
    # Load configuration from the config file
    config = load_config()

    # Directly call the process_file function to process the specific file
    process_file(season_year, specific_file, home_team, away_team, config)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Download and process football data for a specific season.")
    parser.add_argument('--season', type=str, required=True, help="The season/year part of the URL (e.g., '2425').")
    parser.add_argument('--file', type=str, required=True, help="Specific file to process from the ZIP archive.")
    parser.add_argument('--home', type=str, required=False, help="Home team for match prediction.")
    parser.add_argument('--away', type=str, required=False, help="Away team for match prediction.")
    
    args = parser.parse_args()

    # Debugging statement: print out the parsed arguments
    print(f"Parsed arguments: {args}")

    # Ensure that main is called with the parsed arguments
    main(args.season, args.file, args.home, args.away)
