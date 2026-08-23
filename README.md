# Premier League & Transfer Intelligence Engine ⚽📊

A production-grade, mathematically rigorous Machine Learning & Deep Learning intelligence framework for English Football predicting **Match Outcomes, Season Champions, Player Synergy, Darkhorse Talents, Transfer Market Valuations, Weekly Salaries, and Ownership Strategic Decisions**.

---

## 🌟 Executive Highlights

* **Dataset Size**: **10,804 unique Premier League matches** (1993 – Present) across **28 seasons**, fully deduplicated with missing match audit.
* **Player Analytics**: **609 active Premier League players** analyzed across expected metrics ($xG, xA, xGI/90$), ICT Index, position suitability, and synergy scores.
* **4-Model Architecture Suite**:
  1. **XGBoost (Extreme Gradient Boosting)** — Top Performer (**50.13% Accuracy**, 1.0244 Log Loss)
  2. **Support Vector Machine (SVM RBF / LinearSVC)** — High Stability (**49.74% Accuracy**, 1.0147 Log Loss)
  3. **Deep Neural Network (DNN / MLP with Entity Embeddings)** — Complex Non-Linear Representation (**49.74% Accuracy**, 1.0261 Log Loss)
  4. **TabNet Attentive Sparsemax Ensemble** — Dynamic Feature Masking (**49.08% Accuracy**, 1.0442 Log Loss)

---

## 📐 Mathematical Grounding & Model Formulations

### 1. XGBoost (Extreme Gradient Boosting)
Minimizes regularized loss at step $t$ using 1st ($g_i$) and 2nd ($h_i$) order Taylor expansion gradients:

$$\mathcal{L}^{(t)} \approx \sum_{i=1}^n \left[ l(y_i, \hat{y}_i^{(t-1)}) + g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i) \right] + \gamma T + \frac{1}{2}\lambda \sum_{j=1}^T w_j^2$$

Optimal leaf weights $w_j^*$ and split gain:

$$w_j^* = -\frac{\sum_{i \in I_j} g_i}{\sum_{i \in I_j} h_i + \lambda}, \quad \text{Gain} = \frac{1}{2} \left[ \frac{(\sum_{i \in I_L} g_i)^2}{\sum_{i \in I_L} h_i + \lambda} + \frac{(\sum_{i \in I_R} g_i)^2}{\sum_{i \in I_R} h_i + \lambda} - \frac{(\sum_{i \in I} g_i)^2}{\sum_{i \in I} h_i + \lambda} \right] - \gamma$$

---

### 2. Support Vector Machine / Regression (SVM / SVR)
Solves primal quadratic optimization under $\epsilon$-insensitive loss and converts to dual form with Lagrange multipliers $\alpha_i, \alpha_i^*$:

$$\min_{w, b, \xi, \xi^*} \frac{1}{2} \|w\|^2 + C \sum_{i=1}^n (\xi_i + \xi_i^*)$$
$$f(x) = \sum_{i \in SV} (\alpha_i - \alpha_i^*) K(x_i, x) + b, \quad K(x_i, x_j) = \exp(-\gamma \|x_i - x_j\|^2)$$

---

### 3. Deep Neural Network (DNN) with Entity Embeddings
Categorical entities (Teams, Players, Owners) map to low-dimensional embedding vectors $e_i \in \mathbb{R}^d$:

$$e_{team} = E_{team}[x_{team}], \quad h^{(l)} = \text{Dropout}\left(\text{SiLU}\left(W^{(l)} [x_{num} \parallel e_{team}] + b^{(l)}\right)\right)$$

---

### 4. TabNet (Attentive Sparsemax Ensemble)
Selects salient tactical and synergy features sequentially per match step via Sparsemax masks:

$$M[i] = \text{Sparsemax}\left(\gamma \cdot P[i-1] \cdot h_i(a[i-1])\right)$$

---

## 📊 4-Model Prediction Benchmark Results

Evaluated on strict chronological test split (2024–2026 seasons, 760 matches):

| Model Architecture | Test Accuracy | Log Loss | F1 Macro Score | Primary Strengths |
| :--- | :---: | :---: | :---: | :--- |
| **XGBoost (Gradient Boosting)** | **50.13%** | **1.0244** | **0.3731** | Optimal non-linear goal differential & Elo interaction handling |
| **Support Vector Machine (SVM)** | **49.74%** | **1.0147** | **0.3668** | Lowest loss variance; smooth boundary classification |
| **Deep Neural Network (DNN)** | **49.74%** | **1.0261** | **0.3710** | High representation capacity for multi-entity embeddings |
| **TabNet Attentive Ensemble** | **49.08%** | **1.0442** | **0.3866** | Interpretable feature selection masks per decision step |

---

## 🏆 Premier League Title Winner Predictions (10,000 Monte Carlo Simulations)

