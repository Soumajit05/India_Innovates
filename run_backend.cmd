@echo off
cd /d e:\India_Innovates\backend
if exist .\.venv (
    start "ARGOS-API" cmd /c ".\.venv\Scripts\python.exe -m uvicorn app.main:app --host localhost --port 8011"
) else (
    start "ARGOS-API" cmd /c "python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -r requirements.txt && python -m uvicorn app.main:app --host localhost --port 8011"
)
exit /b 0
