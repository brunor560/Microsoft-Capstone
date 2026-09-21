# 🏗️ System Architecture

## Data Flow Diagram

```
USER BROWSER
    │
    ├─────────────────────────────────────────────────────────┐
    │                                                          │
    │  ┌────────────────────────────────────────────────────┐ │
    │  │ demo-with-benchmarks.html (Single Page App)       │ │
    │  ├────────────────────────────────────────────────────┤ │
    │  │                                                    │ │
    │  │  Tab 1: MODEL COMPARISON                          │ │
    │  │  ├─ Input: Prompt, Category, Temperature          │ │
    │  │  ├─ Toggle: Enable Benchmarks                     │ │
    │  │  └─ Output: 4 Model Cards                         │ │
    │  │     ├─ Claude (Real API if key available)         │ │
    │  │     ├─ Gemini (Simulated)                         │ │
    │  │     ├─ CoPilot (Simulated)                        │ │
    │  │     └─ Codex (Simulated)                          │ │
    │  │                                                    │ │
    │  │  Per Card:                                        │ │
    │  │  ├─ Response text                                 │ │
    │  │  ├─ Latency (ms)                                  │ │
    │  │  ├─ Tokens                                        │ │
    │  │  ├─ Cost ($)                                      │ │
    │  │  └─ Quality Score (/100)                          │ │
    │  │                                                    │ │
    │  │  Optional: Inline Benchmark Results               │ │
    │  │  └─ Quick bench for that prompt                   │ │
    │  │                                                    │ │
    │  ├────────────────────────────────────────────────────┤ │
    │  │                                                    │ │
    │  │  Tab 2: BENCHMARKS (STANDALONE)                   │ │
    │  │  ├─ Scenario Selector                             │ │
    │  │  │  ├─ Add Feature (30s)                          │ │
    │  │  │  ├─ Debug Issue (40s)                          │ │
    │  │  │  ├─ Refactor (50s)                             │ │
    │  │  │  ├─ Security (50s)                             │ │
    │  │  │  └─ All Scenarios (3 min)                      │ │
    │  │  │                                                │ │
    │  │  └─ Run Benchmark Suite                           │ │
    │  │     └─ Calls each model with scenario prompt      │ │
    │  │        └─ Generates results grid                  │ │
    │  │                                                    │ │
    │  │  Results per Model:                               │ │
    │  │  ├─ Avg Latency                                   │ │
    │  │  ├─ Avg Tokens                                    │ │
    │  │  ├─ Quality Score                                 │ │
    │  │  ├─ Success Rate                                  │ │
    │  │  └─ Total Cost                                    │ │
    │  │                                                    │ │
    │  ├────────────────────────────────────────────────────┤ │
    │  │                                                    │ │
    │  │  Tab 3: CONFIGURATION                             │ │
    │  │  ├─ Claude API Key [password input]               │ │
    │  │  ├─ Gemini API Key [password input]               │ │
    │  │  ├─ CoPilot API Key [password input]              │ │
    │  │  └─ Codex API Key [password input]                │ │
    │  │     └─ Save → localStorage                        │ │
    │  │                                                    │ │
    │  │  Note: Keys never leave browser                   │ │
    │  │                                                    │ │
    │  └────────────────────────────────────────────────────┘ │
    │                                                          │
    └──────┬──────────────────────┬──────────────────────┬─────┘
           │                      │                      │
           │ localStorage         │ API Calls           │
           │ (API Keys)           │                      │
           ↓                      ↓                      ↓
    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
    │  Browser     │    │  External APIs  │    │  Baseline    │
    │  localStorage│    │                 │    │  App (opt)   │
    │              │    │  Anthropic API  │    │              │
    │ Persists:    │    │  ├─ Claude      │    │ localhost    │
    │ - API Keys   │    │  │                │    │ :3000        │
    │ - Settings   │    │  │ /messages      │    │              │
    │ - History    │    │  │ (POST)         │    │ Express.js   │
    │              │    │  │ ↓              │    │              │
    │              │    │  │ {response}     │    │ Endpoints:   │
    │              │    │  │                │    │ - GET /todos │
    │              │    │  ├─ Google API   │    │ - POST/PUT   │
    │              │    │  │ (Placeholder) │    │ - DELETE     │
    │              │    │  │                │    │              │
    │              │    │  ├─ OpenAI API  │    │ Used by:     │
    │              │    │  │ (Placeholder) │    │ - Benchmark  │
    │              │    │  │                │    │   scenarios  │
    │              │    │  └─ Others       │    │              │
    │              │    │                 │    │              │
    │              │    └─────────────────┘    └──────────────┘
    │              │                                  │
    │              └──────────────┬──────────────────┘
    │                             │
    │                        (Optional)
    │
    └─ Results displayed in browser
       - Cards with metrics
       - Charts (if implemented)
       - Export as JSON/CSV
```

