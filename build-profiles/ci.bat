@echo off
setlocal
echo [build-profile] ci: debug=off tests=on docs=on clean=on
python scripts\build.py --profile ci %*
exit /b %ERRORLEVEL%
