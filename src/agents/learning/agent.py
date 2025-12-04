"""
Learning & Feedback Agent
Learns from user feedback and improves agent performance over time
Implements a feedback loop for continuous improvement
"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FeedbackRecord:
    """User feedback record"""
    feedback_id: str
    transaction_id: str
    agent_type: str
    original_decision: Dict
    user_feedback: str  # CORRECT, INCORRECT, PARTIALLY_CORRECT
    user_comment: Optional[str]
    timestamp: datetime
    applied: bool = False


@dataclass
class LearningInsight:
    """Learning insight derived from feedback"""
    insight_type: str
    description: str
    affected_agent: str
    confidence: float
    supporting_evidence: List[str]
    recommended_action: str


class LearningFeedbackAgent:
    """
    Learns from user feedback and provides improvement recommendations
    """

    def __init__(self, storage_path: str = "data/feedback"):
        """
        Initialize learning agent

        Args:
            storage_path: Path to store feedback data
        """
        self.storage_path = storage_path
        self.feedback_records: List[FeedbackRecord] = []
        self.agent_performance = defaultdict(lambda: {
            'total': 0,
            'correct': 0,
            'incorrect': 0,
            'partial': 0
        })
        self.learning_insights: List[LearningInsight] = []

        logger.info("Learning & Feedback Agent initialized")

    def record_feedback(
        self,
        transaction_id: str,
        agent_type: str,
        original_decision: Dict,
        user_feedback: str,
        user_comment: Optional[str] = None
    ) -> FeedbackRecord:
        """
        Record user feedback on an agent's decision

        Args:
            transaction_id: ID of the transaction
            agent_type: Type of agent (fraud_detection, compliance, etc.)
            original_decision: The original decision made by the agent
            user_feedback: User's assessment (CORRECT, INCORRECT, PARTIALLY_CORRECT)
            user_comment: Optional comment from user

        Returns:
            FeedbackRecord object
        """
        logger.info(f"Recording feedback for {agent_type} on transaction {transaction_id}")

        feedback_id = f"FB-{len(self.feedback_records) + 1:06d}"

        record = FeedbackRecord(
            feedback_id=feedback_id,
            transaction_id=transaction_id,
            agent_type=agent_type,
            original_decision=original_decision,
            user_feedback=user_feedback,
            user_comment=user_comment,
            timestamp=datetime.now(),
            applied=False
        )

        self.feedback_records.append(record)

        # Update performance metrics
        self.agent_performance[agent_type]['total'] += 1
        if user_feedback == 'CORRECT':
            self.agent_performance[agent_type]['correct'] += 1
        elif user_feedback == 'INCORRECT':
            self.agent_performance[agent_type]['incorrect'] += 1
        else:
            self.agent_performance[agent_type]['partial'] += 1

        # Analyze feedback for immediate insights
        self._analyze_feedback(record)

        # Save feedback
        self._save_feedback(record)

        logger.info(f"Feedback recorded: {feedback_id}")
        return record

    def get_agent_performance(self, agent_type: Optional[str] = None) -> Dict:
        """
        Get performance metrics for an agent or all agents

        Args:
            agent_type: Specific agent type, or None for all agents

        Returns:
            Performance metrics
        """
        if agent_type:
            perf = self.agent_performance[agent_type]
            total = perf['total']
            if total == 0:
                return {
                    'agent_type': agent_type,
                    'accuracy': 0.0,
                    'total_decisions': 0,
                    'correct': 0,
                    'incorrect': 0,
                    'partial': 0
                }

            accuracy = (perf['correct'] + 0.5 * perf['partial']) / total

            return {
                'agent_type': agent_type,
                'accuracy': accuracy,
                'total_decisions': total,
                'correct': perf['correct'],
                'incorrect': perf['incorrect'],
                'partial': perf['partial']
            }
        else:
            # Return all agents
            return {
                agent: self.get_agent_performance(agent)
                for agent in self.agent_performance.keys()
            }

    def get_improvement_recommendations(self, agent_type: str) -> List[str]:
        """
        Get recommendations for improving an agent

        Args:
            agent_type: Type of agent

        Returns:
            List of recommendations
        """
        logger.info(f"Generating improvement recommendations for {agent_type}")

        recommendations = []

        # Get performance
        perf = self.get_agent_performance(agent_type)
        accuracy = perf.get('accuracy', 0.0)

        if accuracy < 0.7:
            recommendations.append(
                f"Low accuracy ({accuracy:.1%}) - Consider retraining models or adjusting thresholds"
            )

        # Analyze recent feedback
        recent_feedback = [
            fb for fb in self.feedback_records
            if fb.agent_type == agent_type and
            fb.timestamp > datetime.now() - timedelta(days=30)
        ]

        # Find common patterns in incorrect decisions
        incorrect_feedback = [
            fb for fb in recent_feedback
            if fb.user_feedback == 'INCORRECT'
        ]

        if len(incorrect_feedback) > 5:
            recommendations.append(
                f"High number of incorrect decisions ({len(incorrect_feedback)}) in last 30 days - "
                "Review decision criteria"
            )

        # Check for false positives/negatives
        false_positives = self._count_false_positives(agent_type)
        false_negatives = self._count_false_negatives(agent_type)

        if false_positives > false_negatives:
            recommendations.append(
                "More false positives than false negatives - "
                "Consider increasing decision thresholds"
            )
        elif false_negatives > false_positives:
            recommendations.append(
                "More false negatives than false positives - "
                "Consider decreasing decision thresholds"
            )

        # Get insights specific to this agent
        agent_insights = [
            insight for insight in self.learning_insights
            if insight.affected_agent == agent_type
        ]

        for insight in agent_insights[:3]:  # Top 3 insights
            recommendations.append(insight.recommended_action)

        if not recommendations:
            recommendations.append("Performance is good - continue current approach")

        return recommendations

    def _analyze_feedback(self, record: FeedbackRecord):
        """Analyze a feedback record to generate insights"""
        agent_type = record.agent_type

        # Check for threshold issues
        if agent_type == 'fraud_detection':
            self._analyze_fraud_feedback(record)
        elif agent_type == 'compliance':
            self._analyze_compliance_feedback(record)
        elif agent_type == 'spend_analysis':
            self._analyze_spend_feedback(record)

    def _analyze_fraud_feedback(self, record: FeedbackRecord):
        """Analyze fraud detection feedback"""
        decision = record.original_decision
        risk_level = decision.get('risk_level', 'UNKNOWN')
        risk_score = decision.get('overall_score', 0.0)

        # False positive: High risk but user says it was correct
        if risk_level in ['HIGH', 'CRITICAL'] and record.user_feedback == 'INCORRECT':
            insight = LearningInsight(
                insight_type='FALSE_POSITIVE',
                description=f"Transaction {record.transaction_id} flagged as {risk_level} but was legitimate",
                affected_agent='fraud_detection',
                confidence=0.8,
                supporting_evidence=[
                    f"Risk score: {risk_score:.3f}",
                    f"User feedback: {record.user_feedback}",
                    f"Comment: {record.user_comment or 'None'}"
                ],
                recommended_action="Consider increasing HIGH risk threshold to reduce false positives"
            )
            self.learning_insights.append(insight)

        # False negative: Low risk but user says it was incorrect
        elif risk_level == 'LOW' and record.user_feedback == 'INCORRECT':
            insight = LearningInsight(
                insight_type='FALSE_NEGATIVE',
                description=f"Transaction {record.transaction_id} passed as LOW risk but was fraudulent",
                affected_agent='fraud_detection',
                confidence=0.8,
                supporting_evidence=[
                    f"Risk score: {risk_score:.3f}",
                    f"User feedback: {record.user_feedback}",
                    f"Comment: {record.user_comment or 'None'}"
                ],
                recommended_action="Consider decreasing fraud detection thresholds to catch more cases"
            )
            self.learning_insights.append(insight)

    def _analyze_compliance_feedback(self, record: FeedbackRecord):
        """Analyze compliance feedback"""
        decision = record.original_decision
        status = decision.get('status', 'UNKNOWN')

        if status == 'REJECTED' and record.user_feedback == 'INCORRECT':
            insight = LearningInsight(
                insight_type='FALSE_REJECTION',
                description=f"Entity rejected but should have been approved",
                affected_agent='compliance',
                confidence=0.9,
                supporting_evidence=[
                    f"Status: {status}",
                    f"User feedback: {record.user_feedback}",
                    f"Comment: {record.user_comment or 'None'}"
                ],
                recommended_action="Review compliance screening criteria - possible false match"
            )
            self.learning_insights.append(insight)

    def _analyze_spend_feedback(self, record: FeedbackRecord):
        """Analyze spend analysis feedback"""
        # Can be extended based on spend analysis specifics
        pass

    def _count_false_positives(self, agent_type: str) -> int:
        """Count false positives for an agent"""
        count = 0
        for fb in self.feedback_records:
            if fb.agent_type == agent_type:
                decision = fb.original_decision
                # For fraud/compliance, high risk/rejected but incorrect
                if agent_type == 'fraud_detection':
                    risk_level = decision.get('risk_level', 'LOW')
                    if risk_level in ['HIGH', 'CRITICAL'] and fb.user_feedback == 'INCORRECT':
                        count += 1
                elif agent_type == 'compliance':
                    status = decision.get('status', 'APPROVED')
                    if status == 'REJECTED' and fb.user_feedback == 'INCORRECT':
                        count += 1
        return count

    def _count_false_negatives(self, agent_type: str) -> int:
        """Count false negatives for an agent"""
        count = 0
        for fb in self.feedback_records:
            if fb.agent_type == agent_type:
                decision = fb.original_decision
                # For fraud/compliance, low risk/approved but incorrect
                if agent_type == 'fraud_detection':
                    risk_level = decision.get('risk_level', 'HIGH')
                    if risk_level == 'LOW' and fb.user_feedback == 'INCORRECT':
                        count += 1
                elif agent_type == 'compliance':
                    status = decision.get('status', 'REJECTED')
                    if status == 'APPROVED' and fb.user_feedback == 'INCORRECT':
                        count += 1
        return count

    def suggest_threshold_adjustments(self, agent_type: str) -> Dict:
        """
        Suggest threshold adjustments based on feedback

        Args:
            agent_type: Type of agent

        Returns:
            Suggested threshold adjustments
        """
        logger.info(f"Calculating threshold adjustments for {agent_type}")

        false_positives = self._count_false_positives(agent_type)
        false_negatives = self._count_false_negatives(agent_type)

        suggestions = {
            'agent_type': agent_type,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'adjustments': []
        }

        # Calculate optimal threshold adjustment
        if false_positives > false_negatives * 2:
            # Too many false positives - increase threshold
            adjustment = min(0.1, false_positives * 0.02)
            suggestions['adjustments'].append({
                'threshold_type': 'HIGH_RISK',
                'current_value': 0.7,  # Default
                'suggested_value': 0.7 + adjustment,
                'reason': 'Reduce false positives'
            })
        elif false_negatives > false_positives * 2:
            # Too many false negatives - decrease threshold
            adjustment = min(0.1, false_negatives * 0.02)
            suggestions['adjustments'].append({
                'threshold_type': 'HIGH_RISK',
                'current_value': 0.7,  # Default
                'suggested_value': 0.7 - adjustment,
                'reason': 'Catch more fraudulent cases'
            })
        else:
            suggestions['adjustments'].append({
                'threshold_type': 'ALL',
                'current_value': 'N/A',
                'suggested_value': 'No change needed',
                'reason': 'False positive/negative ratio is balanced'
            })

        return suggestions

    def get_learning_insights(
        self,
        agent_type: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> List[LearningInsight]:
        """
        Get learning insights

        Args:
            agent_type: Filter by agent type
            min_confidence: Minimum confidence threshold

        Returns:
            List of insights
        """
        insights = self.learning_insights

        if agent_type:
            insights = [i for i in insights if i.affected_agent == agent_type]

        insights = [i for i in insights if i.confidence >= min_confidence]

        # Sort by confidence
        insights.sort(key=lambda x: x.confidence, reverse=True)

        return insights

    def generate_training_data(self, agent_type: str) -> List[Dict]:
        """
        Generate training data from feedback for model retraining

        Args:
            agent_type: Type of agent

        Returns:
            List of training examples
        """
        logger.info(f"Generating training data for {agent_type}")

        training_data = []

        for fb in self.feedback_records:
            if fb.agent_type == agent_type:
                # Create labeled training example
                label = 1 if fb.user_feedback == 'INCORRECT' else 0

                if agent_type == 'fraud_detection':
                    # Extract features from original decision
                    example = {
                        'transaction_id': fb.transaction_id,
                        'features': fb.original_decision,
                        'label': label,  # 1 = fraud, 0 = legitimate
                        'feedback': fb.user_feedback,
                        'timestamp': fb.timestamp.isoformat()
                    }
                    training_data.append(example)

        logger.info(f"Generated {len(training_data)} training examples")
        return training_data

    def _save_feedback(self, record: FeedbackRecord):
        """Save feedback record to storage"""
        import os
        os.makedirs(self.storage_path, exist_ok=True)

        filename = f"{self.storage_path}/{record.feedback_id}.json"

        try:
            with open(filename, 'w') as f:
                # Convert to dict
                record_dict = asdict(record)
                record_dict['timestamp'] = record.timestamp.isoformat()
                json.dump(record_dict, f, indent=2)
            logger.debug(f"Feedback saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")

    def load_feedback_history(self):
        """Load historical feedback from storage"""
        import os
        import glob

        if not os.path.exists(self.storage_path):
            logger.info("No feedback history found")
            return

        files = glob.glob(f"{self.storage_path}/FB-*.json")

        for filepath in files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    record = FeedbackRecord(
                        feedback_id=data['feedback_id'],
                        transaction_id=data['transaction_id'],
                        agent_type=data['agent_type'],
                        original_decision=data['original_decision'],
                        user_feedback=data['user_feedback'],
                        user_comment=data.get('user_comment'),
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        applied=data.get('applied', False)
                    )
                    self.feedback_records.append(record)

                    # Update performance metrics
                    agent_type = record.agent_type
                    self.agent_performance[agent_type]['total'] += 1
                    if record.user_feedback == 'CORRECT':
                        self.agent_performance[agent_type]['correct'] += 1
                    elif record.user_feedback == 'INCORRECT':
                        self.agent_performance[agent_type]['incorrect'] += 1
                    else:
                        self.agent_performance[agent_type]['partial'] += 1

            except Exception as e:
                logger.error(f"Error loading {filepath}: {e}")

        logger.info(f"Loaded {len(self.feedback_records)} feedback records")

    def get_feedback_summary(self) -> Dict:
        """Get summary of all feedback"""
        total_feedback = len(self.feedback_records)

        summary = {
            'total_feedback_records': total_feedback,
            'by_agent': {},
            'by_feedback_type': defaultdict(int),
            'recent_insights': len([
                i for i in self.learning_insights
                if datetime.now() - timedelta(days=7) < datetime.now()
            ])
        }

        for fb in self.feedback_records:
            summary['by_feedback_type'][fb.user_feedback] += 1

        for agent_type in self.agent_performance.keys():
            summary['by_agent'][agent_type] = self.get_agent_performance(agent_type)

        return summary


# Global agent instance
_learning_agent = None

def get_learning_agent() -> LearningFeedbackAgent:
    """Get or create global learning agent"""
    global _learning_agent
    if _learning_agent is None:
        _learning_agent = LearningFeedbackAgent()
        _learning_agent.load_feedback_history()
    return _learning_agent


if __name__ == "__main__":
    # Test the learning agent
    logging.basicConfig(level=logging.INFO)

    agent = LearningFeedbackAgent()

    # Simulate feedback
    test_decision = {
        'risk_level': 'HIGH',
        'overall_score': 0.75,
        'risk_factors': ['High amount', 'Unusual time']
    }

    # Record feedback
    feedback1 = agent.record_feedback(
        transaction_id="TXN-001",
        agent_type="fraud_detection",
        original_decision=test_decision,
        user_feedback="INCORRECT",
        user_comment="This was a legitimate business purchase"
    )

    feedback2 = agent.record_feedback(
        transaction_id="TXN-002",
        agent_type="fraud_detection",
        original_decision={'risk_level': 'LOW', 'overall_score': 0.2},
        user_feedback="CORRECT",
        user_comment="Correctly identified as safe"
    )

    # Get performance
    perf = agent.get_agent_performance('fraud_detection')
    print(f"\nFraud Detection Performance:")
    print(f"  Accuracy: {perf['accuracy']:.1%}")
    print(f"  Total Decisions: {perf['total_decisions']}")

    # Get recommendations
    recommendations = agent.get_improvement_recommendations('fraud_detection')
    print(f"\nRecommendations:")
    for rec in recommendations:
        print(f"  - {rec}")

    # Get insights
    insights = agent.get_learning_insights()
    print(f"\nLearning Insights:")
    for insight in insights:
        print(f"  - {insight.description}")
        print(f"    Action: {insight.recommended_action}")