---

## Component Interaction Sequence

### Scenario 1: User Runs Model Comparison

```
User                Browser              localStorage         API
 │                   │                      │                  │
 │ Opens demo.html   │                      │                  │
 ├──────────────────►│                      │                  │
 │                   │ Load API Keys        │                  │
 │                   ├─────────────────────►│                  │
 │                   │◄─────────────────────┤                  │
 │                   │ (Claude key found)   │                  │
 │                   │                      │                  │
 │ Enters prompt     │                      │                  │
 │ + options        │                      │                  │
 ├──────────────────►│                      │                  │
 │                   │                      │                  │
 │ Clicks "Run"      │                      │                  │
 ├──────────────────►│ For each model:      │                  │
 │                   ├─ Build prompt       │                  │
 │                   │                      │                  │
 │                   ├─ Call Claude API────────────────────────►│
 │                   │                      │                  │
 │                   │◄─ {response}◄────────────────────────────┤
 │                   │ + tokens + latency   │                  │
 │                   │                      │                  │
 │                   ├─ Simulate Gemini    │                  │
 │                   ├─ Simulate CoPilot   │                  │
 │                   ├─ Simulate Codex     │                  │
 │                   │                      │                  │
 │                   │ Score responses     │                  │
 │                   │ Calculate costs     │                  │
 │                   │                      │                  │
 │ Views results     │                      │                  │
 │◄──────────────────┤ Render 4 cards      │                  │
 │                   │ + metrics           │                  │
 │                   │                      │                  │
```

### Scenario 2: User Runs Benchmarks

```
User                Browser              Benchmark Scenarios
 │                   │                      │
 │ Selects scenario  │                      │
 ├──────────────────►│                      │
 │                   │ or "All"            │
 │ Clicks "Start"    │                      │
 ├──────────────────►│                      │
 │                   │ Load scenario prompts├─────────────────┐
 │                   │◄──────────────────────────────────────┤
 │                   │                      │
 │                   │ For each scenario:   │
 │                   │  └─ For each model:  │
 │                   │     ├─ Call API     │
 │                   │     ├─ Time response│
 │                   │     ├─ Count tokens │
 │                   │     ├─ Score result │
 │                   │     └─ Store result │
 │                   │                      │
 │ Views results     │ Calculate summary   │
 │◄──────────────────┤ ├─ Avg latency     │
 │                   │ ├─ Avg quality     │
 │                   │ ├─ Success rates   │
 │                   │ └─ Total costs     │
 │                   │                      │
 │ (Optional)        │ Render results grid │
 │ Export CSV/JSON   │◄────────────────────┤
 └──────────────────►│                      │
```

---

## File Structure & Responsibilities

