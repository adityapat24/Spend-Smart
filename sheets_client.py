"""Google Sheets API client for syncing transactions."""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
from config import settings
import logging
import os
import pickle

logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class SheetsClient:
    """Client for interacting with Google Sheets API."""
    
    def __init__(self):
        """Initialize Google Sheets client."""
        self.service = None
        self.spreadsheet_id = settings.google_sheets_spreadsheet_id
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None
        token_file = 'token.pickle'
        
        # Load existing token if available
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(settings.google_sheets_credentials_file):
                    raise FileNotFoundError(
                        f"Google Sheets credentials file not found: {settings.google_sheets_credentials_file}\n"
                        "Please download credentials.json from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.google_sheets_credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('sheets', 'v4', credentials=creds)
        logger.info("Successfully authenticated with Google Sheets API")
    
    def create_sheet_if_not_exists(self, sheet_name: str = "Transactions"):
        """Create a new sheet if it doesn't exist."""
        if not self.spreadsheet_id:
            logger.warning("No spreadsheet ID configured. Skipping sheet creation.")
            return
        
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            
            if sheet_name not in sheet_names:
                # Add new sheet
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
                
                body = {'requests': requests}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                ).execute()
                logger.info(f"Created sheet: {sheet_name}")
            else:
                logger.info(f"Sheet '{sheet_name}' already exists")
                
        except HttpError as error:
            logger.error(f"Error creating sheet: {error}")
            raise
    
    def sync_transactions(self, transactions: List[Dict], sheet_name: str = "Transactions"):
        """
        Sync transactions to Google Sheets.
        
        Args:
            transactions: List of transaction dictionaries
            sheet_name: Name of the sheet to sync to
        """
        if not self.spreadsheet_id:
            logger.warning("No spreadsheet ID configured. Skipping sync.")
            return
        
        try:
            # Create sheet if it doesn't exist
            self.create_sheet_if_not_exists(sheet_name)
            
            # Prepare header row if sheet is empty
            headers = [
                "Date", "Name", "Merchant", "Amount", "Primary Category",
                "Subcategory", "Description", "Confidence", "Transaction ID"
            ]
            
            # Prepare data rows
            values = [headers]
            for tx in transactions:
                row = [
                    tx.get('date', '').strftime('%Y-%m-%d') if hasattr(tx.get('date'), 'strftime') else str(tx.get('date', '')),
                    tx.get('name', ''),
                    tx.get('merchant_name', ''),
                    tx.get('amount', 0),
                    tx.get('primary_category', ''),
                    tx.get('subcategory', ''),
                    tx.get('description', ''),
                    tx.get('category_confidence', 0),
                    tx.get('transaction_id', '')
                ]
                values.append(row)
            
            # Clear existing data and write new data
            range_name = f"{sheet_name}!A1"
            body = {'values': values}
            
            # Clear the sheet first
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:Z"
            ).execute()
            
            # Write new data
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Synced {len(transactions)} transactions to Google Sheets")
            return result
            
        except HttpError as error:
            logger.error(f"Error syncing to Google Sheets: {error}")
            raise
    
    def append_transactions(self, transactions: List[Dict], sheet_name: str = "Transactions"):
        """
        Append new transactions to Google Sheets (without clearing existing data).
        
        Args:
            transactions: List of transaction dictionaries
            sheet_name: Name of the sheet to append to
        """
        if not self.spreadsheet_id:
            logger.warning("No spreadsheet ID configured. Skipping append.")
            return
        
        try:
            # Prepare data rows
            values = []
            for tx in transactions:
                row = [
                    tx.get('date', '').strftime('%Y-%m-%d') if hasattr(tx.get('date'), 'strftime') else str(tx.get('date', '')),
                    tx.get('name', ''),
                    tx.get('merchant_name', ''),
                    tx.get('amount', 0),
                    tx.get('primary_category', ''),
                    tx.get('subcategory', ''),
                    tx.get('description', ''),
                    tx.get('category_confidence', 0),
                    tx.get('transaction_id', '')
                ]
                values.append(row)
            
            if not values:
                return
            
            # Append data
            range_name = f"{sheet_name}!A:Z"
            body = {'values': values}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"Appended {len(transactions)} transactions to Google Sheets")
            return result
            
        except HttpError as error:
            logger.error(f"Error appending to Google Sheets: {error}")
            raise

