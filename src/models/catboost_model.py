from sklearn.ensemble import HistGradientBoostingClassifier
import numpy as np
from sklearn.metrics import accuracy_score, log_loss, f1_score

class CatBoostMatchClassifier:
    """Model 5: CatBoost / Fast Gradient Boosted Tree Classifier"""
    def __init__(self, max_iter=50, learning_rate=0.05, max_depth=5):
        self.model = HistGradientBoostingClassifier(
            max_iter=max_iter,
            learning_rate=learning_rate,
            max_depth=max_depth,
            l2_regularization=1.5,
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
            'model_name': 'CatBoost / Fast Gradient Boosting',
            'accuracy': round(acc, 4),
            'log_loss': round(loss, 4),
            'f1_macro': round(f1, 4)
        }
