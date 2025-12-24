# SpendSmart: AI-Powered Expense Tracker

An intelligent expense tracking application that automatically fetches banking transactions, categorizes them using AI, and syncs them to Google Sheets. Built with Python, PostgreSQL, Plaid API, and Gemini API.

## Features

- 🔄 **Automatic Transaction Fetching**: Integrates with Plaid API to automatically fetch banking transactions
- 🤖 **AI-Powered Categorization**: Uses Google's Gemini AI to categorize transactions with 90% accuracy across 10+ spending categories
- 📊 **Real-time Database Storage**: Stores all transactions in PostgreSQL for fast queries and analysis
- 📈 **Google Sheets Integration**: Automatically syncs categorized transactions to Google Sheets for easy viewing and analysis
- ⚡ **Efficient Pipeline**: Reduces manual financial tracking time by 80%

## Architecture

- **Python**: Core application logic
- **PostgreSQL**: Transaction storage and data persistence
- **Plaid API**: Banking transaction data fetching
- **Gemini API**: AI-powered transaction categorization
- **Google Sheets API**: Data synchronization and visualization
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: Database ORM

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Plaid account with API credentials
- Google Cloud project with Gemini API enabled
- Google Cloud project with Sheets API enabled

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd Spend-Smart
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your credentials:
   - `DATABASE_URL`: PostgreSQL connection string
   - `PLAID_CLIENT_ID` and `PLAID_SECRET`: From Plaid dashboard
   - `GEMINI_API_KEY`: From Google Cloud Console
   - `GOOGLE_SHEETS_SPREADSHEET_ID`: Your Google Sheets spreadsheet ID
   - `GOOGLE_SHEETS_CREDENTIALS_FILE`: Path to your OAuth credentials JSON file

5. **Set up PostgreSQL database**:
   ```bash
   createdb spendsmart
   # Or use your preferred PostgreSQL client
   ```

6. **Set up Google Sheets API credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials JSON file and save as `credentials.json` in the project root

7. **Get Plaid Access Token**:
   - Use [Plaid Link](https://plaid.com/docs/link/) to connect your bank account
   - Exchange the public token for an access token
   - You'll need to pass this access token when running the application

## Usage

### Basic Usage

Run the main application with your Plaid access token:

```bash
python main.py <your_plaid_access_token>
```

The application will:
1. Fetch transactions from Plaid (last 30 days by default)
2. Categorize them using Gemini AI
3. Store them in PostgreSQL
4. Sync to Google Sheets




