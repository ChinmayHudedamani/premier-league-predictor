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

FORMATION_LAYOUT_433 = [
  {'role': 'GK', 'x': 50, 'y': 88},
  {'role': 'LB', 'x': 18, 'y': 70},
  {'role': 'CB', 'x': 38, 'y': 74},
  {'role': 'CB', 'x': 62, 'y': 74},
  {'role': 'RB', 'x': 82, 'y': 70},
  {'role': 'CM', 'x': 32, 'y': 48},
  {'role': 'CDM', 'x': 50, 'y': 54},
  {'role': 'CM', 'x': 68, 'y': 48},
  {'role': 'LW', 'x': 22, 'y': 24},
  {'role': 'ST', 'x': 50, 'y': 18},
  {'role': 'RW', 'x': 78, 'y': 24}
]

def main():
    print("==================================================================")
    print(" COMPILING ENHANCED PREMIER LEAGUE 2026-27 SQUAD & EA FC27 DATA")
    print("==================================================================\n")
    
    # 1. Ingest matches & calculate Elo
    source_dir = r"C:\data\premier league" if os.path.exists(r"C:\data\premier league") else "data"
    cleaned_df, _ = process_and_clean_matches(source_dir)
    df_elo, final_elo = calculate_elo_ratings(cleaned_df)
    
    # 2. Fit Dixon-Coles Poisson Model
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
        
    # 4. Player Analytics & Squad Details
    pots_data = []
    boot_data = []
    synergy_data = []
    darkhorse_data = []
    transfer_data = []
    owner_data = []
    team_squads_dict = {}
    
    fpl_path = "data/player_data/fpl_current_players.csv"
    if os.path.exists(fpl_path):
        df_p = pd.read_csv(fpl_path)
        
        # Calculate FIFA FC27 Predicted OVR Rating (72-91 range)
        numeric_cols = ['expected_goals', 'expected_assists', 'goals_scored', 'assists', 'ict_index', 'price_m', 'form', 'threat', 'creativity']
        for c in numeric_cols:
            if c in df_p.columns:
                df_p[c] = pd.to_numeric(df_p[c], errors='coerce').fillna(0.0)
                
        df_p['fifa_ovr'] = np.clip(
            np.round(74.0 + (df_p['price_m'] * 1.3) + (df_p['ict_index'] / 18.0) + (df_p['form'] * 0.5)),
            70, 92
        ).astype(int)
        
        pots_df, boot_df = predict_player_of_the_season(df_p, team_title_probs=sim_df)
        p_skills, t_synergy = calculate_player_skills_and_synergy(df_p)
        darkhorses = scout_darkhorses_and_emerging_talents(df_p)
        val_salaries, owner_actions = predict_market_valuation_and_salary(df_p)
        
        pots_data = pots_df.head(25)[['web_name', 'team_name', 'position', 'pots_score', 'expected_goals', 'expected_assists', 'form', 'fifa_ovr']].to_dict(orient='records')
        boot_data = boot_df.head(20)[['web_name', 'team_name', 'position', 'goals_scored', 'expected_goals', 'golden_boot_score', 'fifa_ovr']].to_dict(orient='records')
        synergy_data = t_synergy.to_dict(orient='records')
        darkhorse_data = darkhorses.head(20)[['web_name', 'team_name', 'position', 'price_m', 'darkhorse_potential_score', 'form', 'fifa_ovr']].to_dict(orient='records')
        transfer_data = val_salaries.head(25)[['web_name', 'team_name', 'position', 'predicted_market_value_eur_m', 'predicted_weekly_salary_k', 'fifa_ovr']].to_dict(orient='records')
        owner_data = owner_actions.to_dict(orient='records')
        
        # Build Squad & FIFA Tactical Formation Details per Team
        for t_name in current_20_teams:
            t_players = df_p[df_p['team_name'] == t_name].sort_values('fifa_ovr', ascending=False).reset_index(drop=True)
            if len(t_players) == 0:
                continue
                
            squad_list = t_players[['web_name', 'position', 'price_m', 'form', 'expected_goals', 'expected_assists', 'fifa_ovr']].to_dict(orient='records')
            best_player = squad_list[0] if len(squad_list) > 0 else None
            
            # Select Starting 11 players for 4-3-3 formation
            gks = [p for p in squad_list if p['position'] == 'Goalkeeper']
            defs = [p for p in squad_list if p['position'] == 'Defender']
            mids = [p for p in squad_list if p['position'] == 'Midfielder']
            fwds = [p for p in squad_list if p['position'] == 'Forward']
            
            starting_11 = []
            selected_names = set()
            
            # Add 1 GK, 4 DEF, 3 MID, 3 FWD (or fallback to top OVR)
            pool = gks[:1] + defs[:4] + mids[:3] + fwds[:3]
            for p in pool:
                if p['web_name'] not in selected_names:
                    starting_11.append(p)
                    selected_names.add(p['web_name'])
                    
            # Fill remaining slots up to 11 if needed
            for p in squad_list:
                if len(starting_11) >= 11:
                    break
                if p['web_name'] not in selected_names:
                    starting_11.append(p)
                    selected_names.add(p['web_name'])
                    
            # Assign Pitch Coordinates (x, y) & Tactical Roles
            tactical_pitch_11 = []
            for i, p in enumerate(starting_11[:11]):
                layout = FORMATION_LAYOUT_433[i]
                tactical_pitch_11.append({
                    'web_name': p['web_name'],
                    'position': p['position'],
                    'fifa_ovr': p['fifa_ovr'],
                    'role': layout['role'],
                    'x': layout['x'],
                    'y': layout['y']
                })
                
            team_squads_dict[t_name] = {
                'team': t_name,
                'squad_size': len(squad_list),
                'best_player': best_player,
                'avg_squad_ovr': round(np.mean([p['fifa_ovr'] for p in squad_list]), 1),
                'squad': squad_list,
                'tactical_formation_11': tactical_pitch_11
            }

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
        'owners': owner_data,
        'team_squads': team_squads_dict
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/ui_data.json", "w", encoding="utf-8") as f:
        json.dump(ui_package, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Successfully compiled data/ui_data.json ({len(ui_package['teams'])} teams, {len(pots_data)} POTS candidates, {len(team_squads_dict)} team squads & FIFA formations).")

if __name__ == "__main__":
    main()
