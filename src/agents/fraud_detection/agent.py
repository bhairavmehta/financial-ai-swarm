"""
Fraud Detection Agent
Based on AWS fraud detection patterns with PyOD anomaly detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

# PyOD models for anomaly detection
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from pyod.models.knn import KNN
from pyod.models.cblof import CBLOF
from pyod.models.hbos import HBOS

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

logger = logging.getLogger(__name__)


@dataclass
class FraudScore:
    """Fraud detection result"""
    overall_score: float  # 0-1, higher = more fraudulent
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    anomaly_scores: Dict[str, float]
    risk_factors: List[str]
    confidence: float
    model_version: str


class FraudDetectionAgent:
    """
    Multi-model fraud detection agent
    Combines multiple anomaly detection algorithms
    """
    
    # Risk thresholds
    THRESHOLDS = {
        "LOW": 0.3,
        "MEDIUM": 0.5,
        "HIGH": 0.7,
        "CRITICAL": 0.85
    }
    
    def __init__(self, model_dir: str = "models/fraud"):
        self.model_dir = model_dir
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_version = "1.0.0"
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ensemble of anomaly detection models"""
        logger.info("Initializing fraud detection models")
        
        # Isolation Forest - good for global anomalies
        self.models['isolation_forest'] = IForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        
        # Local Outlier Factor - good for local density anomalies
        self.models['lof'] = LOF(
            n_neighbors=20,
            contamination=0.05
        )
        
        # K-Nearest Neighbors - distance-based detection
        self.models['knn'] = KNN(
            n_neighbors=5,
            contamination=0.05,
            method='mean'
        )
        
        # Cluster-based Local Outlier Factor
        self.models['cblof'] = CBLOF(
            n_clusters=8,
            contamination=0.05,
            random_state=42
        )
        
        # Histogram-based Outlier Score
        self.models['hbos'] = HBOS(
            n_bins=10,
            contamination=0.05
        )
        
        # Load pre-trained models if available
        self._load_pretrained_models()
    
    def _load_pretrained_models(self):
        """Load pre-trained models from disk"""
        if os.path.exists(f"{self.model_dir}/scaler.pkl"):
            try:
                with open(f"{self.model_dir}/scaler.pkl", 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Loaded pre-trained scaler")
            except Exception as e:
                logger.warning(f"Could not load scaler: {e}")
    
    def _extract_features(self, transaction: Dict) -> np.ndarray:
        """Extract features from transaction data"""
        features = []
        
        # Amount features
        amount = float(transaction.get('amount', 0))
        features.append(amount)
        features.append(np.log1p(amount))  # Log amount
        
        # Time features
        timestamp = transaction.get('timestamp', datetime.now().isoformat())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        features.append(timestamp.hour)
        features.append(timestamp.weekday())
        features.append(1 if timestamp.weekday() >= 5 else 0)  # Weekend flag
        
        # Category encoding (simple hash for now)
        category = transaction.get('category', 'unknown')
        features.append(hash(category) % 100)
        
        # Merchant encoding
        merchant = transaction.get('merchant', 'unknown')
        features.append(hash(merchant) % 100)
        
        # User behavior features (would be enriched with historical data)
        user_id = transaction.get('user_id', 'unknown')
        features.append(hash(user_id) % 100)
        
        # Geographic features (if available)
        location = transaction.get('location', 'unknown')
        features.append(hash(location) % 50)
        
        # Transaction velocity features (placeholder - would use real history)
        features.append(transaction.get('daily_transaction_count', 1))
        features.append(transaction.get('daily_transaction_volume', amount))
        
        return np.array(features).reshape(1, -1)
    
    def _calculate_risk_factors(self, transaction: Dict, feature_vector: np.ndarray) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        
        amount = float(transaction.get('amount', 0))
        
        # High amount transactions
        if amount > 10000:
            risk_factors.append(f"High transaction amount: ${amount:,.2f}")
        
        # Unusual time
        timestamp = transaction.get('timestamp', datetime.now().isoformat())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        if timestamp.hour < 6 or timestamp.hour > 22:
            risk_factors.append(f"Unusual transaction time: {timestamp.hour}:00")
        
        # Weekend transaction
        if timestamp.weekday() >= 5:
            risk_factors.append("Weekend transaction")
        
        # Round number amounts (common in fraud)
        if amount % 1000 == 0 and amount >= 1000:
            risk_factors.append("Round number amount (potential test transaction)")
        
        # Velocity checks (placeholder)
        daily_count = transaction.get('daily_transaction_count', 0)
        if daily_count > 10:
            risk_factors.append(f"High transaction velocity: {daily_count} transactions today")
        
        return risk_factors
    
    def detect_fraud(self, transaction: Dict) -> FraudScore:
        """
        Main fraud detection method
        
        Args:
            transaction: Dictionary containing transaction details
            
        Returns:
            FraudScore object with detection results
        """
        logger.info(f"Analyzing transaction: {transaction.get('transaction_id')}")
        
        try:
            # Extract features
            features = self._extract_features(transaction)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Get anomaly scores from each model
            anomaly_scores = {}
            for model_name, model in self.models.items():
                try:
                    # Train on single sample (in production, would use historical data)
                    model.fit(features_scaled)
                    score = model.decision_function(features_scaled)[0]
                    # Normalize to 0-1 range
                    normalized_score = (score - model.decision_scores_.min()) / \
                                     (model.decision_scores_.max() - model.decision_scores_.min() + 1e-10)
                    anomaly_scores[model_name] = float(normalized_score)
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    anomaly_scores[model_name] = 0.0
            
            # Ensemble scoring - weighted average
            weights = {
                'isolation_forest': 0.3,
                'lof': 0.25,
                'knn': 0.2,
                'cblof': 0.15,
                'hbos': 0.1
            }
            
            overall_score = sum(
                anomaly_scores.get(model, 0) * weight 
                for model, weight in weights.items()
            )
            
            # Determine risk level
            if overall_score >= self.THRESHOLDS['CRITICAL']:
                risk_level = 'CRITICAL'
            elif overall_score >= self.THRESHOLDS['HIGH']:
                risk_level = 'HIGH'
            elif overall_score >= self.THRESHOLDS['MEDIUM']:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            # Identify risk factors
            risk_factors = self._calculate_risk_factors(transaction, features)
            
            # Calculate confidence based on model agreement
            scores = list(anomaly_scores.values())
            confidence = 1.0 - (np.std(scores) if scores else 0.5)
            
            result = FraudScore(
                overall_score=overall_score,
                risk_level=risk_level,
                anomaly_scores=anomaly_scores,
                risk_factors=risk_factors,
                confidence=confidence,
                model_version=self.model_version
            )
            
            logger.info(f"Fraud analysis complete: {risk_level} (score: {overall_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Fraud detection error: {e}", exc_info=True)
            # Return safe default on error
            return FraudScore(
                overall_score=0.5,
                risk_level='MEDIUM',
                anomaly_scores={},
                risk_factors=['Error during analysis'],
                confidence=0.0,
                model_version=self.model_version
            )
    
    def batch_detect(self, transactions: List[Dict]) -> List[FraudScore]:
        """Batch process multiple transactions"""
        return [self.detect_fraud(txn) for txn in transactions]
    
    def train_models(self, historical_data: pd.DataFrame, labels: np.ndarray = None):
        """
        Train models on historical transaction data
        
        Args:
            historical_data: DataFrame with transaction features
            labels: Optional fraud labels (1=fraud, 0=legitimate)
        """
        logger.info(f"Training models on {len(historical_data)} transactions")
        
        # Scale features
        features_scaled = self.scaler.fit_transform(historical_data)
        
        # Train each model
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name}")
            model.fit(features_scaled)
        
        # Save models
        self.save_models()
        logger.info("Model training complete")
    
    def save_models(self):
        """Save trained models to disk"""
        os.makedirs(self.model_dir, exist_ok=True)
        
        with open(f"{self.model_dir}/scaler.pkl", 'wb') as f:
            pickle.dump(self.scaler, f)
        
        for model_name, model in self.models.items():
            with open(f"{self.model_dir}/{model_name}.pkl", 'wb') as f:
                pickle.dump(model, f)
        
        logger.info(f"Models saved to {self.model_dir}")
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            "version": self.model_version,
            "models": list(self.models.keys()),
            "thresholds": self.THRESHOLDS,
            "feature_count": len(self.feature_names) if self.feature_names else "dynamic"
        }


