"""Configuration management for SpendSmart application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    
    # Plaid API
    plaid_client_id: str
    plaid_secret: str
    plaid_env: str = "sandbox"
    plaid_products: str = "transactions"
    
    # Gemini API
    gemini_api_key: str
    
    # Google Sheets API
    google_sheets_credentials_file: Optional[str] = "credentials.json"
    google_sheets_spreadsheet_id: Optional[str] = None
    
    # Application
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

