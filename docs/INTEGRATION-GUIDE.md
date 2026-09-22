# AI Model Comparison & Benchmark Integration Guide

## 📋 Overview

This guide explains how to integrate the baseline test application with the AI model comparison demo to enable real-time benchmarking capabilities.

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                     Landing Page                            │
│                    (index.html)                             │
│  • Project overview • Team • Requirements • CTA Demo        │
└────────────────────────┬────────────────────────────────────┘
                         │ "Live Demo" Link
                         ↓
┌─────────────────────────────────────────────────────────────┐
│            Enhanced Interactive Demo Page                   │
│          (demo-with-benchmarks.html)                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Tabs: Model Comparison │ Benchmarks │ Configuration │ │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Tab 1: Model Comparison                                   │
│  • Enter free-form prompt                                  │
│  • Select category & temperature                           │
│  • Toggle: "Run Benchmarks Too"                            │
│  • Results: 4 model cards with latency, tokens, cost       │
│  • Optional: Inline benchmark results                      │
│                                                              │
│  Tab 2: Benchmarks (Standalone)                            │
│  • Select scenario (Add Feature, Debug, Refactor, Security)│
│  • Run full benchmark suite                                │
│  • View detailed results per model                         │
│  • Export results to JSON/CSV                              │
│                                                              │
│  Tab 3: Configuration                                      │
│  • Input API keys (Claude, Gemini, CoPilot, Codex)        │
│  • Stored in localStorage (browser only)                   │
│  • Simulated responses if keys missing                     │
│                                                              │
│  Results:                                                   │
│  • Real API calls for Claude (if key provided)             │
│  • Simulated responses for other models                    │
│  • Performance metrics per model                           │
│  • Cost estimation                                         │
│  • Quality scoring                                         │
└─────────────────────────────────────────────────────────────┘
                         
                    Optional: Backend Integration
                    
┌─────────────────────────────────────────────────────────────┐
│         Baseline Application (localhost:3000)               │
│           Running during benchmark tests                    │
│                                                              │
│  • Express.js Todo API (server.js)                         │
│  • 4 REST endpoints: GET, POST, PUT, DELETE                │
│  • In-memory or SQLite storage                             │
│  • Test suite validates API                                │
│                                                              │
│  Benchmark scenarios run against this baseline:             │
│  • Add Feature - Implement new endpoint                    │
│  • Debug Issue - Fix validation bug                        │
│  • Refactor - Migrate to SQLite                            │
│  • Security - Add validation & rate limiting               │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Benchmark Orchestrator (CLI tool)                   │
│      (benchmarks/benchmark-orchestrator.js)                 │
│                                                              │
│  • Runs all 4 scenarios × 4 models = 16 total tests        │
│  • Calls Claude, Gemini, CoPilot, Codex APIs              │
│  • Measures: latency, tokens, cost, quality                │
│  • Generates JSON + CSV reports                            │
│  • Compares model performance                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
your-capstone-repo/
├── index.html                          # Landing page
├── demo-with-benchmarks.html          # ✨ Enhanced demo with benchmarks
├── demo.html                          # Original demo (backup)
├── package.json                        # Root dependencies
│
├── baseline/                           # Baseline test application
│   ├── server.js                       # Express API
│   ├── test.js                         # Test suite
│   ├── package.json                    # Baseline dependencies
│   └── public/
│       └── index.html                  # Todo app UI
│
├── benchmarks/                         # Benchmarking tools
│   ├── benchmark-orchestrator.js       # ✨ Main orchestrator
│   ├── results.json                    # Benchmark results
│   ├── results.csv                     # CSV export
│   └── scenarios.json                  # Benchmark definitions
│
├── docs/                               # Documentation
│   ├── INTEGRATION-GUIDE.md            # This file
│   └── SETUP.md                        # Setup instructions
│
└── .github/
    └── workflows/
        └── deploy.yml                  # GitHub Pages deploy
```

---

## 🚀 Setup Instructions

### Step 1: Organize Files

```bash
# Clone or navigate to your repo
cd your-capstone-repo

# Create new directories
mkdir -p baseline/public benchmarks docs

# Move baseline app files (if not already organized)
mv app/server.js baseline/
mv app/test.js baseline/
mv app/package.json baseline/
mv app/public/index.html baseline/public/

