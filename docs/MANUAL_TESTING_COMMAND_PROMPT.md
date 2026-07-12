# Manual Testing Runbook (Command Prompt)

This guide is for running module-level and end-to-end tests from Windows Command Prompt (cmd.exe).

## 1. Prerequisites

1. Open Command Prompt.
2. Change to project folder:

```bat
cd /d C:\RAMARAO\Learning\AI\N8N\aistockagentlocal
```

3. Activate virtual environment:

```bat
.venv\Scripts\activate.bat
```

4. Install dependencies (first time only):

```bat
pip install -r requirements.txt
```

5. Optional sanity checks:

```bat
where python
python --version
```

## 2. Run Full Automated Test Suite (tests folder)

Run all tests in the tests folder:

```bat
python -m unittest discover -s tests -p "test_*.py" -v
```

Expected result:
- All tests show ok
- Final line shows OK

## 3. Run Each Contract Test Individually

These tests validate contract shape for each module output.

1. Technical contract test:

```bat
python -m unittest tests.test_contract_pipeline_unittest.ContractPipelineTests.test_technical_contract_output -v
```

2. Fundamental contract test:

```bat
python -m unittest tests.test_contract_pipeline_unittest.ContractPipelineTests.test_fundamental_contract_output -v
```

3. Sentiment contract test:

```bat
python -m unittest tests.test_contract_pipeline_unittest.ContractPipelineTests.test_sentiment_contract_output -v
```

4. Trend contract test:

```bat
python -m unittest tests.test_contract_pipeline_unittest.ContractPipelineTests.test_trend_contract_output -v
```

5. Timeframe contract test:

```bat
python -m unittest tests.test_contract_pipeline_unittest.ContractPipelineTests.test_timeframe_contract_output -v
```

6. LLM contract test:

```bat
python -m unittest tests.test_contract_pipeline_unittest.ContractPipelineTests.test_llm_contract_output -v
```

7. End-to-end UI contract pipeline test (mocked E2E):

```bat
python -m unittest tests.test_contract_pipeline_unittest.ContractPipelineTests.test_ui_end_to_end_pipeline -v
```

8. Local webhook HTML compatibility test:

```bat
python -m unittest tests.test_local_webhook.LocalWebhookFormattingTests.test_generate_html_report_contains_key_fields -v
```

## 4. Manual Live UI Test (Interactive Chainlit)

Use this to manually verify UI behavior with real orchestration flow.

1. Start Chainlit app:

```bat
chainlit run main.py
```

2. Open the URL shown in terminal.
3. In chat, enter:

```text
RELIANCE
```

4. Verify response contains:
- Summary
- Sentiment
- Recommendation
- Probability

Pass criteria:
- No pipeline failure message
- Non-empty response values

## 5. Manual Webhook Flow Test

This validates local webhook server and payload posting.

1. Open Terminal A and start webhook server:

```bat
python local_server.py
```

2. Open Terminal B in same project and venv, then run:

```bat
python run_tests.py
```

Expected output:
- Status: 200
- JSON response contains status: ok

Optional custom webhook URL in cmd:

```bat
set TEST_REPORT_URL=http://localhost:8001/report
python run_tests.py
```

## 6. Legacy Script Pack (Optional)

Run all legacy script-based tests:

```bat
python scripts\run_all_tests.py
```

Use this as supplemental verification in addition to tests folder suite.

## 7. Failure Triage Quick Guide

1. If import errors occur:
- Ensure venv is active
- Re-run pip install -r requirements.txt

2. If Chainlit command is not found:
- Verify dependency install
- Try:

```bat
python -m chainlit run main.py
```

3. If webhook test connection fails:
- Confirm local_server.py is running
- Confirm URL and port

4. If tests become flaky due to network:
- Prefer contract tests in tests folder first (these are mocked and deterministic)

## 8. Recommended Execution Order

1. python -m unittest discover -s tests -p "test_*.py" -v
2. Individual module tests only when you need focused debugging
3. chainlit run main.py (manual interactive verification)
4. python local_server.py + python run_tests.py
5. python scripts\run_all_tests.py (optional regression sweep)
