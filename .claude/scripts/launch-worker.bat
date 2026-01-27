@echo off
REM Launch a Claude worker session with multi-session coordination
REM Usage: launch-worker.bat [TAG]
REM Example: launch-worker.bat worker-2

cd /d "%~dp0..\.."
python .claude\scripts\launch-worker.py %*
