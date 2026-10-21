@echo off
chcp 65001 >nul
setlocal
rem ============================================================
rem  Baidu URL daily push - resumable
rem  Called by Windows Scheduled Task "BaiduUrlPush".
rem  Safe to run multiple times: pushed URLs are recorded in
rem  project-progress\baidu-pushed.txt and skipped on next run.
rem  NOTE: keep this file ASCII-only. Chinese here breaks cmd.exe
rem        parsing because it reads .bat in the OEM codepage.
rem ============================================================

set "REPO=D:\Coding\lurenjia_mianshi"
set "PY=C:\Users\yigel\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if not exist "%PY%" set "PY=python"

if not exist "%REPO%\scripts\baidu-push.py" (
    echo [ERR] script not found: %REPO%\scripts\baidu-push.py
    exit /b 1
)

cd /d "%REPO%"
"%PY%" scripts\baidu-push.py --limit 10
exit /b %errorlevel%