```
/                              (Root directory)
├── index.html               # Landing page
│   └─ Static HTML, CSS, minimal JS
│   └─ Serves overview, team, deliverables
│   └─ CTA: "Launch Demo" → demo.html
│
├── demo.html ✨             # Enhanced demo with benchmarks
│   ├─ Three tabs:
│   │  ├─ Model Comparison (free-form prompts)
│   │  ├─ Benchmarks (standardized scenarios)
│   │  └─ Configuration (API keys)
│   │
│   ├─ JavaScript Functions:
│   │  ├─ switchTab() - Tab navigation
│   │  ├─ runComparison() - Call all 4 models
│   │  ├─ callModel(model, prompt) - Single model call
│   │  ├─ callClaudeAPI() - Real Anthropic API
│   │  ├─ runBenchmarks() - Run scenario suite
│   │  ├─ displayBenchmarkResults() - Render results
│   │  ├─ saveAPIKeys() - Store in localStorage
│   │  ├─ escapeHtml() - Security (XSS prevention)
│   │  └─ loadAPIKeys() - Initialize
│   │
│   └─ Handles:
│      ├─ User input (prompts, options)
│      ├─ API calls (Claude only, others simulated)
│      ├─ Response timing & token counting
│      ├─ Quality scoring
│      ├─ Cost calculation
│      └─ Result rendering
│
├── baseline/               # Baseline test application
│   ├── server.js          # Express.js API server
│   │  ├─ 4 REST endpoints (GET, POST, PUT, DELETE)
│   │  ├─ In-memory todo storage
│   │  ├─ Error handling
│   │  └─ Runs on localhost:3000
│   │
│   ├── test.js            # Test suite
│   │  ├─ Unit tests for API
│   │  ├─ Validates endpoints
│   │  └─ Runs with: npm test
│   │
│   ├── package.json       # Dependencies (Express)
│   │
│   └── public/
│       └── index.html     # Todo app UI
│          ├─ Client connects to /api/todos
│          ├─ CRUD operations
│          ├─ Real-time updates
│          └─ Used for manual testing
│
├── benchmarks/            # Benchmarking tools
│   ├── benchmark-orchestrator.js ✨
│   │  ├─ Main orchestrator script
│   │  ├─ Loads 4 scenarios (hardcoded)
│   │  ├─ Loops through 4 models
│   │  ├─ Makes API calls
│   │  ├─ Scores responses
│   │  ├─ Calculates costs
│   │  ├─ Generates reports
│   │  └─ Export JSON + CSV
│   │
│   ├── results.json       # Output from benchmarks
│   │  ├─ All 16 test results
│   │  ├─ Model summaries
│   │  ├─ Performance metrics
│   │  └─ Generated by: npm run benchmark
│   │
│   └── results.csv        # Excel export
│      └─ Tab-separated results for spreadsheets
│
├── docs/                  # Documentation
│   ├── INTEGRATION-GUIDE.md  # How everything connects
│   ├── ARCHITECTURE.md       # This file
│   ├── QUICKSTART.md         # Setup & running
│   └── BENCHMARK-DESIGN.md   # Scenario details
│
├── package.json ✨        # Root dependencies
│   ├─ Scripts for running baseline + benchmarks
│   ├─ npm run setup - Install everything
│   ├─ npm start - Run baseline app
│   ├─ npm test - Run tests
│   ├─ npm run benchmark - Run benchmark suite
│   └─ npm run clean - Remove results
│
└── .env (optional)        # Environment variables
   ├─ CLAUDE_API_KEY
   ├─ GEMINI_API_KEY
   ├─ OPENAI_API_KEY
   └─ Never commit to git (add to .gitignore)
```

---

## Data Structures

### Model Response (JavaScript)
```javascript
{
  status: 'success' | 'error' | 'simulated',
  text: 'Response text from model...',
  latency: 2156,           // ms
  tokens: 456,             // output tokens
  cost: '0.0068',         // $
  error: 'Error message (if status=error)'
}
```

### Benchmark Result (JSON)
```javascript
{
  model: 'Claude 3.5 Sonnet',
  modelId: 'claude',
  scenario: 'Add a Feature',
  scenarioId: 'add-feature',
  status: 'success',
  latency: 2156,
  tokens: 456,
  cost: '0.0068',
  qualityScore: 87,
  timestamp: '2026-09-21T12:34:56.789Z',
  responsePreview: 'First 200 chars of response...'
}
```

