import pandas as pd
import numpy as np
from typing import Tuple, Dict, List

def calculate_elo_ratings(df: pd.DataFrame, k_factor: float = 20.0, initial_elo: float = 1500.0) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Calculates dynamic historical Elo ratings for all teams across all matches from 1993 to present.
    """
    df = df.sort_values('parsed_date').copy() if 'parsed_date' in df.columns else df.copy()
    
    elo_dict = {}
    home_elo_col = []
    away_elo_col = []
    
    for idx, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        
        # Initialize rating if new team
        if home not in elo_dict:
            elo_dict[home] = initial_elo
        if away not in elo_dict:
            elo_dict[away] = initial_elo
            
        r_home = elo_dict[home]
        r_away = elo_dict[away]
        
        home_elo_col.append(r_home)
        away_elo_col.append(r_away)
        
        # Expected scores (with +100 home advantage)
        e_home = 1.0 / (1.0 + 10.0 ** ((r_away - (r_home + 100.0)) / 400.0))
        e_away = 1.0 - e_home
        
        # Actual outcome (1 = Home Win, 0.5 = Draw, 0 = Away Win)
        h_goals = row.get('home_goals', 0)
        a_goals = row.get('away_goals', 0)
        
        if h_goals > a_goals:
            s_home, s_away = 1.0, 0.0
        elif h_goals < a_goals:
            s_home, s_away = 0.0, 1.0
        else:
            s_home, s_away = 0.5, 0.5
            
        # Goal margin weighting
        goal_diff = abs(h_goals - a_goals)
        margin_multiplier = np.log(goal_diff + 1) if goal_diff > 1 else 1.0
        
        # Update Elo
        elo_dict[home] += k_factor * margin_multiplier * (s_home - e_home)
        elo_dict[away] += k_factor * margin_multiplier * (s_away - e_away)
        
    df['home_elo'] = home_elo_col
    df['away_elo'] = away_elo_col
    df['elo_diff'] = df['home_elo'] - df['away_elo']
    
    return df, elo_dict

def calculate_rolling_form(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Computes rolling goal difference, points per game, and form over the past N matches.
    """
    # Create long format match logs
    home_matches = df[['parsed_date', 'season', 'home_team', 'home_goals', 'away_goals']].rename(
        columns={'home_team': 'team', 'home_goals': 'goals_for', 'away_goals': 'goals_against'}
    )
    home_matches['is_home'] = 1
    
    away_matches = df[['parsed_date', 'season', 'away_team', 'away_goals', 'home_goals']].rename(
        columns={'away_team': 'team', 'away_goals': 'goals_for', 'home_goals': 'goals_against'}
    )
    away_matches['is_home'] = 0
    
    all_matches = pd.concat([home_matches, away_matches]).sort_values('parsed_date').reset_index(drop=True)
    
    # Calculate points
    all_matches['points'] = np.where(all_matches['goals_for'] > all_matches['goals_against'], 3,
                            np.where(all_matches['goals_for'] == all_matches['goals_against'], 1, 0))
    all_matches['goal_diff'] = all_matches['goals_for'] - all_matches['goals_against']
    
    # Rolling averages by team
    all_matches['rolling_pts'] = all_matches.groupby('team')['points'].transform(lambda x: x.shift(1).rolling(window, min_periods=1).mean())
    all_matches['rolling_gf'] = all_matches.groupby('team')['goals_for'].transform(lambda x: x.shift(1).rolling(window, min_periods=1).mean())
    all_matches['rolling_ga'] = all_matches.groupby('team')['goals_against'].transform(lambda x: x.shift(1).rolling(window, min_periods=1).mean())
    
    return all_matches
