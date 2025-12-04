"""
Explanation Generator Agent
Provides natural language explanations of financial decisions and analyses
Uses LLM to generate human-friendly explanations
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Explanation:
    """Generated explanation result"""
    title: str
    summary: str
    detailed_explanation: str
    key_points: List[str]
    recommendations: List[str]
    confidence_level: str
    generated_at: datetime


class ExplanationGeneratorAgent:
    """
    Generates natural language explanations for financial decisions
    """

    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize explanation generator

        Args:
            llm_provider: LLM provider to use (openai, anthropic, or None for templates)
        """
        self.llm_provider = llm_provider
        logger.info(f"Explanation Generator initialized with provider: {llm_provider or 'template-based'}")

    def explain_fraud_detection(
        self,
        transaction: Dict,
        fraud_result: Dict
    ) -> Explanation:
        """
        Explain fraud detection results

        Args:
            transaction: Transaction data
            fraud_result: Fraud detection results

        Returns:
            Explanation object
        """
        logger.info(f"Generating fraud explanation for transaction {transaction.get('transaction_id')}")

        risk_level = fraud_result.get('risk_level', 'UNKNOWN')
        risk_score = fraud_result.get('overall_score', 0.0)
        risk_factors = fraud_result.get('risk_factors', [])
        confidence = fraud_result.get('confidence', 0.0)

        # Generate title
        title = f"Fraud Analysis: {risk_level} Risk Detected"

        # Generate summary
        summary = self._generate_fraud_summary(transaction, risk_level, risk_score)

        # Generate detailed explanation
        detailed = self._generate_fraud_detailed(
            transaction, risk_level, risk_score, risk_factors
        )

        # Extract key points
        key_points = self._extract_fraud_key_points(risk_level, risk_factors, risk_score)

        # Generate recommendations
        recommendations = self._generate_fraud_recommendations(risk_level, risk_factors)

        # Determine confidence level
        confidence_level = self._map_confidence_level(confidence)

        return Explanation(
            title=title,
            summary=summary,
            detailed_explanation=detailed,
            key_points=key_points,
            recommendations=recommendations,
            confidence_level=confidence_level,
            generated_at=datetime.now()
        )

    def explain_compliance_check(
        self,
        entity: Dict,
        compliance_result: Dict
    ) -> Explanation:
        """
        Explain compliance checking results

        Args:
            entity: Entity being checked (merchant/vendor)
            compliance_result: Compliance check results

        Returns:
            Explanation object
        """
        logger.info(f"Generating compliance explanation for {entity.get('name')}")

        status = compliance_result.get('status', 'UNKNOWN')
        risk_score = compliance_result.get('risk_score', 0.0)
        findings = compliance_result.get('findings', [])
        sanctions_hit = compliance_result.get('sanctions_hit', False)
        pep_hit = compliance_result.get('pep_hit', False)

        # Generate components
        title = f"Compliance Check: {status}"
        summary = self._generate_compliance_summary(entity, status, sanctions_hit, pep_hit)
        detailed = self._generate_compliance_detailed(entity, compliance_result)
        key_points = self._extract_compliance_key_points(status, findings, sanctions_hit, pep_hit)
        recommendations = self._generate_compliance_recommendations(status, sanctions_hit, pep_hit)

        return Explanation(
            title=title,
            summary=summary,
            detailed_explanation=detailed,
            key_points=key_points,
            recommendations=recommendations,
            confidence_level="HIGH",
            generated_at=datetime.now()
        )

    def explain_spend_analysis(
        self,
        analysis_result: Dict
    ) -> Explanation:
        """
        Explain spend analysis results

        Args:
            analysis_result: Spend analysis results

        Returns:
            Explanation object
        """
        logger.info("Generating spend analysis explanation")

        budget_status = analysis_result.get('budget_status', {})
        anomalies = analysis_result.get('anomalies', [])
        trends = analysis_result.get('trends', {})

        title = "Spend Analysis Report"
        summary = self._generate_spend_summary(budget_status, anomalies)
        detailed = self._generate_spend_detailed(budget_status, anomalies, trends)
        key_points = self._extract_spend_key_points(budget_status, anomalies, trends)
        recommendations = self._generate_spend_recommendations(budget_status, anomalies)

        return Explanation(
            title=title,
            summary=summary,
            detailed_explanation=detailed,
            key_points=key_points,
            recommendations=recommendations,
            confidence_level="MEDIUM",
            generated_at=datetime.now()
        )

    def explain_vendor_analysis(
        self,
        vendor_profile: Dict
    ) -> Explanation:
        """
        Explain vendor analysis results

        Args:
            vendor_profile: Vendor risk profile

        Returns:
            Explanation object
        """
        logger.info(f"Generating vendor analysis explanation for {vendor_profile.get('vendor_name')}")

        vendor_name = vendor_profile.get('vendor_name', 'Unknown')
        risk_level = vendor_profile.get('risk_level', 'UNKNOWN')
        risk_score = vendor_profile.get('risk_score', 0.0)
        risk_factors = vendor_profile.get('risk_factors', [])
        total_spend = vendor_profile.get('total_spend', 0.0)

        title = f"Vendor Analysis: {vendor_name}"
        summary = self._generate_vendor_summary(vendor_name, risk_level, total_spend)
        detailed = self._generate_vendor_detailed(vendor_profile)
        key_points = self._extract_vendor_key_points(vendor_profile)
        recommendations = vendor_profile.get('recommendations', [])

        return Explanation(
            title=title,
            summary=summary,
            detailed_explanation=detailed,
            key_points=key_points,
            recommendations=recommendations,
            confidence_level="MEDIUM",
            generated_at=datetime.now()
        )

    def _generate_fraud_summary(self, transaction: Dict, risk_level: str, risk_score: float) -> str:
        """Generate fraud detection summary"""
        amount = transaction.get('amount', 0)
        merchant = transaction.get('merchant', 'Unknown')

        if risk_level == 'CRITICAL':
            return (f"CRITICAL fraud risk detected for ${amount:,.2f} transaction at {merchant}. "
                   f"Score: {risk_score:.2f}. Immediate review required.")
        elif risk_level == 'HIGH':
            return (f"HIGH fraud risk detected for ${amount:,.2f} transaction at {merchant}. "
                   f"Score: {risk_score:.2f}. Manual review recommended.")
        elif risk_level == 'MEDIUM':
            return (f"MEDIUM fraud risk for ${amount:,.2f} transaction at {merchant}. "
                   f"Score: {risk_score:.2f}. Additional monitoring advised.")
        else:
            return (f"LOW fraud risk for ${amount:,.2f} transaction at {merchant}. "
                   f"Score: {risk_score:.2f}. Transaction appears normal.")

    def _generate_fraud_detailed(
        self,
        transaction: Dict,
        risk_level: str,
        risk_score: float,
        risk_factors: List[str]
    ) -> str:
        """Generate detailed fraud explanation"""
        parts = []

        parts.append(f"Transaction Details:")
        parts.append(f"- Transaction ID: {transaction.get('transaction_id', 'N/A')}")
        parts.append(f"- Amount: ${transaction.get('amount', 0):,.2f}")
        parts.append(f"- Merchant: {transaction.get('merchant', 'Unknown')}")
        parts.append(f"- Category: {transaction.get('category', 'Unknown')}")
        parts.append(f"- Date: {transaction.get('timestamp', 'N/A')}")
        parts.append("")

        parts.append(f"Fraud Analysis Results:")
        parts.append(f"- Overall Risk Score: {risk_score:.3f} (0-1 scale)")
        parts.append(f"- Risk Level: {risk_level}")
        parts.append("")

        if risk_factors:
            parts.append("Risk Factors Identified:")
            for factor in risk_factors:
                parts.append(f"- {factor}")
            parts.append("")

        parts.append("Analysis Method:")
        parts.append("- Multi-model ensemble using 5 anomaly detection algorithms")
        parts.append("- Isolation Forest, LOF, KNN, CBLOF, and HBOS models")
        parts.append("- Weighted voting for final risk score")

        return "\n".join(parts)

    def _extract_fraud_key_points(
        self,
        risk_level: str,
        risk_factors: List[str],
        risk_score: float
    ) -> List[str]:
        """Extract key points from fraud analysis"""
        points = []

        points.append(f"Risk Level: {risk_level} (Score: {risk_score:.2f})")

        if risk_factors:
            points.append(f"Identified {len(risk_factors)} risk factor(s)")
            points.extend(risk_factors[:3])  # Top 3 factors

        if risk_level in ['HIGH', 'CRITICAL']:
            points.append("Immediate action required")

        return points

    def _generate_fraud_recommendations(
        self,
        risk_level: str,
        risk_factors: List[str]
    ) -> List[str]:
        """Generate fraud-related recommendations"""
        recommendations = []

        if risk_level == 'CRITICAL':
            recommendations.append("Block transaction immediately")
            recommendations.append("Contact user to verify transaction")
            recommendations.append("Escalate to fraud investigation team")
            recommendations.append("Review user's recent transaction history")
        elif risk_level == 'HIGH':
            recommendations.append("Hold transaction for manual review")
            recommendations.append("Request additional verification from user")
            recommendations.append("Check for similar patterns in recent transactions")
        elif risk_level == 'MEDIUM':
            recommendations.append("Monitor transaction closely")
            recommendations.append("Flag for follow-up review")
            recommendations.append("Consider increasing monitoring on this account")
        else:
            recommendations.append("Approve transaction")
            recommendations.append("Continue standard monitoring")

        return recommendations

    def _generate_compliance_summary(
        self,
        entity: Dict,
        status: str,
        sanctions_hit: bool,
        pep_hit: bool
    ) -> str:
        """Generate compliance check summary"""
        name = entity.get('name', 'Unknown')

        if sanctions_hit:
            return (f"SANCTIONS HIT: {name} appears on sanctions lists. "
                   f"Transaction must be blocked immediately.")
        elif pep_hit:
            return (f"PEP MATCH: {name} is identified as a Politically Exposed Person. "
                   f"Enhanced due diligence required.")
        elif status == 'APPROVED':
            return f"APPROVED: {name} passed all compliance checks. Clear to proceed."
        elif status == 'REVIEW':
            return f"REVIEW REQUIRED: {name} flagged for manual compliance review."
        else:
            return f"REJECTED: {name} failed compliance screening."

    def _generate_compliance_detailed(self, entity: Dict, compliance_result: Dict) -> str:
        """Generate detailed compliance explanation"""
        parts = []

        parts.append("Entity Information:")
        parts.append(f"- Name: {entity.get('name', 'Unknown')}")
        parts.append(f"- Type: {entity.get('type', 'Vendor')}")
        parts.append("")

        parts.append("Compliance Screening Results:")
        parts.append(f"- Status: {compliance_result.get('status', 'UNKNOWN')}")
        parts.append(f"- Risk Score: {compliance_result.get('risk_score', 0.0):.3f}")
        parts.append(f"- Sanctions Hit: {'YES' if compliance_result.get('sanctions_hit') else 'NO'}")
        parts.append(f"- PEP Hit: {'YES' if compliance_result.get('pep_hit') else 'NO'}")
        parts.append("")

        findings = compliance_result.get('findings', [])
        if findings:
            parts.append("Findings:")
            for finding in findings:
                parts.append(f"- {finding}")
            parts.append("")

        parts.append("Screening Sources:")
        parts.append("- OFAC Sanctions Lists")
        parts.append("- Politically Exposed Persons (PEP) Database")
        parts.append("- Internal Policy Database (RAG-based)")

        return "\n".join(parts)

    def _extract_compliance_key_points(
        self,
        status: str,
        findings: List[str],
        sanctions_hit: bool,
        pep_hit: bool
    ) -> List[str]:
        """Extract key points from compliance check"""
        points = []

        points.append(f"Status: {status}")

        if sanctions_hit:
            points.append("⚠️ SANCTIONS LIST MATCH - BLOCK IMMEDIATELY")

        if pep_hit:
            points.append("⚠️ PEP IDENTIFIED - Enhanced Due Diligence Required")

        if findings:
            points.extend(findings[:2])

        return points

    def _generate_compliance_recommendations(
        self,
        status: str,
        sanctions_hit: bool,
        pep_hit: bool
    ) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []

        if sanctions_hit:
            recommendations.append("IMMEDIATE: Block all transactions")
            recommendations.append("Report to OFAC compliance team")
            recommendations.append("Document all interactions")
            recommendations.append("Do not notify the entity")
        elif pep_hit:
            recommendations.append("Conduct enhanced due diligence")
            recommendations.append("Obtain additional documentation")
            recommendations.append("Review source of funds")
            recommendations.append("Escalate to compliance officer")
        elif status == 'APPROVED':
            recommendations.append("Proceed with transaction")
            recommendations.append("Maintain standard monitoring")
        else:
            recommendations.append("Conduct manual review")
            recommendations.append("Request additional information")

        return recommendations

    def _generate_spend_summary(self, budget_status: Dict, anomalies: List) -> str:
        """Generate spend analysis summary"""
        total_categories = len(budget_status)
        over_budget = sum(1 for cat, data in budget_status.items()
                         if data.get('utilization', 0) > 1.0)

        if over_budget > 0:
            return (f"Budget Alert: {over_budget} of {total_categories} categories over budget. "
                   f"{len(anomalies)} spending anomalies detected.")
        else:
            return (f"Spending within budget across {total_categories} categories. "
                   f"{len(anomalies)} anomalies identified for review.")

    def _generate_spend_detailed(
        self,
        budget_status: Dict,
        anomalies: List,
        trends: Dict
    ) -> str:
        """Generate detailed spend explanation"""
        parts = []

        parts.append("Budget Status by Category:")
        for category, data in budget_status.items():
            utilization = data.get('utilization', 0) * 100
            spent = data.get('spent', 0)
            budget = data.get('budget', 0)
            status_icon = "⚠️" if utilization > 100 else "✓"
            parts.append(f"{status_icon} {category}: ${spent:,.2f} / ${budget:,.2f} ({utilization:.1f}%)")
        parts.append("")

        if anomalies:
            parts.append(f"Anomalies Detected ({len(anomalies)}):")
            for anomaly in anomalies[:5]:  # Top 5
                parts.append(f"- {anomaly}")
            parts.append("")

        if trends:
            parts.append("Spending Trends:")
            for trend_name, trend_data in trends.items():
                parts.append(f"- {trend_name}: {trend_data}")

        return "\n".join(parts)

    def _extract_spend_key_points(
        self,
        budget_status: Dict,
        anomalies: List,
        trends: Dict
    ) -> List[str]:
        """Extract key points from spend analysis"""
        points = []

        # Find categories over budget
        over_budget = [(cat, data) for cat, data in budget_status.items()
                      if data.get('utilization', 0) > 1.0]

        if over_budget:
            for cat, data in over_budget[:2]:  # Top 2
                util = data.get('utilization', 0) * 100
                points.append(f"{cat}: {util:.0f}% of budget used")

        if anomalies:
            points.append(f"{len(anomalies)} spending anomalies detected")

        return points

    def _generate_spend_recommendations(
        self,
        budget_status: Dict,
        anomalies: List
    ) -> List[str]:
        """Generate spend-related recommendations"""
        recommendations = []

        # Check for over-budget categories
        over_budget = [(cat, data) for cat, data in budget_status.items()
                      if data.get('utilization', 0) > 1.0]

        if over_budget:
            for cat, data in over_budget:
                recommendations.append(f"Review and adjust budget for {cat} category")

        if anomalies:
            recommendations.append("Investigate identified spending anomalies")

        # General recommendations
        recommendations.append("Continue monthly budget monitoring")
        recommendations.append("Consider implementing pre-approval for large expenses")

        return recommendations

    def _generate_vendor_summary(
        self,
        vendor_name: str,
        risk_level: str,
        total_spend: float
    ) -> str:
        """Generate vendor analysis summary"""
        return (f"{vendor_name} classified as {risk_level} risk vendor "
               f"with total spend of ${total_spend:,.2f}.")

    def _generate_vendor_detailed(self, vendor_profile: Dict) -> str:
        """Generate detailed vendor explanation"""
        parts = []

        parts.append("Vendor Profile:")
        parts.append(f"- Name: {vendor_profile.get('vendor_name', 'Unknown')}")
        parts.append(f"- Vendor ID: {vendor_profile.get('vendor_id', 'N/A')}")
        parts.append(f"- Risk Level: {vendor_profile.get('risk_level', 'UNKNOWN')}")
        parts.append(f"- Risk Score: {vendor_profile.get('risk_score', 0.0):.3f}")
        parts.append("")

        parts.append("Transaction Statistics:")
        parts.append(f"- Total Spend: ${vendor_profile.get('total_spend', 0):,.2f}")
        parts.append(f"- Transaction Count: {vendor_profile.get('transaction_count', 0)}")
        parts.append(f"- Average Amount: ${vendor_profile.get('avg_transaction_amount', 0):,.2f}")
        parts.append("")

        risk_factors = vendor_profile.get('risk_factors', [])
        if risk_factors:
            parts.append("Risk Factors:")
            for factor in risk_factors:
                parts.append(f"- {factor}")

        return "\n".join(parts)

    def _extract_vendor_key_points(self, vendor_profile: Dict) -> List[str]:
        """Extract key points from vendor analysis"""
        points = []

        points.append(f"Risk: {vendor_profile.get('risk_level', 'UNKNOWN')}")
        points.append(f"Spend: ${vendor_profile.get('total_spend', 0):,.2f}")
        points.append(f"Transactions: {vendor_profile.get('transaction_count', 0)}")

        risk_factors = vendor_profile.get('risk_factors', [])
        if risk_factors:
            points.extend(risk_factors[:2])

        return points

    def _map_confidence_level(self, confidence: float) -> str:
        """Map numeric confidence to level"""
        if confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"

    def explain_multi_agent_decision(
        self,
        transaction: Dict,
        all_results: Dict
    ) -> Explanation:
        """
        Explain a multi-agent decision combining multiple analyses

        Args:
            transaction: Transaction data
            all_results: Results from all agents

        Returns:
            Comprehensive explanation
        """
        logger.info("Generating multi-agent explanation")

        title = "Comprehensive Transaction Analysis"

        # Aggregate results
        fraud = all_results.get('fraud_detection', {})
        compliance = all_results.get('compliance', {})
        spend = all_results.get('spend_analysis', {})

        # Generate summary
        summary_parts = []
        if fraud.get('risk_level') in ['HIGH', 'CRITICAL']:
            summary_parts.append(f"Fraud: {fraud.get('risk_level')} risk")
        if compliance.get('status') == 'REJECTED':
            summary_parts.append("Compliance: REJECTED")
        if spend.get('over_budget'):
            summary_parts.append("Budget: EXCEEDED")

        summary = "; ".join(summary_parts) if summary_parts else "All checks passed"

        # Combine detailed explanations
        detailed_parts = []
        detailed_parts.append("=== FRAUD ANALYSIS ===")
        detailed_parts.append(self._generate_fraud_summary(
            transaction,
            fraud.get('risk_level', 'UNKNOWN'),
            fraud.get('overall_score', 0.0)
        ))
        detailed_parts.append("")

        detailed_parts.append("=== COMPLIANCE CHECK ===")
        detailed_parts.append(f"Status: {compliance.get('status', 'UNKNOWN')}")
        detailed_parts.append("")

        detailed_parts.append("=== SPEND ANALYSIS ===")
        detailed_parts.append(f"Budget Status: {spend.get('budget_status', 'UNKNOWN')}")

        detailed = "\n".join(detailed_parts)

        # Combine key points
        key_points = []
        key_points.append(f"Fraud Risk: {fraud.get('risk_level', 'UNKNOWN')}")
        key_points.append(f"Compliance: {compliance.get('status', 'UNKNOWN')}")
        key_points.append(f"Budget: {spend.get('budget_status', 'UNKNOWN')}")

        # Combine recommendations
        recommendations = []
        recommendations.extend(fraud.get('recommendations', [])[:2])
        recommendations.extend(compliance.get('recommendations', [])[:2])

        return Explanation(
            title=title,
            summary=summary,
            detailed_explanation=detailed,
            key_points=key_points,
            recommendations=recommendations,
            confidence_level="MEDIUM",
            generated_at=datetime.now()
        )


