@echo off
setlocal
echo [build-profile] baseline-sync: generate immutable baseline snapshot
python scripts\build.py --profile baseline-sync %*
exit /b %ERRORLEVEL%
