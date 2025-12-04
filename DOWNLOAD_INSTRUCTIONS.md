# 📥 Download Instructions for Financial AI Swarm

## Available Download Options

### Option 1: Direct Download (Recommended)

**Compressed Archive (TAR.GZ)**
- [Download financial-ai-swarm.tar.gz](computer:///mnt/user-data/outputs/financial-ai-swarm.tar.gz) (45 KB)
- Best for Linux/Mac
- Smallest file size

**ZIP Archive**
- [Download financial-ai-swarm.zip](computer:///mnt/user-data/outputs/financial-ai-swarm.zip) (66 KB)
- Best for Windows
- Universal compatibility

**Individual Folder**
- [Browse financial-ai-swarm folder](computer:///mnt/user-data/outputs/financial-ai-swarm)
- Download specific files
- Explore before downloading

### Option 2: Quick Install Script

[Download install.sh](computer:///mnt/user-data/outputs/install.sh)

One-command installation:
```bash
bash install.sh
```

This script will:
- Create project structure
- Set up virtual environment
- Install dependencies
- Create configuration files

## After Download

### Extract the Archive

**For TAR.GZ (Linux/Mac):**
```bash
tar -xzf financial-ai-swarm.tar.gz
cd financial-ai-swarm
```

**For ZIP (Windows/Mac/Linux):**
```bash
unzip financial-ai-swarm.zip
cd financial-ai-swarm
```

### Quick Start

1. **Install Dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Initialize**
   ```bash
   python scripts/init_db.py
   ```

4. **Run**
   ```bash
   # Terminal 1
   uvicorn src.api.main:app --reload
   
   # Terminal 2
   streamlit run src/ui/demo.py
   ```

## What's Included

```
financial-ai-swarm/
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md               # 5-minute setup guide
├── 📄 CLAUDE_CODE_GUIDE.md        # Claude Code instructions
├── 📄 IMPLEMENTATION_SUMMARY.md   # Technical overview
├── 📄 GET_STARTED.md              # Quick reference
│
├── 📁 src/                        # Source code
│   ├── agents/                    # 6 AI agents
│   │   ├── fraud_detection/       # ✅ Complete
│   │   ├── compliance/            # ✅ Complete
│   │   ├── document_processing/   # ✅ Complete
│   │   ├── spend_analysis/        # ✅ Complete
│   │   ├── vendor_analysis/       # Ready to implement
│   │   └── explanation/           # Ready to implement
│   ├── orchestration/             # ✅ LangGraph supervisor
│   ├── api/                       # ✅ FastAPI server
│   └── ui/                        # ✅ Streamlit interface
│
├── 📁 scripts/                    # Utility scripts
│   ├── init_db.py                # Setup script
│   └── run_demo.py               # Demo runner
│
├── 📁 tests/                      # Test suite
├── 📁 configs/                    # Configuration
├── 📁 data/                       # Data directory
└── 📁 models/                     # ML models
```

## File Sizes

- **TAR.GZ**: 45 KB
- **ZIP**: 66 KB
- **Uncompressed**: ~177 KB

## System Requirements

- **Python**: 3.10 or higher
- **RAM**: 4GB minimum
- **Disk**: 500MB (including dependencies)
- **OS**: Linux, macOS, Windows

## Dependencies

The project uses:
- LangChain/LangGraph (orchestration)
- FastAPI (API server)
- Streamlit (UI)
- PyOD (fraud detection)
- Sentence Transformers (embeddings)
- And more... (see requirements.txt)

Total ~300MB of Python packages will be installed.

## Verification

After download, verify the contents:

```bash
cd financial-ai-swarm

# Check structure
ls -la

# Should see:
# - src/ folder with agents
# - scripts/ folder
# - tests/ folder
# - README.md and other docs
# - requirements.txt
# - docker-compose.yml
```

## Alternative: Clone from Repository

If you push this to GitHub:

```bash
git clone https://github.com/yourusername/financial-ai-swarm.git
cd financial-ai-swarm
```

## Troubleshooting Download Issues

### "Permission Denied"
```bash
chmod +x install.sh
```

### "Cannot Extract"
```bash
# Install extraction tools
# Ubuntu/Debian
sudo apt-get install unzip tar gzip

# macOS
brew install unzip

# Windows
# Use 7-Zip or built-in Windows extraction
```

### "File Corrupted"
- Try downloading again
- Verify file size matches (45 KB for .tar.gz, 66 KB for .zip)
- Try alternative format (ZIP vs TAR.GZ)

## Quick Test After Download

```bash
# Verify Python files
find . -name "*.py" | wc -l
# Should show: 24

# Verify documentation
find . -name "*.md" | wc -l
# Should show: 5

# Check main components
ls src/agents/
# Should show: fraud_detection, compliance, document_processing, spend_analysis, etc.
```

## Need Help?

1. **Read Documentation**
   - Start with GET_STARTED.md
   - Then QUICKSTART.md
   - Check CLAUDE_CODE_GUIDE.md for Claude Code usage

2. **Run Demo**
   ```bash
   python scripts/run_demo.py
   ```

3. **Check API Docs**
   ```bash
   uvicorn src.api.main:app --reload
   # Visit: http://localhost:8000/docs
   ```

## What's Working

✅ Fraud detection with 5 ML models  
✅ Compliance screening (OFAC/PEP)  
✅ Document OCR processing  
✅ Spend analysis & budgeting  
✅ Complete REST API  
✅ Interactive demo UI  
✅ Docker deployment  
✅ Test suite  

## Next Steps

1. Download using one of the options above
2. Extract and navigate to project
3. Follow QUICKSTART.md
4. Run `python scripts/run_demo.py`
5. Start customizing for your needs!

---

**Questions?** All documentation is included in the download!
