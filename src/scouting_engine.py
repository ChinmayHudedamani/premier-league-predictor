import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def scout_darkhorses_and_emerging_talents(players_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies darkhorses, breakout prospects, and under-the-radar talents.
    Criteria: High underlying expected goal involvement per 90 (xGI/90), high ICT Threat, 
    and reasonable price valuation (< £8.5m in FPL terms or non-traditional powerhouse teams).
    """
    df = players_df.copy()
    
    numeric_cols = ['expected_goals', 'expected_assists', 'minutes', 'ict_index', 'threat', 'creativity', 'form', 'price_m']
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
            
    df['ninety_mins'] = np.maximum(df['minutes'] / 90.0, 1.0)
    df['xGI_per_90'] = (df['expected_goals'] + df['expected_assists']) / df['ninety_mins']
    
    # Exclude ultra-expensive established superstars (> £9m) to isolate darkhorses & breakout prospects
    darkhorse_candidates = df[(df['price_m'] <= 9.0)].copy()
    
    # Calculate Darkhorse Index
    darkhorse_candidates['darkhorse_potential_score'] = round(
        (0.40 * darkhorse_candidates['xGI_per_90'] * 20.0) +
        (0.30 * (darkhorse_candidates['threat'] / darkhorse_candidates['ninety_mins'])) +
        (0.20 * darkhorse_candidates['form'] * 2.0) +
        (0.10 * (10.0 - darkhorse_candidates['price_m'])),
        2
    )
    
    scouted_df = darkhorse_candidates.sort_values('darkhorse_potential_score', ascending=False).reset_index(drop=True)
    return scouted_df
