# Football Data Processing Script

This Python script automates the process of downloading, extracting, and processing football match data from [Football Data](https://www.football-data.co.uk). The data is processed to calculate expected goals (xG), expected goals based on their odds, expected points, and team statistics, and the results are saved to a Parquet file. It also allows you to predict the outcome of a match between two teams based on their statistics.

## Features

- **Download & Extract Data**: Downloads match data for a specified season from the Football Data website and extracts the necessary files.
- **Data Transformation**: 
  - Calculates expected goals (xG) for both home and away teams.
  - Uses Poisson distribution to calculate expected points for each match.
  - Aggregates statistics such as points, goal difference (GD), and goals scored (GF) for each team.
- **Match Prediction**: Predicts the result of a match between two teams based on their statistics.
- **Data Storage**: Saves the processed team statistics in a Parquet format for efficient querying.

## Prerequisites

Ensure you have the following Python packages installed:

- `pandas`
- `argparse`
- `requests`

You can install them using `pip`:

## Configuration

The configuration file `config.json` contains settings that specify how the data should be fetched and processed. You only need to modify this file if you want to change the base URL for the data or the naming convention for the downloaded files.

Example `config.json`:

```json
{
    "base_url": "https://www.football-data.co.uk/mmz4281/{season_year}/data.zip",
    "file_format": "{season_year}_{file_name}.csv"
}
```
## Usage

You can run the script from the command line by specifying the season and the file to process. Optionally, you can provide a home and away team for match prediction.

### Command-Line Arguments

- `--season`: The season or year part of the URL (e.g., 2425 for the 2024-2025 season).
- `--file`: The specific match data file to process (e.g., I1, I2).
- `--home`: The home team for match prediction (optional).
- `--away`: The away team for match prediction (optional).

## Example

```bash
python script.py --season 2425 --file I1 --home TeamA --away TeamB
```

## Output

- Processed team statistics will be printed to the console, including rankings based on points, goal difference, and goals scored.
- If match prediction is requested, the predicted score and the top 3 likely results will be displayed.
- The processed data will be saved as a Parquet file in the same directory as the script.

## How It Works

### Download and Extract

- The script constructs a URL for the ZIP file using the season-year and base URL format from `config.json`.
- The ZIP file is downloaded and extracted to a folder based on the season.

## How It Works

### Download and Extract

- The script constructs a URL for the ZIP file using the season-year and base URL format from `config.json`.
- The ZIP file is downloaded and extracted to a folder based on the season.

### Data Transformation

- The script reads the CSV file from the extracted data, calculates xG values for both home and away teams, and computes expected points using Poisson regression.
- It also aggregates the team statistics, such as total points, goal difference, and goals scored, to produce a league table.

### Match Prediction

- Based on the aggregated statistics, the script predicts the result of a match between two specified teams. It generates a prediction along with a probability of different outcomes (e.g., home win, away win, draw).

### Save Output

- The team statistics are saved in a Parquet file, making it easy to query and analyze the data later.

## Team Performance Visualization

This module provides visualizations for comparing the actual performance vs. expected performance of football teams. It generates line plots for the following relationships:

- **Points vs Expected Points** - Compares the total points each team has accumulated in the season to their expected points based on their performance metrics.
- **Goals Scored vs Expected Goals Scored** - Shows how many goals each team has scored versus how many they were expected to score based on their expected goals (xG).
- **Goals Conceded vs Expected Goals Conceded** - Displays the number of goals each team has conceded compared to their expected goals conceded.

For each of these relationships, the plots show actual vs. expected values with distinct lines, allowing you to easily compare the teams' overperformance or underperformance in various areas. The X-axis represents the teams, while the Y-axis displays the respective performance metrics.

The visualization can be accessed and executed via the `visualize_team_performance` function, which takes in the team statistics DataFrame and generates the plots with labeled axes and legends.
