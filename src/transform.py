import pandas as pd
import numpy as np
from scipy.stats import poisson
from predict import calculate_match_outcome_probabilities

def calculate_points(row):
    # Based on the final goals scored or xG scored, calculate points for Home and Away
    home_goals = row['FTHG']  # You can change this to 'FTHG' if using actual goals
    away_goals = row['FTAG']  # Similarly, change this to 'FTAG' if using actual goals

    # Calculate Home and Away points based on the result
    if home_goals > away_goals:
        home_points = 3  # Home win
        away_points = 0  # Away loss
    elif home_goals < away_goals:
        home_points = 0  # Home loss
        away_points = 3  # Away win
    else:
        home_points = 1  # Draw
        away_points = 1  # Draw

    return pd.Series([home_points, away_points])

# Function to calculate xG for shots and corners
def calculate_xg(df, average_xg_per_shot=0.11, average_xg_per_corner=0.02):
    df.fillna(0, inplace=True)
    
    # Calculate xG for shots and corners
    df['Home_xG_scored'] = df['HS'] * average_xg_per_shot + df['HC'] * average_xg_per_corner
    df['Away_xG_scored'] = df['AS'] * average_xg_per_shot + df['AC'] * average_xg_per_corner
    df['Home_xG_conceded'] = df['AS'] * average_xg_per_shot + df['AC'] * average_xg_per_corner
    df['Away_xG_conceded'] = df['HS'] * average_xg_per_shot + df['HC'] * average_xg_per_corner

    return df



# Function to calculate expected points based on Poisson probabilities
def calculate_expected_points_poisson(home_xg, away_xg):
    home_win_prob, draw_prob, away_win_prob, _ = calculate_match_outcome_probabilities(home_xg, away_xg)
    home_xp = (3 * home_win_prob) + (1 * draw_prob) + (0 * away_win_prob)
    away_xp = (3 * away_win_prob) + (1 * draw_prob) + (0 * home_win_prob)
    return home_xp, away_xp

# Function to aggregate team statistics and preserve both Home and Away team information
def aggregate_team_stats(df):
    # Aggregating home stats
    home_stats = df.groupby('HomeTeam').agg(
        Matches_home=('HomePoints', 'count'),
        Points_home=('HomePoints', 'sum'),
        GF_home=('FTHG', 'sum'),
        GA_home=('FTAG', 'sum'),
        xG_Scored_home=('Home_xG_scored', 'sum'),
        xG_Conceded_home=('Home_xG_conceded', 'sum')
    ).reset_index().rename(columns={'HomeTeam': 'Team'})  # Reset index and rename 'HomeTeam' to 'Team'

    # Aggregating away stats
    away_stats = df.groupby('AwayTeam').agg(
        Matches_away=('AwayPoints', 'count'),
        Points_away=('AwayPoints', 'sum'),
        GF_away=('FTAG', 'sum'),
        GA_away=('FTHG', 'sum'),
        xG_Scored_away=('Away_xG_scored', 'sum'),
        xG_Conceded_away=('Away_xG_conceded', 'sum')
    ).reset_index().rename(columns={'AwayTeam': 'Team'})  # Reset index and rename 'AwayTeam' to 'Team'

    # Merge home_stats and away_stats on 'Team'
    team_stats = pd.merge(home_stats, away_stats, on='Team', how='outer').fillna(0)

    # Combine stats into overall statistics
    team_stats['Matches'] = team_stats['Matches_home'] + team_stats['Matches_away']
    team_stats['Points'] = team_stats['Points_home'] + team_stats['Points_away']
    team_stats['GF'] = team_stats['GF_home'] + team_stats['GF_away']
    team_stats['GA'] = team_stats['GA_home'] + team_stats['GA_away']
    team_stats['xG_Scored'] = team_stats['xG_Scored_home'] + team_stats['xG_Scored_away']
    team_stats['xG_Conceded'] = team_stats['xG_Conceded_home'] + team_stats['xG_Conceded_away']

    # Calculate Goal Difference (GD)
    team_stats['GD'] = team_stats['GF'] - team_stats['GA']

    # Final DataFrame
    team_stats = team_stats[['Team', 'Matches', 'Points', 'GF', 'GA', 'GD', 'xG_Scored', 'xG_Conceded']]

    # Sort by Points, GD, and GF
    team_stats = team_stats.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False])

    return team_stats





# Example: the file you are working with is already loaded into the variable `df`
# Example usage:
# Assuming 'df' is your DataFrame loaded from a file
