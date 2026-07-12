@echo off
setlocal
if "%~1"=="" (
  echo Usage: build-profiles\cr-prepare.bat CR-YYYYMMDD-XXX [title]
  exit /b 2
)
echo [build-profile] cr-prepare: %~1
python scripts\build.py --profile cr-prepare --cr-id %~1 --cr-title "%~2"
exit /b %ERRORLEVEL%
