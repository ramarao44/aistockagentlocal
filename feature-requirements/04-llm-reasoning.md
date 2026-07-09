# Feature: LLM Reasoning

## User Story
- **As a** user
- **I want** AI-generated stock analysis reports
- **So that** I can get actionable insights from market data

## Sub-Requirements

### 4.1 Local LLM Integration (Subprocess-based)
- **As a** privacy-focused user
- **I want** to use local LLMs via subprocess
- **So that** my data stays private and integration is simpler
- **Acceptance Criteria:**
  - [x] Integrate with Ollama via subprocess
  - [x] Support qwen2.5:3b model for main reasoning
  - [x] Support llama3.2:3b model for fast reasoning
  - [x] Support phi3:3.8b model for logic reasoning
  - [x] Return analysis report
- **Status:** Complete

### 4.2 Cloud LLM Fallback
- **As a** user
- **I want** cloud LLM as backup
- **So that** I can get results when local fails
- **Acceptance Criteria:**
  - [x] Support OpenAI API
  - [x] Graceful fallback on local failure
  - [x] Handle missing API key
- **Status:** Complete

### 4.3 Report Generation
- **As a** user
- **I want** structured analysis reports
- **So that** I can make informed decisions
- **Acceptance Criteria:**
  - [x] Generate price trend summary
  - [x] Generate technical indicator interpretation
  - [x] Generate market sentiment analysis
  - [x] Generate risks and opportunities
  - [x] Generate final recommendation
- **Status:** Complete

### 4.4 Prompt Engineering
- **As a** system
- **I want** well-structured prompts
- **So that** LLM gives accurate analysis
- **Acceptance Criteria:**
  - [x] Include real market data in prompt
  - [x] Structure prompt for Indian markets
  - [x] Include all indicators in prompt
- **Status:** Complete

### 4.5 Token Optimization Mode
- **As a** performance-focused user
- **I want** a compact reasoning mode
- **So that** I can reduce latency and output size while preserving decision quality
- **Acceptance Criteria:**
  - [x] Support `mode="optimized"` in `generate_llm_report()`
  - [x] Use compact prompts for optimized mode
  - [x] Reuse fast model path for low-latency summaries
  - [x] Keep core sections: summary, sentiment, trend logic
- **Status:** Complete

## Implementation Details

### Functions to Create/Modify
- `src/reasoning/llm_reasoner.py` - LLM integration
  - `run_model(model: str, prompt: str)` - Call Ollama via subprocess
  - `main_reasoning(prompt: str)` - Use qwen2.5:3b for main analysis
  - `fast_reasoning(prompt: str)` - Use llama3.2:3b for fast sentiment
  - `logic_reasoning(prompt: str)` - Use phi3:3.8b for logic analysis
  - `generate_ai_summary(data: dict)` - Generate stock analysis summary
  - `quick_sentiment(data: dict)` - Generate sentiment classification
  - `explain_trend_score(data: dict)` - Explain trend score
  - `run_cloud_llm(prompt: str)` - Call OpenAI (fallback)
  - `generate_llm_report(ticker: str, mode: str)` - Generate report

### Code Structure
```
src/
└── reasoning/
    └── llm_reasoner.py
```

### Integration Method
- **Ollama: subprocess-based (`ollama run <model>`)** - Direct CLI integration
- **OpenAI: HTTP API (`openai.ChatCompletion.create()`)** - Cloud fallback

### Data Flow
1. Fetch market data
2. Build prompt with real data
3. Call subprocess LLM (`run_model(model, prompt)`)
4. For optimized mode, use compact prompts and fast-model routing
5. Return generated report
6. Display in Chainlit

### Example Code Pattern
```python
import subprocess

def run_model(model, prompt):
    """Call Ollama model via subprocess CLI."""
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True
    )
    return result.stdout.decode().strip()

def main_reasoning(prompt):
    return run_model("qwen2.5:3b", prompt)

def fast_reasoning(prompt):
    return run_model("llama3.2:3b", prompt)

def logic_reasoning(prompt):
    return run_model("phi3:3.8b", prompt)

def generate_ai_summary(data):
    prompt = f"""
    Provide a clear reasoning summary for this stock:

    {data}
    """
    return main_reasoning(prompt)

def quick_sentiment(data):
    prompt = f"""
    Classify sentiment (bullish/bearish/neutral) for this stock:

    {data}
    """
    return fast_reasoning(prompt)

def explain_trend_score(data):
    prompt = f"""
    Explain the trend score logically:

    {data}
    """
    return logic_reasoning(prompt)
```

## Source Code Flow Chart
```
[User Input: ticker]
        |
        v
[fetch_indian_stock_data()] --> [market_data dict]
        |
        v
[Build Prompt with real data]
        |
        v
[run_model() via subprocess]
        |
        v
[LLM Response: analysis text]
        |
        v
[Return: formatted report]
```

## Definition of Done
- [x] All sub-requirements implemented
- [x] Test cases for each sub-feature created
- [x] All tests pass (positive, negative, edge cases)
- [x] User has reviewed and approved the changes
- [x] Documentation updated in `docs/DESIGN_DEVELOPMENT_DOCUMENT.md`
- [x] Test report generated
- [x] Changes pushed to repository

## Technical Notes
- Use subprocess CLI approach (no HTTP server needed)
- Supports multiple models for different use cases:
  - `qwen2.5:3b` - Main reasoning (highest quality)
  - `llama3.2:3b` - Fast reasoning (speed optimized)
  - `phi3:3.8b` - Logic reasoning (mathematical analysis)
- Supported modes in `generate_llm_report()`:
  - `local` / `default` - Full quality report
  - `optimized` - Compact output, faster reasoning path
  - `cloud` - Force cloud-only generation
- No API key required for local models
- Fallback to cloud on local failure

## Dependencies
- No HTTP dependencies required for subprocess approach
- openai (optional) - For cloud fallback
- subprocess (standard library) - Included in Python

## Test Cases
- `scripts/test_llm_reasoning.py` - LLM tests
- `scripts/test_reasoning.py` - Reasoning tests
- `scripts/test_ai_report.py` - Report generation tests
- Tests validate standard mode, optimized mode, and cloud fallback behavior

## Manual Testing
1. Run `python scripts/test_llm_reasoning.py` to verify the local, optimized, and cloud branches.
2. Launch the UI and request a report for a ticker such as `RELIANCE`.
3. Compare a normal report with `mode="optimized"` and confirm the optimized report is shorter and faster.
4. Temporarily disable or remove the local model and verify cloud fallback or error handling behaves as expected.
5. On Windows, confirm the report generation no longer fails with a console encoding error.