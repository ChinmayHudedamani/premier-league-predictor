import numpy as np
import pandas as pd
from scipy.stats import poisson
from typing import Tuple, Dict, List

class DixonColesModel:
    """
    Dixon-Coles & Poisson Goal Distribution model for predicting football match outcomes and simulating seasons.
    """
    def __init__(self):
        self.attack_params = {}
        self.defence_params = {}

    def fit(self, matches_df: pd.DataFrame):
        """Fits attack and defense parameters for teams based on match history."""
        teams = sorted(list(set(matches_df['home_team']).union(set(matches_df['away_team']))))
        avg_home_goals = matches_df['home_goals'].mean()
        avg_away_goals = matches_df['away_goals'].mean()
        
        for team in teams:
            h_matches = matches_df[matches_df['home_team'] == team]
            a_matches = matches_df[matches_df['away_team'] == team]
            
            h_scored = h_matches['home_goals'].mean() if len(h_matches) > 0 else avg_home_goals
            a_scored = a_matches['away_goals'].mean() if len(a_matches) > 0 else avg_away_goals
            h_conceded = h_matches['away_goals'].mean() if len(h_matches) > 0 else avg_away_goals
            a_conceded = a_matches['home_goals'].mean() if len(a_matches) > 0 else avg_home_goals
            
            self.attack_params[team] = ((h_scored / avg_home_goals) + (a_scored / avg_away_goals)) / 2.0
            self.defence_params[team] = ((h_conceded / avg_away_goals) + (a_conceded / avg_home_goals)) / 2.0
            
    def predict_match_probs(self, home_team: str, away_team: str, max_goals: int = 7) -> Tuple[float, float, float]:
        """Predicts (Home Win %, Draw %, Away Win %) for a specific match."""
        h_att = self.attack_params.get(home_team, 1.0)
        a_def = self.defence_params.get(away_team, 1.0)
        a_att = self.attack_params.get(away_team, 1.0)
        h_def = self.defence_params.get(home_team, 1.0)
        
        lambda_home = max(0.2, h_att * a_def * 1.35)
        lambda_away = max(0.2, a_att * h_def * 1.05)
        
        home_probs = poisson.pmf(np.arange(max_goals), lambda_home)
        away_probs = poisson.pmf(np.arange(max_goals), lambda_away)
        
        joint_matrix = np.outer(home_probs, away_probs)
        
        p_home_win = np.sum(np.tril(joint_matrix, -1))
        p_draw = np.sum(np.diag(joint_matrix))
        p_away_win = np.sum(np.triu(joint_matrix, 1))
        
        total = p_home_win + p_draw + p_away_win
        return p_home_win / total, p_draw / total, p_away_win / total

def simulate_season(teams: List[str], model: DixonColesModel, num_simulations: int = 10000) -> pd.DataFrame:
    """
    Vectorized Fast Monte Carlo simulation of an entire 38-game Premier League season (380 matches) across N runs.
    """
    fixtures = [(h, a) for h in teams for a in teams if h != a]
    n_fixtures = len(fixtures)
    n_teams = len(teams)
    team_map = {t: i for i, t in enumerate(teams)}
    
    # Pre-calculate match outcome probabilities for all 380 fixtures
    probs_matrix = np.zeros((n_fixtures, 3))
    home_indices = np.zeros(n_fixtures, dtype=int)
    away_indices = np.zeros(n_fixtures, dtype=int)
    
    for i, (home, away) in enumerate(fixtures):
        p_h, p_d, p_a = model.predict_match_probs(home, away)
        probs_matrix[i] = [p_h, p_d, p_a]
        home_indices[i] = team_map[home]
        away_indices[i] = team_map[away]
        
    # Generate random choices for all simulations at once (n_fixtures x num_simulations)
    # 0 = Home Win (3 pts home), 1 = Draw (1 pt each), 2 = Away Win (3 pts away)
    cum_probs = np.cumsum(probs_matrix, axis=1) # (380, 3)
    rand_vals = np.random.rand(n_fixtures, num_simulations)
    
    # Outcomes matrix: (380, num_simulations)
    outcomes = (rand_vals[:, :, None] > cum_probs[:, None, :]).sum(axis=2) # 0, 1, or 2
    
    # Calculate points across all simulations
    sim_points = np.zeros((n_teams, num_simulations))
    
    # Home wins
    h_win_mask = (outcomes == 0)
    # Draws
    draw_mask = (outcomes == 1)
    # Away wins
    a_win_mask = (outcomes == 2)
    
    for i in range(n_fixtures):
        h_idx = home_indices[i]
        a_idx = away_indices[i]
        
        sim_points[h_idx] += h_win_mask[i] * 3 + draw_mask[i] * 1
        sim_points[a_idx] += a_win_mask[i] * 3 + draw_mask[i] * 1

    # Ranks across simulations: (n_teams, num_simulations)
    # Rank 0 is highest points
    ranks = np.argsort(np.argsort(-sim_points, axis=0), axis=0)
    
    title_wins = (ranks == 0).sum(axis=1)
    top4_finishes = (ranks < 4).sum(axis=1)
    relegations = (ranks >= (n_teams - 3)).sum(axis=1)
    avg_points = sim_points.mean(axis=1)
    
    summary = []
    for t_idx, team in enumerate(teams):
        summary.append({
            'team': team,
            'title_win_prob_%': round((title_wins[t_idx] / num_simulations) * 100, 2),
            'top4_prob_%': round((top4_finishes[t_idx] / num_simulations) * 100, 2),
            'relegation_prob_%': round((relegations[t_idx] / num_simulations) * 100, 2),
            'avg_projected_points': round(avg_points[t_idx], 1)
        })
        
    return pd.DataFrame(summary).sort_values('title_win_prob_%', ascending=False).reset_index(drop=True)