| Rank | Club | Title Win Prob % | Top 4 Finish % | Relegation Prob % | Projected Points |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | **Arsenal** | **50.88%** | **97.95%** | 0.00% | **79.8 pts** |
| **2** | **Manchester City** | **35.39%** | **95.30%** | 0.00% | **77.1 pts** |
| **3** | **Liverpool** | **11.18%** | **82.87%** | 0.00% | **71.7 pts** |
| **4** | **Chelsea** | **0.99%** | **29.74%** | 0.06% | **61.1 pts** |
| **5** | **Newcastle United** | **0.71%** | **27.32%** | 0.04% | **60.7 pts** |
| **6** | **Aston Villa** | **0.34%** | **19.04%** | 0.09% | **58.5 pts** |

---

## 🔍 Scouted Darkhorses & Emerging Talents

Isolating high underlying per-90 metrics ($xGI/90$) and value pricing ($\le £9.0m$):

| Player | Club | Position | Price | $xGI / 90$ | Darkhorse Score |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Maxim De Cuyper** | Brighton | Defender | £4.5m | **1.68** | **20.79** |
| **Jack Hinshelwood** | Brighton | Midfielder | £6.0m | **1.43** | **18.24** |
| **Marc Guéhi** | Man City | Defender | £6.0m | **1.20** | **14.00** |
| **Dominik Szoboszlai** | Liverpool | Midfielder | £7.0m | **1.12** | **12.46** |
| **Keane Lewis-Potter** | Brentford | Midfielder | £5.5m | **0.89** | **11.57** |

---

## 💰 Transfer Valuation & Weekly Salary Predictions

| Player | Club | Position | Predicted Market Value (€M) | Predicted Weekly Salary (£k/wk) |
| :--- | :--- | :---: | :---: | :---: |
| **Erling Haaland** | Manchester City | Forward | **€119.4M** | **£279k / week** |
| **Alexander Isak** | Liverpool | Forward | **€84.2M** | **£201k / week** |
| **Igor Thiago** | Brentford | Forward | **€77.4M** | **£170k / week** |
| **Bruno Fernandes** | Manchester United | Midfielder | **€76.0M** | **£183k / week** |
| **Bukayo Saka** | Arsenal | Midfielder | **€71.4M** | **£233k / week** |

---

## 👔 Club Ownership Behavioral & Strategy Profiling

| Club | Owner Group | Investment Archetype | Window Budget | Wage Policy & Strategy |
| :--- | :--- | :--- | :---: | :--- |
| **Chelsea** | Boehly / Clearlake | Aggressive High-Volume Youth | **£250M** | Multi-year amortization, incentive-heavy contracts |
| **Man City** | City Football Group | Surgical Precision & Multi-Club | **£180M** | Top-tier premium wages for instant impact stars |
| **Liverpool** | FSG (John W. Henry) | Data-Driven Moneyball | **£90M** | Strict ROI discipline, high renewal priority |
| **Newcastle** | PIF | PSR-Constrained Ambition | **£120M** | Commercial revenue expansion to unlock FFP cap |
| **Man Utd** | Ratcliffe / INEOS | Restructuring & Tactical Value | **£150M** | Trimming wage bloat, target youth European talent |

---

## 📁 Repository Structure

```
premier-league-predictor/
├── data/
│   ├── cleaned_matches.csv                # 10,804 deduplicated match records
│   ├── data_health_report.json            # Match completeness audit report
│   ├── model_comparison_metrics.json      # Benchmark results across 4 ML models
│   ├── winner_predictions.csv              # Monte Carlo title & relegation probabilities
│   ├── darkhorse_scouting_report.csv      # Scouted breakout prospects & emerging talents
│   ├── transfer_salary_predictions.csv    # Market fee (€M) & weekly salary (£k) estimates
│   ├── owner_strategy_predictions.csv     # Owner strategic behavioral profiles
│   └── player_data/
│       └── fpl_current_players.csv        # 609 active Premier League players dataset
├── src/
│   ├── models/
│   │   ├── xgboost_model.py               # Model 1: XGBoost Gradient Boosting
│   │   ├── svm_model.py                   # Model 2: Support Vector Machine (LinearSVC/Calibrated)
│   │   ├── dnn_model.py                   # Model 3: Deep Neural Network (MLP / Embeddings)
│   │   └── tabnet_model.py                # Model 4: TabNet Attentive Sparsemax Ensemble
│   ├── data_processing.py                 # Multi-season match cleaning & deduplication
│   ├── dataset_builder.py                 # Temporal train/test split & strict featurization
│   ├── feature_engineering.py             # Historical Elo & rolling form metrics
│   ├── synergy_engine.py                  # Player individual skills & team synergy scores
│   ├── scouting_engine.py                 # Darkhorse talent discovery model
│   └── transfer_owner_engine.py           # Valuation, salary & owner action model
├── requirements.txt                       # Project dependencies
├── run_pipeline.py                        # Monte Carlo season simulation runner
└── train_models.py                        # Master multi-model training & evaluation script
```

---

## ⚙️ Quickstart & Reproduction Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Master 4-Model Training & Scouting Pipeline
```bash
python train_models.py
```

### 3. Run Monte Carlo Season Winner Simulator
```bash
python run_pipeline.py
```
