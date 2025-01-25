import numpy as np
from scipy.stats import poisson

# Function to predict the exact score
def predict_match_result(team_stats, home_team, away_team, max_goals=6):
    # Ensure that home_team and away_team exist in the team_stats DataFrame
    home_stats = team_stats.loc[team_stats['Team'] == home_team].iloc[0]
    away_stats = team_stats.loc[team_stats['Team'] == away_team].iloc[0]

    # Calculate combined xG for the match based on the proportion of goals scored/conceded
    home_xg = (home_stats['xG_Scored'] / home_stats['Matches'] + away_stats['xG_Conceded'] / away_stats['Matches']) - 0.8
    away_xg = (away_stats['xG_Scored'] / away_stats['Matches'] + home_stats['xG_Conceded'] / home_stats['Matches']) - 1.4

    # Calculate goal probabilities
    _, _, _, goal_matrix = calculate_match_outcome_probabilities(home_xg, away_xg, max_goals)

    # Calculate the expected number of goals as a weighted average
    home_goals_probabilities = np.sum(goal_matrix, axis=1)
    away_goals_probabilities = np.sum(goal_matrix, axis=0)

    predicted_home_goals = np.sum(home_goals_probabilities * np.arange(max_goals)) / np.sum(home_goals_probabilities)
    predicted_away_goals = np.sum(away_goals_probabilities * np.arange(max_goals)) / np.sum(away_goals_probabilities)

    # Round the results to one decimal place
    predicted_home_goals = round(predicted_home_goals, 1)
    predicted_away_goals = round(predicted_away_goals, 1)

    return predicted_home_goals, predicted_away_goals

# Function to calculate Poisson distribution probabilities
def calculate_match_outcome_probabilities(home_xg, away_xg, max_goals=6):
    home_win_prob = 0
    draw_prob = 0
    away_win_prob = 0
    goal_matrix = np.zeros((max_goals, max_goals))  # Matrix to store goal probabilities

    # Iterate over all possible goal combinations
    for home_goals in range(max_goals):
        for away_goals in range(max_goals):
            prob = poisson.pmf(home_goals, home_xg) * poisson.pmf(away_goals, away_xg)
            goal_matrix[home_goals, away_goals] = prob
            if home_goals > away_goals:
                home_win_prob += prob
            elif home_goals == away_goals:
                draw_prob += prob
            else:
                away_win_prob += prob

    # Normalize the goal matrix so the probabilities sum to 1
    goal_matrix /= np.sum(goal_matrix)

    return home_win_prob, draw_prob, away_win_prob, goal_matrix

# Function to suggest possible results based on goal matrix and predictions
def suggest_possible_results(goal_matrix, predicted_home_goals, predicted_away_goals, max_goals=6):
    possible_results = []

    # Iterate over all goal combinations
    for home_goals in range(max_goals):
        for away_goals in range(max_goals):
            prob = goal_matrix[home_goals, away_goals]
            distance = abs(predicted_home_goals - home_goals) + abs(predicted_away_goals - away_goals)
            possible_results.append((home_goals, away_goals, prob, distance))
    
    # Sort by probability (descending) and distance (ascending)
    possible_results = sorted(possible_results, key=lambda x: (-x[2], x[3]))
    
    # Select the top 3 most likely results
    top_3_results = possible_results[:3]

    return [(home_goals, away_goals, round(prob * 100, 2)) for home_goals, away_goals, prob, _ in top_3_results]

# Main function to predict match and suggest possible results
def predict_match_with_suggestions(team_stats, home_team, away_team, max_goals=6):
    # Predict the match result
    predicted_home_goals, predicted_away_goals = predict_match_result(team_stats, home_team, away_team, max_goals)

    # Calculate goal probabilities
    home_stats = team_stats.loc[team_stats['Team'] == home_team].iloc[0]
    away_stats = team_stats.loc[team_stats['Team'] == away_team].iloc[0]
    home_xg = (home_stats['xG_Scored'] / home_stats['Matches'] + away_stats['xG_Conceded'] / away_stats['Matches']) - 0.8
    away_xg = (away_stats['xG_Scored'] / away_stats['Matches'] + home_stats['xG_Conceded'] / home_stats['Matches']) - 1.4

    # Recalculate the goal matrix with customized xG values
    _, _, _, goal_matrix = calculate_match_outcome_probabilities(home_xg, away_xg, max_goals)

    # Suggest 3 possible results
    suggestions = suggest_possible_results(goal_matrix, predicted_home_goals, predicted_away_goals, max_goals)

    return predicted_home_goals, predicted_away_goals, suggestions
