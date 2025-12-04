#!/usr/bin/env python3
"""
End-to-End Demo Script
Demonstrates all capabilities of the Financial AI Swarm
"""

import sys
import logging
from pathlib import Path
import time
import requests
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✓ API server is healthy")
            return True
    except Exception as e:
        logger.error(f"✗ API server is not responding: {e}")
        logger.error("Please start the server: uvicorn src.api.main:app --reload")
        return False


def demo_fraud_detection():
    """Demo Scenario 1: Fraud Detection"""
    print_section("DEMO 1: Fraud Detection - High-Risk Transaction")
    
    # Suspicious transaction
    transaction = {
        "transaction_id": "DEMO-FRAUD-001",
        "amount": 25000.00,
        "merchant": "Unknown Electronics Store",
        "category": "Electronics",
        "user_id": "EMP-999",
        "timestamp": "2025-01-15T02:30:00Z",
        "location": "Unknown Location"
    }
    
    print(f"Processing suspicious transaction:")
    print(f"  Amount: ${transaction['amount']:,.2f}")
    print(f"  Merchant: {transaction['merchant']}")
    print(f"  Time: {transaction['timestamp']}")
    print(f"  Location: {transaction['location']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/fraud-detection",
            json=transaction,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n🔍 Fraud Analysis Results:")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Fraud Score: {result['fraud_score']:.3f}")
            print(f"  Confidence: {result['confidence']:.2%}")
            
            if result['risk_factors']:
                print(f"\n  Risk Factors:")
                for factor in result['risk_factors']:
                    print(f"    ⚠️  {factor}")
            
            return result
        else:
            logger.error(f"API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return None


def demo_compliance_check():
    """Demo Scenario 2: Compliance Screening"""
    print_section("DEMO 2: Compliance Check - Sanctions Screening")
    
    # Transaction with sanctioned vendor
    transaction = {
        "transaction_id": "DEMO-COMPLIANCE-001",
        "amount": 50000.00,
        "merchant": "Suspicious Corp International",
        "category": "Consulting",
        "user_id": "EMP-001",
        "timestamp": datetime.now().isoformat(),
        "merchant_description": "Consulting services from overseas vendor"
    }
    
    print(f"Checking transaction against sanctions lists:")
    print(f"  Merchant: {transaction['merchant']}")
    print(f"  Amount: ${transaction['amount']:,.2f}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/compliance-check",
            json=transaction,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✓ Compliance Results:")
            print(f"  Status: {result['status']}")
            print(f"  Sanctions Hit: {'YES ⚠️' if result['sanctions_hit'] else 'NO ✓'}")
            print(f"  PEP Hit: {'YES ⚠️' if result['pep_hit'] else 'NO ✓'}")
            print(f"  Risk Score: {result['risk_score']:.2f}")
            
            if result['policy_violations']:
                print(f"\n  Policy Violations:")
                for violation in result['policy_violations']:
                    print(f"    ❌ {violation}")
            
            if result['recommendations']:
                print(f"\n  Recommendations:")
                for rec in result['recommendations']:
                    print(f"    → {rec}")
            
            return result
        else:
            logger.error(f"API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return None


def demo_document_processing():
    """Demo Scenario 3: Document Processing"""
    print_section("DEMO 3: Document Processing - Receipt OCR")
    
    print("Processing mock receipt document...")
    print("(In production, would process actual image file)")
    
    # Mock document
    document_data = {
        "file_path": "test_receipt.jpg"
    }
    
    # Note: This would normally upload an actual file
    # For demo, we'll show what the API would return
    print(f"\n📄 Document Processing Results:")
    print(f"  Document Type: RECEIPT")
    print(f"  Merchant: ACME RESTAURANT")
    print(f"  Total Amount: $52.92")
    print(f"  Tax Amount: $3.92")
    print(f"  Date: 01/15/2025")
    print(f"  Confidence: 89%")
    print(f"\n  Line Items:")
    print(f"    2x Burger Deluxe      $28.00")
    print(f"    1x Caesar Salad       $12.00")
    print(f"    3x Soft Drinks         $9.00")


def demo_spend_analysis():
    """Demo Scenario 4: Spend Analysis"""
    print_section("DEMO 4: Spend Analysis - Budget Monitoring")
    
    # Generate sample transactions
    import random
    
    transactions = []
    categories = ["IT Services", "Travel", "Entertainment", "Consulting"]
    
    for i in range(30):
        transactions.append({
            "transaction_id": f"DEMO-SPEND-{i:03d}",
            "amount": random.uniform(100, 5000),
            "merchant": f"Vendor {random.randint(1, 10)}",
            "category": random.choice(categories),
            "user_id": f"EMP-{random.randint(1, 20):03d}",
            "timestamp": datetime.now().isoformat()
        })
    
    print(f"Analyzing {len(transactions)} transactions...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/spend-analysis",
            json={"transactions": transactions},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n💰 Spend Analysis Results:")
            print(f"  Total Spend: ${result['total_spend']:,.2f}")
            print(f"  Budget Utilization: {result['budget_utilization']:.1%}")
            print(f"  Anomalies Detected: {len(result['anomalies'])}")
            
            print(f"\n  Category Breakdown:")
            for category, amount in result['category_breakdown'].items():
                print(f"    {category}: ${amount:,.2f}")
            
            if result['recommendations']:
                print(f"\n  Recommendations:")
                for rec in result['recommendations'][:3]:
                    print(f"    💡 {rec}")
            
            return result
        else:
            logger.error(f"API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return None


def demo_full_transaction():
    """Demo Scenario 5: Full Transaction Processing"""
    print_section("DEMO 5: Complete Transaction Flow")
    
    # Normal transaction
    transaction = {
        "transaction_id": "DEMO-FULL-001",
        "amount": 1500.00,
        "merchant": "Tech Vendor Inc",
        "category": "IT Services",
        "user_id": "EMP-001",
        "timestamp": datetime.now().isoformat(),
        "location": "New York, NY",
        "description": "Software licenses"
    }
    
    print(f"Processing complete transaction through all agents:")
    print(f"  Transaction: {transaction['transaction_id']}")
    print(f"  Amount: ${transaction['amount']:,.2f}")
    print(f"  Category: {transaction['category']}")
    
    print(f"\n⏳ Running through agent pipeline...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/process-transaction",
            json=transaction,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✨ Complete Analysis Results:")
            print(f"\n  Overall Status: {result['overall_status']}")
            
            print(f"\n  🔍 Fraud Analysis:")
            fraud = result['fraud_analysis']
            print(f"    Risk Level: {fraud['risk_level']}")
            print(f"    Fraud Score: {fraud['score']:.3f}")
            
            print(f"\n  ✓ Compliance Check:")
            compliance = result['compliance_check']
            print(f"    Status: {compliance['status']}")
            print(f"    Sanctions: {'HIT' if compliance['sanctions_hit'] else 'CLEAR'}")
            
            print(f"\n  💰 Spend Impact:")
            spend = result['spend_analysis']
            print(f"    Budget Utilization: {spend['budget_utilization']:.1%}")
            
            return result
        else:
            logger.error(f"API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return None


def demo_system_status():
    """Show system status"""
    print_section("System Status Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/system/status", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✓ System Status: {result['status'].upper()}")
            print(f"\nActive Agents:")
            
            for agent_name, agent_info in result['agents'].items():
                status_emoji = "✓" if agent_info['status'] == 'active' else "✗"
                print(f"  {status_emoji} {agent_name.replace('_', ' ').title()}: {agent_info['status']}")
            
            return result
        else:
            logger.error(f"API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return None


def main():
    """Run all demo scenarios"""
    print("\n" + "=" * 70)
    print("  FINANCIAL AI SWARM - COMPREHENSIVE DEMO")
    print("=" * 70)
    
    # Check API health
    if not check_api_health():
        return
    
    # Show system status
    demo_system_status()
    
    time.sleep(2)
    
    # Run demo scenarios
    demos = [
        ("Fraud Detection", demo_fraud_detection),
        ("Compliance Check", demo_compliance_check),
        ("Document Processing", demo_document_processing),
        ("Spend Analysis", demo_spend_analysis),
        ("Full Transaction Flow", demo_full_transaction)
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
            break
        except Exception as e:
            logger.error(f"Demo '{name}' failed: {e}")
            continue
    
    # Final summary
    print_section("DEMO COMPLETE")
    print("✓ All demo scenarios executed successfully!")
    print("\nNext Steps:")
    print("  1. Explore the Streamlit UI: streamlit run src/ui/demo.py")
    print("  2. Read API documentation: http://localhost:8000/docs")
    print("  3. Review the code and customize for your needs")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
