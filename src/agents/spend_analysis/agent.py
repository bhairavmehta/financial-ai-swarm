"""
Spend Analysis Agent
Budget tracking, category analysis, and spending anomaly detection
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SpendAnalysis:
    """Spend analysis result"""
    total_spend: float
    budget_utilization: float  # 0-1
    category_breakdown: Dict[str, float]
    anomalies: List[Dict]
    trends: Dict
    recommendations: List[str]
    risk_areas: List[str]
    period: str


class SpendAnalysisAgent:
    """
    Spend analysis and budget tracking agent
    Monitors spending patterns and identifies anomalies
    """
    
    # Default budget limits by category
    DEFAULT_BUDGETS = {
        'travel': 50000,
        'entertainment': 10000,
        'it_services': 100000,
        'consulting': 75000,
        'supplies': 20000,
        'training': 15000,
        'other': 25000
    }
    
    def __init__(self, budget_config: Optional[Dict] = None):
        self.budgets = budget_config or self.DEFAULT_BUDGETS
        self.historical_data = defaultdict(list)
        
    def _normalize_category(self, category: str) -> str:
        """Normalize category names"""
        category_mapping = {
            'travel & transport': 'travel',
            'food & dining': 'entertainment',
            'entertainment & events': 'entertainment',
            'it equipment': 'it_services',
            'software': 'it_services',
            'professional services': 'consulting',
            'office supplies': 'supplies',
            'learning & development': 'training'
        }
        
        category_lower = category.lower()
        return category_mapping.get(category_lower, 'other')
    
    def _calculate_statistics(self, transactions: List[Dict]) -> Dict:
        """Calculate spending statistics"""
        if not transactions:
            return {
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }
        
        amounts = [float(t.get('amount', 0)) for t in transactions]
        
        return {
            'mean': np.mean(amounts),
            'median': np.median(amounts),
            'std': np.std(amounts),
            'min': np.min(amounts),
            'max': np.max(amounts),
            'count': len(amounts)
        }
    
    def _detect_anomalies(self, transactions: List[Dict]) -> List[Dict]:
        """Detect anomalous spending patterns"""
        anomalies = []
        
        if len(transactions) < 3:
            return anomalies
        
        # Calculate baseline statistics
        amounts = [float(t.get('amount', 0)) for t in transactions]
        mean = np.mean(amounts)
        std = np.std(amounts)
        
        # Z-score method for outlier detection
        threshold = 2.5  # Z-score threshold
        
        for transaction in transactions:
            amount = float(transaction.get('amount', 0))
            
            if std > 0:
                z_score = abs((amount - mean) / std)
                
                if z_score > threshold:
                    anomalies.append({
                        'transaction_id': transaction.get('transaction_id'),
                        'amount': amount,
                        'category': transaction.get('category'),
                        'merchant': transaction.get('merchant'),
                        'z_score': z_score,
                        'reason': f'Amount ${amount:.2f} is {z_score:.1f} standard deviations from mean'
                    })
        
        # Check for unusual frequency
        if len(transactions) > 10:
            # Group by day
            daily_counts = defaultdict(int)
            for txn in transactions:
                date = txn.get('timestamp', datetime.now().isoformat())[:10]
                daily_counts[date] += 1
            
            avg_daily = np.mean(list(daily_counts.values()))
            for date, count in daily_counts.items():
                if count > avg_daily * 2:
                    anomalies.append({
                        'date': date,
                        'transaction_count': count,
                        'reason': f'Unusually high transaction volume: {count} transactions'
                    })
        
        return anomalies
    
    def _identify_trends(self, transactions: List[Dict]) -> Dict:
        """Identify spending trends"""
        if len(transactions) < 2:
            return {'trend': 'insufficient_data'}
        
        # Sort by timestamp
        sorted_txns = sorted(
            transactions,
            key=lambda x: x.get('timestamp', '')
        )
        
        # Split into periods
        mid_point = len(sorted_txns) // 2
        first_half = sorted_txns[:mid_point]
        second_half = sorted_txns[mid_point:]
        
        first_total = sum(float(t.get('amount', 0)) for t in first_half)
        second_total = sum(float(t.get('amount', 0)) for t in second_half)
        
        # Calculate trend
        if first_total > 0:
            change_pct = ((second_total - first_total) / first_total) * 100
        else:
            change_pct = 0
        
        trend_direction = 'increasing' if change_pct > 5 else 'decreasing' if change_pct < -5 else 'stable'
        
        return {
            'trend': trend_direction,
            'change_percentage': change_pct,
            'first_period_total': first_total,
            'second_period_total': second_total
        }
    
    def _generate_recommendations(
        self, 
        category_totals: Dict[str, float],
        budget_utilization: Dict[str, float],
        anomalies: List[Dict]
    ) -> List[str]:
        """Generate spending recommendations"""
        recommendations = []
        
        # Budget utilization recommendations
        for category, utilization in budget_utilization.items():
            if utilization > 0.9:
                recommendations.append(
                    f"⚠️ {category.upper()}: {utilization*100:.1f}% of budget used - consider cost reduction"
                )
            elif utilization > 0.8:
                recommendations.append(
                    f"ℹ️ {category.upper()}: {utilization*100:.1f}% of budget used - monitor closely"
                )
        
        # Category-specific recommendations
        for category, total in category_totals.items():
            if category == 'travel' and total > 0:
                recommendations.append(
                    "✈️ TRAVEL: Consider booking in advance for better rates"
                )
            if category == 'it_services' and total > 50000:
                recommendations.append(
                    "💻 IT SERVICES: Evaluate subscription consolidation opportunities"
                )
        
        # Anomaly-based recommendations
        if len(anomalies) > 3:
            recommendations.append(
                f"🔍 {len(anomalies)} spending anomalies detected - review for accuracy"
            )
        
        return recommendations
    
    def analyze_spending(
        self,
        transactions: List[Dict],
        period: str = "monthly",
        user_id: Optional[str] = None
    ) -> SpendAnalysis:
        """
        Main spend analysis method
        
        Args:
            transactions: List of transaction dictionaries
            period: Analysis period (daily, weekly, monthly, quarterly)
            user_id: Optional user ID for personalized analysis
            
        Returns:
            SpendAnalysis with comprehensive spending insights
        """
        logger.info(f"Analyzing {len(transactions)} transactions for period: {period}")
        
        # Calculate total spend
        total_spend = sum(float(t.get('amount', 0)) for t in transactions)
        
        # Break down by category
        category_totals = defaultdict(float)
        for transaction in transactions:
            category = self._normalize_category(transaction.get('category', 'other'))
            amount = float(transaction.get('amount', 0))
            category_totals[category] += amount
        
        # Calculate budget utilization
        budget_utilization = {}
        for category, budget_limit in self.budgets.items():
            spent = category_totals.get(category, 0)
            budget_utilization[category] = min(spent / budget_limit, 1.0) if budget_limit > 0 else 0
        
        # Overall budget utilization
        total_budget = sum(self.budgets.values())
        overall_utilization = total_spend / total_budget if total_budget > 0 else 0
        
        # Detect anomalies
        anomalies = self._detect_anomalies(transactions)
        
        # Identify trends
        trends = self._identify_trends(transactions)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            dict(category_totals),
            budget_utilization,
            anomalies
        )
        
        # Identify risk areas
        risk_areas = []
        for category, utilization in budget_utilization.items():
            if utilization > 0.9:
                risk_areas.append(f"{category}: Over budget")
        
        if len(anomalies) > 5:
            risk_areas.append(f"High anomaly count: {len(anomalies)} detected")
        
        if trends.get('change_percentage', 0) > 30:
            risk_areas.append("Rapid spending increase detected")
        
        result = SpendAnalysis(
            total_spend=total_spend,
            budget_utilization=overall_utilization,
            category_breakdown=dict(category_totals),
            anomalies=anomalies,
            trends=trends,
            recommendations=recommendations,
            risk_areas=risk_areas,
            period=period
        )
        
        logger.info(f"Spend analysis complete: ${total_spend:.2f} ({overall_utilization*100:.1f}% of budget)")
        return result
    
    def get_budget_status(self, category: Optional[str] = None) -> Dict:
        """Get current budget status"""
        if category:
            category = self._normalize_category(category)
            return {
                'category': category,
                'budget': self.budgets.get(category, 0),
                'spent': sum(t.get('amount', 0) for t in self.historical_data.get(category, [])),
            }
        else:
            return {
                'budgets': self.budgets,
                'total_budget': sum(self.budgets.values())
            }
    
    def update_budget(self, category: str, new_limit: float):
        """Update budget limit for a category"""
        category = self._normalize_category(category)
        old_limit = self.budgets.get(category, 0)
        self.budgets[category] = new_limit
        logger.info(f"Updated {category} budget: ${old_limit:.2f} -> ${new_limit:.2f}")


# Global agent instance
_spend_agent = None

def get_spend_agent() -> SpendAnalysisAgent:
    """Get or create global spend analysis agent"""
    global _spend_agent
    if _spend_agent is None:
        _spend_agent = SpendAnalysisAgent()
    return _spend_agent


if __name__ == "__main__":
    # Test the spend analysis agent
    logging.basicConfig(level=logging.INFO)
    
    # Generate test transactions
    test_transactions = [
        {'transaction_id': f'TXN-{i:03d}', 'amount': np.random.normal(500, 200), 
         'category': np.random.choice(['Travel', 'IT Services', 'Entertainment']),
         'timestamp': (datetime.now() - timedelta(days=i)).isoformat()}
        for i in range(30)
    ]
    
    # Add some anomalies
    test_transactions.append({
        'transaction_id': 'TXN-999',
        'amount': 15000,
        'category': 'Entertainment',
        'timestamp': datetime.now().isoformat()
    })
    
    agent = SpendAnalysisAgent()
    result = agent.analyze_spending(test_transactions, period='monthly')
    
    print(f"\nSpend Analysis Results:")
    print(f"Total Spend: ${result.total_spend:.2f}")
    print(f"Budget Utilization: {result.budget_utilization*100:.1f}%")
    print(f"\nCategory Breakdown:")
    for category, amount in result.category_breakdown.items():
        print(f"  {category}: ${amount:.2f}")
    print(f"\nAnomalies Detected: {len(result.anomalies)}")
    print(f"Spending Trend: {result.trends.get('trend')}")
    print(f"\nRecommendations:")
    for rec in result.recommendations:
        print(f"  {rec}")
