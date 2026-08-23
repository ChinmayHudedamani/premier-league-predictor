import os
import json
import pandas as pd
import numpy as np

from src.data_processing import process_and_clean_matches
from src.feature_engineering import calculate_elo_ratings, calculate_rolling_form
from src.dataset_builder import build_ml_dataset
from src.feature_optimizer import run_monte_carlo_feature_optimizer
from src.synergy_engine import calculate_player_skills_and_synergy
from src.scouting_engine import scout_darkhorses_and_emerging_talents
from src.transfer_owner_engine import predict_market_valuation_and_salary

from src.models.xgboost_model import XGBoostMatchClassifier
from src.models.catboost_model import CatBoostMatchClassifier
from src.models.svm_model import SVMMatchClassifier
from src.models.dnn_model import DNNMatchClassifier
from src.models.tabnet_model import TabNetEnsembleClassifier
from src.models.stacking_ensemble import StackingMetaLearnerClassifier

def main():
    print("==================================================================", flush=True)
    print(" ADVANCED STACKING META-LEARNER & FEATURE OPTIMIZATION ENGINE", flush=True)
    print("==================================================================\n", flush=True)
    
    # 1. Ingest & Deduplicate Match Data
    source_dir = r"C:\data\premier league" if os.path.exists(r"C:\data\premier league") else "data"
    print(f"--> Step 1: Ingesting & Deduplicating Match Dataset from {source_dir}...", flush=True)
    cleaned_df, health_report = process_and_clean_matches(source_dir)
    cleaned_df.to_csv("data/cleaned_matches.csv", index=False)
    print(f"    [OK] Ingested & Deduplicated: {health_report['final_clean_rows']} matches across {health_report['seasons_covered_count']} seasons.", flush=True)
    
    # 2. Historical Elo & Feature Interaction Building
    print("\n--> Step 2: Calculating Elo & Cross-Feature Interaction Terms...", flush=True)
    df_elo, final_elo = calculate_elo_ratings(cleaned_df)
    
    # 3. Build Train / Validation / Test Datasets with Strict Featurization Ordering
    print("\n--> Step 3: Enforcing Strict Featurization Ordering & Temporal Splits...", flush=True)
    X_train, y_train, X_val, y_val, X_test, y_test, metadata = build_ml_dataset(df_elo)
    print(f"    [OK] Train samples: {metadata['train_samples']} | Val samples: {metadata['val_samples']} | Test samples: {metadata['test_samples']}", flush=True)
    
    # 4. Monte Carlo Feature Combination Optimization
    print("\n--> Step 4: Running Monte Carlo Feature Combination Optimization...", flush=True)
    best_features, opt_summary = run_monte_carlo_feature_optimizer(
        X_train, y_train, metadata['feature_names'], num_simulations=50
    )
    with open("data/feature_optimization_summary.json", "w") as f:
        json.dump(opt_summary, f, indent=4)
        
    # 5. Train Base Models + Stacking Meta-Learner
    print("\n--> Step 5: Training Base Models & Stacking Meta-Learner Architecture...", flush=True)
    base_models = {
        'XGBoost': XGBoostMatchClassifier(),
        'CatBoost': CatBoostMatchClassifier(),
        'SVM_Linear': SVMMatchClassifier(),
        'DNN_MLP': DNNMatchClassifier(),
        'TabNet': TabNetEnsembleClassifier()
    }
    
    metrics_summary = []
    
    # Train base models
    for name, model_obj in base_models.items():
        print(f"    Training Base Model: {name}...", flush=True)
        model_obj.fit(X_train, y_train)
        eval_metrics = model_obj.evaluate(X_test, y_test)
        metrics_summary.append(eval_metrics)
        print(f"      -> {eval_metrics['model_name']}: Accuracy = {eval_metrics['accuracy']}, Log Loss = {eval_metrics['log_loss']}, F1 = {eval_metrics['f1_macro']}", flush=True)
        
    # Train Stacking Meta-Learner using fitted base models
    print("    Training Stacking Meta-Learner (Stage 2 Meta-Classifier)...", flush=True)
    stacking_model = StackingMetaLearnerClassifier(base_models)
    stacking_model.fit(X_train, y_train)
    stacking_eval = stacking_model.evaluate(X_test, y_test)
    metrics_summary.append(stacking_eval)
    print(f"      -> {stacking_eval['model_name']}: Accuracy = {stacking_eval['accuracy']}, Log Loss = {stacking_eval['log_loss']}, F1 = {stacking_eval['f1_macro']}", flush=True)
    
    metrics_df = pd.DataFrame(metrics_summary).sort_values('accuracy', ascending=False).reset_index(drop=True)
    
    print("\n==================================================================", flush=True)
    print(" ADVANCED ML MODEL & STACKING META-LEARNER BENCHMARK TABLE", flush=True)
    print("==================================================================", flush=True)
    print(metrics_df.to_string(index=False), flush=True)
    
    with open("data/model_comparison_metrics.json", "w") as f:
        json.dump(metrics_summary, f, indent=4)
        
    # 6. Scouting & Transfer Models
    fpl_path = "data/player_data/fpl_current_players.csv"
    if os.path.exists(fpl_path):
        print("\n--> Step 6: Executing Synergy, Darkhorse Scouting & Transfer Valuation Models...", flush=True)
        df_p = pd.read_csv(fpl_path)
        p_skills, t_synergy = calculate_player_skills_and_synergy(df_p)
        darkhorses = scout_darkhorses_and_emerging_talents(df_p)
        val_salaries, owner_actions = predict_market_valuation_and_salary(df_p)
        
        p_skills.head(20).to_csv("data/player_skill_ratings.csv", index=False)
        t_synergy.to_csv("data/team_synergy_scores.csv", index=False)
        darkhorses.head(20).to_csv("data/darkhorse_scouting_report.csv", index=False)
        val_salaries.head(20).to_csv("data/transfer_salary_predictions.csv", index=False)
        owner_actions.to_csv("data/owner_strategy_predictions.csv", index=False)
        
    print("\n[OK] Stacking Meta-Learner, Monte Carlo Feature Search & Transfer Intelligence Suite Completed!", flush=True)

if __name__ == "__main__":
    main()
