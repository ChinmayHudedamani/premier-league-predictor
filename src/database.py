import os
import json
import sqlite3
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
from scipy.stats import poisson

DB_PATH = "data/predictions.db"

class PredictionDatabase:
    """
    Dedicated SQLite Database Manager for Premier League 2026-27 Predictions.
    Stores and maps all 380 pairwise match fixture predictions for Leg 1 (Home) & Leg 2 (Away),
    Aggregate winners, Team Standings, Squad Rosters, and AI Self-Improvisation logs.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Matches 2-Leg Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches_2leg (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    leg1_home_win_pct REAL,
                    leg1_draw_pct REAL,
                    leg1_away_win_pct REAL,
                    leg1_home_xg REAL,
                    leg1_away_xg REAL,
                    leg1_home_poss INTEGER,
                    leg1_away_poss INTEGER,
                    leg1_scoreline TEXT,
                    leg2_home_win_pct REAL,
                    leg2_draw_pct REAL,
                    leg2_away_win_pct REAL,
                    leg2_home_xg REAL,
                    leg2_away_xg REAL,
                    leg2_home_poss INTEGER,
                    leg2_away_poss INTEGER,
                    leg2_scoreline TEXT,
                    aggregate_winner TEXT,
                    aggregate_scoreline TEXT,
                    UNIQUE(home_team, away_team)
                )
            """)
            
            # 2. Team Standings Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_standings (
                    rank INTEGER PRIMARY KEY,
                    team TEXT UNIQUE,
                    title_win_pct REAL,
                    top4_pct REAL,
                    relegation_pct REAL,
                    avg_points REAL,
                    elo REAL,
                    attack_rating REAL,
                    defence_rating REAL
                )
            """)
            
            # 3. AI Improvisation Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS improvisation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    improvisation_score_pct REAL,
                    precision_gain_pct REAL,
                    recommendations_json TEXT
                )
            """)
            
            conn.commit()

    def populate_database_from_ui_json(self, ui_json_path: str = "data/ui_data.json"):
        if not os.path.exists(ui_json_path):
            print(f"[Warning] {ui_json_path} not found. Run export_ui_data.py first.")
            return

        with open(ui_json_path, "r", encoding="utf-8") as f:
            ui_data = json.load(f)

        teams = ui_data.get("teams", [])
        team_stats = ui_data.get("team_stats", {})
        standings = ui_data.get("standings", [])
        home_adv = ui_data.get("home_advantage", 1.35)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Populate Standings
            cursor.execute("DELETE FROM team_standings")
            for idx, s in enumerate(standings):
                t_name = s["team"]
                ts = team_stats.get(t_name, {})
                cursor.execute("""
                    INSERT OR REPLACE INTO team_standings 
                    (rank, team, title_win_pct, top4_pct, relegation_pct, avg_points, elo, attack_rating, defence_rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    idx + 1, t_name, s["title_win_prob_%"], s["top4_prob_%"], s["relegation_prob_%"],
                    s["avg_projected_points"], ts.get("elo", 1600.0), ts.get("attack_rating", 1.0), ts.get("defence_rating", 1.0)
                ))

            # Populate 2-Leg Pairwise Match Predictions
            cursor.execute("DELETE FROM matches_2leg")
            
            max_goals = 7
            for i, t1 in enumerate(teams):
                for j, t2 in enumerate(teams):
                    if t1 == t2:
                        continue
                    
                    # Leg 1: t1 at Home vs t2
                    t1_stats = team_stats.get(t1, {"elo": 1600, "attack_rating": 1.0, "defence_rating": 1.0})
                    t2_stats = team_stats.get(t2, {"elo": 1600, "attack_rating": 1.0, "defence_rating": 1.0})
                    
                    l1_h_xg = max(0.2, t1_stats["attack_rating"] * t2_stats["defence_rating"] * home_adv)
                    l1_a_xg = max(0.2, t2_stats["attack_rating"] * t1_stats["defence_rating"] * 1.05)
                    
                    l1_h_probs = [poisson.pmf(g, l1_h_xg) for g in range(max_goals)]
                    l1_a_probs = [poisson.pmf(g, l1_a_xg) for g in range(max_goals)]
                    
                    p_h1, p_d1, p_a1 = 0, 0, 0
                    max_p1, l1_hg, l1_ag = -1, 0, 0
                    for h in range(max_goals):
                        for a in range(max_goals):
                            p = l1_h_probs[h] * l1_a_probs[a]
                            if h > a: p_h1 += p
                            elif h == a: p_d1 += p
                            else: p_a1 += p
                            if p > max_p1: max_p1, l1_hg, l1_ag = p, h, a
                            
                    sum1 = p_h1 + p_d1 + p_a1
                    l1_hw_pct = round((p_h1 / sum1) * 100, 1)
                    l1_d_pct = round((p_d1 / sum1) * 100, 1)
                    l1_aw_pct = round((p_a1 / sum1) * 100, 1)
                    
                    e1_h_pow = math_pow(t1_stats["elo"], 1.25)
                    e1_a_pow = math_pow(t2_stats["elo"], 1.25)
                    l1_h_poss = int(round((e1_h_pow / (e1_h_pow + e1_a_pow)) * 100))
                    l1_a_poss = 100 - l1_h_poss
                    
                    # Leg 2: t2 at Home vs t1
                    l2_h_xg = max(0.2, t2_stats["attack_rating"] * t1_stats["defence_rating"] * home_adv)
                    l2_a_xg = max(0.2, t1_stats["attack_rating"] * t2_stats["defence_rating"] * 1.05)
                    
                    l2_h_probs = [poisson.pmf(g, l2_h_xg) for g in range(max_goals)]
                    l2_a_probs = [poisson.pmf(g, l2_a_xg) for g in range(max_goals)]
                    
                    p_h2, p_d2, p_a2 = 0, 0, 0
                    max_p2, l2_hg, l2_ag = -1, 0, 0
                    for h in range(max_goals):
                        for a in range(max_goals):
                            p = l2_h_probs[h] * l2_a_probs[a]
                            if h > a: p_h2 += p
                            elif h == a: p_d2 += p
                            else: p_a2 += p
                            if p > max_p2: max_p2, l2_hg, l2_ag = p, h, a
                            
                    sum2 = p_h2 + p_d2 + p_a2
                    l2_hw_pct = round((p_h2 / sum2) * 100, 1)
                    l2_d_pct = round((p_d2 / sum2) * 100, 1)
                    l2_aw_pct = round((p_a2 / sum2) * 100, 1)
                    
                    l2_h_poss = int(round((e1_a_pow / (e1_h_pow + e1_a_pow)) * 100))
                    l2_a_poss = 100 - l2_h_poss
                    
                    # Aggregate 2-Leg Calculations
                    t1_total_goals = l1_hg + l2_ag
                    t2_total_goals = l1_ag + l2_hg
                    
                    if t1_total_goals > t2_total_goals:
                        agg_winner = t1
                    elif t2_total_goals > t1_total_goals:
                        agg_winner = t2
                    else:
                        agg_winner = "Tie (Penalties)"
                        
                    agg_scoreline = f"{t1} {t1_total_goals} - {t2_total_goals} {t2}"
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO matches_2leg
                        (home_team, away_team, 
                         leg1_home_win_pct, leg1_draw_pct, leg1_away_win_pct, leg1_home_xg, leg1_away_xg, leg1_home_poss, leg1_away_poss, leg1_scoreline,
                         leg2_home_win_pct, leg2_draw_pct, leg2_away_win_pct, leg2_home_xg, leg2_away_xg, leg2_home_poss, leg2_away_poss, leg2_scoreline,
                         aggregate_winner, aggregate_scoreline)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        t1, t2,
                        l1_hw_pct, l1_d_pct, l1_aw_pct, round(l1_h_xg, 2), round(l1_a_xg, 2), l1_h_poss, l1_a_poss, f"{l1_hg} - {l1_ag}",
                        l2_hw_pct, l2_d_pct, l2_aw_pct, round(l2_h_xg, 2), round(l2_a_xg, 2), l2_h_poss, l2_a_poss, f"{l2_hg} - {l2_ag}",
                        agg_winner, agg_scoreline
                    ))
                    
            conn.commit()
            print(f"[OK] Successfully populated SQLite database '{self.db_path}' with {len(teams)*19} 2-Leg match predictions.")

    def get_2leg_prediction(self, home_team: str, away_team: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM matches_2leg WHERE home_team = ? AND away_team = ?", (home_team, away_team))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

def math_pow(val, p):
    return pow(float(val), float(p))

if __name__ == "__main__":
    db = PredictionDatabase()
    db.populate_database_from_ui_json()
    pred = db.get_2leg_prediction("Arsenal", "Manchester City")
    if pred:
        print("2-Leg Match Prediction Test (Arsenal vs Manchester City):")
        print(f"  Leg 1 (Arsenal Home): Win {pred['leg1_home_win_pct']}% | xG {pred['leg1_home_xg']} - {pred['leg1_away_xg']} | Score {pred['leg1_scoreline']}")
        print(f"  Leg 2 (Man City Home): Win {pred['leg2_home_win_pct']}% | xG {pred['leg2_home_xg']} - {pred['leg2_away_xg']} | Score {pred['leg2_scoreline']}")
        print(f"  [OK] Aggregate Winner: {pred['aggregate_winner']} ({pred['aggregate_scoreline']})")
