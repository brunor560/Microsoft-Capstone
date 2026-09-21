# 🚀 Quick Start Guide

Get the capstone demo and benchmarks up and running in 5 minutes.

## Prerequisites

- Node.js 18+ (download from https://nodejs.org)
- Git
- A text editor or IDE
- One Claude API key (recommended) or test keys from other providers

## Installation (5 min)

### 1. Clone Repository
```bash
git clone https://github.com/brunor560/Microsoft-Capstone.git
cd Microsoft-Capstone
```

### 2. Install Dependencies
```bash
npm run setup
```

This runs:
- Root: `npm install`
- Baseline: `cd baseline && npm install`

### 3. Set API Keys (2 min)

**Option A: Environment Variables (Recommended)**
```bash
export CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Option B: .env File**
Create `.env` in project root:
```env
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

**Option C: Browser UI**
Add keys directly in demo → Configuration tab (stored locally in browser only)

## Running (Choose One)

### Option 1: Just the Demo (No Backend)
Best for: Quick testing, presentations

```bash
# Open demo.html in your browser
open demo.html
# or
python -m http.server 8000
# Visit http://localhost:8000/demo.html
```

Uses simulated benchmark responses. Safe for presentations—no need for API calls or running services.

### Option 2: Demo + Baseline App (Recommended)
Best for: Development, real testing

**Terminal 1 - Start baseline app:**
```bash
npm start
# App runs at http://localhost:3000
```

**Terminal 2 - Open demo:**
```bash
# In another terminal, open demo.html in browser
open demo.html
```

**Test the baseline app directly:**
- Visit http://localhost:3000
- Add/edit/delete todos
- Run baseline test suite: `npm test` (in baseline/ directory)

### Option 3: Run Full Benchmark Suite (CLI)
Best for: Comprehensive testing, generating reports

**Terminal 1 - Start baseline app:**
```bash
npm start
```

**Terminal 2 - Run benchmarks:**
```bash
npm run benchmark
```

This runs all 4 scenarios × 4 models = 16 tests total.

Generates:
- `benchmarks/results.json` — Machine-readable results
- `benchmarks/results.csv` — Excel-compatible results
- Console output with summary report

**View results:**
- JSON: Open `benchmarks/results.json` in text editor
- CSV: Open `benchmarks/results.csv` in Excel/Sheets
- Web: Copy results to demo page manually

## What You Get

### Landing Page (`index.html`)
- Project overview
- Team bios
- Tech stack & deliverables
- CTA button: "Launch Interactive Demo"

### Demo Page (`demo.html`)
Three tabs:

**Tab 1: Model Comparison** ← Start here
- Enter any software engineering prompt
- Compare responses from Claude, Gemini, CoPilot, Codex
- See latency, tokens, estimated cost
- Optional: Run benchmarks on same prompt

**Tab 2: Benchmarks**
- Choose from 4 standardized scenarios:
  1. **Add Feature** - Implement new endpoint
  2. **Debug Issue** - Fix code bug
  3. **Refactor** - Migrate to database
  4. **Security** - Add validation & rate limiting
- Runs each scenario against all 4 models
- View performance metrics

**Tab 3: Configuration**
- Add API keys for Claude, Gemini, CoPilot, Codex
- Keys stored locally in browser
- Test with simulated responses if no keys

### Baseline App (`baseline/`)
Simple Node.js Todo app that benchmarks test against:
- REST API with CRUD operations
- Test suite validates endpoints
- Serves as standardized testbed

---

## 📊 Example: Running Your First Comparison

1. **Open demo.html**
2. **Go to "Model Comparison" tab**
3. **Enter prompt:**
   ```
   Create a function that validates email addresses using regex.
   Include error handling and comments.
   ```
4. **Select Category:** `Code Implementation`
5. **Select Temperature:** `Medium`
6. **Check:** `Also Run Baseline Benchmarks`
7. **Click:** `Run Comparison`

**Result (30 seconds):**
- 4 response cards with code solutions
- Latency per model
- Token count
- Estimated cost
- Inline benchmark results with quality scores

---

## 🎯 Example: Running Benchmarks

1. **Open demo.html**
2. **Go to "Benchmarks" tab**
3. **Select Scenario:** `Add a Feature` (or `All Scenarios`)
4. **Click:** `Start Benchmark Suite`

**Result (2-3 minutes):**
- Results per model
- Quality scores
- Avg latency, tokens, cost
- Success rates

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Demo page loads (HTML file or via HTTP server)
- [ ] Can enter prompts and get responses
- [ ] API Configuration tab shows (even without keys)
- [ ] Can see simulated responses
- [ ] Baseline app starts: `npm start` → http://localhost:3000
- [ ] Baseline app works: Can add/edit/delete todos
- [ ] Baseline tests pass: `cd baseline && npm test`

✨ **All green?** You're ready to benchmark!

---

## 🔧 Common Commands

```bash
# Start baseline app
npm start

# Run tests
npm test

# Run full benchmark suite
npm run benchmark

# Watch files and reload
npm run dev

# Clean up results
npm run clean

# View baseline app
npm server    # starts at localhost:3000

# Open demo in browser
open demo.html

# Run with different port
PORT=3001 npm start

# Run benchmarks with environment variable
CLAUDE_API_KEY=sk-ant-... npm run benchmark
```

---

## 🐛 Troubleshooting

**Q: Demo shows "simulated" responses**
A: Add API keys in Configuration tab or set environment variables

**Q: Baseline app won't start**
A: 
```bash
cd baseline
npm install  # Reinstall
npm start
```

**Q: Port 3000 already in use**
A: 
```bash
PORT=3001 npm start
```

**Q: Benchmarks take forever**
A: Normal — each model API call takes 1-2 seconds, with 4 scenarios × 4 models = 16 calls total (2-3 min)

**Q: Demo page won't load**
A:
```bash
# Use HTTP server
python -m http.server 8000
# Visit http://localhost:8000/demo.html
```

**Q: Can't find `demo.html`**
A: Make sure you renamed/copied `../demo.html` to `demo.html`

---

## 📚 Next Steps

1. **Explore the demo** - Try different prompts and benchmarks
2. **Review integration guide** - Read `INTEGRATION-GUIDE.md` for architecture details
3. **Add your API keys** - Get real responses from all 4 models
4. **Deploy to GitHub Pages** - Publish the site publicly
5. **Run benchmarks at scale** - Test against more scenarios

---

## 🎬 Video Tour (Coming Soon)

- 2 min: Landing page overview
- 3 min: Demo walkthrough
- 5 min: Benchmark example
- 2 min: Results interpretation

---

## ❓ Questions?

- Check `INTEGRATION-GUIDE.md` for detailed architecture
- See `benchmarks/benchmark-orchestrator.js` for how benchmarks work
- Review `baseline/` folder for API implementation
- Ask team members (contact in INTEGRATION-GUIDE.md)

**Happy benchmarking! 🚀**
