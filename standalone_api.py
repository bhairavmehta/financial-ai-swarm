#!/usr/bin/env python3
"""
Standalone Financial AI Swarm API Server
Runs without heavy ML dependencies for demonstration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial AI Swarm API (Standalone Demo)",
    description="Multi-agent AI system for financial operations - Demo Mode",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class Transaction(BaseModel):
    transaction_id: str
    amount: float = Field(..., gt=0)
    merchant: str
    category: str
    user_id: str
    timestamp: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ProcessTransactionResponse(BaseModel):
    transaction_id: str
    fraud_analysis: Dict
    compliance_check: Dict
    spend_analysis: Dict
    overall_status: str
    timestamp: str


# Simulated fraud detection
def simulate_fraud_detection(transaction: Dict) -> Dict:
    """Simulate fraud detection logic"""
    amount = transaction.get('amount', 0)

    # Simple rule-based simulation
    if amount > 15000:
        risk_level = 'HIGH'
        score = 0.75
        risk_factors = [
            f"High transaction amount: ${amount:,.2f}",
            "Amount exceeds normal threshold"
        ]
    elif amount > 5000:
        risk_level = 'MEDIUM'
        score = 0.45
        risk_factors = [f"Elevated transaction amount: ${amount:,.2f}"]
    else:
        risk_level = 'LOW'
        score = 0.15
        risk_factors = []

    return {
        "risk_level": risk_level,
        "fraud_score": score,
        "confidence": 0.85,
        "risk_factors": risk_factors,
        "anomaly_scores": {
            "isolation_forest": score * 0.9,
            "lof": score * 1.1,
            "knn": score * 0.95
        }
    }


# Simulated compliance check
def simulate_compliance_check(transaction: Dict) -> Dict:
    """Simulate compliance checking logic"""
    merchant = transaction.get('merchant', '').lower()

    # Check for suspicious keywords
    suspicious_terms = ['suspicious', 'offshore', 'blocked', 'sanctioned']
    sanctions_hit = any(term in merchant for term in suspicious_terms)
    pep_hit = 'government' in merchant or 'official' in merchant

    if sanctions_hit:
        status = 'REJECTED'
        risk_score = 0.95
        violations = [f"Merchant '{merchant}' appears on sanctions list"]
    elif pep_hit:
        status = 'REVIEW_REQUIRED'
        risk_score = 0.65
        violations = ["Politically Exposed Person detected"]
    else:
        status = 'APPROVED'
        risk_score = 0.1
        violations = []

    return {
        "status": status,
        "sanctions_hit": sanctions_hit,
        "pep_hit": pep_hit,
        "risk_score": risk_score,
        "policy_violations": violations,
        "recommendations": ["Manual review required"] if violations else ["Transaction approved"]
    }


# Simulated spend analysis
def simulate_spend_analysis(transaction: Dict) -> Dict:
    """Simulate spend analysis logic"""
    amount = transaction.get('amount', 0)
    category = transaction.get('category', 'Other')

    # Simple budget simulation
    budgets = {
        'IT Services': 100000,
        'Travel': 50000,
        'Entertainment': 10000,
        'Consulting': 75000,
        'Electronics': 50000,
        'Other': 25000
    }

    budget = budgets.get(category, 25000)
    utilization = min(amount / budget, 1.0)

    return {
        "total_spend": amount,
        "budget_utilization": utilization,
        "category": category,
        "budget_limit": budget,
        "over_budget": utilization > 1.0
    }


# Simulated vendor analysis
def simulate_vendor_analysis(vendor_name: str, transactions: List[Dict]) -> Dict:
    """Simulate vendor analysis logic"""
    total_spend = sum(t.get('amount', 0) for t in transactions)

    # Simple risk assessment
    if total_spend > 50000:
        risk_level = 'HIGH'
        risk_score = 0.7
        risk_factors = [f"High total spend: ${total_spend:,.2f}"]
    elif total_spend > 20000:
        risk_level = 'MEDIUM'
        risk_score = 0.4
        risk_factors = []
    else:
        risk_level = 'LOW'
        risk_score = 0.2
        risk_factors = []

    return {
        "vendor_id": f"VND-{hash(vendor_name) % 100000:05d}",
        "vendor_name": vendor_name,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "total_spend": total_spend,
        "transaction_count": len(transactions),
        "avg_transaction_amount": total_spend / len(transactions) if transactions else 0,
        "recommendations": ["Monitor closely"] if risk_level == 'HIGH' else ["Continue standard monitoring"]
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "standalone_demo",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Fraud detection endpoint
@app.post("/api/v1/fraud-detection")
async def detect_fraud(transaction: Transaction):
    """Detect fraud in a single transaction"""
    try:
        result = simulate_fraud_detection(transaction.model_dump())
        result["transaction_id"] = transaction.transaction_id
        result["timestamp"] = datetime.now().isoformat()

        logger.info(f"Fraud detection for {transaction.transaction_id}: {result['risk_level']}")
        return result
    except Exception as e:
        logger.error(f"Fraud detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Compliance check endpoint
@app.post("/api/v1/compliance-check")
async def check_compliance(transaction: Transaction):
    """Check transaction compliance"""
    try:
        result = simulate_compliance_check(transaction.model_dump())
        result["transaction_id"] = transaction.transaction_id
        result["timestamp"] = datetime.now().isoformat()

        logger.info(f"Compliance check for {transaction.transaction_id}: {result['status']}")
        return result
    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Spend analysis endpoint
@app.post("/api/v1/spend-analysis")
async def analyze_spending(transaction: Transaction):
    """Analyze spending patterns"""
    try:
        result = simulate_spend_analysis(transaction.model_dump())
        result["transaction_id"] = transaction.transaction_id
        result["timestamp"] = datetime.now().isoformat()

        logger.info(f"Spend analysis for {transaction.transaction_id}")
        return result
    except Exception as e:
        logger.error(f"Spend analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Vendor analysis endpoint
@app.post("/api/v1/vendor-analysis")
async def analyze_vendor(vendor_name: str, transactions: List[Transaction]):
    """Analyze vendor risk"""
    try:
        txn_list = [t.model_dump() for t in transactions]
        result = simulate_vendor_analysis(vendor_name, txn_list)
        result["timestamp"] = datetime.now().isoformat()

        logger.info(f"Vendor analysis for {vendor_name}: {result['risk_level']}")
        return result
    except Exception as e:
        logger.error(f"Vendor analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Comprehensive transaction processing
@app.post("/api/v1/process-transaction", response_model=ProcessTransactionResponse)
async def process_transaction(transaction: Transaction):
    """Process transaction through all agents"""
    try:
        logger.info(f"Processing transaction: {transaction.transaction_id}")

        # Run all analyses
        fraud_result = simulate_fraud_detection(transaction.model_dump())
        compliance_result = simulate_compliance_check(transaction.model_dump())
        spend_result = simulate_spend_analysis(transaction.model_dump())

        # Determine overall status
        if compliance_result['status'] == 'REJECTED':
            overall_status = 'REJECTED'
        elif fraud_result['risk_level'] in ['HIGH', 'CRITICAL']:
            overall_status = 'FLAGGED_FOR_REVIEW'
        elif compliance_result['status'] == 'REVIEW_REQUIRED':
            overall_status = 'REVIEW_REQUIRED'
        else:
            overall_status = 'APPROVED'

        response = ProcessTransactionResponse(
            transaction_id=transaction.transaction_id,
            fraud_analysis=fraud_result,
            compliance_check=compliance_result,
            spend_analysis=spend_result,
            overall_status=overall_status,
            timestamp=datetime.now().isoformat()
        )

        logger.info(f"Transaction {transaction.transaction_id} processed: {overall_status}")
        return response

    except Exception as e:
        logger.error(f"Transaction processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System status endpoint
@app.get("/api/v1/system/status")
async def get_system_status():
    """Get system status and agent health"""
    return {
        "status": "operational",
        "mode": "standalone_demo",
        "agents": {
            "fraud_detection": {"status": "active", "mode": "simulated"},
            "compliance": {"status": "active", "mode": "simulated"},
            "spend_analysis": {"status": "active", "mode": "simulated"},
            "vendor_analysis": {"status": "active", "mode": "simulated"},
            "document_processing": {"status": "ready", "mode": "simulated"},
            "explanation": {"status": "ready", "mode": "simulated"},
            "learning": {"status": "ready", "mode": "simulated"}
        },
        "timestamp": datetime.now().isoformat(),
        "note": "Running in standalone demo mode without ML dependencies"
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("  FINANCIAL AI SWARM - STANDALONE DEMO MODE")
    print("=" * 70)
    print()
    print("  Running without heavy ML dependencies")
    print("  Using simulated logic for demonstration")
    print()
    print("  API Server starting on: http://localhost:8000")
    print("  API Documentation: http://localhost:8000/docs")
    print("  Health Check: http://localhost:8000/health")
    print()
    print("=" * 70)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
