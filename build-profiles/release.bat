@echo off
setlocal
echo [build-profile] release: debug=off tests=on docs=on clean=on
python scripts\build.py --profile release %*
exit /b %ERRORLEVEL%
