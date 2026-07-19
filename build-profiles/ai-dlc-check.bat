@echo off
setlocal

set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%.."

python scripts\build.py --profile ai-dlc-check
set EXIT_CODE=%ERRORLEVEL%

popd
exit /b %EXIT_CODE%
