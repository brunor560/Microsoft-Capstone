/**
 * Benchmark Orchestrator
 * Runs standardized test scenarios against baseline application
 * and evaluates AI model responses
 */

const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

const BASELINE_URL = process.env.BASELINE_URL || 'http://localhost:3000/api';

// Standardized benchmark scenarios
const SCENARIOS = [
  {
    id: 'add-feature',
    name: 'Add a Feature',
    description: 'Implement GET /api/todos/stats endpoint',
    prompt: `You are a software engineer. Add a new endpoint to a Todo REST API.
    
The endpoint should be:
- Route: GET /api/todos/stats
- Returns JSON: { completed: number, pending: number }
- Implementation should include proper error handling

Provide only the complete implementation code for this endpoint.
Do not include explanations.`,
    expectedSuccess: 'Returns correct stats for todos',
    category: 'feature-implementation'
  },
  {
    id: 'fix-bug',
    name: 'Debug Issue',
    description: 'Fix todo update validation bug',
    prompt: `There's a bug in this Express.js Todo API update endpoint:

\`\`\`javascript
app.put('/api/todos/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const todo = todos.find(t => t.id === id);
  if (req.body.completed !== undefined) todo.completed = Boolean(req.body.completed);
  if (req.body.title) todo.title = req.body.title;
  res.status(200).json(todo);
});
\`\`\`

Problem: The function should return a 404 status code when the todo is not found, but currently it crashes with "Cannot read property 'completed' of undefined".

Fix the bug and explain what was wrong.`,
    expectedSuccess: 'Returns 404 when todo not found',
    category: 'bug-fix'
  },
  {
    id: 'refactor',
    name: 'Refactor to SQLite',
    description: 'Migrate from in-memory to SQLite storage',
    prompt: `Refactor an Express.js Todo API to use SQLite instead of in-memory array storage.

Current storage pattern:
\`\`\`javascript
let todos = [
  { id: 1, title: 'Task 1', completed: false },
  { id: 2, title: 'Task 2', completed: true }
];
\`\`\`

Requirements:
1. Use sqlite3 npm package
2. Create todos table with columns: id (PRIMARY KEY), title (TEXT NOT NULL), completed (BOOLEAN DEFAULT 0)
3. Maintain all existing API endpoints: GET /api/todos, POST, PUT, DELETE
4. Add basic error handling

Provide the refactored server.js code. Focus on the database setup and the GET endpoint implementation.`,
    expectedSuccess: 'API persists todos to SQLite database',
    category: 'refactoring'
  },
  {
    id: 'security',
    name: 'Security Hardening',
    description: 'Add security measures (validation, rate limiting)',
    prompt: `Secure this Express.js Todo API against common vulnerabilities:

Current issues:
- No input validation
- No rate limiting
- Vulnerable to XSS and injection attacks
- No CORS configuration
- No security headers

Implement:
1. Input validation using express-validator
2. Rate limiting using express-rate-limit (max 100 requests per 15 minutes)
3. CORS configuration
4. Helmet.js for security headers
5. Input sanitization

Provide the security-hardened server.js code with:
- All necessary imports
- Middleware setup
- Modified endpoints with validation
- Error handling

Keep it production-ready.`,
    expectedSuccess: 'API has validation, rate limiting, and security headers',
    category: 'security'
  }
];

// Model configurations
const MODELS = [
  {
    id: 'claude',
    name: 'Claude 3.5 Sonnet',
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022',
    pricing: { input: 0.003, output: 0.015 } // per 1K tokens
  },
  {
    id: 'gemini',
    name: 'Gemini Pro',
    provider: 'google',
    model: 'gemini-pro',
    pricing: { input: 0.000075, output: 0.0003 } // per 1K tokens
  },
  {
    id: 'copilot',
    name: 'GitHub Copilot (GPT-4)',
    provider: 'openai',
    model: 'gpt-4',
    pricing: { input: 0.03, output: 0.06 } // per 1K tokens
  },
  {
    id: 'codex',
    name: 'OpenAI Codex',
    provider: 'openai',
    model: 'code-davinci-003',
    pricing: { input: 0.0008, output: 0.0032 } // per 1K tokens
  }
];

