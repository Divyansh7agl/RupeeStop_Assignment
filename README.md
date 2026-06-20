# Investment Committee Agent

A multi-agent AI system that simulates an investment committee, enabling nuanced portfolio analysis through structured debate, evidence gathering, and consensus-driven recommendations.

## Architecture

```
User Question
     │
     ▼
┌─────────────────────────────────────────┐
│              Planner Agent              │
│  - Parses question intent               │
│  - Selects relevant tools               │
│  - Orchestrates parallel execution      │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│           Tool Execution Layer          │
│                                         │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │  Portfolio   │  │  Fund Metadata  │  │
│  │  Analyzer    │  │  Tool           │  │
│  └──────────────┘  └─────────────────┘  │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │  Historical  │  │  Risk Metrics   │  │
│  │  Returns     │  │  Tool           │  │
│  └──────────────┘  └─────────────────┘  │
│  ┌──────────────────────────────────┐   │
│  │  Market Context Tool             │   │
│  │  (Gemini Google Search grounding)│   │
│  └──────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │ Tool outputs passed to all specialists
                ▼
┌───────────────────────────────────────────────────────────┐
│          Parallel Specialist Execution (asyncio.gather)   │
│                                                           │
│  ┌────────────────┐  ┌─────────────┐  ┌───────────────┐  │
│  │  Conservative  │  │   Growth    │  │  Cost &       │  │
│  │  Advisor       │  │   Advisor   │  │  Efficiency   │  │
│  │                │  │             │  │  Advisor      │  │
│  │  Capital       │  │  Long-term  │  │  Overlap,     │  │
│  │  preservation  │  │  returns    │  │  expense      │  │
│  │  downside risk │  │  high risk  │  │  ratios       │  │
│  └────────────────┘  └─────────────┘  └───────────────┘  │
└───────────────────────┬───────────────────────────────────┘
                        │ Opinions passed forward
                        ▼
┌─────────────────────────────────────────┐
│           Devil's Advocate              │
│  - Receives all 3 specialist opinions   │
│  - Challenges specific claims           │
│  - Exposes hidden risks & assumptions   │
│  - Stress-tests recommendations         │
└───────────────┬─────────────────────────┘
                │ All 4 opinions
                ▼
┌─────────────────────────────────────────┐
│            Consensus Agent              │
│  - Identifies agreements                │
│  - Resolves disagreements               │
│  - Calculates confidence score          │
│  - Produces final recommendation        │
│  - Lists action items & risk warnings   │
└───────────────┬─────────────────────────┘
                │
                ▼
         Final JSON Output
```

## Design Decisions

### LLM Strategy: Gemini Primary + Groq Fallback
- **Gemini 2.0 Flash** is the primary model for all agent calls — fast, capable, cost-effective
- **Google Search Grounding** is used via Gemini for the Market Context Tool, giving real-time market data without a separate search API
- **Groq (Llama-3.3-70b)** is the fallback — if Gemini fails after 2 retries, Groq picks up the request
- This dual-provider approach ensures high availability and is demonstrated clearly in code

### Parallel Agent Execution
The three core specialists (Conservative, Growth, Cost & Efficiency) run in parallel using `asyncio.gather()`. This is not just an optimization — it prevents one agent's response from anchoring the others' reasoning, ensuring genuine independent analysis. Devil's Advocate runs after and receives all three opinions explicitly, enabling it to challenge specific claims rather than reasoning in a vacuum.

### Structured Prompting
Every agent prompt specifies:
1. The exact JSON output schema
2. An explicit instruction to reference tool data numbers (prevents generic advice)
3. A distinct persona and lens that shapes reasoning
4. Temperature is tuned per agent: lower for Conservative/Consensus (0.2-0.25), higher for Devil's Advocate (0.45) to encourage creative challenge

### Tool Architecture
Tools are pure Python computation functions — no LLM calls inside tools. This keeps them:
- Deterministic and testable
- Fast (no API latency)
- Easy to swap for real data sources in production

The Market Context Tool is the exception — it calls Gemini with search grounding enabled.

### Confidence Scoring
Confidence is not a simple average of individual agent confidence scores. The Consensus Agent reasons about the *pattern* of agreement vs disagreement and assigns a score based on a rubric provided in its system prompt. High disagreement naturally produces lower confidence scores.

### Observability
`structlog` is used throughout for structured JSON logging. Every tool call, every agent invocation, and every pipeline step emits a log with duration, status, and relevant context.

## Assumptions

1. **Synthetic fund data** is used in place of a live MF data API. The expense ratios, CAGR figures, and metadata are realistic approximations of actual Indian mutual funds as of 2024-2025.
2. **Market Context Tool** requires a valid Gemini API key with Google Search grounding access. Without it, the tool gracefully falls back to Groq's training knowledge.
3. **Overlap detection** is simplified: two funds in the same category (e.g., two Large Cap funds) are flagged as overlapping. In production, this would use actual portfolio holdings data.
4. **Risk-free rate** is set to 7.0% (approximate India 10Y G-Sec yield) for Sharpe/Sortino calculations.

## Limitations

1. **No live fund data**: Expense ratios and NAVs are synthetic. Production would integrate with AMFI API or a data provider like Morningstar.
2. **Overlap analysis is category-level**: Real overlap analysis requires underlying stock holdings data per fund.
3. **No portfolio history**: Time-series analysis of the investor's own contribution history is not available.
4. **LLM hallucination risk**: While agents are instructed to use tool data, they can occasionally hallucinate specific numbers. Production would add output validation.
5. **Market Context search quality**: Depends on Gemini's search grounding quality and may not always retrieve the most current data.

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

```
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/portfolio` | GET | Sample portfolio data |
| `/analyze` | POST | Full pipeline (blocking) |
| `/analyze/stream` | POST | SSE stream with real-time step updates |

### Example Request

```json
POST /analyze
{
  "question": "Should I redeem my small cap fund?",
  "use_sample_data": true
}
```

### Example Response

```json
{
  "committee_opinions": {
    "conservative": {
      "advisor": "Conservative Advisor",
      "stance": "CAUTION",
      "confidence": 0.78,
      "reasoning": "...",
      "key_points": ["...", "..."],
      "evidence_used": ["portfolio_analysis", "risk_metrics"]
    },
    ...
  },
  "agreements": ["Portfolio has significant large cap overlap", "..."],
  "disagreements": ["Risk tolerance for small cap exposure", "..."],
  "confidence_score": 0.72,
  "final_recommendation": "...",
  "action_items": ["...", "..."],
  "evidence": ["...", "..."],
  "risk_warnings": ["...", "..."]
}
```

## Evaluation Design

The system can be evaluated on:

1. **Stance consistency**: Given the same portfolio, does the Conservative Advisor reliably produce more conservative stances than the Growth Advisor?
2. **Evidence grounding**: Do agents cite specific numbers from tool outputs, or give generic responses?
3. **Disagreement quality**: Are disagreements substantive (different values/assumptions) or superficial?
4. **Confidence calibration**: Does the confidence score correlate with actual committee agreement?
5. **Fallback reliability**: Does the Groq fallback produce comparable quality output?

## Tech Stack

- **Backend**: FastAPI, Pydantic v2, structlog, asyncio
- **LLM**: Google Gemini 2.0 Flash (primary), Groq Llama-3.3-70b (fallback)
- **Search**: Gemini Google Search Grounding (Market Context Tool)
- **Frontend**: React 18, Vite, SSE for streaming
