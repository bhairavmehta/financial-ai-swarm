# Financial AI Swarm - Claude Code Implementation Guide

This guide is specifically for implementing the Financial AI Swarm using Claude Code.

## Quick Implementation with Claude Code

### Step 1: Clone or Create Repository
```bash
# If cloning from existing repo
git clone <your-repo-url>
cd financial-ai-swarm

# Or start fresh
mkdir financial-ai-swarm
cd financial-ai-swarm
```

### Step 2: Let Claude Code Set Everything Up
```bash
# Claude Code can execute all setup commands
claude code "Set up the financial-ai-swarm project: 
1. Create virtual environment
2. Install requirements from requirements.txt
3. Run scripts/init_db.py
4. Verify all components are working"
```

### Step 3: Start Services with Claude Code
```bash
# Claude Code can manage multiple processes
claude code "Start the financial AI swarm:
1. Start FastAPI server on port 8000
2. Start Streamlit UI on port 8501
3. Show me the health status"
```

## Claude Code Workflow

### Development Tasks

**1. Test Individual Agents**
```bash
claude code "Test the fraud detection agent with these transactions:
- A normal $50 coffee purchase
- A suspicious $25,000 late-night transaction
- Show me the risk scores"
```

**2. Customize Agent Behavior**
```bash
claude code "Modify the fraud detection thresholds in 
src/agents/fraud_detection/agent.py to be more sensitive:
- Lower HIGH threshold from 0.7 to 0.6
- Lower CRITICAL threshold from 0.85 to 0.75"
```

**3. Add New Policies**
```bash
claude code "Add these new compliance policies to the system:
1. All cryptocurrency transactions require CFO approval
2. International wire transfers over $100K need dual authorization
Update the compliance agent and test it"
```

**4. Generate Reports**
```bash
claude code "Analyze the last 100 transactions in data/mock/transactions.csv
and generate a PDF report with:
- Fraud detection summary
- Compliance issues
- Budget utilization by category
- Recommendations"
```

### Integration Tasks

**1. Connect to Real Database**
```bash
claude code "Update database configuration to connect to:
Host: prod-db.company.com
Database: financial_transactions
Update src/api/main.py and test connection"
```

**2. Deploy to Cloud**
```bash
claude code "Create AWS deployment configuration:
1. Create Dockerfile optimizations for Lambda
2. Set up API Gateway integration
3. Configure environment variables for production
4. Create deployment script"
```

**3. Set Up Monitoring**
```bash
claude code "Add Datadog monitoring:
1. Install datadog client
2. Add metrics to each agent
3. Create custom dashboard configuration
4. Set up alerts for high fraud scores"
```

### Troubleshooting with Claude Code

**Debug Import Issues**
```bash
claude code "I'm getting ImportError for langchain. 
Check the imports, fix the paths, and verify all dependencies are installed"
```

**Fix API Errors**
```bash
claude code "The /api/v1/process-transaction endpoint is returning 500 errors.
Debug the issue, show me the stack trace, and fix it"
```

**Performance Optimization**
```bash
claude code "The fraud detection is too slow. 
Profile the code, identify bottlenecks, and optimize for <100ms response time"
```

## Project Structure for Claude Code

```
financial-ai-swarm/
├── README.md                    # Main documentation
├── QUICKSTART.md               # Quick start guide
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── docker-compose.yml         # Docker configuration
├── Dockerfile                 # Container definition
│
├── src/                       # Source code
│   ├── agents/                # AI agents
│   │   ├── fraud_detection/   # Fraud detection agent
│   │   ├── compliance/        # Compliance checking
│   │   ├── document_processing/ # OCR and extraction
│   │   ├── spend_analysis/    # Budget tracking
│   │   └── ...
│   ├── orchestration/         # LangGraph orchestrator
│   ├── api/                   # FastAPI server
│   └── ui/                    # Streamlit interface
│
├── scripts/                   # Utility scripts
│   ├── init_db.py            # Setup script
│   └── run_demo.py           # Demo runner
│
├── tests/                     # Test suite
│   └── test_agents.py        # Agent tests
│
├── configs/                   # Configuration
│   └── config.yaml           # Main config
│
├── data/                      # Data directory
│   ├── mock/                 # Mock data for testing
│   └── policies/             # Compliance policies
│
└── models/                    # Trained ML models
```

## Common Claude Code Commands

### Setup & Installation
```bash
# Full setup from scratch
claude code "Set up this financial AI project from requirements.txt"

# Install specific dependency
claude code "Install pinecone-client and update the compliance agent to use it"
```

### Running & Testing
```bash
# Start development server
claude code "Start the FastAPI server in development mode with auto-reload"

# Run specific test
claude code "Run the fraud detection agent tests and show results"

# Run all tests
claude code "Run pytest with coverage report"
```

