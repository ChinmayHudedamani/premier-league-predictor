import pandas as pd
import numpy as np
from typing import Tuple

def predict_player_of_the_season(players_df: pd.DataFrame, team_title_probs: pd.DataFrame = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ranks candidates for Premier League Player of the Season / Best Player using per-90 metrics,
    underlying expected goals & assists (xGI), ICT influence score, and team title strength multiplier.
    """
    df = players_df.copy()
    
    # Filter players who have played or are active in squad
    if 'minutes' in df.columns:
        min_threshold = 90 if (df['minutes'] >= 450).sum() > 20 else 0
        df = df[df['minutes'] >= min_threshold].copy()
    
    # Convert numerical metrics
    numeric_cols = [
        'expected_goals', 'expected_assists', 'goals_scored', 'assists', 
        'ict_index', 'total_points', 'form', 'minutes', 'influence', 'creativity', 'threat'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
    # Per 90 metrics
    if 'minutes' in df.columns and (df['minutes'] > 0).any():
        df['ninety_mins'] = np.maximum(df['minutes'] / 90.0, 1.0)
        df['xG_per_90'] = df['expected_goals'] / df['ninety_mins']
        df['xA_per_90'] = df['expected_assists'] / df['ninety_mins']
        df['xGI_per_90'] = df['xG_per_90'] + df['xA_per_90']
    else:
        df['xGI_per_90'] = df['expected_goals'] + df['expected_assists']
        
    # Team title weight multiplier (Player of the Season award strongly favors top team stars)
    team_weights = {}
    if team_title_probs is not None and 'team' in team_title_probs.columns:
        for idx, row in team_title_probs.iterrows():
            team = row['team']
            title_p = row.get('title_win_prob_%', 0.0)
            top4_p = row.get('top4_prob_%', 0.0)
            team_weights[team] = 1.0 + (title_p / 100.0) * 1.2 + (top4_p / 100.0) * 0.3
    
    df['team_weight'] = df['team_name'].map(lambda x: team_weights.get(x, 1.0))
    
    # Player composite score for Best Player (POTS)
    # Normalized components
    def min_max(s):
        return (s - s.min()) / (s.max() - s.min() + 1e-5)

    df['norm_xGI'] = min_max(df['xGI_per_90'])
    df['norm_ict'] = min_max(df['ict_index'])
    df['norm_form'] = min_max(df['form'])
    df['norm_points'] = min_max(df['total_points'])
    
    df['pots_score'] = (
        (0.35 * df['norm_xGI']) +
        (0.25 * df['norm_form']) +
        (0.20 * df['norm_ict']) +
        (0.20 * df['norm_points'])
    ) * df['team_weight']
    
    # Golden Boot Score (Goals scored + Expected goals underlying trend)
    df['golden_boot_score'] = df['goals_scored'] + (df['expected_goals'] * 0.5)
    
    pots_ranking = df.sort_values('pots_score', ascending=False).reset_index(drop=True)
    golden_boot_ranking = df.sort_values('golden_boot_score', ascending=False).reset_index(drop=True)
    
    return pots_ranking, golden_boot_ranking
