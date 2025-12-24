#!/bin/bash

# Quick setup script for SpendSmart

echo "SpendSmart Setup Script"
echo "======================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your API credentials:"
    echo "   - DATABASE_URL (PostgreSQL connection string)"
    echo "   - PLAID_CLIENT_ID and PLAID_SECRET"
    echo "   - GEMINI_API_KEY"
    echo "   - GOOGLE_SHEETS_SPREADSHEET_ID"
    echo "   - GOOGLE_SHEETS_CREDENTIALS_FILE"
else
    echo ".env file already exists"
fi

# Check if PostgreSQL is accessible (basic check)
echo ""
echo "Checking PostgreSQL connection..."
if command -v psql &> /dev/null; then
    echo "PostgreSQL client found. Make sure your database is running and DATABASE_URL is correct."
else
    echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed and running."
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials"
echo "2. Create PostgreSQL database: createdb spendsmart"
echo "3. Get Plaid access token using: python setup_plaid.py <public_token>"
echo "4. Run the application: python main.py <plaid_access_token>"
echo ""

