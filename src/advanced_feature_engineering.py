import pandas as pd
import numpy as np
from typing import Dict, Tuple, List

def compute_advanced_feature_interactions(df_matches: pd.DataFrame) -> pd.DataFrame:
    """
    Computes STRICT PRE-MATCH rolling feature interaction terms with zero target leakage:
    1. Rest-Weighted Elo Differential (Pre-Match Elo & Rest Days)
    2. Rolling Goal Difference Differential (Past 5 matches)
    3. Rolling Points Differential (Past 5 matches)
    4. Pre-Match Team Dominance Index
    """
    df = df_matches.sort_values('parsed_date').copy() if 'parsed_date' in df_matches.columns else df_matches.copy()
    
    # 1. Rest-Weighted Elo Differential (Pre-Match)
    if 'home_elo' in df.columns and 'away_elo' in df.columns:
        home_rest = df.get('home_rest_days', pd.Series(7, index=df.index)).fillna(7.0)
        away_rest = df.get('away_rest_days', pd.Series(7, index=df.index)).fillna(7.0)
        
        elo_diff = df['home_elo'] - df['away_elo']
        rest_ratio = np.log((home_rest + 1.0) / (away_rest + 1.0))
        df['elo_fatigue_interaction'] = elo_diff * (1.0 + rest_ratio)
    else:
        df['elo_fatigue_interaction'] = 0.0

    # 2. Compute Rolling Form per Team (Strictly Prior Matches)
    home_m = df[['parsed_date', 'season', 'home_team', 'home_goals', 'away_goals']].rename(
        columns={'home_team': 'team', 'home_goals': 'gf', 'away_goals': 'ga'}
    )
    home_m['pts'] = np.where(home_m['gf'] > home_m['ga'], 3, np.where(home_m['gf'] == home_m['ga'], 1, 0))
    home_m['gd'] = home_m['gf'] - home_m['ga']
    
    away_m = df[['parsed_date', 'season', 'away_team', 'away_goals', 'home_goals']].rename(
        columns={'away_team': 'team', 'away_goals': 'gf', 'home_goals': 'ga'}
    )
    away_m['pts'] = np.where(away_m['gf'] > away_m['ga'], 3, np.where(away_m['gf'] == away_m['ga'], 1, 0))
    away_m['gd'] = away_m['gf'] - away_m['ga']
    
    all_m = pd.concat([home_m, away_m]).sort_values('parsed_date').reset_index(drop=True)
    
    # Rolling averages over past 5 matches (shift by 1 to exclude current match)
    all_m['rolling_gd_5'] = all_m.groupby('team')['gd'].transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean()).fillna(0.0)
    all_m['rolling_pts_5'] = all_m.groupby('team')['pts'].transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean()).fillna(0.0)
    
    # Map back to home and away teams
    # Create lookup dict: (parsed_date, team) -> rolling_gd_5, rolling_pts_5
    gd_dict = dict(zip(zip(all_m['parsed_date'], all_m['team']), all_m['rolling_gd_5']))
    pts_dict = dict(zip(zip(all_m['parsed_date'], all_m['team']), all_m['rolling_pts_5']))
    
    df['home_rolling_gd_5'] = [gd_dict.get((dt, tm), 0.0) for dt, tm in zip(df['parsed_date'], df['home_team'])]
    df['away_rolling_gd_5'] = [gd_dict.get((dt, tm), 0.0) for dt, tm in zip(df['parsed_date'], df['away_team'])]
    df['rolling_gd_diff'] = df['home_rolling_gd_5'] - df['away_rolling_gd_5']
    
    df['home_rolling_pts_5'] = [pts_dict.get((dt, tm), 0.0) for dt, tm in zip(df['parsed_date'], df['home_team'])]
    df['away_rolling_pts_5'] = [pts_dict.get((dt, tm), 0.0) for dt, tm in zip(df['parsed_date'], df['away_team'])]
    df['rolling_pts_diff'] = df['home_rolling_pts_5'] - df['away_rolling_pts_5']

    # 3. Pre-Match Relative Dominance Index (Interaction term)
    df['relative_dominance_index'] = (
        (0.50 * df.get('elo_diff', 0.0) / 400.0) +
        (0.30 * df['rolling_gd_diff'] / 3.0) +
        (0.20 * df['rolling_pts_diff'] / 3.0)
    )

    return df
