@echo off
setlocal
echo [build-profile] dev: debug=on tests=on docs=off clean=off
python scripts\build.py --profile dev %*
exit /b %ERRORLEVEL%
