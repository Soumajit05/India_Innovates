@echo off
cd /d C:\Users\Soumajit Goswami\OneDrive\Desktop\India_innovates\backend
start "ARGOS-API" /min "C:\Users\Soumajit Goswami\anaconda3\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8011
exit /b 0
