# Feature: LLM Reasoning

## User Story
- **As a** user
- **I want** AI-generated stock analysis reports
- **So that** I can get actionable insights from market data

## Sub-Requirements

### 4.1 Local LLM Integration
- **As a** privacy-focused user
- **I want** to use local LLMs
- **So that** my data stays private
- **Acceptance Criteria:**
  - [x] Integrate with Ollama
  - [x] Support llama3.2:3b model
  - [x] Support phi3.5 model
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

## Implementation Details

### Functions to Create/Modify
- `src/reasoning/llm_reasoner.py` - LLM integration
  - `run_local_llama(prompt: str)` - Call Ollama
  - `run_cloud_llm(prompt: str)` - Call OpenAI
  - `generate_llm_report(ticker: str, mode: str)` - Generate report

### Code Structure
```
src/
└── reasoning/
    └── llm_reasoner.py
```

### API Integration
- Ollama: `http://localhost:11434/api/generate`
- OpenAI: `openai.ChatCompletion.create()`

### Data Flow
1. Fetch market data
2. Build prompt with real data
3. Call local LLM (or cloud)
4. Return generated report
5. Display in Chainlit

### Example Code Pattern
```python
def generate_llm_report(ticker: str, mode: str = "local") -> str:
    """
    Generate AI stock analysis report.
    
    Args:
        ticker: Stock ticker symbol
        mode: "local" or "cloud"
        
    Returns:
        Generated analysis report
    """
    market_data = fetch_indian_stock_data(ticker)
    
    prompt = f"""
    You are an AI financial analyst specializing in Indian stock markets.
    Use ONLY the REAL market data provided below.
    
    REAL MARKET DATA:
    - Ticker: {market_data['ticker']}
    - Current Price: {market_data['current_price']}
    - RSI (14): {market_data['rsi']}
    - MA50: {market_data['ma50']}
    ...
    """
    
    if mode == "local":
        return run_local_llama(prompt)
    else:
        return run_cloud_llm(prompt)
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
[run_local_llama() or run_cloud_llm()]
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
- Use /api/generate endpoint (not /api/chat)
- 120-second timeout for large models
- Fallback to cloud on local failure

## Dependencies
- requests
- openai (optional)
- ollama

## Test Cases
- `scripts/test_llm_reasoning.py` - LLM tests
- `scripts/test_reasoning.py` - Reasoning tests
- `scripts/test_ai_report.py` - Report generation tests