# Global agent instance
_explanation_agent = None

def get_explanation_agent() -> ExplanationGeneratorAgent:
    """Get or create global explanation generator agent"""
    global _explanation_agent
    if _explanation_agent is None:
        _explanation_agent = ExplanationGeneratorAgent()
    return _explanation_agent


if __name__ == "__main__":
    # Test the explanation generator
    logging.basicConfig(level=logging.INFO)

    agent = ExplanationGeneratorAgent()

    # Test fraud explanation
    test_transaction = {
        "transaction_id": "TXN-001",
        "amount": 15000.00,
        "merchant": "Tech Store",
        "category": "Electronics",
        "timestamp": "2025-01-15T02:30:00Z"
    }

    test_fraud_result = {
        "risk_level": "HIGH",
        "overall_score": 0.75,
        "risk_factors": [
            "High transaction amount: $15,000.00",
            "Unusual transaction time: 2:00"
        ],
        "confidence": 0.85
    }

    explanation = agent.explain_fraud_detection(test_transaction, test_fraud_result)
    print(f"\n{explanation.title}")
    print(f"\nSummary: {explanation.summary}")
    print(f"\nKey Points:")
    for point in explanation.key_points:
        print(f"  - {point}")
    print(f"\nRecommendations:")
    for rec in explanation.recommendations:
        print(f"  - {rec}")
