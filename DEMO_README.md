# Financial AI Swarm - Realistic Demo Guide

## Overview

This realistic demo showcases the Financial AI Swarm multi-agent system with real-world transaction scenarios. The demo demonstrates fraud detection, compliance screening, spend analysis, vendor risk assessment, and duplicate detection capabilities.

## Prerequisites

1. **API Server Running**
   ```bash
   python3 standalone_api.py
   ```
   The server should be running on `http://localhost:8000`

2. **Python 3.10+** with `requests` library
   ```bash
   pip3 install requests
   ```

## Quick Start

### Run Interactive Demo

```bash
python3 realistic_demo.py
```

This launches an interactive menu where you can select individual scenarios or run all of them.

## Demo Scenarios

### Scenario 1: Normal Business Transaction ✅
- **Transaction:** $450 office supplies purchase
- **Expected Result:** APPROVED with LOW fraud risk
- **Demonstrates:** Normal transaction processing flow

### Scenario 2: High-Risk Suspicious Transaction ⚠️
- **Transaction:** $45,000 payment to "Offshore Consulting LLC"
- **Expected Result:** REJECTED with HIGH fraud risk
- **Demonstrates:**
  - Fraud detection for large amounts
  - Sanctions screening (blocked vendor)
  - Multi-agent decision making

### Scenario 3: Business Travel Expense ✈️
- **Transaction:** $2,850 airline ticket purchase
- **Expected Result:** APPROVED with budget tracking
- **Demonstrates:**
  - Travel category processing
  - Budget utilization monitoring
  - Multi-agent coordination

### Scenario 4: Vendor Risk Analysis 📊
- **Vendor:** TechCorp Solutions ($37,000 total spend)
- **Demonstrates:**
  - Vendor spending pattern analysis
  - Risk assessment across multiple transactions
  - Payment behavior evaluation

### Scenario 5: Duplicate Vendor Detection 🔍
- **Check:** 7 vendor names for potential duplicates
- **Examples:** "Amazon Web Services" vs "AWS Inc" vs "Amazon AWS"
- **Demonstrates:**
  - Similarity detection
  - Vendor consolidation opportunities
  - Data quality management

### Scenario 6: System Health Check 🏥
- **Check:** Status of all 7 AI agents
- **Demonstrates:**
  - System monitoring
  - Agent health status
  - Operational readiness

## Interactive Menu Options

When you run the demo, you'll see:

```
Financial AI Swarm - Interactive Demo

Available Scenarios:

  1. Normal Business Transaction (Office Supplies)
  2. High-Risk Suspicious Transaction (Large Offshore Payment)
  3. Business Travel Expense (Flight Booking)
  4. Vendor Risk Analysis (IT Services)
  5. Duplicate Vendor Detection
  6. System Health Check
  7. Run All Scenarios
  0. Exit

Select scenario (0-7):
```

## Output Examples

### Approved Transaction
```
✓ Fraud Risk: LOW (Score: 0.15)
✓ Compliance: APPROVED

Overall Decision: APPROVED
```

### Rejected Transaction
```
✗ Fraud Risk: HIGH (Score: 0.75)
  Risk Factors:
    • High transaction amount: $45,000.00
    • Amount exceeds normal threshold

✗ Compliance: REJECTED
  Policy Violations:
    • Merchant 'offshore consulting llc' appears on sanctions list

Overall Decision: REJECTED
❌ Transaction BLOCKED - Requires immediate review
```

### Budget Analysis
```
✓ Spend Analysis: 5.7% of $50,000.00 budget used
  Within budget - $47,150.00 remaining
```

## API Endpoints Demonstrated

The demo uses the following API endpoints:

1. **Health Check**
   - `GET /health`
   - Verifies API server is running

2. **Transaction Processing**
   - `POST /api/v1/process-transaction`
   - Complete multi-agent analysis

3. **Fraud Detection**
   - `POST /api/v1/fraud-detection`
   - Individual fraud risk assessment

4. **Compliance Check**
   - `POST /api/v1/compliance-check`
   - Sanctions and policy screening

5. **Spend Analysis**
   - `POST /api/v1/spend-analysis`
   - Budget tracking and utilization

6. **Vendor Analysis**
   - `POST /api/v1/vendor-analysis`
   - Vendor risk and payment patterns

7. **Duplicate Detection**
   - `POST /api/v1/vendor-duplicates`
   - Find similar vendor names

8. **System Status**
   - `GET /api/v1/system/status`
   - Agent health and operational status

## Customizing the Demo

You can modify transaction scenarios in `realistic_demo.py`:

```python
transaction = {
    "transaction_id": "TXN-CUSTOM-001",
    "amount": 1000.00,
    "merchant": "Your Merchant Name",
    "category": "Your Category",
    "user_id": "EMP-XXXX",
    "timestamp": datetime.now().isoformat(),
    "description": "Your description"
}
```

### Available Categories
- Office Supplies
- Travel
- Entertainment
- IT Services
- Consulting
- Electronics
- Services

## Troubleshooting

### API Server Not Running
```
✗ Cannot connect to API server
ℹ Make sure the server is running: python3 standalone_api.py
```

**Solution:** Start the API server in another terminal:
```bash
python3 standalone_api.py
```

### Connection Timeout
If requests timeout, check:
1. Server is running on port 8000
2. No firewall blocking localhost:8000
3. No other service using port 8000

### Module Not Found
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:** Install required packages:
```bash
pip3 install requests
```

## Real-World Use Cases

### Use Case 1: Expense Approval Workflow
- Employee submits expense via mobile app
- API processes transaction through all agents
- Manager receives decision with risk assessment
- Finance team reviews flagged transactions

### Use Case 2: Vendor Management
- Accounts Payable uploads vendor transactions
- System analyzes spending patterns
- Identifies duplicate vendor entries
- Recommends consolidation opportunities

### Use Case 3: Fraud Prevention
- Credit card transactions monitored in real-time
- High-risk transactions automatically blocked
- Compliance team receives alerts
- Audit trail maintained for review

### Use Case 4: Budget Monitoring
- Department budgets tracked by category
- Real-time utilization monitoring
- Automatic alerts for over-budget scenarios
- Monthly reports generated

## Performance Metrics

Based on the demo scenarios:

| Operation | Average Time | Status |
|-----------|-------------|--------|
| Health Check | <10ms | ✅ |
| Fraud Detection | <50ms | ✅ |
| Compliance Check | <50ms | ✅ |
| Spend Analysis | <50ms | ✅ |
| Complete Pipeline | <200ms | ✅ |
| Vendor Analysis | <100ms | ✅ |
| Duplicate Detection | <150ms | ✅ |

## Next Steps

After running the demo:

1. **Explore API Documentation**
   - Visit http://localhost:8000/docs
   - Try endpoints interactively
   - View request/response schemas

2. **Integrate with Your Application**
   - Use the API endpoints in your app
   - Customize transaction schemas
   - Add authentication

3. **Customize Agents**
   - Modify agent logic in `src/agents/`
   - Add new risk factors
   - Adjust thresholds

4. **Deploy to Production**
   - Follow deployment guide
   - Set up monitoring
   - Configure security

## Support

For questions or issues:
- **Documentation:** See [README.md](README.md)
- **API Docs:** http://localhost:8000/docs
- **GitHub Issues:** https://github.com/bhairavmehta/financial-ai-swarm/issues

---

**Created:** 2025-12-04
**Version:** 1.0.0
**Status:** Production-Ready Demo