# Global agent instance
_fraud_agent = None

def get_fraud_agent() -> FraudDetectionAgent:
    """Get or create global fraud detection agent"""
    global _fraud_agent
    if _fraud_agent is None:
        _fraud_agent = FraudDetectionAgent()
    return _fraud_agent


if __name__ == "__main__":
    # Test the fraud detection agent
    logging.basicConfig(level=logging.INFO)
    
    test_transactions = [
        {
            "transaction_id": "TXN-001",
            "amount": 150.50,
            "merchant": "Coffee Shop",
            "category": "Food & Dining",
            "user_id": "USER-001",
            "timestamp": "2025-01-15T10:30:00Z",
            "location": "New York, NY"
        },
        {
            "transaction_id": "TXN-002",
            "amount": 15000.00,
            "merchant": "Electronics Store",
            "category": "Electronics",
            "user_id": "USER-001",
            "timestamp": "2025-01-15T02:30:00Z",
            "location": "Unknown"
        }
    ]
    
    agent = FraudDetectionAgent()
    
    for txn in test_transactions:
        result = agent.detect_fraud(txn)
        print(f"\nTransaction: {txn['transaction_id']}")
        print(f"Risk Level: {result.risk_level}")
        print(f"Score: {result.overall_score:.3f}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Risk Factors: {result.risk_factors}")
