@echo off
REM 🚀 Run Server Script for Senzor de Calitate Web

cd "D:\senzor de calitate web"

echo.
echo ============================================
echo   🚀 Senzor de Calitate Web - Django Server  
echo ============================================
echo.
echo Starting server at http://localhost:8000/
echo Press CTRL+C to stop the server
echo.

"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py runserver

echo.
echo Server stopped.
pause