# Clean up
rmdir app
```

### Step 2: Replace Demo File

```bash
# Backup original demo
cp demo.html demo.html.backup

# Use enhanced version (copy the demo.html content)
cp demo.html demo.html
```

### Step 3: Install Dependencies

**Baseline app:**
```bash
cd baseline
npm install
cd ..
```

**Root (for benchmarking CLI):**
```bash
npm install node-fetch dotenv
```

### Step 4: Set API Keys

Create `.env` file in project root:
```env
# Anthropic
CLAUDE_API_KEY=sk-ant-...

# Google
GEMINI_API_KEY=your-gemini-key...

# OpenAI
OPENAI_API_KEY=sk-...
```

**Or set environment variables:**
```bash
export CLAUDE_API_KEY=sk-ant-...
export GEMINI_API_KEY=...
export OPENAI_API_KEY=...
```

### Step 5: Run Locally

**Terminal 1 - Start baseline app:**
```bash
cd baseline
npm start
# App runs at http://localhost:3000
```

**Terminal 2 - Open demo in browser:**
```bash
# Open in your browser
open demo.html
# Or use a simple HTTP server:
python -m http.server 8000
# Visit http://localhost:8000/demo.html
```

**Terminal 3 - Run benchmarks (optional CLI):**
```bash
node benchmarks/benchmark-orchestrator.js
```

---

## 🎮 How Users Interact

### **Path 1: Model Comparison Tab**

1. User opens demo page
2. Navigates to **"Model Comparison"** tab
3. Enters prompt (e.g., "Create a REST API for user authentication")
4. Selects category (Code Implementation, Debug, etc.)
5. Selects temperature (Low/Medium/High)
6. **Optional:** Checks "Also Run Baseline Benchmarks"
7. Clicks **"Run Comparison"**

**Results displayed:**
- 4 model cards with responses
- Latency, tokens, cost per model
- If benchmarks enabled: inline benchmark results

### **Path 2: Benchmarks Tab (Standalone)**

1. User opens demo page
2. Navigates to **"Benchmarks"** tab
3. Selects benchmark scenario:
   - Add a Feature
   - Debug Issue
   - Refactor Code
   - Security Audit
   - All Scenarios (runs all 4)
4. Clicks **"Start Benchmark Suite"**

**Results displayed:**
- Summary card per model
- Average latency, tokens, quality, cost
- Success rates per scenario

### **Path 3: Configuration Tab**

1. User opens demo page
2. Navigates to **"Configuration"** tab
3. Enters API keys for models they have access to
4. Clicks **"Save API Keys"**
5. Keys stored in localStorage (browser only, never sent to server)

---

## 🔧 Features Explained

### **Model Comparison (Default Tab)**

**Input Options:**
- **Prompt**: Free-form text (any software engineering question)
- **Task Category**: General | Code | Debug | Refactor | Security
- **Temperature**: Low (0.3) | Medium (0.7) | High (1.0)
- **Include Benchmarks**: Toggle to run optional baseline benchmarks

**Output Metrics:**
- **Latency**: Time to get response (ms)
- **Tokens**: Output tokens used
- **Cost**: Estimated cost based on model pricing
- **Status**: Success or error

**Response Handling:**
- Claude: Real API call if key provided
- Others: Simulated with realistic latencies

### **Benchmarks (Standalone)**

**Four Standardized Scenarios:**

1. **Add a Feature** (30 seconds)
   - Task: Implement GET /api/todos/stats endpoint
   - Tests: Can model create new endpoint with correct logic?
   - Metrics: Code correctness, latency, token efficiency

2. **Debug Issue** (40 seconds)
   - Task: Fix undefined reference in update function
   - Tests: Can model identify and fix the bug?
   - Metrics: Problem diagnosis, solution quality

3. **Refactor to SQLite** (50 seconds)
   - Task: Migrate from in-memory to database storage
   - Tests: Can model refactor architecture?
   - Metrics: Code quality, completeness, best practices

4. **Security Hardening** (50 seconds)
   - Task: Add validation, rate limiting, security headers
   - Tests: Can model implement security best practices?
   - Metrics: Security awareness, implementation depth

**Results per Model:**
- Tests run
- Average latency
- Average tokens
- Average quality score
- Success rate
- Estimated cost

### **Quality Scoring**

Each response is scored 0-100 based on:
- **Response length**: Longer, more complete responses = higher score
- **Relevant keywords**: Presence of domain-specific terms
- **Code blocks**: Presence of actual code implementation
- **Scenario-specific criteria**:
  - Feature: Function, error handling, status codes
  - Bug: Bug identification, validation, null checks
  - Refactor: Database schema, queries, migrations
  - Security: Validation, sanitization, rate limiting

---

## 📊 Results & Exports

### **Benchmark Results File**

`benchmarks/results.json`:
```json
{
  "timestamp": "2026-09-21T12:34:56.789Z",
  "totalDuration": 120000,
  "scenarios": 4,
  "models": 4,
  "results": [
    {
      "model": "Claude 3.5 Sonnet",
      "modelId": "claude",
      "scenario": "Add a Feature",
      "scenarioId": "add-feature",
      "status": "success",
      "latency": 2156,
      "tokens": 456,
      "cost": "0.0068",
      "qualityScore": 87,
      "timestamp": "2026-09-21T12:34:56.789Z"
    }
    // ... more results
  ],
  "summary": {
    "claude": {
      "name": "Claude 3.5 Sonnet",
      "avgLatency": 1823,
      "avgTokens": 512,
      "avgQuality": 84,
      "totalCost": "0.0512",
      "successRate": "100%"
    }
    // ... more models
  }
}
```

### **CSV Export**

`benchmarks/results.csv`:
```csv
"Model","Scenario","Status","Latency (ms)","Tokens","Cost","Quality Score"
"Claude 3.5 Sonnet","Add a Feature","success","2156","456","0.0068","87"
```

### **Access Results in Browser**

After running benchmarks, results are displayed in the demo UI:
- Model comparison cards with metrics
- Benchmark summary cards
- Quality scores per model
- Cost breakdowns

---

## 🔐 Security & Privacy

### **API Keys**
- Stored in browser's localStorage only
- Never sent to Anthropic servers
- User can clear anytime in browser settings
- Use separate test keys if concerned

### **Benchmark Data**
- Results stored locally in `benchmarks/results.json`
- Not automatically uploaded
- User can manually share results if desired

### **Model Responses**
- Real responses only sent between user's browser and model APIs
- Simulated responses for demo models (no real data)

---

## 🐛 Troubleshooting

### **Issue: Claude API returns 401 error**
**Solution:** Check API key is correct and has valid credits

### **Issue: Benchmarks run very slowly**
**Solution:** 
- Benchmarks make multiple API calls
- First run takes ~2-3 minutes for all scenarios
- Subsequent runs faster if using cached responses

### **Issue: Demo page shows "simulated" responses**
**Solution:** Add API keys in Configuration tab

### **Issue: Baseline app won't start**
**Solution:**
```bash
cd baseline
npm install  # Reinstall dependencies
npm start
```

### **Issue: Port 3000 already in use**
**Solution:**
```bash
# Use different port
PORT=3001 npm start
```

---

## 📈 Next Steps

### **Phase 1: Basic Integration** (Current)
- ✅ Landing page with overview
- ✅ Interactive demo with model comparison
- ✅ Benchmark scenarios defined
- ✅ UI with tabs and configuration

### **Phase 2: Backend Integration**
- Implement Gemini API calls
- Implement OpenAI API calls
- Add real database storage for results
- Implement cost calculation per model

### **Phase 3: Advanced Features**
- Historical benchmark tracking
- Model performance trends
- Custom scenario creation
- Automated benchmarks on schedule
- Slack/email integration for results

### **Phase 4: Production Deployment**
- Deploy to GitHub Pages (frontend)
- Deploy API backend to cloud (GCP/AWS)
- Set up CI/CD pipeline for benchmarks
- Add authentication & result storage

---

## 📚 Additional Resources

- **Anthropic API Docs**: https://docs.anthropic.com
- **Express.js Docs**: https://expressjs.com
- **Benchmark Design**: See `BENCHMARK-DESIGN.md`
- **Team Repository**: https://github.com/brunor560/Microsoft-Capstone

---

## ✋ Questions?

Contact team members:
- **Bruno Rocha** (Anthropic Lead)
- **Joseph Bressani** (OpenAI Lead)
- **Kapil Srikanth** (Google Lead)
- **Ross Volenec** (Microsoft Lead)

Faculty: Scot Hollingsworth
