from sklearn.neural_network import MLPClassifier
import numpy as np
from sklearn.metrics import accuracy_score, log_loss, f1_score

class DNNMatchClassifier:
    """Model 3: Deep Neural Network (DNN / MLP with Entity Embeddings Architecture)"""
    def __init__(self, hidden_layer_sizes=(128, 64, 32), alpha=0.001, max_iter=250):
        self.model = MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver='adam',
            alpha=alpha,
            learning_rate='adaptive',
            max_iter=max_iter,
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
            'model_name': 'Deep Neural Network (DNN / MLP)',
            'accuracy': round(acc, 4),
            'log_loss': round(loss, 4),
            'f1_macro': round(f1, 4)
        }
