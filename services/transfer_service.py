from sqlalchemy.orm import Session
from backend.models.models import Loan, User, TransactionLog, LoanStatus, MerchantVoucher
from datetime import datetime
import hashlib
import uuid

class TransferService:
    def _compute_hash(self, prev_hash: str, reference_id: str, amount: float, to_account: str, timestamp: datetime):
        payload = f"{prev_hash or ''}|{reference_id}|{amount}|{to_account}|{timestamp.isoformat()}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def release_funds(self, db: Session, loan_id: int, performed_by: int):
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            return {"error": "Loan not found"}
        if loan.status != LoanStatus.APPROVED:
            return {"error": "Loan must be APPROVED before fund release"}
        if loan.merchant_restricted:
            code = f"VCH-{uuid.uuid4().hex[:10].upper()}"
            voucher = MerchantVoucher(
                loan_id=loan.id,
                voucher_code=code,
                merchant_category=loan.merchant_category or "general",
                amount=loan.amount,
            )
            db.add(voucher)
            db.commit()
            db.refresh(voucher)
            return {"voucher_code": code, "amount": loan.amount, "merchant_category": voucher.merchant_category}
        farmer = db.query(User).filter(User.id == loan.farmer_id).first()
        if not farmer or not farmer.bank_account or not farmer.ifsc:
            return {"error": "Farmer bank details missing"}
        # Unique reference
        reference_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        timestamp = datetime.utcnow()
        # Prev hash for immutability chain
        last_txn = db.query(TransactionLog).order_by(TransactionLog.id.desc()).first()
        prev_hash = last_txn.hash if last_txn else None
        tx_hash = self._compute_hash(prev_hash, reference_id, loan.amount, farmer.bank_account, timestamp)
        txn = TransactionLog(
            loan_id=loan.id,
            reference_id=reference_id,
            amount=loan.amount,
            to_account=farmer.bank_account,
            timestamp=timestamp,
            prev_hash=prev_hash,
            hash=tx_hash,
            remarks=f"Released to {farmer.username} ({farmer.bank_account})"
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)
        return {"reference_id": reference_id, "hash": tx_hash, "amount": loan.amount, "to_account": farmer.bank_account, "timestamp": timestamp.isoformat()}

transfer_service = TransferService()