class BenchmarkOrchestrator {
  constructor() {
    this.results = [];
    this.apiKeys = {
      claude: process.env.CLAUDE_API_KEY,
      gemini: process.env.GEMINI_API_KEY,
      openai: process.env.OPENAI_API_KEY
    };
  }

  async runFullBenchmark() {
    console.log('🚀 Starting Full Benchmark Suite\n');
    console.log(`📋 Testing ${SCENARIOS.length} scenarios × ${MODELS.length} models\n`);

    const startTime = Date.now();

    for (const scenario of SCENARIOS) {
      console.log(`\n${scenario.name}`);
      console.log('─'.repeat(50));

      for (const model of MODELS) {
        if (!this.apiKeys[model.provider]) {
          console.log(`  ⏭️  ${model.name} (API key not configured)`);
          continue;
        }

        const result = await this.evaluateModel(model, scenario);
        this.results.push(result);
        this.printResult(result);
      }
    }

    const totalTime = Date.now() - startTime;
    this.saveBenchmarkResults(totalTime);
    this.generateReport();
  }

  async evaluateModel(model, scenario) {
    const startTime = Date.now();

    try {
      const response = await this.callModelAPI(model, scenario.prompt);
      const latency = Date.now() - startTime;

      return {
        model: model.name,
        modelId: model.id,
        scenario: scenario.name,
        scenarioId: scenario.id,
        status: 'success',
        latency,
        tokens: response.tokens || 0,
        cost: this.calculateCost(model, response.tokens || 0),
        responseLength: response.text?.length || 0,
        qualityScore: this.scoreResponse(response.text, scenario),
        timestamp: new Date().toISOString(),
        responsePreview: (response.text || '').substring(0, 200)
      };
    } catch (error) {
      return {
        model: model.name,
        modelId: model.id,
        scenario: scenario.name,
        scenarioId: scenario.id,
        status: 'error',
        error: error.message,
        latency: Date.now() - startTime,
        timestamp: new Date().toISOString()
      };
    }
  }

  async callModelAPI(model, prompt) {
    switch (model.provider) {
      case 'anthropic':
        return await this.callClaudeAPI(model, prompt);
      case 'google':
        return await this.callGeminiAPI(model, prompt);
      case 'openai':
        return await this.callOpenAIAPI(model, prompt);
      default:
        throw new Error(`Unknown provider: ${model.provider}`);
    }
  }

