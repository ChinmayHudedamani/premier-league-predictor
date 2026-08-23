from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import numpy as np
from sklearn.metrics import accuracy_score, log_loss, f1_score

class SVMMatchClassifier:
    """Model 2: Support Vector Machine (SVM) Classifier"""
    def __init__(self, C=1.0):
        base_svm = LinearSVC(C=C, max_iter=2000, random_state=42)
        self.model = CalibratedClassifierCV(base_svm)

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
            'model_name': 'Support Vector Machine (SVM)',
            'accuracy': round(acc, 4),
            'log_loss': round(loss, 4),
            'f1_macro': round(f1, 4)
        }
