import os
import json
import pandas as pd
import numpy as np

from src.data_processing import process_and_clean_matches
from src.feature_engineering import calculate_elo_ratings, calculate_rolling_form
from src.winner_model import DixonColesModel, simulate_season
from src.player_model import predict_player_of_the_season

def main():
    print("==================================================================")
    print(" PREMIER LEAGUE WINNER & BEST PLAYER PREDICTION ENGINE (1993-2026)")
    print("==================================================================\n")
    
    # 1. Ingest & Clean Match Data
    source_dir = r"C:\data\premier league" if os.path.exists(r"C:\data\premier league") else "data"
    print(f"--> Step 1: Processing & Deduplicating Match Dataset from {source_dir}...")
    
    cleaned_df, health_report = process_and_clean_matches(source_dir)
    cleaned_df.to_csv("data/cleaned_matches.csv", index=False)
    
    print(f"    [OK] Loaded {health_report['initial_rows']} raw records.")
    print(f"    [OK] Deduplicated & Cleaned: {health_report['final_clean_rows']} unique matches across {health_report['seasons_covered_count']} seasons.")
    
    if health_report['season_anomalies_or_missing']:
        print("\n    [Audit Notice] Missing / Anomalous Matches per Season:")
        for s, info in sorted(health_report['season_anomalies_or_missing'].items()):
            diff_text = f"Missing {info['missing_matches']} matches" if info['missing_matches'] > 0 else f"Extra {-info['missing_matches']} matches"
            print(f"      - Season {s}: {info['found']}/{info['expected']} matches ({diff_text})")
    else:
        print("    [Audit OK] 100% complete match coverage across all seasons!")
        
    # 2. Feature Engineering & Elo Calculation
    print("\n--> Step 2: Calculating Historical Elo Ratings & Rolling Team Form...")
    df_elo, final_elo = calculate_elo_ratings(cleaned_df)
    
    print("    [OK] Top 6 Current Team Elo Ratings:")
    sorted_elo = sorted(final_elo.items(), key=lambda x: x[1], reverse=True)
    for team, elo in sorted_elo[:6]:
        print(f"      - {team:22s}: {elo:.1f} Elo")
        
    # 3. Train Match Model & Run Monte Carlo 10,000 Season Simulator
    print("\n--> Step 3: Training Dixon-Coles Poisson Model & Running 10,000 Season Simulations...")
    
    # Train model on recent 3 seasons of historical matches for optimal form calibration
    recent_matches = df_elo.tail(1140).copy()
    model = DixonColesModel()
    model.fit(recent_matches)
    
    # Current Premier League 20 Teams
    current_20_teams = [
        'Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Tottenham Hotspur',
        'Manchester United', 'Newcastle United', 'Aston Villa', 'Brighton & Hove Albion',
        'West Ham United', 'AFC Bournemouth', 'Brentford', 'Fulham', 'Wolverhampton Wanderers',
        'Everton', 'Crystal Palace', 'Nottingham Forest', 'Leicester City', 'Ipswich Town', 'Southampton'
    ]
    
    sim_df = simulate_season(current_20_teams, model, num_simulations=10000)
    
    print("\n==================================================================")
    print(" PREMIER LEAGUE TITLE WINNER PREDICTIONS (10,000 SIMULATIONS)")
    print("==================================================================")
    print(sim_df[['team', 'title_win_prob_%', 'top4_prob_%', 'relegation_prob_%', 'avg_projected_points']].to_string(index=False))
    
    # Save winner predictions
    sim_df.to_csv("data/winner_predictions.csv", index=False)
    
    # 4. Player of the Season & Golden Boot Prediction
    print("\n--> Step 4: Predicting Best Player of the Season & Golden Boot...")
    fpl_path = "data/player_data/fpl_current_players.csv"
    
    if os.path.exists(fpl_path):
        players_df = pd.read_csv(fpl_path)
        pots_df, boot_df = predict_player_of_the_season(players_df, team_title_probs=sim_df)
        
        print("\n==================================================================")
        print(" TOP 10 CANDIDATES: PREMIER LEAGUE PLAYER OF THE SEASON (POTS)")
        print("==================================================================")
        print(pots_df[['web_name', 'team_name', 'position', 'pots_score', 'expected_goals', 'expected_assists', 'form']].head(10).to_string(index=False))
        
        print("\n==================================================================")
        print(" TOP 10 CANDIDATES: GOLDEN BOOT (TOP GOALSCORER)")
        print("==================================================================")
        print(boot_df[['web_name', 'team_name', 'position', 'goals_scored', 'expected_goals', 'golden_boot_score']].head(10).to_string(index=False))
        
        pots_df.head(20).to_csv("data/player_of_season_predictions.csv", index=False)
        boot_df.head(20).to_csv("data/golden_boot_predictions.csv", index=False)
    else:
        print("    [Notice] Player data file not found. Run player_data_fetcher.py first.")

if __name__ == "__main__":
    main()
