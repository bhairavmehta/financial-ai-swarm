# 🚀 Quick Access Guide - Financial AI Swarm

## 🌐 Your System is LIVE at:

### Main Access Points
- **🏠 API Home:** http://localhost:8000
- **📚 API Docs (Interactive):** http://localhost:8000/docs
- **📖 API Docs (ReDoc):** http://localhost:8000/redoc
- **❤️ Health Check:** http://localhost:8000/health

---

## ⚡ Quick Test Commands

### Test in Your Browser
Just click: **http://localhost:8000/docs**

### Test with cURL

```bash
# Health check
curl http://localhost:8000/health

# Fraud detection
curl -X POST http://localhost:8000/api/v1/fraud-detection \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"TEST-001","amount":15000,"merchant":"Tech Store","category":"IT Services","user_id":"EMP-001"}'

# Complete analysis
curl -X POST http://localhost:8000/api/v1/process-transaction \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"TEST-002","amount":5000,"merchant":"Office Supplies","category":"Supplies","user_id":"EMP-001"}'
```

---

## 📊 System Status

| Component | Status | URL |
|-----------|--------|-----|
| API Server | ✅ Running | http://localhost:8000 |
| Fraud Detection | ✅ Active | /api/v1/fraud-detection |
| Compliance Check | ✅ Active | /api/v1/compliance-check |
| Spend Analysis | ✅ Active | /api/v1/spend-analysis |
| Vendor Analysis | ✅ Active | /api/v1/vendor-analysis |
| Complete Pipeline | ✅ Active | /api/v1/process-transaction |
| System Status | ✅ Active | /api/v1/system/status |

---

## 🎯 Common Operations

### Stop Server
```bash
pkill -f standalone_api.py
```

### Start Server
```bash
python3 standalone_api.py &
```

### View Logs
```bash
tail -f api_server.log
```

### Check Process
```bash
ps aux | grep standalone_api
```

---

## 📝 Example Transaction

```json
{
  "transaction_id": "TXN-12345",
  "amount": 10000.00,
  "merchant": "Tech Vendor Inc",
  "category": "IT Services",
  "user_id": "EMP-001",
  "timestamp": "2025-12-04T10:30:00Z",
  "location": "New York, NY",
  "description": "Software licenses"
}
```

---

**Need help?** Check [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md) for detailed documentation.
