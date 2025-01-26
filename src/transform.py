import pandas as pd
import numpy as np
from scipy.stats import poisson
from predict import calculate_match_outcome_probabilities


def calculate_points(row):
    # Based on the final goals scored, calculate points for Home and Away
    home_goals = row['FTHG']  # Change to 'FTHG' if using actual goals
    away_goals = row['FTAG']  # Similarly, change to 'FTAG' if using actual goals

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


# Function to calculate expected points based on xG (scored and conceded)
def calculate_expected_points_xg(home_xg_scored, away_xg_scored, home_xg_conceded, away_xg_conceded):
    home_win_prob = poisson.cdf(home_xg_scored - 1, home_xg_conceded)
    away_win_prob = poisson.cdf(away_xg_scored - 1, away_xg_conceded)
    draw_prob = 1 - home_win_prob - away_win_prob

    home_xp = (3 * home_win_prob) + (1 * draw_prob) + (0 * away_win_prob)
    away_xp = (3 * away_win_prob) + (1 * draw_prob) + (0 * home_win_prob)

    return home_xp, away_xp


# Function to calculate expected points for each match
def calculate_expected_points(df):
    df['HomeExpectedPoints_Prob'] = 0
    df['AwayExpectedPoints_Prob'] = 0
    df['HomeExpectedPoints_xG'] = 0
    df['AwayExpectedPoints_xG'] = 0

    for idx, row in df.iterrows():
        home_xg_scored = row['Home_xG_scored']
        away_xg_scored = row['Away_xG_scored']
        home_xg_conceded = row['Home_xG_conceded']
        away_xg_conceded = row['Away_xG_conceded']

        # Expected points from probabilities
        home_xp_prob, away_xp_prob = calculate_expected_points_poisson(home_xg_scored, away_xg_scored)

        # Expected points from xG (scored/conceded)
        home_xp_xg, away_xp_xg = calculate_expected_points_xg(
            home_xg_scored, away_xg_scored, home_xg_conceded, away_xg_conceded
        )

        # Assign to DataFrame
        df.at[idx, 'HomeExpectedPoints_Prob'] = float(home_xp_prob)
        df.at[idx, 'AwayExpectedPoints_Prob'] = float(away_xp_prob)
        df.at[idx, 'HomeExpectedPoints_xG'] = float(home_xp_xg)
        df.at[idx, 'AwayExpectedPoints_xG'] = float(away_xp_xg)

    return df


# Function to aggregate team statistics and preserve both Home and Away team information
def aggregate_team_stats(df):
    # Aggregating home stats
    home_stats = df.groupby('HomeTeam').agg(
        Matches_home=('HomePoints', 'count'),
        Points_home=('HomePoints', 'sum'),
        ExpectedPoints_Prob_home=('HomeExpectedPoints_Prob', 'sum'),
        ExpectedPoints_xG_home=('HomeExpectedPoints_xG', 'sum'),
        GF_home=('FTHG', 'sum'),
        GA_home=('FTAG', 'sum'),
        xG_Scored_home=('Home_xG_scored', 'sum'),
        xG_Conceded_home=('Home_xG_conceded', 'sum')
    ).reset_index().rename(columns={'HomeTeam': 'Team'})  # Reset index and rename 'HomeTeam' to 'Team'

    # Aggregating away stats
    away_stats = df.groupby('AwayTeam').agg(
        Matches_away=('AwayPoints', 'count'),
        Points_away=('AwayPoints', 'sum'),
        ExpectedPoints_Prob_away=('AwayExpectedPoints_Prob', 'sum'),
        ExpectedPoints_xG_away=('AwayExpectedPoints_xG', 'sum'),
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
    team_stats['ExpectedPoints_Prob'] = team_stats['ExpectedPoints_Prob_home'] + team_stats['ExpectedPoints_Prob_away']
    team_stats['ExpectedPoints_xG'] = team_stats['ExpectedPoints_xG_home'] + team_stats['ExpectedPoints_xG_away']
    team_stats['GF'] = team_stats['GF_home'] + team_stats['GF_away']
    team_stats['GA'] = team_stats['GA_home'] + team_stats['GA_away']
    team_stats['xG_Scored'] = team_stats['xG_Scored_home'] + team_stats['xG_Scored_away']
    team_stats['xG_Conceded'] = team_stats['xG_Conceded_home'] + team_stats['xG_Conceded_away']

    # Calculate Goal Difference (GD)
    team_stats['GD'] = team_stats['GF'] - team_stats['GA']

    # Sort by Points, GD, and GF to determine rank
    team_stats = team_stats.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False])

    # Assign ranks based on sorting
    team_stats['Rank'] = range(1, len(team_stats) + 1)

    # Final DataFrame
    team_stats = team_stats[
        ['Team', 'Rank', 'Matches', 'Points', 'ExpectedPoints_Prob', 'ExpectedPoints_xG', 'GF', 'GA', 'GD', 'xG_Scored', 'xG_Conceded']
    ]

    return team_stats


def calculate_form(df, n_matches=5):
    # Create a DataFrame to store form
    form_data = pd.DataFrame()

    # Iterate over each team to calculate their form based on the last N matches
    teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    for team in teams:
        # Filter matches where the team was involved
        team_matches = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].copy()

        # Sort matches by date (assuming the DataFrame is not already sorted)
        team_matches = team_matches.sort_values('Date', ascending=False)

        # Take the last N matches
        recent_matches = team_matches.head(n_matches)

        # Calculate total points earned in these matches
        points = 0
        for _, match in recent_matches.iterrows():
            if match['HomeTeam'] == team:
                points += match['HomePoints']
            elif match['AwayTeam'] == team:
                points += match['AwayPoints']

        # Append the result to form_data
        form_data = pd.concat([form_data, pd.DataFrame({'Team': [team], 'Form': [points]})])

    return form_data.reset_index(drop=True)