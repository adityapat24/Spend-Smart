"""Plaid API client for fetching banking transactions."""
from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_response import TransactionsGetResponse
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class PlaidClient:
    """Client for interacting with Plaid API."""
    
    def __init__(self):
        """Initialize Plaid client with configuration."""
        configuration = Configuration(
            host=getattr(plaid_api.PlaidEnvironment, settings.plaid_env.upper()),
            api_key={
                'clientId': settings.plaid_client_id,
                'secret': settings.plaid_secret
            }
        )
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        self.access_token: Optional[str] = None
    
    def set_access_token(self, access_token: str):
        """Set the access token for authenticated requests."""
        self.access_token = access_token
    
    def get_transactions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Fetch transactions from Plaid.
        
        Args:
            start_date: Start date for transaction fetch (defaults to 30 days ago)
            end_date: End date for transaction fetch (defaults to today)
            account_ids: Optional list of account IDs to filter by
        
        Returns:
            List of transaction dictionaries
        """
        if not self.access_token:
            raise ValueError("Access token not set. Call set_access_token() first.")
        
        # Default to last 30 days if not specified
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Format dates for Plaid API (YYYY-MM-DD)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        try:
            options = None
            if account_ids:
                options = TransactionsGetRequestOptions(account_ids=account_ids)
            
            request = TransactionsGetRequest(
                access_token=self.access_token,
                start_date=start_date_str,
                end_date=end_date_str,
                options=options
            )
            
            response: TransactionsGetResponse = self.client.transactions_get(request)
            transactions = response.transactions
            
            logger.info(f"Fetched {len(transactions)} transactions from Plaid")
            
            # Convert to list of dictionaries
            transaction_list = []
            for transaction in transactions:
                transaction_dict = {
                    'transaction_id': transaction.transaction_id,
                    'account_id': transaction.account_id,
                    'amount': transaction.amount,
                    'date': datetime.strptime(transaction.date, '%Y-%m-%d'),
                    'name': transaction.name,
                    'merchant_name': getattr(transaction, 'merchant_name', None),
                    'description': getattr(transaction, 'original_description', transaction.name),
                    'is_pending': getattr(transaction, 'pending', False),
                    'category': getattr(transaction, 'category', None),  # Plaid's category
                    'category_id': getattr(transaction, 'category_id', None)
                }
                transaction_list.append(transaction_dict)
            
            return transaction_list
            
        except Exception as e:
            logger.error(f"Error fetching transactions from Plaid: {str(e)}")
            raise
    
    def get_all_transactions_since(self, days: int = 30) -> List[Dict]:
        """Get all transactions since N days ago."""
        start_date = datetime.now() - timedelta(days=days)
        return self.get_transactions(start_date=start_date)

