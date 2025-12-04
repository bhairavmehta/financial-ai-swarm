"""
Compliance Agent
OFAC/PEP screening and policy RAG implementation
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import re
import hashlib

# Vector database for policy RAG
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

logger = logging.getLogger(__name__)


@dataclass
class ComplianceResult:
    """Compliance check result"""
    status: str  # APPROVED, REJECTED, REVIEW_REQUIRED
    sanctions_hit: bool
    pep_hit: bool
    policy_violations: List[str]
    risk_score: float
    reviewed_policies: List[str]
    recommendations: List[str]
    timestamp: str


@dataclass
class SanctionsList:
    """Mock sanctions list entry"""
    entity_name: str
    entity_type: str  # INDIVIDUAL, ORGANIZATION
    country: str
    list_type: str  # OFAC, UN, EU
    added_date: str
    aliases: List[str]


class ComplianceAgent:
    """
    Compliance checking agent with OFAC/PEP screening and policy RAG
    """
    
    def __init__(self, policy_db_path: str = "data/policies"):
        self.policy_db_path = policy_db_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize sanctions lists (mock data)
        self.sanctions_lists = self._load_sanctions_lists()
        self.pep_list = self._load_pep_list()
        
        # Initialize policy RAG
        self.policy_embeddings = None
        self.policy_texts = []
        self.policy_index = None
        self._initialize_policy_rag()
        
    def _load_sanctions_lists(self) -> List[SanctionsList]:
        """Load mock OFAC sanctions lists"""
        # In production, this would connect to actual OFAC API
        mock_sanctions = [
            SanctionsList(
                entity_name="Suspicious Corp International",
                entity_type="ORGANIZATION",
                country="Country X",
                list_type="OFAC_SDN",
                added_date="2024-01-15",
                aliases=["SCI", "Sus Corp"]
            ),
            SanctionsList(
                entity_name="John Doe Sanctioned",
                entity_type="INDIVIDUAL",
                country="Country Y",
                list_type="OFAC_SDN",
                added_date="2023-06-20",
                aliases=["J. Doe", "Johnny Doe"]
            ),
            SanctionsList(
                entity_name="Blocked Vendor LLC",
                entity_type="ORGANIZATION",
                country="Country Z",
                list_type="EU_SANCTIONS",
                added_date="2024-03-10",
                aliases=["BV LLC"]
            )
        ]
        logger.info(f"Loaded {len(mock_sanctions)} sanctions entries")
        return mock_sanctions
    
    def _load_pep_list(self) -> Set[str]:
        """Load mock Politically Exposed Persons list"""
        # In production, connect to PEP database
        mock_peps = {
            "government official",
            "minister of finance",
            "senator",
            "ambassador",
            "military general",
            "central bank governor"
        }
        logger.info(f"Loaded {len(mock_peps)} PEP entries")
        return mock_peps
    
    def _initialize_policy_rag(self):
        """Initialize policy retrieval system with vector embeddings"""
        # Mock company policies
        self.policy_texts = [
            "All transactions above $10,000 require manager approval and documented business justification.",
            "Expenses for entertainment and gifts are limited to $500 per event and must have detailed receipts.",
            "Travel expenses must be booked through approved corporate travel agency. Economy class required for flights under 6 hours.",
            "IT equipment purchases require IT department approval and must meet security standards.",
            "Vendor payments require three competitive bids for contracts over $25,000.",
            "Personal purchases or gifts using company funds are strictly prohibited.",
            "All foreign transactions must be screened for OFAC compliance before processing.",
            "Consulting services require documented statements of work and deliverables.",
            "Recurring subscriptions must be reviewed quarterly for necessity and cost optimization.",
            "Cash advances are limited to $1,000 and require repayment within 30 days with receipts."
        ]
        
        # Generate embeddings
        logger.info("Generating policy embeddings for RAG")
        self.policy_embeddings = self.embedding_model.encode(self.policy_texts)
        
        # Create FAISS index for fast similarity search
        dimension = self.policy_embeddings.shape[1]
        self.policy_index = faiss.IndexFlatL2(dimension)
        self.policy_index.add(self.policy_embeddings.astype('float32'))
        
        logger.info(f"Policy RAG initialized with {len(self.policy_texts)} policies")
    
    def _check_sanctions(self, entity_name: str, entity_type: str = "ORGANIZATION") -> tuple[bool, List[str]]:
        """Check if entity is on sanctions list"""
        entity_lower = entity_name.lower()
        matches = []
        
        for sanction in self.sanctions_lists:
            # Check main name
            if sanction.entity_name.lower() in entity_lower or entity_lower in sanction.entity_name.lower():
                matches.append(f"Matched {sanction.list_type}: {sanction.entity_name}")
                continue
            
            # Check aliases
            for alias in sanction.aliases:
                if alias.lower() in entity_lower or entity_lower in alias.lower():
                    matches.append(f"Matched {sanction.list_type} alias: {alias} -> {sanction.entity_name}")
                    break
        
        hit = len(matches) > 0
        if hit:
            logger.warning(f"SANCTIONS HIT: {entity_name} - {matches}")
        
        return hit, matches
    
    def _check_pep(self, entity_description: str) -> tuple[bool, List[str]]:
        """Check if entity might be a Politically Exposed Person"""
        desc_lower = entity_description.lower()
        matches = []
        
        for pep_term in self.pep_list:
            if pep_term in desc_lower:
                matches.append(f"PEP indicator: {pep_term}")
        
        hit = len(matches) > 0
        if hit:
            logger.warning(f"PEP HIT: {entity_description} - {matches}")
        
        return hit, matches
    
    def _retrieve_relevant_policies(self, transaction: Dict, k: int = 3) -> List[str]:
        """Retrieve relevant policies using RAG"""
        # Create query from transaction
        query_parts = [
            f"Transaction amount ${transaction.get('amount', 0)}",
            f"Category: {transaction.get('category', 'unknown')}",
            f"Merchant: {transaction.get('merchant', 'unknown')}"
        ]
        query = " ".join(query_parts)
        
        # Encode query
        query_embedding = self.embedding_model.encode([query])
        
        # Search for similar policies
        distances, indices = self.policy_index.search(
            query_embedding.astype('float32'), 
            k
        )
        
        relevant_policies = [self.policy_texts[idx] for idx in indices[0]]
        logger.info(f"Retrieved {len(relevant_policies)} relevant policies")
        
        return relevant_policies
    
    def _check_policy_violations(self, transaction: Dict, policies: List[str]) -> List[str]:
        """Check for policy violations"""
        violations = []
        amount = float(transaction.get('amount', 0))
        category = transaction.get('category', '').lower()
        
        # Check against each policy
        for policy in policies:
            policy_lower = policy.lower()
            
            # Amount thresholds
            if 'above $10,000' in policy_lower and amount > 10000:
                if not transaction.get('manager_approval'):
                    violations.append(f"Policy violation: {policy}")
            
            if 'above $25,000' in policy_lower and amount > 25000:
                if not transaction.get('competitive_bids'):
                    violations.append(f"Policy violation: {policy}")
            
            # Entertainment limits
            if 'entertainment' in policy_lower and 'entertainment' in category:
                if amount > 500:
                    violations.append(f"Policy violation: {policy}")
            
            # Travel requirements
            if 'travel' in policy_lower and 'travel' in category:
                if not transaction.get('corporate_booking'):
                    violations.append(f"Policy violation: {policy}")
        
        return violations
    
    def check_compliance(self, transaction: Dict) -> ComplianceResult:
        """
        Main compliance check method
        
        Args:
            transaction: Transaction data including merchant, amount, etc.
            
        Returns:
            ComplianceResult with detailed compliance status
        """
        logger.info(f"Checking compliance for transaction: {transaction.get('transaction_id')}")
        
        merchant = transaction.get('merchant', 'Unknown')
        amount = float(transaction.get('amount', 0))
        
        # Check sanctions
        sanctions_hit, sanction_matches = self._check_sanctions(merchant)
        
        # Check PEP
        merchant_description = transaction.get('merchant_description', merchant)
        pep_hit, pep_matches = self._check_pep(merchant_description)
        
        # Retrieve and check policies
        relevant_policies = self._retrieve_relevant_policies(transaction)
        policy_violations = self._check_policy_violations(transaction, relevant_policies)
        
        # Calculate risk score
        risk_score = 0.0
        if sanctions_hit:
            risk_score += 0.8
        if pep_hit:
            risk_score += 0.3
        risk_score += len(policy_violations) * 0.1
        risk_score = min(risk_score, 1.0)
        
        # Determine status
        if sanctions_hit:
            status = "REJECTED"
        elif pep_hit or len(policy_violations) > 2 or risk_score > 0.7:
            status = "REVIEW_REQUIRED"
        elif len(policy_violations) > 0:
            status = "REVIEW_REQUIRED"
        else:
            status = "APPROVED"
        
        # Generate recommendations
        recommendations = []
        if sanctions_hit:
            recommendations.append("IMMEDIATE ESCALATION: Sanctions match detected")
            recommendations.extend(sanction_matches)
        if pep_hit:
            recommendations.append("Enhanced due diligence required for PEP")
            recommendations.extend(pep_matches)
        if policy_violations:
            recommendations.append("Resolve policy violations before approval")
        if status == "APPROVED" and amount > 5000:
            recommendations.append("Consider additional documentation for audit trail")
        
        result = ComplianceResult(
            status=status,
            sanctions_hit=sanctions_hit,
            pep_hit=pep_hit,
            policy_violations=policy_violations,
            risk_score=risk_score,
            reviewed_policies=relevant_policies,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Compliance check complete: {status} (risk: {risk_score:.2f})")
        return result
    
    def batch_check(self, transactions: List[Dict]) -> List[ComplianceResult]:
        """Batch process multiple transactions"""
        return [self.check_compliance(txn) for txn in transactions]
    
    def update_sanctions_list(self, new_entries: List[SanctionsList]):
        """Update sanctions list with new entries"""
        self.sanctions_lists.extend(new_entries)
        logger.info(f"Added {len(new_entries)} new sanctions entries")
    
    def add_policy(self, policy_text: str):
        """Add a new policy to the RAG system"""
        self.policy_texts.append(policy_text)
        
        # Re-generate embeddings
        new_embedding = self.embedding_model.encode([policy_text])
        self.policy_index.add(new_embedding.astype('float32'))
        
        logger.info(f"Added new policy: {policy_text[:50]}...")


# Global agent instance
_compliance_agent = None

def get_compliance_agent() -> ComplianceAgent:
    """Get or create global compliance agent"""
    global _compliance_agent
    if _compliance_agent is None:
        _compliance_agent = ComplianceAgent()
    return _compliance_agent


if __name__ == "__main__":
    # Test the compliance agent
    logging.basicConfig(level=logging.INFO)
    
    test_transactions = [
        {
            "transaction_id": "TXN-001",
            "amount": 500.00,
            "merchant": "Local Restaurant",
            "category": "Entertainment",
            "merchant_description": "Business dinner"
        },
        {
            "transaction_id": "TXN-002",
            "amount": 15000.00,
            "merchant": "Suspicious Corp International",
            "category": "Consulting",
            "merchant_description": "Consulting services"
        },
        {
            "transaction_id": "TXN-003",
            "amount": 30000.00,
            "merchant": "Tech Vendor",
            "category": "IT Services",
            "merchant_description": "Software licenses"
        }
    ]
    
    agent = ComplianceAgent()
    
    for txn in test_transactions:
        result = agent.check_compliance(txn)
        print(f"\nTransaction: {txn['transaction_id']}")
        print(f"Status: {result.status}")
        print(f"Risk Score: {result.risk_score:.2f}")
        print(f"Sanctions Hit: {result.sanctions_hit}")
        print(f"PEP Hit: {result.pep_hit}")
        print(f"Violations: {result.policy_violations}")
        print(f"Recommendations: {result.recommendations}")
