@echo off
setlocal enabledelayedexpansion

set "MODE=%~1"
if "%MODE%"=="" set "MODE=fast"

if /I "%MODE%"=="full" (
  set "OVERRIDES="
  echo [smoke] mode=full ^(uses each profile defaults^)
) else (
  set "OVERRIDES=--tests off --docs off --clean off"
  echo [smoke] mode=fast ^(forces tests/docs/clean off for quick validation^)
)

set "FAILED=0"

echo.
echo [smoke] running profile: quick
python scripts\build.py --profile quick %OVERRIDES%
if errorlevel 1 (
  echo [smoke] FAIL: quick
  set "FAILED=1"
) else (
  echo [smoke] PASS: quick
)

echo.
echo [smoke] running profile: dev
python scripts\build.py --profile dev %OVERRIDES%
if errorlevel 1 (
  echo [smoke] FAIL: dev
  set "FAILED=1"
) else (
  echo [smoke] PASS: dev
)

echo.
echo [smoke] running profile: ci
python scripts\build.py --profile ci %OVERRIDES%
if errorlevel 1 (
  echo [smoke] FAIL: ci
  set "FAILED=1"
) else (
  echo [smoke] PASS: ci
)

echo.
echo [smoke] running profile: release
python scripts\build.py --profile release %OVERRIDES%
if errorlevel 1 (
  echo [smoke] FAIL: release
  set "FAILED=1"
) else (
  echo [smoke] PASS: release
)

echo.
if "%FAILED%"=="0" (
  echo [smoke] RESULT: PASS
  exit /b 0
) else (
  echo [smoke] RESULT: FAIL
  exit /b 1
)
