import random
from backend.services.ml_service import ml_service

class DecisionEngine:
    def decide_loan(self, loan_data: dict, farmer_data: dict = None):
        """
        Decides loan approval based on rules (Phase 1) or ML (Phase 2).
        Returns: (status, reason, confidence_score)
        """
        # Extract features
        income = loan_data.get("annual_income", 0)
        land_size = loan_data.get("land_size", 0)
        amount = loan_data.get("amount", 0)
        
        # --- Rule-Based Logic (Strict Phase 1) ---
        # If small loan and good land, auto-approve
        if amount <= 50000 and land_size >= 1.0:
            return "APPROVED", "Auto-Approved: Meets Micro-loan criteria (Amount <= 50k, Land >= 1 acre)", 1.0

        # If very high amount, requires strict ML check or auto-reject if too high
        if amount > 200000:
             return "REJECTED", "Auto-Rejected: Loan amount exceeds maximum limit of 200k", 1.0

        # Geography risk adjust
        loc = loan_data.get("location", "").lower()
        geo_penalty = 0.0
        if any(k in loc for k in ["flood", "drought", "high-risk"]):
            geo_penalty -= 0.15
        if any(k in loc for k in ["irrigated", "low-risk"]):
            geo_penalty += 0.1
        
        # Insurance adjust
        insured = loan_data.get("insured", False)
        insurance_boost = 0.1 if insured else 0.0

        # --- ML Logic (Phase 2) ---
        # If user data is available, use it for ML
        if farmer_data:
            credit_score = farmer_data.get("credit_score", 650)
            balance = farmer_data.get("balance", 5000.0)
            
            status, probability, reason = ml_service.predict(
                credit_score=credit_score,
                balance=balance,
                loan_amount=amount,
                land_size=land_size,
                annual_income=income
            )
            adj_prob = max(0.0, min(1.0, probability + geo_penalty + insurance_boost))
            adj_status = "APPROVED" if adj_prob >= 0.5 else "REJECTED"
            return adj_status, reason, adj_prob
        
        # Fallback if no farmer data (shouldn't happen in real flow)
        return "PENDING", "Requires Manual Review", 0.5

decision_engine = DecisionEngine()
