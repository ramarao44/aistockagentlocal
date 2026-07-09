# Feature: Cloud LLM Integration

## User Story
- **As a** user
- **I want** a cloud fallback for analysis
- **So that** I can still get results when local models fail

## Sub-Requirements

### 6.1 OpenAI Cloud Integration
- **As a** developer
- **I want** to integrate OpenAI API as cloud fallback
- **So that** report generation remains available if local execution fails
- **Acceptance Criteria:**
  - [x] Add OpenAI API key support in `.env`
  - [x] Create `run_cloud_llm()` function
  - [x] Handle API and missing-key errors gracefully
  - [x] Use configurable cloud model

### 6.2 Model Selection
- **As a** user
- **I want** to choose between local and cloud
- **So that** I can balance privacy and speed
- **Acceptance Criteria:**
  - [x] Add `mode` parameter to LLM functions
  - [x] Default to `local` for privacy
  - [x] Allow `cloud` mode
  - [x] Document the choice in UI
- **Status:** Complete

### 6.3 Fallback Mechanism
- **As a** system
- **I want** automatic fallback to local
- **So that** I can ensure availability
- **Acceptance Criteria:**
  - [x] Try local first
  - [x] Fall back to cloud on local failure when enabled
  - [x] Return cloud error if fallback cannot complete
  - [x] Return local error if fallback is disabled
- **Status:** Complete

## Implementation Details

### Functions to Create/Modify
- `src/reasoning/llm_reasoner.py` - LLM integration
  - `run_cloud_llm(prompt: str)` - Call OpenAI API
  - `generate_llm_report(ticker: str, mode: str)` - Updated with mode parameter

### Code Structure
```
src/
└── reasoning/
    └── llm_reasoner.py
```

### API Integration
- OpenAI Chat Completions API via `openai.ChatCompletion.create()`
- Headers/auth managed by OpenAI SDK with `OPENAI_API_KEY`
- Model from `CLOUD_MODEL` environment variable (default: `gpt-4o-mini`)

### Data Flow
1. User requests analysis
2. Check mode (local/cloud)
3. If cloud mode: Call OpenAI API
4. If local mode: Call Ollama models
5. On local failure, use cloud fallback if enabled
6. Return generated report

### Example Code Pattern
```python
def run_cloud_llm(prompt: str) -> str:
  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
    return "[Cloud LLM Error] Missing OPENAI_API_KEY"

  import openai
  openai.api_key = api_key

  completion = openai.ChatCompletion.create(
    model=os.getenv("CLOUD_MODEL", "gpt-4o-mini"),
    messages=[{"role": "user", "content": prompt}],
  )
  return completion.choices[0].message["content"]
```

## Source Code Flow Chart
```
[User Request: ticker, mode]
        |
        v
[Check mode: "local" or "cloud"]
        |
  +---> [cloud] --> [run_cloud_llm()] --> [API Response]
        |
  +---> [local] --> [run_model()/main_reasoning()] --> [Local Response]
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
- OpenAI is cloud fallback path only
- Local Ollama remains primary for privacy
- Fallback behavior can be controlled with `ENABLE_CLOUD_FALLBACK`

## Dependencies
- openai
- python-dotenv

## Test Cases
- `scripts/test_llm_reasoning.py` - mode and fallback tests

## Manual Testing
1. Set `OPENAI_API_KEY` and `ENABLE_CLOUD_FALLBACK` in `.env`.
2. Run a cloud report directly with `mode="cloud"` and confirm the API response is returned.
3. Run a local report with cloud fallback enabled and temporarily break the local model path to confirm fallback works.
4. Clear `OPENAI_API_KEY` and confirm the missing-key error is reported cleanly.
5. Compare local and cloud output structure to confirm both produce usable stock-analysis reports.