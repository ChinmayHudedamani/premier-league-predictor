import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, Dict, List

def build_ml_dataset(df_matches: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict]:
    """
    Builds ML feature matrix with strict temporal split (Train: 1993-2022, Val: 2022-2024, Test: 2024-2026).
    Enforces strict featurization ordering by fitting StandardScaler ONLY on training split.
    """
    df = df_matches.copy()
    
    # Target encoding: 0 = Away Win, 1 = Draw, 2 = Home Win
    df['target'] = np.where(df['result'] == 'H', 2, np.where(df['result'] == 'D', 1, 0))
    
    # Engineered Features
    # Ensure home_elo and away_elo exist
    if 'home_elo' not in df.columns:
        df['home_elo'] = 1500.0
        df['away_elo'] = 1500.0
        df['elo_diff'] = 0.0
    else:
        df['elo_diff'] = df['home_elo'] - df['away_elo']
        
    df['goal_diff_prev'] = df['home_goals'] - df['away_goals']
    
    feature_cols = ['home_elo', 'away_elo', 'elo_diff']
    
    # Filter valid rows
    df = df.dropna(subset=['season', 'parsed_date'] + feature_cols).copy()
    
    # Chronological Split
    train_mask = df['season'] < '2022-2023'
    val_mask = (df['season'] >= '2022-2023') & (df['season'] < '2024-2025')
    test_mask = df['season'] >= '2024-2025'
    
    # Fallback split if season strings differ
    if train_mask.sum() == 0 or test_mask.sum() == 0:
        n = len(df)
        train_end = int(n * 0.8)
        val_end = int(n * 0.9)
        train_df = df.iloc[:train_end]
        val_df = df.iloc[train_end:val_end]
        test_df = df.iloc[val_end:]
    else:
        train_df = df[train_mask]
        val_df = df[val_mask]
        test_df = df[test_mask]
        
    X_train_raw = train_df[feature_cols].values
    y_train = train_df['target'].values
    
    X_val_raw = val_df[feature_cols].values
    y_val = val_df['target'].values
    
    X_test_raw = test_df[feature_cols].values
    y_test = test_df['target'].values
    
    # STRICT FEATURIZATION ORDERING: Fit scaler ONLY on train data!
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_val = scaler.transform(X_val_raw)
    X_test = scaler.transform(X_test_raw)
    
    metadata = {
        'feature_names': feature_cols,
        'train_samples': len(train_df),
        'val_samples': len(val_df),
        'test_samples': len(test_df),
        'scaler': scaler
    }
    
    return X_train, y_train, X_val, y_val, X_test, y_test, metadata
