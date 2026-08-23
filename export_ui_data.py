import os
import json
import pandas as pd
import numpy as np

from src.data_processing import process_and_clean_matches
from src.feature_engineering import calculate_elo_ratings
from src.winner_model import DixonColesModel, simulate_season
from src.player_model import predict_player_of_the_season
from src.synergy_engine import calculate_player_skills_and_synergy
from src.scouting_engine import scout_darkhorses_and_emerging_talents
from src.transfer_owner_engine import predict_market_valuation_and_salary

def main():
    print("==================================================================")
    print(" COMPILING PREMIER LEAGUE 2026-27 UI DATA JSON EXPORTER")
    print("==================================================================\n")
    
    # 1. Ingest matches & calculate Elo
    source_dir = r"C:\data\premier league" if os.path.exists(r"C:\data\premier league") else "data"
    cleaned_df, _ = process_and_clean_matches(source_dir)
    df_elo, final_elo = calculate_elo_ratings(cleaned_df)
    
    # 2. Fit Dixon-Coles Poisson Model to extract attack/defence parameters
    recent_matches = df_elo.tail(1140).copy()
    model = DixonColesModel()
    model.fit(recent_matches)
    
    current_20_teams = sorted([
        'Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Tottenham Hotspur',
        'Manchester United', 'Newcastle United', 'Aston Villa', 'Brighton & Hove Albion',
        'West Ham United', 'AFC Bournemouth', 'Brentford', 'Fulham', 'Wolverhampton Wanderers',
        'Everton', 'Crystal Palace', 'Nottingham Forest', 'Leicester City', 'Ipswich Town', 'Southampton'
    ])
    
    # 3. Simulate 10,000 Seasons for Team Standings
    sim_df = simulate_season(current_20_teams, model, num_simulations=10000)
    
    # Format Team Standings & Attack/Defence Strength Dict
    team_stats_dict = {}
    for idx, row in sim_df.iterrows():
        t_name = row['team']
        team_stats_dict[t_name] = {
            'team': t_name,
            'elo': round(final_elo.get(t_name, 1500.0), 1),
            'title_win_prob': float(row['title_win_prob_%']),
            'top4_prob': float(row['top4_prob_%']),
            'relegation_prob': float(row['relegation_prob_%']),
            'avg_projected_points': float(row['avg_projected_points']),
            'attack_rating': round(float(model.attack_params.get(t_name, 1.0)), 3),
            'defence_rating': round(float(model.defence_params.get(t_name, 1.0)), 3)
        }
        
    # 4. Player Analytics & Predictions
    pots_data = []
    boot_data = []
    synergy_data = []
    darkhorse_data = []
    transfer_data = []
    owner_data = []
    
    fpl_path = "data/player_data/fpl_current_players.csv"
    if os.path.exists(fpl_path):
        df_p = pd.read_csv(fpl_path)
        pots_df, boot_df = predict_player_of_the_season(df_p, team_title_probs=sim_df)
        p_skills, t_synergy = calculate_player_skills_and_synergy(df_p)
        darkhorses = scout_darkhorses_and_emerging_talents(df_p)
        val_salaries, owner_actions = predict_market_valuation_and_salary(df_p)
        
        pots_data = pots_df.head(25)[['web_name', 'team_name', 'position', 'pots_score', 'expected_goals', 'expected_assists', 'form']].to_dict(orient='records')
        boot_data = boot_df.head(20)[['web_name', 'team_name', 'position', 'goals_scored', 'expected_goals', 'golden_boot_score']].to_dict(orient='records')
        synergy_data = t_synergy.to_dict(orient='records')
        darkhorse_data = darkhorses.head(20)[['web_name', 'team_name', 'position', 'price_m', 'darkhorse_potential_score', 'form']].to_dict(orient='records')
        transfer_data = val_salaries.head(25)[['web_name', 'team_name', 'position', 'predicted_market_value_eur_m', 'predicted_weekly_salary_k']].to_dict(orient='records')
        owner_data = owner_actions.to_dict(orient='records')
        
    # Build complete JSON package
    ui_package = {
        'teams': current_20_teams,
        'team_stats': team_stats_dict,
        'standings': sim_df.to_dict(orient='records'),
        'home_advantage': 1.35,
        'pots': pots_data,
        'golden_boot': boot_data,
        'team_synergy': synergy_data,
        'darkhorses': darkhorse_data,
        'transfers': transfer_data,
        'owners': owner_data
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/ui_data.json", "w", encoding="utf-8") as f:
        json.dump(ui_package, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Successfully compiled data/ui_data.json ({len(ui_package['teams'])} teams, {len(pots_data)} POTS candidates).")

if __name__ == "__main__":
    main()
