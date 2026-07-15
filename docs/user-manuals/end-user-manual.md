# End User Manual

## Purpose
This manual helps end users run the AI Stock Agent to fetch stock data and generate analysis outputs.

## What You Can Do
- Run local analysis workflows.
- Fetch market data for Indian stocks.
- Generate report outputs using local models.
- Use local server/webhook flows.

## Quick Start
1. Set up environment:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the user interface:
```powershell
chainlit run main.py
```

3. Or start local server:
```powershell
python local_server.py
```

## Optional Health Checks
Model service check:
```powershell
curl http://localhost:11434/api/tags
```

Webhook test run:
```powershell
python run_tests.py
```

## Typical Input Examples
- RELIANCE
- TCS.NS
- INFY.BO
- HCL Technologies

## Expected Output
- Resolved ticker/exchange information
- Price and indicator fields (when data is available)
- Structured analysis report sections

## Common Problems
1. Missing dependencies:
- Re-activate .venv and re-run pip install.
2. Model not available:
- Ensure Ollama is running and models are pulled.
3. Invalid symbol:
- Try an exchange-qualified symbol or company name.

## Important Note
This project provides analysis support and does not constitute financial advice.
