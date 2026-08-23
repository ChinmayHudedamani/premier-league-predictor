import xgboost as xgb
import numpy as np
from sklearn.metrics import accuracy_score, log_loss, f1_score

class XGBoostMatchClassifier:
    """Model 1: XGBoost (Extreme Gradient Boosting) Classifier"""
    def __init__(self, n_estimators=100, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8):
        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            objective='multi:softprob',
            num_class=3,
            eval_metric='mlogloss',
            random_state=42
        )

    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        self.model.fit(X_train, y_train)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        preds = self.predict(X_test)
        probs = self.predict_proba(X_test)
        
        acc = accuracy_score(y_test, preds)
        loss = log_loss(y_test, probs)
        f1 = f1_score(y_test, preds, average='macro')
        
        return {
            'model_name': 'XGBoost (Gradient Boosting)',
            'accuracy': round(acc, 4),
            'log_loss': round(loss, 4),
            'f1_macro': round(f1, 4)
        }
