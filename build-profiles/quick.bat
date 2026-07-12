@echo off
setlocal
echo [build-profile] quick: debug=off tests=off docs=off clean=off
python scripts\build.py --profile quick %*
exit /b %ERRORLEVEL%
