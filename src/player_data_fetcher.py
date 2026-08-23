import os
import requests
import pandas as pd
import json
from typing import Optional

FPL_BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

def fetch_fpl_player_data(output_dir: str = "data/player_data") -> pd.DataFrame:
    """
    Fetches real-time player data from the official Fantasy Premier League (FPL) API.
    Includes stats: xG, xA, goals, assists, ICT Index, minutes, position, team, form, etc.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Fetching current season player data from FPL API ({FPL_BOOTSTRAP_URL})...")
    
    try:
        response = requests.get(FPL_BOOTSTRAP_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Extract players and teams
        players_df = pd.DataFrame(data['elements'])
        teams_df = pd.DataFrame(data['teams'])
        positions_df = pd.DataFrame(data['element_types'])
        
        # Map teams and positions
        team_map = dict(zip(teams_df['id'], teams_df['name']))
        pos_map = dict(zip(positions_df['id'], positions_df['singular_name']))
        
        players_df['team_name'] = players_df['team'].map(team_map)
        players_df['position'] = players_df['element_type'].map(pos_map)
        players_df['full_name'] = players_df['first_name'] + " " + players_df['second_name']
        
        # Select key statistical columns
        cols_to_keep = [
            'id', 'full_name', 'web_name', 'team_name', 'position', 
            'now_cost', 'selected_by_percent', 'form', 'points_per_game',
            'total_points', 'minutes', 'goals_scored', 'assists', 'clean_sheets',
            'goals_conceded', 'yellow_cards', 'red_cards', 'saves', 'bonus',
            'influence', 'creativity', 'threat', 'ict_index', 
            'expected_goals', 'expected_assists', 'expected_goal_involvements', 'expected_goals_conceded'
        ]
        
        existing_cols = [c for c in cols_to_keep if c in players_df.columns]
        output_df = players_df[existing_cols].copy()
        
        # Convert cost to millions
        if 'now_cost' in output_df.columns:
            output_df['price_m'] = output_df['now_cost'] / 10.0
            
        csv_path = os.path.join(output_dir, "fpl_current_players.csv")
        output_df.to_csv(csv_path, index=False)
        print(f"Successfully saved {len(output_df)} players to '{csv_path}'!")
        
        return output_df
    except Exception as e:
        print(f"Error fetching FPL player data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_fpl_player_data()
    if not df.empty:
        print(df[['web_name', 'team_name', 'position', 'goals_scored', 'assists', 'expected_goals']].head(10))