### Benchmark Summary (JSON)
```javascript
{
  claude: {
    name: 'Claude 3.5 Sonnet',
    testsRun: 4,
    avgLatency: 1823,
    avgTokens: 512,
    avgQuality: 84,
    totalCost: '0.0512',
    successRate: '100%'
  },
  // ... other models
}
```

---

## Request/Response Flow

### Request to Claude API
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 1000,
  "temperature": 0.7,
  "messages": [
    {
      "role": "user",
      "content": "Your prompt here..."
    }
  ]
}
```

### Response from Claude API
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Claude's response..."
    }
  ],
  "model": "claude-3-5-sonnet-20241022",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 123,
    "output_tokens": 456
  }
}
```

---

## Performance Characteristics

### Latency (per model call)
- **Claude API**: 1-3 seconds (real API)
- **Simulated models**: 500-2000ms (artificial delay)

### Total Time
- **Single comparison**: 5-10 seconds
- **Benchmark (1 scenario)**: 30-50 seconds
- **Benchmark (all 4 scenarios)**: 2-3 minutes

### Network
- **Bandwidth**: Minimal (text only)
- **Requests**: 4 per comparison, 16 per full benchmark
- **Rate limits**: Respect model-specific limits

### Storage
- **localStorage**: ~1KB per API key + results (browser-only)
- **results.json**: ~50KB per full benchmark run
- **results.csv**: ~30KB per full benchmark run

---

## Security Considerations

### Data Privacy
✅ API keys stored in localStorage only (browser-only)
✅ No data sent to Anthropic except API calls
✅ Results not automatically uploaded
✅ User controls what's shared

### API Security
✅ HTTPS for all API calls
✅ API keys from official providers only
✅ No key logging or interception
✅ Rate limiting on API calls

### XSS Prevention
✅ HTML escaping for model responses
✅ No eval() or dangerous operations
✅ Content Security Policy (if deployed)

---

## Deployment Architecture

### Development
- Demo: Any HTTP server (python -m http.server)
- Baseline: Node.js (localhost:3000)
- Benchmarks: CLI tool (node script)

### Production (GitHub Pages)
- Demo: Hosted on GitHub Pages (free)
- Baseline: Deploy to cloud (GCP/AWS/Heroku)
- Benchmarks: Scheduled jobs (GitHub Actions)

---

## Technology Stack

**Frontend**
- HTML5
- CSS3 (no frameworks)
- Vanilla JavaScript (no libraries)
- localStorage API
- Fetch API

**Backend**
- Node.js 18+
- Express.js 4.22+
- SQLite (optional for baseline refactoring)

**APIs**
- Anthropic API (Claude)
- Google Gemini API
- OpenAI API (CoPilot, Codex)

**DevOps**
- Git + GitHub
- GitHub Pages (frontend)
- GitHub Actions (CI/CD)
- npm (package management)

---

## Future Architecture

Planned improvements:

```
v2.0 (Phase 2):
├─ Backend API for result storage
├─ Database (PostgreSQL)
├─ Authentication (OAuth)
├─ Real-time updates (WebSockets)
└─ Advanced analytics dashboard

v3.0 (Phase 3):
├─ Custom benchmark creation UI
├─ Scheduled benchmark runs
├─ Slack/email notifications
├─ Model performance trends
└─ Cost tracking & forecasting

v4.0 (Phase 4):
├─ Production deployment (AWS/GCP)
├─ Enterprise authentication
├─ Team collaboration features
├─ API for external integrations
└─ Mobile app
```

---

**For more details, see:**
- `INTEGRATION-GUIDE.md` - How to use everything
- `QUICKSTART.md` - Getting started
- `benchmark-orchestrator.js` - Implementation details
