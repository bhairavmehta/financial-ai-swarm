#!/usr/bin/env python3
"""
Realistic Demo of Financial AI Swarm
Shows real-world use cases and scenarios
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List
import sys

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def check_api_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("API server is running and healthy")
            data = response.json()
            print_info(f"Mode: {data.get('mode', 'unknown')}")
            print_info(f"Version: {data.get('version', 'unknown')}")
            return True
        else:
            print_error("API server is not healthy")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to API server: {e}")
        print_info(f"Make sure the server is running: python3 standalone_api.py")
        return False

def scenario_1_normal_transaction():
    """Scenario 1: Normal business transaction"""
    print_header("Scenario 1: Normal Business Transaction")

    print_info("Employee purchases office supplies for the team")

    transaction = {
        "transaction_id": "TXN-2025-001",
        "amount": 450.00,
        "merchant": "Office Depot",
        "category": "Office Supplies",
        "user_id": "EMP-1234",
        "timestamp": datetime.now().isoformat(),
        "description": "Printer paper, pens, notebooks for Q1"
    }

    print(f"\n{Colors.BOLD}Transaction Details:{Colors.ENDC}")
    print(f"  Amount: ${transaction['amount']:,.2f}")
    print(f"  Merchant: {transaction['merchant']}")
    print(f"  Category: {transaction['category']}")
    print(f"  Employee: {transaction['user_id']}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/process-transaction",
            json=transaction,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            print(f"\n{Colors.BOLD}Analysis Results:{Colors.ENDC}")

            # Fraud Analysis
            fraud = result.get('fraud_analysis', {})
            risk_level = fraud.get('risk_level', 'UNKNOWN')
            if risk_level == 'LOW':
                print_success(f"Fraud Risk: {risk_level} (Score: {fraud.get('fraud_score', 0):.2f})")
            elif risk_level == 'MEDIUM':
                print_warning(f"Fraud Risk: {risk_level} (Score: {fraud.get('fraud_score', 0):.2f})")
            else:
                print_error(f"Fraud Risk: {risk_level} (Score: {fraud.get('fraud_score', 0):.2f})")

            # Compliance
            compliance = result.get('compliance_check', {})
            status = compliance.get('status', 'UNKNOWN')
            if status == 'APPROVED':
                print_success(f"Compliance: {status}")
            else:
                print_warning(f"Compliance: {status}")

            # Overall Status
            overall = result.get('overall_status', 'UNKNOWN')
            print(f"\n{Colors.BOLD}Overall Decision: {Colors.OKGREEN if overall == 'APPROVED' else Colors.WARNING}{overall}{Colors.ENDC}")

        else:
            print_error(f"Request failed: {response.status_code}")

    except Exception as e:
        print_error(f"Error: {e}")

def scenario_2_high_risk_transaction():
    """Scenario 2: High-risk suspicious transaction"""
    print_header("Scenario 2: High-Risk Suspicious Transaction")

    print_warning("Large unusual payment to new vendor")

    transaction = {
        "transaction_id": "TXN-2025-002",
        "amount": 45000.00,
        "merchant": "Offshore Consulting LLC",
        "category": "Consulting",
        "user_id": "EMP-9999",
        "timestamp": datetime.now().isoformat(),
        "description": "Strategic advisory services"
    }

    print(f"\n{Colors.BOLD}Transaction Details:{Colors.ENDC}")
    print(f"  Amount: ${transaction['amount']:,.2f}")
    print(f"  Merchant: {transaction['merchant']}")
    print(f"  Category: {transaction['category']}")
    print(f"  Employee: {transaction['user_id']}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/process-transaction",
            json=transaction,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            print(f"\n{Colors.BOLD}Analysis Results:{Colors.ENDC}")

            # Fraud Analysis
            fraud = result.get('fraud_analysis', {})
            risk_level = fraud.get('risk_level', 'UNKNOWN')
            fraud_score = fraud.get('fraud_score', 0)

            if risk_level in ['HIGH', 'CRITICAL']:
                print_error(f"Fraud Risk: {risk_level} (Score: {fraud_score:.2f})")
                risk_factors = fraud.get('risk_factors', [])
                if risk_factors:
                    print(f"\n  {Colors.WARNING}Risk Factors:{Colors.ENDC}")
                    for factor in risk_factors:
                        print(f"    • {factor}")
            else:
                print_warning(f"Fraud Risk: {risk_level} (Score: {fraud_score:.2f})")

            # Compliance
            compliance = result.get('compliance_check', {})
            status = compliance.get('status', 'UNKNOWN')

            if status == 'REJECTED':
                print_error(f"Compliance: {status}")
            elif status == 'REVIEW_REQUIRED':
                print_warning(f"Compliance: {status}")
            else:
                print_success(f"Compliance: {status}")

            violations = compliance.get('policy_violations', [])
            if violations:
                print(f"\n  {Colors.FAIL}Policy Violations:{Colors.ENDC}")
                for violation in violations:
                    print(f"    • {violation}")

            # Overall Status
            overall = result.get('overall_status', 'UNKNOWN')
            if overall == 'REJECTED':
                print(f"\n{Colors.BOLD}Overall Decision: {Colors.FAIL}{overall}{Colors.ENDC}")
                print_error("❌ Transaction BLOCKED - Requires immediate review")
            elif overall == 'FLAGGED_FOR_REVIEW':
                print(f"\n{Colors.BOLD}Overall Decision: {Colors.WARNING}{overall}{Colors.ENDC}")
                print_warning("⚠️  Transaction FLAGGED - Manual review required")

        else:
            print_error(f"Request failed: {response.status_code}")

    except Exception as e:
        print_error(f"Error: {e}")

def scenario_3_travel_expense():
    """Scenario 3: Business travel expense"""
    print_header("Scenario 3: Business Travel Expense")

    print_info("Employee books flight and hotel for conference")

    transaction = {
        "transaction_id": "TXN-2025-003",
        "amount": 2850.00,
        "merchant": "United Airlines",
        "category": "Travel",
        "user_id": "EMP-5678",
        "timestamp": datetime.now().isoformat(),
        "description": "Round-trip SFO to NYC for Q1 Sales Conference"
    }

    print(f"\n{Colors.BOLD}Transaction Details:{Colors.ENDC}")
    print(f"  Amount: ${transaction['amount']:,.2f}")
    print(f"  Merchant: {transaction['merchant']}")
    print(f"  Category: {transaction['category']}")
    print(f"  Employee: {transaction['user_id']}")

    try:
        # Check fraud
        fraud_response = requests.post(
            f"{API_BASE_URL}/api/v1/fraud-detection",
            json=transaction,
            timeout=10
        )

        # Check compliance
        compliance_response = requests.post(
            f"{API_BASE_URL}/api/v1/compliance-check",
            json=transaction,
            timeout=10
        )

        # Check spend analysis
        spend_response = requests.post(
            f"{API_BASE_URL}/api/v1/spend-analysis",
            json=transaction,
            timeout=10
        )

        print(f"\n{Colors.BOLD}Multi-Agent Analysis:{Colors.ENDC}")

        if fraud_response.status_code == 200:
            fraud = fraud_response.json()
            print_success(f"✓ Fraud Detection: {fraud.get('risk_level')} risk")

        if compliance_response.status_code == 200:
            compliance = compliance_response.json()
            print_success(f"✓ Compliance Check: {compliance.get('status')}")

        if spend_response.status_code == 200:
            spend = spend_response.json()
            utilization = spend.get('budget_utilization', 0)
            budget = spend.get('budget_limit', 0)
            print_success(f"✓ Spend Analysis: {utilization*100:.1f}% of ${budget:,.2f} budget used")

            if spend.get('over_budget', False):
                print_warning("  ⚠️  This transaction will exceed budget!")
            else:
                print_info(f"  Within budget - ${budget - (utilization * budget):,.2f} remaining")

    except Exception as e:
        print_error(f"Error: {e}")

def scenario_4_vendor_analysis():
    """Scenario 4: Vendor risk analysis"""
    print_header("Scenario 4: Vendor Risk Analysis")

    print_info("Analyzing spending patterns with IT vendor")

    transactions = [
        {
            "transaction_id": f"TXN-2025-00{i}",
            "amount": amount,
            "merchant": "TechCorp Solutions",
            "category": "IT Services",
            "user_id": "EMP-1111",
            "timestamp": datetime.now().isoformat()
        }
        for i, amount in enumerate([5000, 7500, 8200, 6800, 9500], start=10)
    ]

    vendor_name = "TechCorp Solutions"
    total_spend = sum(t['amount'] for t in transactions)

    print(f"\n{Colors.BOLD}Vendor Information:{Colors.ENDC}")
    print(f"  Vendor: {vendor_name}")
    print(f"  Transactions: {len(transactions)}")
    print(f"  Total Spend: ${total_spend:,.2f}")
    print(f"  Average: ${total_spend/len(transactions):,.2f}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/vendor-analysis",
            json={"transactions": transactions},
            params={"vendor_name": vendor_name},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            print(f"\n{Colors.BOLD}Vendor Risk Assessment:{Colors.ENDC}")

            risk_level = result.get('risk_level', 'UNKNOWN')
            risk_score = result.get('risk_score', 0)

            if risk_level == 'LOW':
                print_success(f"Risk Level: {risk_level} (Score: {risk_score:.2f})")
            elif risk_level == 'MEDIUM':
                print_warning(f"Risk Level: {risk_level} (Score: {risk_score:.2f})")
            else:
                print_error(f"Risk Level: {risk_level} (Score: {risk_score:.2f})")

            recommendations = result.get('recommendations', [])
            if recommendations:
                print(f"\n{Colors.BOLD}Recommendations:{Colors.ENDC}")
                for rec in recommendations:
                    print(f"  • {rec}")

    except Exception as e:
        print_error(f"Error: {e}")

def scenario_5_duplicate_vendors():
    """Scenario 5: Duplicate vendor detection"""
    print_header("Scenario 5: Duplicate Vendor Detection")

    print_info("Checking for duplicate vendor entries in the system")

    vendor_names = [
        "Amazon Web Services",
        "AWS Inc",
        "Amazon AWS",
        "Microsoft Corporation",
        "Microsoft Corp",
        "Google Cloud Platform",
        "Google LLC"
    ]

    print(f"\n{Colors.BOLD}Checking {len(vendor_names)} vendors:{Colors.ENDC}")
    for vendor in vendor_names:
        print(f"  • {vendor}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/vendor-duplicates",
            json=vendor_names,
            params={"threshold": 0.75},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            duplicates_found = result.get('duplicates_found', 0)

            print(f"\n{Colors.BOLD}Detection Results:{Colors.ENDC}")
            print_info(f"Total vendors checked: {result.get('total_checked', 0)}")

            if duplicates_found > 0:
                print_warning(f"Potential duplicates found: {duplicates_found}")

                print(f"\n{Colors.BOLD}Duplicate Pairs:{Colors.ENDC}")
                for dup in result.get('results', []):
                    similarity = dup.get('similarity_score', 0)
                    print(f"\n  {Colors.WARNING}Match found:{Colors.ENDC}")
                    print(f"    Vendor 1: {dup.get('vendor_1')}")
                    print(f"    Vendor 2: {dup.get('vendor_2')}")
                    print(f"    Similarity: {similarity*100:.1f}%")
                    print(f"    Action: {dup.get('recommended_action')}")
            else:
                print_success("No duplicate vendors detected")

    except Exception as e:
        print_error(f"Error: {e}")

def scenario_6_system_status():
    """Scenario 6: System health and agent status"""
    print_header("Scenario 6: System Health Check")

    print_info("Checking status of all AI agents")

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/system/status",
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            print(f"\n{Colors.BOLD}System Status: {Colors.OKGREEN}{result.get('status', 'unknown').upper()}{Colors.ENDC}")

            agents = result.get('agents', {})

            print(f"\n{Colors.BOLD}Agent Status:{Colors.ENDC}")

            agent_names = {
                'fraud_detection': 'Fraud Detection Agent',
                'compliance': 'Compliance Screening Agent',
                'spend_analysis': 'Spend Analysis Agent',
                'vendor_analysis': 'Vendor Analysis Agent',
                'document_processing': 'Document Processing Agent',
                'explanation': 'Explanation Generator Agent',
                'learning': 'Learning & Feedback Agent'
            }

            for agent_key, agent_name in agent_names.items():
                agent_data = agents.get(agent_key, {})
                status = agent_data.get('status', 'unknown')

                if status == 'active':
                    print_success(f"{agent_name}: ACTIVE")
                elif status == 'ready':
                    print_info(f"{agent_name}: READY")
                else:
                    print_warning(f"{agent_name}: {status.upper()}")

            print(f"\n{Colors.OKGREEN}✓ All agents operational{Colors.ENDC}")

    except Exception as e:
        print_error(f"Error: {e}")

def interactive_menu():
    """Display interactive menu for demo scenarios"""
    while True:
        print_header("Financial AI Swarm - Interactive Demo")

        print(f"{Colors.BOLD}Available Scenarios:{Colors.ENDC}")
        print(f"\n  {Colors.OKCYAN}1.{Colors.ENDC} Normal Business Transaction (Office Supplies)")
        print(f"  {Colors.WARNING}2.{Colors.ENDC} High-Risk Suspicious Transaction (Large Offshore Payment)")
        print(f"  {Colors.OKBLUE}3.{Colors.ENDC} Business Travel Expense (Flight Booking)")
        print(f"  {Colors.OKCYAN}4.{Colors.ENDC} Vendor Risk Analysis (IT Services)")
        print(f"  {Colors.WARNING}5.{Colors.ENDC} Duplicate Vendor Detection")
        print(f"  {Colors.OKGREEN}6.{Colors.ENDC} System Health Check")
        print(f"\n  {Colors.BOLD}7.{Colors.ENDC} Run All Scenarios")
        print(f"  {Colors.BOLD}0.{Colors.ENDC} Exit")

        choice = input(f"\n{Colors.BOLD}Select scenario (0-7): {Colors.ENDC}").strip()

        if choice == '0':
            print_success("Thank you for using Financial AI Swarm Demo!")
            break
        elif choice == '1':
            scenario_1_normal_transaction()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '2':
            scenario_2_high_risk_transaction()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '3':
            scenario_3_travel_expense()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '4':
            scenario_4_vendor_analysis()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '5':
            scenario_5_duplicate_vendors()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '6':
            scenario_6_system_status()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '7':
            run_all_scenarios()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        else:
            print_error("Invalid choice. Please select 0-7.")
            time.sleep(1)

def run_all_scenarios():
    """Run all demo scenarios"""
    scenarios = [
        scenario_1_normal_transaction,
        scenario_2_high_risk_transaction,
        scenario_3_travel_expense,
        scenario_4_vendor_analysis,
        scenario_5_duplicate_vendors,
        scenario_6_system_status
    ]

    for i, scenario in enumerate(scenarios, 1):
        scenario()
        if i < len(scenarios):
            time.sleep(2)

def main():
    """Main entry point"""
    print_header("Financial AI Swarm - Realistic Demo")
    print_info("Demonstrating multi-agent AI system for financial operations")
    print()

    # Check API health
    if not check_api_health():
        print_error("\nPlease start the API server first:")
        print_info("  python3 standalone_api.py")
        sys.exit(1)

    time.sleep(1)

    # Start interactive menu
    interactive_menu()

if __name__ == "__main__":
    main()
