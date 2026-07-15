# Developer Manual

## Purpose
This manual guides developers to implement non-breaking changes using baseline and CR governance, gated builds, and required documentation updates.

## Prerequisites
- Python 3.11+
- Virtual environment
- Local model runtime (Ollama) for local reasoning paths
- Repository cloned with hooks enabled

## Initial Setup
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional model setup:
```powershell
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
ollama pull phi3:3.8b
```

## Governance-First Change Flow
1. Generate or verify active baseline.
2. Create a CR workspace.
3. Complete impact analysis.
4. Approve CR.
5. Run impact gate before implementation and before gated CI.

Commands:
```powershell
python scripts/build.py --profile baseline-sync
python scripts/build.py --profile cr-prepare --cr-id CR-YYYYMMDD-XXX --cr-title "Change title" --cr-owner "owner"
python scripts/build.py --profile cr-impact-check --cr-id CR-YYYYMMDD-XXX
```

## Build Profiles and Commands
Fast local checks:
```powershell
python scripts/build.py --profile quick
python scripts/build.py --profile dev
```

Gated non-trivial validation:
```powershell
python scripts/build.py --profile ci --cr-id CR-YYYYMMDD-XXX
python scripts/build.py --profile release --cr-id CR-YYYYMMDD-XXX
```

Windows launchers:
```powershell
build-profiles\quick.bat
build-profiles\dev.bat
build-profiles\ci.bat
build-profiles\release.bat
build-profiles\baseline-sync.bat
build-profiles\cr-prepare.bat CR-YYYYMMDD-XXX "Change title"
build-profiles\cr-impact-check.bat CR-YYYYMMDD-XXX
build-profiles\all-profiles-smoke.bat
build-profiles\all-profiles-smoke.bat full
```

## Clean Policy
Only disposable generated outputs may be cleaned.

Safe cleanup:
```powershell
python scripts/build.py --profile quick --clean on --docs off --tests off --debug off
```

Do not clean governance/canonical paths:
- docs/**
- docs/baseline/**
- docs/change-requests/**
- gen/docs/**
- reports/**

## Required Documentation Updates
When behavior changes, update as applicable:
- docs/DESIGN_DEVELOPMENT_DOCUMENT.md
- docs/QUICK_REFERENCE.md
- feature-requirements/* impacted feature file
- reports/TEST_REPORT.md

## Pre-Push Requirements
Set CR id so the push hook can run gated validation:
```powershell
$env:AISA_CR_ID="CR-YYYYMMDD-XXX"
git push
```
