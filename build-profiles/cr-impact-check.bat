@echo off
setlocal
if "%~1"=="" (
  echo Usage: build-profiles\cr-impact-check.bat CR-YYYYMMDD-XXX
  exit /b 2
)
echo [build-profile] cr-impact-check: %~1
python scripts\build.py --profile cr-impact-check --cr-id %~1
exit /b %ERRORLEVEL%
