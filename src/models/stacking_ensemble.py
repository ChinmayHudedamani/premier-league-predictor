import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, f1_score
from typing import List, Dict

class StackingMetaLearnerClassifier:
    """
    2-Stage Stacking Meta-Learner Architecture:
    Stage 1: Reuses probability predictions from pre-fitted base models
             (XGBoost, CatBoost, SVM, DNN, TabNet).
    Stage 2: Regularized Logistic Regression Meta-Classifier fuses predictions to eliminate model bias.
    """
    def __init__(self, fitted_base_models: Dict):
        self.fitted_base_models = fitted_base_models
        self.meta_classifier = LogisticRegression(C=1.0, max_iter=300, random_state=42)

    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        meta_features = []
        for name, model in self.fitted_base_models.items():
            probs = model.predict_proba(X_train)
            meta_features.append(probs)
            
        X_meta_train = np.hstack(meta_features)
        self.meta_classifier.fit(X_meta_train, y_train)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        meta_features = []
        for name, model in self.fitted_base_models.items():
            probs = model.predict_proba(X)
            meta_features.append(probs)
        X_meta = np.hstack(meta_features)
        return self.meta_classifier.predict_proba(X_meta)

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        preds = self.predict(X_test)
        probs = self.predict_proba(X_test)
        
        acc = accuracy_score(y_test, preds)
        loss = log_loss(y_test, probs)
        f1 = f1_score(y_test, preds, average='macro')
        
        return {
            'model_name': 'Stacking Meta-Learner (Ensemble)',
            'accuracy': round(acc, 4),
            'log_loss': round(loss, 4),
            'f1_macro': round(f1, 4)
        }
