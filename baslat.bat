@echo off
echo Envanter Sistemi baslatiliyor, lutfen bekleyin...

start "Backend - Envanter Sistemi" cmd /k "cd /d %~dp0backend && venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

start "Frontend - Envanter Sistemi" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 6 /nobreak > nul
start http://localhost:5173

echo.
echo Sistem baslatildi. Acilan iki siyah pencereyi (Backend / Frontend) KAPATMAYIN,
echo sistemi kapatmak icin onlari kapatmaniz yeterli.
pause