### Development
```bash
# Implement new feature
claude code "Add a new vendor analysis agent that:
1. Tracks payment patterns
2. Identifies duplicate vendors
3. Calculates vendor risk scores"

# Fix bugs
claude code "The compliance agent is raising KeyError. Debug and fix it"

# Add logging
claude code "Add structured logging to all agent methods using structlog"
```

### Data & Models
```bash
# Generate test data
claude code "Generate 1000 realistic transaction samples with fraud patterns"

# Train models
claude code "Train the fraud detection model on data/transactions.csv"

# Export results
claude code "Export the last week's transaction analysis to Excel"
```

### Deployment
```bash
# Build Docker image
claude code "Build and tag Docker image for production deployment"

# Deploy to cloud
claude code "Deploy this application to Render.com with environment variables from .env"

# Scale services
claude code "Update docker-compose to run 4 API workers for higher throughput"
```

## Advanced Claude Code Workflows

### 1. Complete Feature Implementation
```bash
claude code "Implement a new 'Vendor Risk Scoring' feature:

1. Create src/agents/vendor_analysis/agent.py with:
   - VendorRiskScore dataclass
   - Payment pattern analysis
   - Duplicate vendor detection
   - Risk scoring algorithm

2. Add API endpoint /api/v1/vendor-analysis

3. Update orchestrator to include vendor agent

4. Add UI tab in demo.py for vendor analysis

5. Write tests in tests/test_vendor_agent.py

6. Update README with vendor analysis documentation

Test everything and show me the results"
```

### 2. Integration with External Systems
```bash
claude code "Integrate with Concur API:

1. Create src/integrations/concur_client.py
2. Add authentication using OAuth2
3. Implement expense report fetching
4. Connect to document processing agent
5. Add sync script to scripts/sync_concur.py
6. Test with mock API responses"
```

### 3. Production Optimization
```bash
claude code "Optimize for production:

1. Add Redis caching for fraud model predictions
2. Implement request batching for compliance checks
3. Add connection pooling for database
4. Set up Prometheus metrics
5. Create health check endpoints
6. Add graceful shutdown handling
7. Test performance improvements"
```

## Tips for Using Claude Code

1. **Be Specific**: The more specific your request, the better the results
   - ✅ "Add logging to fraud_detection/agent.py with DEBUG level"
   - ❌ "Add logging"

2. **Iterative Development**: Break large tasks into steps
   ```bash
   claude code "Step 1: Create the vendor agent class structure"
   claude code "Step 2: Implement the risk scoring algorithm"
   claude code "Step 3: Add tests for the vendor agent"
   ```

3. **Use Context**: Reference existing code
   ```bash
   claude code "Following the pattern in fraud_detection/agent.py, 
   create a similar structure for vendor_analysis/agent.py"
   ```

4. **Test Often**: Ask Claude Code to test after changes
   ```bash
   claude code "Run all tests and fix any failures"
   ```

5. **Documentation**: Keep docs updated
   ```bash
   claude code "Update README.md with the new vendor analysis feature"
   ```

## Troubleshooting Guide

### Issue: Import Errors
```bash
claude code "Fix all import errors in the project and ensure PYTHONPATH is set correctly"
```

### Issue: API Not Responding
```bash
claude code "Debug why the API isn't responding:
1. Check if port 8000 is in use
2. Verify environment variables
3. Check logs for errors
4. Test with a simple request"
```

### Issue: Slow Performance
```bash
claude code "Profile the fraud detection agent and optimize for better performance"
```

### Issue: Test Failures
```bash
claude code "All tests in test_agents.py are failing. Debug and fix them"
```

## Next Steps

After setup with Claude Code:

1. **Customize for Your Needs**
   ```bash
   claude code "Modify the system for my company's specific requirements:
   - Different budget categories
   - Custom compliance rules
   - Integration with our ERP system"
   ```

2. **Add More Agents**
   ```bash
   claude code "Add a new 'Invoice Matching' agent that compares 
   POs with invoices and flags discrepancies"
   ```

3. **Improve ML Models**
   ```bash
   claude code "Improve fraud detection accuracy:
   - Add more features
   - Try different algorithms
   - Implement ensemble methods
   - Show before/after comparison"
   ```

4. **Production Deployment**
   ```bash
   claude code "Prepare for production deployment:
   - Add authentication
   - Set up SSL
   - Configure monitoring
   - Create deployment docs"
   ```

## Support

For Claude Code specific issues:
- Check Claude Code documentation
- Use `claude code help` for command reference
- Ask Claude Code to explain any part of the codebase

For project issues:
- Run `python scripts/run_demo.py` to test all components
- Check logs in `logs/app.log`
- Review API docs at http://localhost:8000/docs

---

**Pro Tip**: Claude Code can understand the entire project context. Just ask!
```bash
claude code "Explain how the orchestration supervisor routes tasks to agents"
claude code "Show me all places where the fraud score is calculated"
claude code "What would break if I change the database schema?"
```
