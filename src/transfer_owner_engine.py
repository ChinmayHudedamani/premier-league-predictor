import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

# Comprehensive Owner Strategic Behavioral Profiles
OWNER_PROFILES = {
    'Chelsea': {
        'owner': 'Boehly / Clearlake Capital',
        'investment_archetype': 'Aggressive High-Volume Youth Acquisition',
        'avg_window_spend_m': 250.0,
        'contract_length_strategy': 'Long-Term (7-8 Years)',
        'wage_structure_policy': 'Incentive & Performance Heavy',
        'predictive_action': 'Targeting under-23 talents with multi-year amortization, aggressive winter & summer market activity.'
    },
    'Manchester City': {
        'owner': 'City Football Group (Sheikh Mansour)',
        'investment_archetype': 'Surgical High-Value Precision & Global Multi-Club Synergy',
        'avg_window_spend_m': 180.0,
        'contract_length_strategy': 'Standard Elite (5 Years)',
        'wage_structure_policy': 'Top Tier Premium',
        'predictive_action': 'Opportunistic elite signings, key positional upgrades, immediate squad depth reinforcement.'
    },
    'Liverpool': {
        'owner': 'Fenway Sports Group (John W. Henry)',
        'investment_archetype': 'Strict Data-Driven Moneyball & Financial Self-Sustainability',
        'avg_window_spend_m': 90.0,
        'contract_length_strategy': 'Balanced (4-5 Years)',
        'wage_structure_policy': 'Disciplined Wage Cap with Renewal Priority',
        'predictive_action': 'Targeting high-underlying-metric undervalued targets, selling before buying high.'
    },
    'Newcastle United': {
        'owner': 'Public Investment Fund (PIF)',
        'investment_archetype': 'PSR-Constrained Strategic Ambitious Escalation',
        'avg_window_spend_m': 120.0,
        'contract_length_strategy': 'Standard (5 Years)',
        'wage_structure_policy': 'Progressive Top Tier Expansion',
        'predictive_action': 'High-impact starters fitting PSR limits, expanding commercial sponsorship revenue to unlock cap.'
    },
    'Manchester United': {
        'owner': 'Sir Jim Ratcliffe / INEOS & Glazers',
        'investment_archetype': 'Operational Restructuring & Tactical Value Purchasing',
        'avg_window_spend_m': 150.0,
        'contract_length_strategy': 'Standard (5 Years + 1 Year Option)',
        'wage_structure_policy': 'Wage Bill Reduction & Incentive Alignment',
        'predictive_action': 'Trimming high-earner wage bloat, investing in young domestic & European talents.'
    },
    'Tottenham Hotspur': {
        'owner': 'ENIC Group (Daniel Levy / Joe Lewis Trust)',
        'investment_archetype': 'Infrastructure First & High-Resale Prospect Trading',
        'avg_window_spend_m': 85.0,
        'contract_length_strategy': 'Long-Term (5-6 Years)',
        'wage_structure_policy': 'Strict Internal Wage Cap Structure',
        'predictive_action': 'Buying under-22 high-potential talents, tight negotiation on sell-on clauses.'
    },
    'Arsenal': {
        'owner': 'Kroenke Sports & Entertainment (Stan Kroenke)',
        'investment_archetype': 'Targeted Elite System Alignment',
        'avg_window_spend_m': 140.0,
        'contract_length_strategy': 'Standard (5 Years)',
        'wage_structure_policy': 'Competitive Top Tier',
        'predictive_action': 'Backing manager with prime-age versatile international stars.'
    },
    'Aston Villa': {
        'owner': 'V Sports (Nassef Sawiris & Wes Edens)',
        'investment_archetype': 'European Expansion Heavy Investment',
        'avg_window_spend_m': 100.0,
        'contract_length_strategy': 'Standard (5 Years)',
        'wage_structure_policy': 'Aggressive Growth Wage',
        'predictive_action': 'Champions League tier recruitment, balancing PSR compliance.'
    }
}

def predict_market_valuation_and_salary(players_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Predicts estimated transfer market valuations (€M) and weekly salary demands (£k/week)
    based on expected metrics, positional premiums, team strength, and performance form.
    """
    df = players_df.copy()
    
    numeric_cols = ['expected_goals', 'expected_assists', 'goals_scored', 'assists', 'ict_index', 'minutes', 'price_m', 'form']
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
            
    mins = np.maximum(df['minutes'], 90.0)
    ninety_mins = mins / 90.0
    xGI_90 = (df['expected_goals'] + df['expected_assists']) / ninety_mins
    
    # Position Multiplier (Forwards & Attackers command higher transfer market fees)
    pos_multiplier = df['position'].map({'Forward': 1.4, 'Midfielder': 1.25, 'Defender': 1.0, 'Goalkeeper': 0.85}).fillna(1.0)
    
    # Base estimated transfer valuation (€M)
    df['predicted_market_value_eur_m'] = round(
        (df['price_m'] * 4.5 * pos_multiplier) + 
        (xGI_90 * 25.0) + 
        (df['ict_index'] / 3.0), 
        1
    )
    
    # Base estimated weekly wage (£k / week)
    df['predicted_weekly_salary_k'] = round(
        (df['predicted_market_value_eur_m'] * 2.2) + 
        (df['form'] * 8.0) + 
        (df['goals_scored'] * 4.0), 
        0
    )
    
    val_ranking = df.sort_values('predicted_market_value_eur_m', ascending=False).reset_index(drop=True)
    
    # Generate Owner Action Predictions Table
    owner_rows = []
    for team, profile in OWNER_PROFILES.items():
        owner_rows.append({
            'team_name': team,
            'owner_group': profile['owner'],
            'investment_archetype': profile['investment_archetype'],
            'avg_window_budget_m': f"£{profile['avg_window_spend_m']}M",
            'wage_policy': profile['wage_structure_policy'],
            'predictive_action_summary': profile['predictive_action']
        })
        
    owner_df = pd.DataFrame(owner_rows)
    return val_ranking, owner_df

if __name__ == "__main__":
    import os
    fpl_path = "data/player_data/fpl_current_players.csv"
    if os.path.exists(fpl_path):
        df_p = pd.read_csv(fpl_path)
        vals, owners = predict_market_valuation_and_salary(df_p)
        print("Top 5 Highest Predicted Market Values & Salaries:")
        print(vals[['web_name', 'team_name', 'position', 'predicted_market_value_eur_m', 'predicted_weekly_salary_k']].head())
        print("\nOwner Behavioral Predictions:")
        print(owners[['team_name', 'owner_group', 'avg_window_budget_m']].head())
