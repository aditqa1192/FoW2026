@echo off
REM Lilaq Course Content Agent - HTML UI Launcher
REM This script starts the Flask web application

echo ====================================
echo Lilaq Course Content Agent - HTML UI
echo ====================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create a .env file with your GOOGLE_API_KEY
    echo.
    echo Example .env file:
    echo GOOGLE_API_KEY=your_api_key_here
    echo GEMINI_MODEL=gemini-2.5-flash
    echo PORT=5000
    echo FLASK_DEBUG=False
    echo.
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask is not installed. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting Flask application...
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run Flask app
python app_flask.py

pause
