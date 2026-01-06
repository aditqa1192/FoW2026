#!/bin/bash
# Lilaq Course Content Agent - HTML UI Launcher
# This script starts the Flask web application

echo "===================================="
echo "Lilaq Course Content Agent - HTML UI"
echo "===================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with your GOOGLE_API_KEY"
    echo ""
    echo "Example .env file:"
    echo "GOOGLE_API_KEY=your_api_key_here"
    echo "GEMINI_MODEL=gemini-2.5-flash"
    echo "PORT=5000"
    echo "FLASK_DEBUG=False"
    echo ""
    exit 1
fi

# Check if Flask is installed
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Flask is not installed. Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo "Starting Flask application..."
echo ""
echo "The application will be available at:"
echo "http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Flask app
python app_flask.py
