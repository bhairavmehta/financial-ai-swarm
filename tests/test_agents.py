"""
Comprehensive Test Suite
Tests all agents and orchestration
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agents.fraud_detection.agent import FraudDetectionAgent
from agents.compliance.agent import ComplianceAgent
from agents.document_processing.agent import DocumentProcessingAgent
from agents.spend_analysis.agent import SpendAnalysisAgent


class TestFraudDetectionAgent:
    """Test fraud detection agent"""
    
    def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = FraudDetectionAgent()
        assert agent is not None
        assert len(agent.models) > 0
    
    def test_fraud_detection_low_risk(self):
        """Test detection of low-risk transaction"""
        agent = FraudDetectionAgent()
        
        transaction = {
            "transaction_id": "TEST-001",
            "amount": 50.00,
            "merchant": "Coffee Shop",
            "category": "Food",
            "user_id": "EMP-001",
            "timestamp": "2025-01-15T10:30:00Z"
        }
        
        result = agent.detect_fraud(transaction)
        assert result is not None
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert 0 <= result.overall_score <= 1
        assert 0 <= result.confidence <= 1
    
    def test_fraud_detection_high_risk(self):
        """Test detection of high-risk transaction"""
        agent = FraudDetectionAgent()
        
        transaction = {
            "transaction_id": "TEST-002",
            "amount": 25000.00,
            "merchant": "Unknown Store",
            "category": "Electronics",
            "user_id": "EMP-999",
            "timestamp": "2025-01-15T02:30:00Z",
            "location": "Unknown"
        }
        
        result = agent.detect_fraud(transaction)
        assert result is not None
        assert len(result.risk_factors) > 0
    
    def test_batch_detection(self):
        """Test batch processing"""
        agent = FraudDetectionAgent()
        
        transactions = [
            {"transaction_id": f"TEST-{i}", "amount": 100.0, "merchant": "Test", 
             "category": "Test", "user_id": "EMP-001"}
            for i in range(5)
        ]
        
        results = agent.batch_detect(transactions)
        assert len(results) == 5
        assert all(r.overall_score >= 0 for r in results)


class TestComplianceAgent:
    """Test compliance agent"""
    
    def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = ComplianceAgent()
        assert agent is not None
        assert len(agent.sanctions_lists) > 0
        assert len(agent.policy_texts) > 0
    
    def test_clean_transaction(self):
        """Test transaction with no issues"""
        agent = ComplianceAgent()
        
        transaction = {
            "transaction_id": "TEST-001",
            "amount": 500.00,
            "merchant": "Normal Vendor",
            "category": "Supplies",
            "merchant_description": "Office supplies"
        }
        
        result = agent.check_compliance(transaction)
        assert result is not None
        assert result.status in ["APPROVED", "REVIEW_REQUIRED", "REJECTED"]
        assert isinstance(result.sanctions_hit, bool)
        assert isinstance(result.pep_hit, bool)
    
    def test_sanctioned_entity(self):
        """Test detection of sanctioned entity"""
        agent = ComplianceAgent()
        
        transaction = {
            "transaction_id": "TEST-002",
            "amount": 10000.00,
            "merchant": "Suspicious Corp International",
            "category": "Consulting",
            "merchant_description": "Consulting services"
        }
        
        result = agent.check_compliance(transaction)
        assert result is not None
        assert result.sanctions_hit == True
        assert result.status == "REJECTED"
    
    def test_policy_rag(self):
        """Test policy retrieval"""
        agent = ComplianceAgent()
        
        transaction = {
            "transaction_id": "TEST-003",
            "amount": 15000.00,
            "merchant": "Tech Vendor",
            "category": "IT Services"
        }
        
        policies = agent._retrieve_relevant_policies(transaction, k=3)
        assert len(policies) <= 3
        assert all(isinstance(p, str) for p in policies)


class TestDocumentProcessingAgent:
    """Test document processing agent"""
    
    def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = DocumentProcessingAgent()
        assert agent is not None
    
    def test_mock_receipt_processing(self):
        """Test processing with mock receipt text"""
        agent = DocumentProcessingAgent()
        
        # Process with mock data (no actual image)
        document_data = {
            "file_path": "test_receipt.jpg"
        }
        
        result = agent.process_document(document_data)
        assert result is not None
        assert result.document_type in ["RECEIPT", "INVOICE", "CONTRACT", "UNKNOWN"]
        assert 0 <= result.confidence_score <= 1
    
    def test_field_extraction(self):
        """Test field extraction from text"""
        agent = DocumentProcessingAgent()
        
        text = "Total: $52.92\nTax: $3.92\nDate: 01/15/2025"
        
        total = agent._extract_field(text, 'total')
        tax = agent._extract_field(text, 'tax')
        date = agent._extract_field(text, 'date')
        
        assert total is not None
        assert tax is not None
        assert date is not None


class TestSpendAnalysisAgent:
    """Test spend analysis agent"""
    
    def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = SpendAnalysisAgent()
        assert agent is not None
        assert len(agent.budgets) > 0
    
    def test_single_transaction_analysis(self):
        """Test analysis of single transaction"""
        agent = SpendAnalysisAgent()
        
        transaction = {
            "transaction_id": "TEST-001",
            "amount": 1000.00,
            "category": "IT Services",
            "timestamp": "2025-01-15T10:30:00Z"
        }
        
        result = agent.analyze_spending([transaction])
        assert result is not None
        assert result.total_spend == 1000.00
        assert 0 <= result.budget_utilization <= 1
    
    def test_multiple_transactions_analysis(self):
        """Test analysis of multiple transactions"""
        agent = SpendAnalysisAgent()
        
        transactions = [
            {"transaction_id": f"TEST-{i}", "amount": 500.0, 
             "category": "Travel", "timestamp": "2025-01-15T10:30:00Z"}
            for i in range(10)
        ]
        
        result = agent.analyze_spending(transactions)
        assert result.total_spend == 5000.00
        assert len(result.category_breakdown) > 0
    
    def test_anomaly_detection(self):
        """Test anomaly detection in spending"""
        agent = SpendAnalysisAgent()
        
        # Normal transactions + one anomaly
        transactions = [
            {"transaction_id": f"TEST-{i}", "amount": 100.0, 
             "category": "Supplies", "timestamp": "2025-01-15T10:30:00Z"}
            for i in range(20)
        ]
        transactions.append({
            "transaction_id": "TEST-ANOMALY",
            "amount": 10000.0,
            "category": "Supplies",
            "timestamp": "2025-01-15T10:30:00Z"
        })
        
        result = agent.analyze_spending(transactions)
        assert len(result.anomalies) > 0
    
    def test_budget_utilization(self):
        """Test budget utilization calculation"""
        agent = SpendAnalysisAgent()
        
        # Transactions that exceed budget
        transactions = [
            {"transaction_id": f"TEST-{i}", "amount": 20000.0, 
             "category": "Travel", "timestamp": "2025-01-15T10:30:00Z"}
            for i in range(5)
        ]
        
        result = agent.analyze_spending(transactions)
        assert result.budget_utilization > 0.5
        assert len(result.risk_areas) > 0


class TestIntegration:
    """Integration tests for full pipeline"""
    
    def test_full_transaction_pipeline(self):
        """Test processing transaction through multiple agents"""
        # Initialize agents
        fraud_agent = FraudDetectionAgent()
        compliance_agent = ComplianceAgent()
        spend_agent = SpendAnalysisAgent()
        
        transaction = {
            "transaction_id": "INTEGRATION-001",
            "amount": 1500.00,
            "merchant": "Tech Vendor",
            "category": "IT Services",
            "user_id": "EMP-001",
            "timestamp": "2025-01-15T10:30:00Z"
        }
        
        # Process through each agent
        fraud_result = fraud_agent.detect_fraud(transaction)
        compliance_result = compliance_agent.check_compliance(transaction)
        spend_result = spend_agent.analyze_spending([transaction])
        
        # Verify all results
        assert fraud_result is not None
        assert compliance_result is not None
        assert spend_result is not None
        
        # Verify consistency
        assert spend_result.total_spend == transaction['amount']


# Pytest fixtures
@pytest.fixture
def sample_transaction():
    """Fixture for sample transaction"""
    return {
        "transaction_id": "FIXTURE-001",
        "amount": 1000.00,
        "merchant": "Test Merchant",
        "category": "Test Category",
        "user_id": "EMP-TEST",
        "timestamp": "2025-01-15T10:30:00Z"
    }


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
