# Financial AI Swarm - Quick Start Guide

Get your multi-agent financial AI system running in minutes!

## Prerequisites

- Python 3.10+
- Docker & Docker Compose (optional)
- 4GB+ RAM
- API keys (OpenAI or Anthropic)

## Quick Setup (5 minutes)

### 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd financial-ai-swarm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Minimum required configuration:**
```bash
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Initialize System

```bash
# Run initialization script
python scripts/init_db.py

# This will:
# - Create necessary directories
# - Download ML models
# - Generate mock data
# - Initialize fraud detection models
```

### 4. Start Services

**Option A: Local Development**
```bash
# Terminal 1: Start API server
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Start UI (in new terminal)
streamlit run src/ui/demo.py
```

**Option B: Docker**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 5. Test the System

```bash
# Run demo scenarios
python scripts/run_demo.py
```

## Access Points

After starting the services:

- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **Health Check**: http://localhost:8000/health
- **Grafana (Docker)**: http://localhost:3000 (admin/admin)

## Quick Test

### Test Fraud Detection
```bash
curl -X POST "http://localhost:8000/api/v1/fraud-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST-001",
    "amount": 15000.00,
    "merchant": "Tech Store",
    "category": "Electronics",
    "user_id": "EMP-001",
    "timestamp": "2025-01-15T10:30:00Z"
  }'
```

### Test Compliance Check
```bash
curl -X POST "http://localhost:8000/api/v1/compliance-check" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST-002",
    "amount": 50000.00,
    "merchant": "Foreign Vendor",
    "category": "Consulting",
    "user_id": "EMP-001"
  }'
```

## Demo Scenarios

The system includes 5 comprehensive demo scenarios:

1. **Fraud Detection**: High-risk transaction analysis
2. **Compliance Check**: Sanctions and PEP screening
3. **Document Processing**: Receipt OCR and extraction
4. **Spend Analysis**: Budget tracking and anomaly detection
5. **Full Flow**: Complete multi-agent processing

Run all demos:
```bash
python scripts/run_demo.py
```

## Troubleshooting

### API Server Won't Start
- Check if port 8000 is available: `lsof -i :8000`
- Verify API keys are set in .env
- Check logs: `tail -f logs/app.log`

### Import Errors
```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Model Download Issues
```bash
# Manually download models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Docker Issues
```bash
# Reset everything
docker-compose down -v
docker-compose up --build
```

## Next Steps

### 1. Explore the UI
- Open http://localhost:8501
- Try the Transaction Analysis page
- Upload a receipt in Document Processing
- Generate spend analytics

### 2. Customize Agents
Edit agent configurations in `configs/config.yaml`:
- Adjust fraud detection thresholds
- Update budget limits
- Configure compliance rules

### 3. Integrate Your Data
Replace mock data with real data:
```python
# Load your transactions
import pandas as pd
transactions = pd.read_csv('your_data.csv')

# Process through API
import requests
for _, txn in transactions.iterrows():
    response = requests.post(
        'http://localhost:8000/api/v1/process-transaction',
        json=txn.to_dict()
    )
```

### 4. Train Custom Models
```bash
# Train fraud detection model with your data
python scripts/train_fraud_model.py --data your_transactions.csv

# Update compliance rules
python scripts/update_compliance_rules.py --source your_rules.yaml
```

## Production Deployment

### Using Docker Compose
```bash
# Production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Using Kubernetes
```bash
# Apply configurations
kubectl apply -f k8s/
```

### Environment Variables for Production
```bash
DEBUG=false
LOG_LEVEL=WARNING
ENABLE_CORS=false
API_KEY_HEADER=X-API-Key
RATE_LIMIT_PER_MINUTE=1000
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Client (UI/API)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Server                             │
│                  (Port 8000)                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              LangGraph Orchestrator                          │
│           (Supervisor Pattern)                               │
└──────┬───────────────────────────────────────────┬──────────┘
       │                                            │
   ┌───▼────────────────────────────────────────────▼───┐
   │          6 Specialized Agents                      │
   ├────────────────────────────────────────────────────┤
   │ Fraud → Compliance → Spend → Vendor → Explain     │
   └────────────────────────────────────────────────────┘
```

## Performance Benchmarks

Expected performance on standard hardware:

- **Fraud Detection**: <100ms per transaction
- **Compliance Check**: <200ms per transaction
- **Document OCR**: <2s per image
- **Full Pipeline**: <500ms per transaction
- **Throughput**: 100+ transactions/second

## Support

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Email**: support@example.com
- **API Docs**: http://localhost:8000/docs

## What's Included

✅ 6 specialized AI agents  
✅ LangGraph orchestration  
✅ Fraud detection with PyOD  
✅ Compliance screening (OFAC/PEP)  
✅ Document OCR with Tesseract  
✅ Spend analysis & budgeting  
✅ RESTful API with FastAPI  
✅ Interactive Streamlit UI  
✅ Docker deployment  
✅ Mock data for testing  
✅ Comprehensive documentation  

## License

MIT License - See LICENSE file

## Contributing

See CONTRIBUTING.md for guidelines.

---

**Ready to go?** Start with `python scripts/init_db.py` and follow the steps above!
