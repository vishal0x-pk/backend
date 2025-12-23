import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

class LoanRiskModel:
    def __init__(self):
        self.model = None
        self.model_path = "loan_risk_model.pkl"
        self._train_dummy_model()

    def _train_dummy_model(self):
        """
        Trains a model on synthetic data to simulate a real-world scenario.
        Features: Credit Score, Balance, Loan Amount, Land Size, Annual Income
        Target: Approved (1) or Rejected (0)
        """
        # Check if model exists (skip for now to ensure we always have a fresh one for demo)
        # if os.path.exists(self.model_path):
        #     self.model = joblib.load(self.model_path)
        #     return

        # Generate synthetic data
        np.random.seed(42)
        n_samples = 1000
        
        # Features
        credit_scores = np.random.randint(300, 850, n_samples)
        balances = np.random.uniform(1000, 50000, n_samples)
        loan_amounts = np.random.uniform(5000, 200000, n_samples)
        land_sizes = np.random.uniform(0.5, 100, n_samples)
        incomes = np.random.uniform(2000, 100000, n_samples)
        
        # Logic for "Ground Truth"
        approvals = []
        for i in range(n_samples):
            score = 0
            # Credit Score impact
            if credit_scores[i] > 700: score += 3
            elif credit_scores[i] > 600: score += 1
            else: score -= 2
            
            # Balance vs Loan Amount
            if balances[i] > loan_amounts[i] * 0.2: score += 2 
            else: score -= 1
            
            # Land Size (More land = more collateral/production)
            if land_sizes[i] > 5: score += 2
            elif land_sizes[i] < 1: score -= 1
            
            # Income
            if incomes[i] > 10000: score += 2
            
            # Decision
            approvals.append(1 if score > 2 else 0)
            
        X = pd.DataFrame({
            'credit_score': credit_scores,
            'balance': balances,
            'loan_amount': loan_amounts,
            'land_size': land_sizes,
            'annual_income': incomes
        })
        y = np.array(approvals)
        
        # Train Model
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.model.fit(X, y)
        
        # joblib.dump(self.model, self.model_path)
        print("AI Model Trained on 1000 synthetic records.")

    def predict(self, credit_score, balance, loan_amount, land_size, annual_income):
        """
        Predicts loan approval probability.
        Returns: (is_approved, probability, reason)
        """
        if not self.model:
            self._train_dummy_model()
            
        features = pd.DataFrame([[credit_score, balance, loan_amount, land_size, annual_income]], 
                                columns=['credit_score', 'balance', 'loan_amount', 'land_size', 'annual_income'])
        
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0][1] # Probability of class 1 (Approved)
        
        # Generate explanation
        reasons = []
        if credit_score < 600:
            reasons.append("Credit score is too low.")
        if balance < loan_amount * 0.1:
            reasons.append("Insufficient balance/collateral.")
        if probability < 0.5:
            reasons.append(f"AI Risk Assessment Score: {int(probability*100)}/100 (Too Low).")
        else:
            reasons.append(f"AI Risk Assessment Score: {int(probability*100)}/100 (Good).")
            
        status = "APPROVED" if prediction == 1 else "REJECTED"
        return status, probability, " ".join(reasons)

ml_service = LoanRiskModel()
