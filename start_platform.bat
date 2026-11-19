@echo off
title Microstash Platform & Ngrok Tunnel
echo ====================================================================
echo   Starting Microstash Server and Ngrok Tunnel
echo   Domain: https://uncrown-washbowl-glucose.ngrok-free.dev
echo ====================================================================

cd /d C:\LLM\deepstash_microlearning

:: Start FastAPI backend in a separate window
start "Microstash FastAPI Backend" cmd /k "python run.py"

:: Wait 2 seconds for server to bind port 8000
timeout /t 2 /nobreak >nul

:: Start ngrok tunnel in a separate window
start "Microstash Ngrok Tunnel" cmd /k "ngrok http 8000 --url https://uncrown-washbowl-glucose.ngrok-free.dev"

echo [OK] Both processes launched!
echo Local:  http://localhost:8000
echo Public: https://uncrown-washbowl-glucose.ngrok-free.dev
echo ====================================================================
pause
