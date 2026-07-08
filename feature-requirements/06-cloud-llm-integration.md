# Feature: Cloud LLM Integration

## User Story
- **As a** user
- **I want** to use free cloud LLMs for analysis
- **So that** I can get fast responses without local hardware

## Sub-Requirements

### 6.1 DeepSeek API Integration
- **As a** developer
- **I want** to integrate DeepSeek API
- **So that** I can use free cloud inference
- **Acceptance Criteria:**
  - [x] Add DeepSeek API key to .env
  - [x] Create `run_deepseek()` function
  - [x] Handle API errors gracefully
  - [x] Support 10M tokens/day free tier

### 6.2 Model Selection
- **As a** user
- **I want** to choose between local and cloud
- **So that** I can balance privacy and speed
- **Acceptance Criteria:**
  - [ ] Add `mode` parameter to LLM functions
  - [ ] Default to "local" for privacy
  - [ ] Allow "cloud" for speed
  - [ ] Document the choice in UI
- **Status:** Not Started

### 6.3 Fallback Mechanism
- **As a** system
- **I want** automatic fallback to local
- **So that** I can ensure availability
- **Acceptance Criteria:**
  - [ ] Try cloud first
  - [ ] Fall back to local on failure
  - [ ] Log fallback events
  - [ ] Return error if both fail
- **Status:** Not Started

## Implementation Details

### Functions to Create/Modify
- `src/reasoning/llm_reasoner.py` - LLM integration
  - `run_deepseek(prompt: str)` - Call DeepSeek API
  - `generate_llm_report(ticker: str, mode: str)` - Updated with mode parameter

### Code Structure
```
src/
└── reasoning/
    └── llm_reasoner.py
```

### API Integration
- DeepSeek: `https://api.deepseek.com/v1/chat/completions`
- Headers: `Authorization: Bearer {DEEPSEEK_API_KEY}`
- Model: `deepseek-chat`

### Data Flow
1. User requests analysis
2. Check mode (local/cloud)
3. If cloud: Call DeepSeek API
4. If local: Call Ollama
5. Return generated report

### Example Code Pattern
```python
def run_deepseek(prompt: str) -> str:
    """
    Call DeepSeek API for analysis.
    
    Args:
        prompt: Analysis prompt with market data
        
    Returns:
        Generated analysis text
    """
    import requests
    
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    return response.json()["choices"][0]["message"]["content"]
```

## Source Code Flow Chart
```
[User Request: ticker, mode]
        |
        v
[Check mode: "local" or "cloud"]
        |
        +---> [cloud] --> [run_deepseek()] --> [API Response]
        |
        +---> [local] --> [run_local_llama()] --> [Local Response]
        |
        v
[Return: analysis report]
```

## Definition of Done
- [ ] All sub-requirements implemented
- [ ] Test cases for each sub-feature created
- [ ] All tests pass (positive, negative, edge cases)
- [ ] User has reviewed and approved the changes
- [ ] Documentation updated in `docs/DESIGN_DEVELOPMENT_DOCUMENT.md`
- [ ] Test report generated
- [ ] Changes pushed to repository

## Technical Notes
- DeepSeek free tier: 10M tokens/day
- Keep Ollama as fallback
- Add rate limiting if needed

## Dependencies
- requests
- python-dotenv

## Test Cases
- `scripts/test_deepseek.py` - DeepSeek API tests
- `scripts/test_llm_reasoning.py` - Updated LLM tests