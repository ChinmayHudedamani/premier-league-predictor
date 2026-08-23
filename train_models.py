import os
import json
import pandas as pd
import numpy as np

from src.data_processing import process_and_clean_matches
from src.feature_engineering import calculate_elo_ratings, calculate_rolling_form
from src.dataset_builder import build_ml_dataset
from src.synergy_engine import calculate_player_skills_and_synergy
from src.scouting_engine import scout_darkhorses_and_emerging_talents
from src.transfer_owner_engine import predict_market_valuation_and_salary

from src.models.xgboost_model import XGBoostMatchClassifier
from src.models.svm_model import SVMMatchClassifier
from src.models.dnn_model import DNNMatchClassifier
from src.models.tabnet_model import TabNetEnsembleClassifier

def main():
    print("==================================================================")
    print(" 4-MODEL PREMIER LEAGUE & TRANSFER INTELLIGENCE SUITE (1993-2026)")
    print("==================================================================\n")
    
    # 1. Ingest & Deduplicate Match Data
    source_dir = r"C:\data\premier league" if os.path.exists(r"C:\data\premier league") else "data"
    print(f"--> Step 1: Processing Match Dataset from {source_dir}...")
    cleaned_df, health_report = process_and_clean_matches(source_dir)
    cleaned_df.to_csv("data/cleaned_matches.csv", index=False)
    print(f"    [OK] Ingested & Deduplicated: {health_report['final_clean_rows']} matches across {health_report['seasons_covered_count']} seasons.")
    
    # 2. Historical Elo & Feature Building
    print("\n--> Step 2: Calculating Historical Elo & Temporal Features...")
    df_elo, final_elo = calculate_elo_ratings(cleaned_df)
    
    # 3. Build Train / Validation / Test Datasets
    print("\n--> Step 3: Enforcing Strict Featurization Ordering & Temporal Splits...")
    X_train, y_train, X_val, y_val, X_test, y_test, metadata = build_ml_dataset(df_elo)
    print(f"    [OK] Train samples: {metadata['train_samples']} | Val samples: {metadata['val_samples']} | Test samples: {metadata['test_samples']}")
    
    # 4. Train & Benchmarking 4 ML / Deep Learning Models
    print("\n--> Step 4: Training & Evaluating 4 Advanced ML/DL Models...")
    
    models = {
        'XGBoost': XGBoostMatchClassifier(),
        'SVM_RBF': SVMMatchClassifier(),
        'DNN_MLP': DNNMatchClassifier(),
        'TabNet_Ensemble': TabNetEnsembleClassifier()
    }
    
    metrics_summary = []
    
    for name, model_obj in models.items():
        print(f"    Training {name}...")
        model_obj.fit(X_train, y_train)
        eval_metrics = model_obj.evaluate(X_test, y_test)
        metrics_summary.append(eval_metrics)
        print(f"      -> {eval_metrics['model_name']}: Accuracy = {eval_metrics['accuracy']}, Log Loss = {eval_metrics['log_loss']}, F1 Macro = {eval_metrics['f1_macro']}")
        
    metrics_df = pd.DataFrame(metrics_summary).sort_values('accuracy', ascending=False).reset_index(drop=True)
    
    print("\n==================================================================")
    print(" 4-MODEL PREDICTION BENCHMARK COMPARISON TABLE")
    print("==================================================================")
    print(metrics_df.to_string(index=False))
    
    with open("data/model_comparison_metrics.json", "w") as f:
        json.dump(metrics_summary, f, indent=4)
        
    # 5. Synergy, Darkhorses, Transfer Valuation & Owner Action Execution
    fpl_path = "data/player_data/fpl_current_players.csv"
    if os.path.exists(fpl_path):
        print("\n--> Step 5: Executing Synergy, Darkhorse Scouting & Transfer Market Models...")
        df_p = pd.read_csv(fpl_path)
        
        p_skills, t_synergy = calculate_player_skills_and_synergy(df_p)
        darkhorses = scout_darkhorses_and_emerging_talents(df_p)
        val_salaries, owner_actions = predict_market_valuation_and_salary(df_p)
        
        p_skills.head(20).to_csv("data/player_skill_ratings.csv", index=False)
        t_synergy.to_csv("data/team_synergy_scores.csv", index=False)
        darkhorses.head(20).to_csv("data/darkhorse_scouting_report.csv", index=False)
        val_salaries.head(20).to_csv("data/transfer_salary_predictions.csv", index=False)
        owner_actions.to_csv("data/owner_strategy_predictions.csv", index=False)
        
        print("\n==================================================================")
        print(" TOP 5 SCOUTED DARKHORSES & EMERGING TALENTS")
        print("==================================================================")
        print(darkhorses[['web_name', 'team_name', 'position', 'price_m', 'xGI_per_90', 'darkhorse_potential_score']].head(5).to_string(index=False))
        
        print("\n==================================================================")
        print(" TOP 5 PREDICTED HIGHEST TRANSFER VALUATIONS & SALARIES")
        print("==================================================================")
        print(val_salaries[['web_name', 'team_name', 'position', 'predicted_market_value_eur_m', 'predicted_weekly_salary_k']].head(5).to_string(index=False))
        
        print("\n==================================================================")
        print(" CLUB OWNER BEHAVIORAL & STRATEGY PREDICTIONS")
        print("==================================================================")
        print(owner_actions[['team_name', 'owner_group', 'avg_window_budget_m', 'wage_policy']].head(5).to_string(index=False))
        
    print("\n[OK] All 4 ML Models, Synergy Networks, Darkhorse Scouting Reports & Owner Action Predictions executed cleanly!")

if __name__ == "__main__":
    main()
