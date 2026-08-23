import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import accuracy_score
from typing import Dict, List, Tuple

def run_monte_carlo_feature_optimizer(X_train: np.ndarray, y_train: np.ndarray, feature_names: List[str], num_simulations: int = 50) -> Tuple[List[str], Dict]:
    """
    Ultra-Fast Vectorized Monte Carlo Feature Combination Search across N simulations.
    Evaluates random feature subsets to select the optimal feature subset maximizing Accuracy.
    """
    n_features = len(feature_names)
    best_acc = 0.0
    best_subset_indices = list(range(n_features))
    
    print(f"Executing Monte Carlo Feature Combination Search across {num_simulations} iterations for {n_features} candidate features...")
    
    # Subsample for ultra-fast simulation speed
    sub_sample_size = min(len(X_train), 2000)
    indices_sub = np.random.choice(len(X_train), size=sub_sample_size, replace=False)
    X_sub_full = X_train[indices_sub]
    y_sub_full = y_train[indices_sub]
    
    n_train = int(len(X_sub_full) * 0.8)
    X_tr, y_tr = X_sub_full[:n_train], y_sub_full[:n_train]
    X_va, y_va = X_sub_full[n_train:], y_sub_full[n_train:]
    
    for sim in range(num_simulations):
        k = np.random.randint(1, n_features + 1)
        sub_indices = sorted(list(np.random.choice(n_features, size=k, replace=False)))
        
        clf = RidgeClassifier(alpha=1.0, random_state=42)
        clf.fit(X_tr[:, sub_indices], y_tr)
        
        preds = clf.predict(X_va[:, sub_indices])
        acc = accuracy_score(y_va, preds)
        
        if acc > best_acc:
            best_acc = acc
            best_subset_indices = sub_indices
            
    best_feature_names = [feature_names[i] for i in best_subset_indices]
    
    summary = {
        'best_oof_accuracy': round(best_acc, 4),
        'selected_features_count': len(best_feature_names),
        'selected_feature_names': best_feature_names
    }
    
    print(f"  [Optimizer Result] Best Feature Accuracy: {summary['best_oof_accuracy']} | Features Selected: {summary['selected_features_count']}/{n_features}")
    return best_feature_names, summary
