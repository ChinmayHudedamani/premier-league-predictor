import pandas as pd
import numpy as np
from typing import Dict, Tuple, List

def calculate_player_skills_and_synergy(players_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes individual skill ratings, tactical suitability, and team synergy scores.
    """
    df = players_df.copy()
    
    # Ensure numeric columns
    numeric_cols = [
        'goals_scored', 'assists', 'expected_goals', 'expected_assists',
        'ict_index', 'influence', 'creativity', 'threat', 'minutes', 'total_points', 'form'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    mins = np.maximum(df['minutes'], 90.0)
    ninety_mins = mins / 90.0
    
    # 1. Individual Skill Ratings (0 - 100 Scale)
    df['shooting_skill'] = np.clip((df['goals_scored'] / ninety_mins * 25.0) + (df['expected_goals'] / ninety_mins * 20.0), 0, 100)
    df['playmaking_skill'] = np.clip((df['assists'] / ninety_mins * 30.0) + (df['expected_assists'] / ninety_mins * 25.0) + (df['creativity'] / 10.0), 0, 100)
    df['defensive_workrate'] = np.clip((df['influence'] / 15.0) + np.where(df['position'] == 'Defender', 40.0, 10.0), 0, 100)
    df['tactical_flexibility'] = np.clip((df['ict_index'] / 5.0) + (df['form'] * 5.0), 0, 100)
    
    # Composite Individual Skill Index
    df['individual_skill_index'] = (
        (0.35 * df['shooting_skill']) +
        (0.35 * df['playmaking_skill']) +
        (0.15 * df['defensive_workrate']) +
        (0.15 * df['tactical_flexibility'])
    )
    
    # 2. Team-Level Synergy Calculation
    team_synergy = []
    grouped = df.groupby('team_name')
    
    for team_name, group in grouped:
        if len(group) == 0:
            continue
            
        top_creators = group.nlargest(3, 'playmaking_skill')
        top_finishers = group.nlargest(3, 'shooting_skill')
        
        avg_creation = top_creators['playmaking_skill'].mean()
        avg_finishing = top_finishers['shooting_skill'].mean()
        
        # Harmonic mean for offensive synergy (both high creation & high finishing needed)
        offensive_synergy = (2 * avg_creation * avg_finishing) / (avg_creation + avg_finishing + 1e-5)
        defensive_cohesion = group['defensive_workrate'].mean()
        tactical_adaptability = group['tactical_flexibility'].mean()
        
        overall_team_synergy = (0.50 * offensive_synergy) + (0.30 * defensive_cohesion) + (0.20 * tactical_adaptability)
        
        team_synergy.append({
            'team_name': team_name,
            'squad_size': len(group),
            'offensive_synergy_score': round(offensive_synergy, 2),
            'defensive_cohesion_score': round(defensive_cohesion, 2),
            'tactical_adaptability_score': round(tactical_adaptability, 2),
            'overall_synergy_score': round(overall_team_synergy, 2)
        })
        
    team_synergy_df = pd.DataFrame(team_synergy).sort_values('overall_synergy_score', ascending=False).reset_index(drop=True)
    player_skills_df = df.sort_values('individual_skill_index', ascending=False).reset_index(drop=True)
    
    return player_skills_df, team_synergy_df

if __name__ == "__main__":
    import os
    fpl_path = "data/player_data/fpl_current_players.csv"
    if os.path.exists(fpl_path):
        df_players = pd.read_csv(fpl_path)
        p_df, t_df = calculate_player_skills_and_synergy(df_players)
        print("Top 5 Player Skill Indices:")
        print(p_df[['web_name', 'team_name', 'position', 'individual_skill_index']].head())
        print("\nTop 5 Team Synergy Scores:")
        print(t_df.head())
