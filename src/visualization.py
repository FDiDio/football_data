import matplotlib.pyplot as plt
import seaborn as sns

def visualize_team_performance(team_stats):
    """
    Visualize the relationships between Actual vs Expected performance metrics for teams.
    Creates line plots for Points/Expected Points, Goals Scored/Expected Goals Scored, and
    Goals Conceded/Expected Goals Conceded with reference lines.
    
    Parameters:
    - team_stats (DataFrame): The team statistics DataFrame containing the relevant columns.
    """
    # Set up the seaborn style
    sns.set(style="whitegrid")

    # Create a figure with subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1. Points vs Expected Points
    axes[0].plot(team_stats['Team'], team_stats['Points'], label='Actual Points', marker='o', color='blue')
    axes[0].plot(team_stats['Team'], team_stats['ExpectedPoints_xG'], label='Expected Points', marker='x', color='orange')
    axes[0].set_title('Points vs Expected Points')
    axes[0].set_xlabel('Team')
    axes[0].set_ylabel('Points')
    axes[0].tick_params(axis='x', rotation=90)  # Rotate team names for readability
    axes[0].legend()

    # 2. Goals Scored vs Expected Goals Scored
    axes[1].plot(team_stats['Team'], team_stats['GF'], label='Goals Scored', marker='o', color='blue')
    axes[1].plot(team_stats['Team'], team_stats['xG_Scored'], label='Expected Goals Scored', marker='x', color='orange')
    axes[1].set_title('Goals Scored vs Expected Goals Scored')
    axes[1].set_xlabel('Team')
    axes[1].set_ylabel('Goals Scored')
    axes[1].tick_params(axis='x', rotation=90)  # Rotate team names for readability
    axes[1].legend()

    # 3. Goals Conceded vs Expected Goals Conceded
    axes[2].plot(team_stats['Team'], team_stats['GA'], label='Goals Conceded', marker='o', color='blue')
    axes[2].plot(team_stats['Team'], team_stats['xG_Conceded'], label='Expected Goals Conceded', marker='x', color='orange')
    axes[2].set_title('Goals Conceded vs Expected Goals Conceded')
    axes[2].set_xlabel('Team')
    axes[2].set_ylabel('Goals Conceded')
    axes[2].tick_params(axis='x', rotation=90)  # Rotate team names for readability
    axes[2].legend()

    # Adjust layout to make sure labels and titles fit
    plt.tight_layout()

    # Show the plot
    plt.show()
