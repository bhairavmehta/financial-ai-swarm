"""
FastAPI Server
Main API endpoints for financial AI swarm
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import logging
import uvicorn

# Import agents
import sys
sys.path.append('/home/claude/financial-ai-swarm/src')

from agents.fraud_detection.agent import get_fraud_agent
from agents.compliance.agent import get_compliance_agent
from agents.document_processing.agent import get_document_agent
from agents.spend_analysis.agent import get_spend_agent
from agents.vendor_analysis.agent import get_vendor_agent
from agents.explanation.agent import get_explanation_agent
from agents.learning.agent import get_learning_agent

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial AI Swarm API",
    description="Multi-agent AI system for financial operations",
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
    amount: float = Field(..., gt=0, description="Transaction amount")
    merchant: str
    category: str
    user_id: str
    timestamp: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-12345",
                "amount": 150.00,
                "merchant": "Tech Store",
                "category": "IT Equipment",
                "user_id": "EMP-001",
                "timestamp": "2025-01-15T10:30:00Z",
                "location": "New York, NY"
            }
        }


class ProcessTransactionResponse(BaseModel):
    transaction_id: str
    fraud_analysis: Dict
    compliance_check: Dict
    spend_analysis: Dict
    overall_status: str
    timestamp: str


class BatchTransactionRequest(BaseModel):
    transactions: List[Transaction]


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Fraud detection endpoint
@app.post("/api/v1/fraud-detection", response_model=Dict)
async def detect_fraud(transaction: Transaction):
    """
    Detect fraud in a single transaction
    """
    try:
        agent = get_fraud_agent()
        result = agent.detect_fraud(transaction.model_dump())
        
        return {
            "transaction_id": transaction.transaction_id,
            "risk_level": result.risk_level,
            "fraud_score": result.overall_score,
            "confidence": result.confidence,
            "risk_factors": result.risk_factors,
            "anomaly_scores": result.anomaly_scores,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Fraud detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Compliance check endpoint
@app.post("/api/v1/compliance-check", response_model=Dict)
async def check_compliance(transaction: Transaction):
    """
    Check transaction compliance
    """
    try:
        agent = get_compliance_agent()
        result = agent.check_compliance(transaction.model_dump())
        
        return {
            "transaction_id": transaction.transaction_id,
            "status": result.status,
            "sanctions_hit": result.sanctions_hit,
            "pep_hit": result.pep_hit,
            "risk_score": result.risk_score,
            "policy_violations": result.policy_violations,
            "recommendations": result.recommendations,
            "timestamp": result.timestamp
        }
    except Exception as e:
        logger.error(f"Compliance check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Document upload endpoint
@app.post("/api/v1/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process receipt/invoice document
    """
    try:
        # Read file
        contents = await file.read()
        
        agent = get_document_agent()
        result = agent.process_document({'image_bytes': contents})
        
        return {
            "filename": file.filename,
            "document_type": result.document_type,
            "merchant_name": result.merchant_name,
            "total_amount": result.total_amount,
            "tax_amount": result.tax_amount,
            "date": result.date,
            "items": result.items,
            "confidence_score": result.confidence_score,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Document processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Spend analysis endpoint
@app.post("/api/v1/spend-analysis", response_model=Dict)
async def analyze_spending(request: BatchTransactionRequest):
    """
    Analyze spending patterns across multiple transactions
    """
    try:
        agent = get_spend_agent()
        transactions = [txn.model_dump() for txn in request.transactions]
        result = agent.analyze_spending(transactions)
        
        return {
            "total_spend": result.total_spend,
            "budget_utilization": result.budget_utilization,
            "category_breakdown": result.category_breakdown,
            "anomalies": result.anomalies,
            "trends": result.trends,
            "recommendations": result.recommendations,
            "risk_areas": result.risk_areas,
            "period": result.period,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Spend analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Comprehensive transaction processing
@app.post("/api/v1/process-transaction", response_model=ProcessTransactionResponse)
async def process_transaction(transaction: Transaction, background_tasks: BackgroundTasks):
    """
    Process transaction through all agents
    """
    try:
        # Fraud detection
        fraud_agent = get_fraud_agent()
        fraud_result = fraud_agent.detect_fraud(transaction.model_dump())
        
        # Compliance check
        compliance_agent = get_compliance_agent()
        compliance_result = compliance_agent.check_compliance(transaction.model_dump())
        
        # Spend analysis (single transaction)
        spend_agent = get_spend_agent()
        spend_result = spend_agent.analyze_spending([transaction.model_dump()])
        
        # Determine overall status
        if compliance_result.status == "REJECTED":
            overall_status = "REJECTED"
        elif fraud_result.risk_level in ["HIGH", "CRITICAL"]:
            overall_status = "FLAGGED_FOR_REVIEW"
        elif compliance_result.status == "REVIEW_REQUIRED":
            overall_status = "REVIEW_REQUIRED"
        else:
            overall_status = "APPROVED"
        
        return ProcessTransactionResponse(
            transaction_id=transaction.transaction_id,
            fraud_analysis={
                "risk_level": fraud_result.risk_level,
                "score": fraud_result.overall_score,
                "confidence": fraud_result.confidence,
                "risk_factors": fraud_result.risk_factors
            },
            compliance_check={
                "status": compliance_result.status,
                "sanctions_hit": compliance_result.sanctions_hit,
                "pep_hit": compliance_result.pep_hit,
                "risk_score": compliance_result.risk_score,
                "violations": compliance_result.policy_violations
            },
            spend_analysis={
                "total_spend": spend_result.total_spend,
                "budget_utilization": spend_result.budget_utilization,
                "category": transaction.category
            },
            overall_status=overall_status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Transaction processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Batch processing endpoint
@app.post("/api/v1/batch-process")
async def batch_process(request: BatchTransactionRequest):
    """
    Process multiple transactions in batch
    """
    try:
        results = []
        for transaction in request.transactions:
            result = await process_transaction(transaction, BackgroundTasks())
            results.append(result)
        
        return {
            "processed_count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Batch processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Vendor analysis endpoint
@app.post("/api/v1/vendor-analysis")
async def analyze_vendor(request: BatchTransactionRequest, vendor_name: str):
    """
    Analyze vendor risk and payment patterns
    """
    try:
        agent = get_vendor_agent()
        transactions = [txn.model_dump() for txn in request.transactions]
        result = agent.analyze_vendor(vendor_name, transactions)

        return {
            "vendor_id": result.vendor_id,
            "vendor_name": result.vendor_name,
            "risk_level": result.risk_level,
            "risk_score": result.risk_score,
            "risk_factors": result.risk_factors,
            "total_spend": result.total_spend,
            "transaction_count": result.transaction_count,
            "avg_transaction_amount": result.avg_transaction_amount,
            "payment_patterns": result.payment_patterns,
            "duplicate_likelihood": result.duplicate_likelihood,
            "recommendations": result.recommendations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Vendor analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Duplicate vendor detection endpoint
@app.post("/api/v1/vendor-duplicates")
async def detect_duplicate_vendors(vendor_names: List[str], threshold: float = 0.8):
    """
    Detect potential duplicate vendors
    """
    try:
        agent = get_vendor_agent()
        results = agent.detect_duplicates(vendor_names, threshold)

        return {
            "total_checked": len(vendor_names),
            "duplicates_found": len(results),
            "results": [
                {
                    "vendor_1": dup.vendor_1,
                    "vendor_2": dup.vendor_2,
                    "similarity_score": dup.similarity_score,
                    "duplicate_probability": dup.duplicate_probability,
                    "matching_factors": dup.matching_factors,
                    "recommended_action": dup.recommended_action
                }
                for dup in results
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Duplicate detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Feedback submission endpoint
@app.post("/api/v1/feedback")
async def submit_feedback(
    transaction_id: str,
    agent_type: str,
    feedback: str,
    comment: Optional[str] = None,
    original_decision: Optional[Dict] = None
):
    """
    Submit feedback on agent decision
    """
    try:
        agent = get_learning_agent()
        result = agent.record_feedback(
            transaction_id=transaction_id,
            agent_type=agent_type,
            original_decision=original_decision or {},
            user_feedback=feedback,
            user_comment=comment
        )

        return {
            "feedback_id": result.feedback_id,
            "transaction_id": result.transaction_id,
            "status": "recorded",
            "timestamp": result.timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Feedback error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Agent performance endpoint
@app.get("/api/v1/agent-performance/{agent_type}")
async def get_agent_performance(agent_type: str):
    """
    Get performance metrics for a specific agent
    """
    try:
        agent = get_learning_agent()
        performance = agent.get_agent_performance(agent_type)
        recommendations = agent.get_improvement_recommendations(agent_type)

        return {
            **performance,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Performance metrics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Learning insights endpoint
@app.get("/api/v1/learning-insights")
async def get_learning_insights(agent_type: Optional[str] = None, min_confidence: float = 0.5):
    """
    Get learning insights from feedback analysis
    """
    try:
        agent = get_learning_agent()
        insights = agent.get_learning_insights(agent_type, min_confidence)

        return {
            "total_insights": len(insights),
            "insights": [
                {
                    "insight_type": insight.insight_type,
                    "description": insight.description,
                    "affected_agent": insight.affected_agent,
                    "confidence": insight.confidence,
                    "supporting_evidence": insight.supporting_evidence,
                    "recommended_action": insight.recommended_action
                }
                for insight in insights
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Learning insights error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# System status endpoint
@app.get("/api/v1/system/status")
async def get_system_status():
    """
    Get system status and agent health
    """
    try:
        fraud_agent = get_fraud_agent()
        compliance_agent = get_compliance_agent()
        learning_agent = get_learning_agent()

        return {
            "status": "operational",
            "agents": {
                "fraud_detection": {
                    "status": "active",
                    "info": fraud_agent.get_model_info()
                },
                "compliance": {
                    "status": "active",
                    "sanctions_count": len(compliance_agent.sanctions_lists),
                    "policy_count": len(compliance_agent.policy_texts)
                },
                "document_processing": {
                    "status": "active"
                },
                "spend_analysis": {
                    "status": "active"
                },
                "vendor_analysis": {
                    "status": "active"
                },
                "explanation": {
                    "status": "active"
                },
                "learning": {
                    "status": "active",
                    "feedback_records": len(learning_agent.feedback_records)
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"System status error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