  async callClaudeAPI(model, prompt) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': this.apiKeys.claude,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      },
      body: JSON.stringify({
        model: model.model,
        max_tokens: 2000,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status}`);
    }

    const data = await response.json();
    return {
      text: data.content[0]?.text,
      tokens: data.usage?.output_tokens || 0
    };
  }

  async callGeminiAPI(model, prompt) {
    // Placeholder - implement with actual Gemini API
    console.log('  ⚠️  Gemini integration not yet implemented');
    return { text: 'Gemini response (placeholder)', tokens: 500 };
  }

  async callOpenAIAPI(model, prompt) {
    // Placeholder - implement with actual OpenAI API
    console.log('  ⚠️  OpenAI integration not yet implemented');
    return { text: 'OpenAI response (placeholder)', tokens: 500 };
  }

  scoreResponse(text, scenario) {
    if (!text) return 0;

    let score = 40; // Base score

    // Length bonus
    if (text.length > 500) score += 20;
    if (text.length > 1000) score += 10;

    // Content quality indicators
    const keywords = {
      'feature-implementation': ['function', 'async', 'await', 'error', 'status'],
      'bug-fix': ['bug', 'issue', 'undefined', 'null', 'check', 'validate'],
      'refactoring': ['database', 'sqlite', 'schema', 'query', 'connection'],
      'security': ['validation', 'sanitize', 'limit', 'helmet', 'cors']
    };

    const relevantKeywords = keywords[scenario.category] || [];
    const foundKeywords = relevantKeywords.filter(kw =>
      text.toLowerCase().includes(kw)
    ).length;

    score += Math.min(30, foundKeywords * 5);

    // Check for code blocks
    if (text.includes('```') || text.includes('```javascript')) {
      score += 10;
    }

    return Math.min(100, score);
  }

  calculateCost(model, tokens) {
    const rates = model.pricing;
    // Assuming output tokens - adjust if needed
    return ((tokens / 1000) * rates.output).toFixed(4);
  }

  printResult(result) {
    if (result.status === 'success') {
      console.log(`  ✅ ${result.model}`);
      console.log(`     Latency: ${result.latency}ms | Tokens: ${result.tokens} | Quality: ${result.qualityScore}/100 | Cost: $${result.cost}`);
    } else {
      console.log(`  ❌ ${result.model}: ${result.error}`);
    }
  }

  saveBenchmarkResults(totalTime) {
    const benchmark = {
      timestamp: new Date().toISOString(),
      totalDuration: totalTime,
      scenarios: SCENARIOS.length,
      models: MODELS.length,
      results: this.results,
      summary: this.generateSummary()
    };

    const filepath = path.join(__dirname, 'results.json');
    fs.writeFileSync(filepath, JSON.stringify(benchmark, null, 2));
    console.log(`\n💾 Results saved to ${filepath}`);
  }

  generateSummary() {
    const summary = {};

    MODELS.forEach(model => {
      const modelResults = this.results.filter(
        r => r.modelId === model.id && r.status === 'success'
      );

      if (modelResults.length === 0) return;

      const avgLatency = modelResults.reduce((sum, r) => sum + r.latency, 0) / modelResults.length;
      const avgTokens = modelResults.reduce((sum, r) => sum + r.tokens, 0) / modelResults.length;
      const avgQuality = modelResults.reduce((sum, r) => sum + r.qualityScore, 0) / modelResults.length;
      const totalCost = modelResults.reduce((sum, r) => sum + parseFloat(r.cost), 0);

      summary[model.id] = {
        name: model.name,
        testsRun: modelResults.length,
        avgLatency: Math.round(avgLatency),
        avgTokens: Math.round(avgTokens),
        avgQuality: Math.round(avgQuality),
        totalCost: totalCost.toFixed(4),
        successRate: `${((modelResults.length / SCENARIOS.length) * 100).toFixed(0)}%`
      };
    });

    return summary;
  }

  generateReport() {
    console.log('\n\n' + '='.repeat(60));
    console.log('📊 BENCHMARK SUMMARY REPORT');
    console.log('='.repeat(60));

    const summary = this.generateSummary();
    const sortedModels = Object.values(summary).sort((a, b) => b.avgQuality - a.avgQuality);

    console.log('\nRanking by Quality Score:\n');
    sortedModels.forEach((model, idx) => {
      console.log(`${idx + 1}. ${model.name}`);
      console.log(`   Quality Score: ${model.avgQuality}/100`);
      console.log(`   Avg Latency: ${model.avgLatency}ms`);
      console.log(`   Success Rate: ${model.successRate}`);
      console.log(`   Total Cost: $${model.totalCost}`);
      console.log('');
    });

    console.log('\nDetailed Model Comparison:\n');
    Object.entries(summary).forEach(([modelId, stats]) => {
      console.log(`${stats.name}:`);
      console.log(`  Tests Run: ${stats.testsRun}`);
      console.log(`  Success Rate: ${stats.successRate}`);
      console.log(`  Avg Latency: ${stats.avgLatency}ms`);
      console.log(`  Avg Tokens: ${stats.avgTokens}`);
      console.log(`  Avg Quality: ${stats.avgQuality}/100`);
      console.log(`  Total Cost: $${stats.totalCost}`);
      console.log('');
    });

    console.log('='.repeat(60));
  }

  exportToCSV() {
    const csv = [
      ['Model', 'Scenario', 'Status', 'Latency (ms)', 'Tokens', 'Cost', 'Quality Score', 'Timestamp']
    ];

    this.results.forEach(result => {
      csv.push([
        result.model,
        result.scenario,
        result.status,
        result.latency || 'N/A',
        result.tokens || 'N/A',
        result.cost || 'N/A',
        result.qualityScore || 'N/A',
        result.timestamp
      ]);
    });

    const filepath = path.join(__dirname, 'results.csv');
    const csvContent = csv.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    fs.writeFileSync(filepath, csvContent);
    console.log(`📊 CSV report saved to ${filepath}`);
  }
}

// Run if called directly
if (require.main === module) {
  const orchestrator = new BenchmarkOrchestrator();
  orchestrator.runFullBenchmark()
    .then(() => orchestrator.exportToCSV())
    .catch(console.error);
}

module.exports = BenchmarkOrchestrator;
