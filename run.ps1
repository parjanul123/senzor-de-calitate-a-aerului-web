# 🚀 Run Server Script for Senzor de Calitate Web

# Set working directory
Set-Location "D:\senzor de calitate web"

# Display banner
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  🚀 Senzor de Calitate Web - Django Server  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting server at http://localhost:8000/" -ForegroundColor Green
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run Django development server
& "C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py runserver

# If server exits, show message
Write-Host ""
Write-Host "Server stopped." -ForegroundColor Red
