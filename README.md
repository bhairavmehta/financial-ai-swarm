# Financial AI Swarm - Multi-Agent Orchestration System

A comprehensive multi-agent AI system for financial operations featuring fraud detection, compliance checking, document processing, and intelligent orchestration.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                        │
│              (LangGraph Supervisor Pattern)                  │
└──────┬───────────────────────────────────────────┬──────────┘
       │                                            │
   ┌───▼────────────────────────────────────────────▼───┐
   │              Agent Registry (6 Agents)              │
   ├─────────────────────────────────────────────────────┤
   │ 1. Fraud Detection    │ 4. Vendor Analysis         │
   │ 2. Compliance Check   │ 5. Explanation Generator   │
   │ 3. Spend Analysis     │ 6. Learning & Feedback     │
   └─────────────────────────────────────────────────────┘
```

## System Components

### 1. Core Orchestration (LangGraph)
- **Supervisor Pattern**: Routes tasks to specialized agents
- **State Management**: Maintains conversation and transaction context
- **Oracle MCP Architecture**: Message passing and coordination

### 2. Fraud Detection Agent
- Real-time anomaly detection using PyOD
- ML-based scoring (Isolation Forest, LOF, AutoEncoder)
- Transaction pattern analysis
- Risk scoring engine

### 3. Document Processing Agents
- OCR for receipts and invoices (Sparrow-based)
- Automated field extraction
- Integration with expense management systems
- Mock Concur data connector

### 4. Compliance Agent
- OFAC/PEP screening
- Sanctions list checking
- Policy RAG with vector database
- Regulatory rule engine

### 5. Spend Analysis Agent
- Budget tracking and alerts
- Category classification
- Anomaly detection in spending patterns
- Vendor relationship analysis

### 6. Vendor Analysis Agent
- Vendor risk assessment
- Payment pattern analysis
- Duplicate detection
- Vendor consolidation recommendations

## Installation

### Prerequisites
- Python 3.10+
- Docker (optional, for containerized deployment)
- API Keys (see `.env.example`)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd financial-ai-swarm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize databases
python scripts/init_db.py

# Download ML models
python scripts/download_models.py
```

## Quick Start

### Run the FastAPI Server
```bash
uvicorn src.api.main:app --reload --port 8000
```

### Run the Streamlit Demo
```bash
streamlit run src.ui/demo.py
```

### Test the System
```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Run end-to-end demo
python scripts/run_demo.py
```

## API Usage

### Transaction Processing Endpoint
```python
import requests

transaction = {
    "transaction_id": "TXN-12345",
    "amount": 15000.00,
    "merchant": "Tech Vendor Inc",
    "category": "IT Services",
    "user_id": "EMP-001",
    "timestamp": "2025-01-15T10:30:00Z"
}

response = requests.post(
    "http://localhost:8000/api/v1/process-transaction",
    json=transaction
)

result = response.json()
print(f"Fraud Score: {result['fraud_score']}")
print(f"Compliance Status: {result['compliance_status']}")
```

### Document Upload Endpoint
```python
files = {"file": open("receipt.jpg", "rb")}
response = requests.post(
    "http://localhost:8000/api/v1/upload-document",
    files=files
)

extracted_data = response.json()
```

## Project Structure

```
financial-ai-swarm/
├── src/
│   ├── agents/               # Agent implementations
│   │   ├── fraud_detection/
│   │   ├── compliance/
│   │   ├── document_processing/
│   │   ├── spend_analysis/
│   │   ├── vendor_analysis/
│   │   └── explanation/
│   ├── orchestration/        # LangGraph orchestrator
│   ├── models/              # ML models
│   ├── api/                 # FastAPI endpoints
│   ├── ui/                  # Streamlit interface
│   └── utils/               # Shared utilities
├── tests/                   # Test suite
├── data/                    # Sample data
├── models/                  # Trained model files
├── configs/                 # Configuration files
└── docs/                    # Documentation
```

## Configuration

Edit `configs/config.yaml` to customize:
- Agent behavior and thresholds
- Model parameters
- API endpoints
- Logging settings

## Demo Scenarios

### Scenario 1: High-Risk Transaction
Processes a large transaction through all agents, demonstrating fraud detection and compliance checking.

### Scenario 2: Receipt Processing
Uploads a receipt image, extracts fields, and validates against policy.

### Scenario 3: Vendor Analysis
Analyzes vendor payment patterns and identifies duplicates.

### Scenario 4: Compliance Screening
Checks a vendor against OFAC/PEP lists.

## Development

### Adding a New Agent
1. Create agent class in `src/agents/`
2. Implement `process()` method
3. Register in `src/orchestration/registry.py`
4. Add tests in `tests/agents/`

### Training Fraud Models
```bash
python scripts/train_fraud_model.py --data data/transactions.csv
```

### Updating Compliance Rules
```bash
python scripts/update_compliance_rules.py --source configs/rules.yaml
```

## Monitoring & Observability

- **Metrics**: Prometheus-compatible metrics at `/metrics`
- **Logging**: Structured JSON logging
- **Tracing**: OpenTelemetry integration
- **Dashboard**: Grafana dashboards in `monitoring/`

## Security

- API key authentication
- Rate limiting on endpoints
- Data encryption at rest
- PII redaction in logs
- Audit trail for all decisions

## Performance

- Fraud detection: <100ms per transaction
- Document OCR: <2s per image
- Concurrent processing: 100+ TPS
- Scalable with Kubernetes

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE)

## References

- LangGraph: https://github.com/langchain-ai/langgraph
- AWS Fraud Detection: https://github.com/aws-solutions-library-samples/fraud-detection-using-machine-learning
- Sparrow OCR: https://github.com/katanaml/sparrow
- FinCrime Multi-Agent: https://github.com/ajananth/fincrime-multiagent-fsi

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: <repository-url>/docs
- Email: support@example.com
