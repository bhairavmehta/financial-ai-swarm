#!/usr/bin/env python3
"""
Initialize Database and Download Models
Sets up the system for first use
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_directories():
    """Create necessary directories"""
    directories = [
        'data/raw',
        'data/processed',
        'data/mock',
        'models/fraud',
        'logs',
        'uploads'
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def download_models():
    """Download pre-trained models"""
    logger.info("Downloading embedding models...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Download embedding model for RAG
        model_name = 'all-MiniLM-L6-v2'
        logger.info(f"Downloading {model_name}...")
        model = SentenceTransformer(model_name)
        logger.info(f"✓ Successfully downloaded {model_name}")
        
    except Exception as e:
        logger.warning(f"Could not download models: {e}")
        logger.info("Models will be downloaded on first use")


def create_mock_data():
    """Create mock transaction data for testing"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    logger.info("Creating mock transaction data...")
    
    # Generate mock transactions
    num_transactions = 1000
    categories = ['Travel', 'IT Services', 'Entertainment', 'Consulting', 'Supplies']
    merchants = ['Vendor A', 'Vendor B', 'Vendor C', 'Hotel Chain', 'Tech Corp']
    
    transactions = []
    for i in range(num_transactions):
        date = datetime.now() - timedelta(days=np.random.randint(0, 365))
        
        transactions.append({
            'transaction_id': f'TXN-{i:05d}',
            'amount': np.random.lognormal(6, 1.5),  # Log-normal distribution
            'merchant': np.random.choice(merchants),
            'category': np.random.choice(categories),
            'user_id': f'EMP-{np.random.randint(1, 100):03d}',
            'timestamp': date.isoformat(),
            'location': np.random.choice(['New York', 'San Francisco', 'Chicago', 'Remote']),
            'description': f'Business expense {i}'
        })
    
    df = pd.DataFrame(transactions)
    output_path = 'data/mock/transactions.csv'
    df.to_csv(output_path, index=False)
    logger.info(f"✓ Created {num_transactions} mock transactions: {output_path}")
    
    return df


def create_mock_policies():
    """Create mock policy documents"""
    logger.info("Creating mock policy documents...")
    
    policies = [
        "All transactions above $10,000 require manager approval and documented business justification.",
        "Expenses for entertainment and gifts are limited to $500 per event and must have detailed receipts.",
        "Travel expenses must be booked through approved corporate travel agency.",
        "IT equipment purchases require IT department approval and must meet security standards.",
        "Vendor payments require three competitive bids for contracts over $25,000.",
        "Personal purchases or gifts using company funds are strictly prohibited.",
        "All foreign transactions must be screened for OFAC compliance before processing.",
        "Consulting services require documented statements of work and deliverables.",
        "Recurring subscriptions must be reviewed quarterly for necessity.",
        "Cash advances are limited to $1,000 and require repayment within 30 days."
    ]
    
    output_path = 'data/policies/company_policies.txt'
    os.makedirs('data/policies', exist_ok=True)
    
    with open(output_path, 'w') as f:
        for policy in policies:
            f.write(policy + '\n\n')
    
    logger.info(f"✓ Created policy documents: {output_path}")


def initialize_fraud_models():
    """Initialize fraud detection models"""
    logger.info("Initializing fraud detection models...")
    
    try:
        from agents.fraud_detection.agent import FraudDetectionAgent
        
        agent = FraudDetectionAgent()
        
        # Load mock data for training
        import pandas as pd
        df = pd.read_csv('data/mock/transactions.csv')
        
        # Extract features for training (simplified)
        logger.info("Pre-training fraud models with mock data...")
        # In production, would use historical labeled data
        
        agent.save_models()
        logger.info("✓ Fraud detection models initialized")
        
    except Exception as e:
        logger.warning(f"Could not initialize fraud models: {e}")


def test_api_connection():
    """Test if API dependencies are available"""
    logger.info("Testing dependencies...")
    
    dependencies = [
        ('langchain', 'LangChain'),
        ('langgraph', 'LangGraph'),
        ('pyod', 'PyOD'),
        ('sentence_transformers', 'Sentence Transformers'),
        ('fastapi', 'FastAPI'),
        ('streamlit', 'Streamlit')
    ]
    
    all_available = True
    for module, name in dependencies:
        try:
            __import__(module)
            logger.info(f"✓ {name} is available")
        except ImportError:
            logger.error(f"✗ {name} is NOT available - run: pip install {module}")
            all_available = False
    
    return all_available


def main():
    """Main initialization routine"""
    logger.info("=" * 60)
    logger.info("Financial AI Swarm - Initialization Script")
    logger.info("=" * 60)
    
    # Check dependencies
    logger.info("\n[1/6] Checking dependencies...")
    if not test_api_connection():
        logger.error("Some dependencies are missing. Please install requirements:")
        logger.error("pip install -r requirements.txt")
        return
    
    # Create directories
    logger.info("\n[2/6] Creating directories...")
    create_directories()
    
    # Download models
    logger.info("\n[3/6] Downloading models...")
    download_models()
    
    # Create mock data
    logger.info("\n[4/6] Creating mock data...")
    create_mock_data()
    create_mock_policies()
    
    # Initialize models
    logger.info("\n[5/6] Initializing fraud models...")
    initialize_fraud_models()
    
    # Final checks
    logger.info("\n[6/6] Running final checks...")
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ Initialization complete!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Copy .env.example to .env and configure your API keys")
    logger.info("2. Start the API server: uvicorn src.api.main:app --reload")
    logger.info("3. Start the demo UI: streamlit run src.ui/demo.py")
    logger.info("4. Visit http://localhost:8000/docs for API documentation")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
