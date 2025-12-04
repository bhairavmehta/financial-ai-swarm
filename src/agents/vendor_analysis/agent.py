"""
Vendor Analysis Agent
Analyzes vendor relationships, detects duplicates, assesses risk
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class VendorRiskProfile:
    """Vendor risk assessment result"""
    vendor_id: str
    vendor_name: str
    risk_score: float  # 0-1, higher = riskier
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_factors: List[str]
    payment_patterns: Dict
    duplicate_likelihood: float
    recommendations: List[str]
    total_spend: float
    transaction_count: int
    avg_transaction_amount: float


@dataclass
class DuplicateDetectionResult:
    """Duplicate vendor detection result"""
    vendor_1: str
    vendor_2: str
    similarity_score: float
    duplicate_probability: float
    matching_factors: List[str]
    recommended_action: str


class VendorAnalysisAgent:
    """
    Vendor analysis and risk assessment agent
    """

    # Risk thresholds
    RISK_THRESHOLDS = {
        "LOW": 0.3,
        "MEDIUM": 0.5,
        "HIGH": 0.7,
        "CRITICAL": 0.85
    }

    def __init__(self):
        self.vendor_history = defaultdict(list)
        self.vendor_metadata = {}
        logger.info("Vendor Analysis Agent initialized")

    def analyze_vendor(self, vendor_name: str, transactions: List[Dict]) -> VendorRiskProfile:
        """
        Analyze a vendor based on transaction history

        Args:
            vendor_name: Name of the vendor
            transactions: List of transactions with this vendor

        Returns:
            VendorRiskProfile with analysis results
        """
        logger.info(f"Analyzing vendor: {vendor_name}")

        if not transactions:
            return self._create_default_profile(vendor_name)

        # Calculate basic statistics
        total_spend = sum(float(t.get('amount', 0)) for t in transactions)
        transaction_count = len(transactions)
        avg_amount = total_spend / transaction_count if transaction_count > 0 else 0

        # Analyze payment patterns
        payment_patterns = self._analyze_payment_patterns(transactions)

        # Calculate risk factors
        risk_factors = self._identify_vendor_risk_factors(
            vendor_name, transactions, payment_patterns
        )

        # Calculate overall risk score
        risk_score = self._calculate_vendor_risk_score(
            transactions, payment_patterns, risk_factors
        )

        # Determine risk level
        risk_level = self._get_risk_level(risk_score)

        # Generate recommendations
        recommendations = self._generate_vendor_recommendations(
            vendor_name, risk_score, risk_factors, payment_patterns
        )

        # Calculate duplicate likelihood
        duplicate_likelihood = self._calculate_duplicate_likelihood(vendor_name)

        profile = VendorRiskProfile(
            vendor_id=f"VND-{hash(vendor_name) % 100000:05d}",
            vendor_name=vendor_name,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            payment_patterns=payment_patterns,
            duplicate_likelihood=duplicate_likelihood,
            recommendations=recommendations,
            total_spend=total_spend,
            transaction_count=transaction_count,
            avg_transaction_amount=avg_amount
        )

        # Update history
        self.vendor_history[vendor_name] = transactions
        self.vendor_metadata[vendor_name] = profile

        logger.info(f"Vendor analysis complete: {risk_level} risk (score: {risk_score:.3f})")
        return profile

    def _analyze_payment_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze payment patterns for anomalies"""
        if not transactions:
            return {}

        amounts = [float(t.get('amount', 0)) for t in transactions]
        timestamps = []

        for t in transactions:
            ts = t.get('timestamp', datetime.now().isoformat())
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            timestamps.append(ts)

        # Calculate time intervals
        intervals = []
        if len(timestamps) > 1:
            sorted_times = sorted(timestamps)
            intervals = [(sorted_times[i+1] - sorted_times[i]).days
                        for i in range(len(sorted_times)-1)]

        return {
            'total_amount': sum(amounts),
            'avg_amount': np.mean(amounts) if amounts else 0,
            'std_amount': np.std(amounts) if len(amounts) > 1 else 0,
            'min_amount': min(amounts) if amounts else 0,
            'max_amount': max(amounts) if amounts else 0,
            'transaction_count': len(transactions),
            'avg_interval_days': np.mean(intervals) if intervals else 0,
            'std_interval_days': np.std(intervals) if len(intervals) > 1 else 0,
            'regularity_score': 1.0 / (1 + np.std(intervals)) if intervals else 0.5
        }

    def _identify_vendor_risk_factors(
        self,
        vendor_name: str,
        transactions: List[Dict],
        payment_patterns: Dict
    ) -> List[str]:
        """Identify specific risk factors for a vendor"""
        risk_factors = []

        # High spend concentration
        total_spend = payment_patterns.get('total_amount', 0)
        if total_spend > 100000:
            risk_factors.append(f"High total spend: ${total_spend:,.2f}")

        # Large transaction variability
        std_amount = payment_patterns.get('std_amount', 0)
        avg_amount = payment_patterns.get('avg_amount', 0)
        if avg_amount > 0 and std_amount / avg_amount > 0.8:
            risk_factors.append("High payment amount variability")

        # Irregular payment schedule
        regularity = payment_patterns.get('regularity_score', 0.5)
        if regularity < 0.3:
            risk_factors.append("Irregular payment schedule")

        # Round number payments (potential shell companies)
        amounts = [float(t.get('amount', 0)) for t in transactions]
        round_number_count = sum(1 for a in amounts if a % 1000 == 0 and a >= 1000)
        if round_number_count / len(amounts) > 0.5 if amounts else False:
            risk_factors.append("Frequent round-number payments (potential shell company)")

        # Rapid payment frequency
        avg_interval = payment_patterns.get('avg_interval_days', 365)
        if avg_interval < 7 and len(transactions) > 5:
            risk_factors.append(f"High payment frequency (avg {avg_interval:.1f} days)")

        # Suspicious vendor name patterns
        suspicious_keywords = ['shell', 'offshore', 'consulting', 'services', 'holdings']
        vendor_lower = vendor_name.lower()
        if any(keyword in vendor_lower for keyword in suspicious_keywords):
            risk_factors.append("Vendor name contains potentially suspicious keywords")

        # New vendor with large transactions
        if len(transactions) < 3 and avg_amount > 10000:
            risk_factors.append("New vendor with large transaction amounts")

        return risk_factors

    def _calculate_vendor_risk_score(
        self,
        transactions: List[Dict],
        payment_patterns: Dict,
        risk_factors: List[str]
    ) -> float:
        """Calculate overall vendor risk score"""
        score = 0.0

        # Base score from number of risk factors
        score += min(len(risk_factors) * 0.15, 0.6)

        # Amount variability contribution
        std_amount = payment_patterns.get('std_amount', 0)
        avg_amount = payment_patterns.get('avg_amount', 1)
        variability = min(std_amount / avg_amount, 2.0) if avg_amount > 0 else 0
        score += variability * 0.1

        # Irregularity contribution
        regularity = payment_patterns.get('regularity_score', 0.5)
        score += (1 - regularity) * 0.2

        # High spend contribution
        total_spend = payment_patterns.get('total_amount', 0)
        if total_spend > 50000:
            score += min(total_spend / 500000, 0.2)

        return min(score, 1.0)

    def _get_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score >= self.RISK_THRESHOLDS['CRITICAL']:
            return 'CRITICAL'
        elif risk_score >= self.RISK_THRESHOLDS['HIGH']:
            return 'HIGH'
        elif risk_score >= self.RISK_THRESHOLDS['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_vendor_recommendations(
        self,
        vendor_name: str,
        risk_score: float,
        risk_factors: List[str],
        payment_patterns: Dict
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if risk_score >= self.RISK_THRESHOLDS['HIGH']:
            recommendations.append("Conduct enhanced due diligence on this vendor")
            recommendations.append("Require additional documentation for future payments")

        if risk_score >= self.RISK_THRESHOLDS['CRITICAL']:
            recommendations.append("Immediate review required - consider payment hold")
            recommendations.append("Escalate to procurement and legal teams")

        # Specific recommendations based on patterns
        regularity = payment_patterns.get('regularity_score', 0.5)
        if regularity > 0.8:
            recommendations.append("Consider setting up automated recurring payments")

        total_spend = payment_patterns.get('total_amount', 0)
        if total_spend > 100000:
            recommendations.append("Negotiate volume discount or payment terms")

        # Duplicate check recommendation
        if self._calculate_duplicate_likelihood(vendor_name) > 0.5:
            recommendations.append("Check for potential duplicate vendor entries")

        if not recommendations:
            recommendations.append("No immediate action required - continue monitoring")

        return recommendations

    def _calculate_duplicate_likelihood(self, vendor_name: str) -> float:
        """Calculate likelihood of duplicate vendor entries"""
        max_similarity = 0.0

        for existing_vendor in self.vendor_metadata.keys():
            if existing_vendor != vendor_name:
                similarity = self._calculate_name_similarity(vendor_name, existing_vendor)
                max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two vendor names"""
        # Normalize names
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()

        # Remove common suffixes
        suffixes = ['inc', 'llc', 'ltd', 'corp', 'corporation', 'company', 'co']
        for suffix in suffixes:
            n1 = n1.replace(suffix, '').strip()
            n2 = n2.replace(suffix, '').strip()

        # Calculate sequence similarity
        return SequenceMatcher(None, n1, n2).ratio()

    def detect_duplicates(
        self,
        vendors: List[str],
        threshold: float = 0.8
    ) -> List[DuplicateDetectionResult]:
        """
        Detect potential duplicate vendors

        Args:
            vendors: List of vendor names to check
            threshold: Similarity threshold for duplicate detection

        Returns:
            List of potential duplicate pairs
        """
        logger.info(f"Checking {len(vendors)} vendors for duplicates")
        duplicates = []

        for i in range(len(vendors)):
            for j in range(i + 1, len(vendors)):
                similarity = self._calculate_name_similarity(vendors[i], vendors[j])

                if similarity >= threshold:
                    matching_factors = self._identify_matching_factors(
                        vendors[i], vendors[j]
                    )

                    result = DuplicateDetectionResult(
                        vendor_1=vendors[i],
                        vendor_2=vendors[j],
                        similarity_score=similarity,
                        duplicate_probability=similarity,
                        matching_factors=matching_factors,
                        recommended_action=self._recommend_duplicate_action(similarity)
                    )
                    duplicates.append(result)

        logger.info(f"Found {len(duplicates)} potential duplicate pairs")
        return duplicates

    def _identify_matching_factors(self, vendor1: str, vendor2: str) -> List[str]:
        """Identify what makes vendors similar"""
        factors = []

        v1_lower = vendor1.lower()
        v2_lower = vendor2.lower()

        # Check for common words
        words1 = set(v1_lower.split())
        words2 = set(v2_lower.split())
        common_words = words1.intersection(words2)

        if common_words:
            factors.append(f"Common words: {', '.join(common_words)}")

        # Check for abbreviations
        if v1_lower[:3] == v2_lower[:3]:
            factors.append("Similar prefixes")

        # Check edit distance
        similarity = SequenceMatcher(None, v1_lower, v2_lower).ratio()
        if similarity > 0.9:
            factors.append(f"Very high text similarity ({similarity:.1%})")

        return factors

    def _recommend_duplicate_action(self, similarity: float) -> str:
        """Recommend action based on duplicate similarity"""
        if similarity >= 0.95:
            return "MERGE - Almost certain duplicate"
        elif similarity >= 0.85:
            return "REVIEW - Likely duplicate, manual review recommended"
        else:
            return "MONITOR - Possible duplicate, continue monitoring"

    def _create_default_profile(self, vendor_name: str) -> VendorRiskProfile:
        """Create a default profile for vendors with no transaction history"""
        return VendorRiskProfile(
            vendor_id=f"VND-{hash(vendor_name) % 100000:05d}",
            vendor_name=vendor_name,
            risk_score=0.5,
            risk_level='MEDIUM',
            risk_factors=['No transaction history available'],
            payment_patterns={},
            duplicate_likelihood=0.0,
            recommendations=['New vendor - establish transaction history before assessment'],
            total_spend=0.0,
            transaction_count=0,
            avg_transaction_amount=0.0
        )

    def get_vendor_consolidation_opportunities(self) -> List[Dict]:
        """Identify opportunities to consolidate vendors"""
        opportunities = []

        # Group vendors by category/type
        vendor_groups = defaultdict(list)

        for vendor_name, profile in self.vendor_metadata.items():
            # Simple categorization based on name
            category = self._categorize_vendor(vendor_name)
            vendor_groups[category].append({
                'name': vendor_name,
                'spend': profile.total_spend,
                'count': profile.transaction_count
            })

        # Identify consolidation opportunities
        for category, vendors in vendor_groups.items():
            if len(vendors) >= 3:
                total_spend = sum(v['spend'] for v in vendors)
                opportunities.append({
                    'category': category,
                    'vendor_count': len(vendors),
                    'total_spend': total_spend,
                    'vendors': [v['name'] for v in vendors],
                    'recommendation': f"Consider consolidating {len(vendors)} vendors in {category} category",
                    'potential_savings': total_spend * 0.05  # Estimate 5% savings
                })

        return sorted(opportunities, key=lambda x: x['potential_savings'], reverse=True)

    def _categorize_vendor(self, vendor_name: str) -> str:
        """Simple vendor categorization"""
        name_lower = vendor_name.lower()

        if any(word in name_lower for word in ['tech', 'software', 'computer', 'it']):
            return 'Technology'
        elif any(word in name_lower for word in ['office', 'supply', 'supplies']):
            return 'Office Supplies'
        elif any(word in name_lower for word in ['consult', 'advisory', 'services']):
            return 'Consulting'
        elif any(word in name_lower for word in ['travel', 'hotel', 'airline']):
            return 'Travel'
        else:
            return 'Other'


# Global agent instance
_vendor_agent = None

def get_vendor_agent() -> VendorAnalysisAgent:
    """Get or create global vendor analysis agent"""
    global _vendor_agent
    if _vendor_agent is None:
        _vendor_agent = VendorAnalysisAgent()
    return _vendor_agent


if __name__ == "__main__":
    # Test the vendor analysis agent
    logging.basicConfig(level=logging.INFO)

    test_transactions = [
        {
            "transaction_id": "TXN-001",
            "amount": 5000.00,
            "merchant": "Tech Solutions Inc",
            "timestamp": "2025-01-01T10:00:00Z"
        },
        {
            "transaction_id": "TXN-002",
            "amount": 5000.00,
            "merchant": "Tech Solutions Inc",
            "timestamp": "2025-01-15T10:00:00Z"
        },
        {
            "transaction_id": "TXN-003",
            "amount": 15000.00,
            "merchant": "Tech Solutions Inc",
            "timestamp": "2025-01-30T10:00:00Z"
        }
    ]

    agent = VendorAnalysisAgent()

    # Analyze vendor
    profile = agent.analyze_vendor("Tech Solutions Inc", test_transactions)
    print(f"\nVendor: {profile.vendor_name}")
    print(f"Risk Level: {profile.risk_level}")
    print(f"Risk Score: {profile.risk_score:.3f}")
    print(f"Total Spend: ${profile.total_spend:,.2f}")
    print(f"Risk Factors: {profile.risk_factors}")
    print(f"Recommendations: {profile.recommendations}")

    # Test duplicate detection
    vendors = ["Tech Solutions Inc", "Tech Solutions LLC", "Office Supplies Co"]
    duplicates = agent.detect_duplicates(vendors)
    print(f"\n\nDuplicate Detection:")
    for dup in duplicates:
        print(f"{dup.vendor_1} vs {dup.vendor_2}")
        print(f"  Similarity: {dup.similarity_score:.3f}")
        print(f"  Action: {dup.recommended_action}")
