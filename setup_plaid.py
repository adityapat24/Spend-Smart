"""Helper script to get Plaid access token using Plaid Link."""
from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exchange_public_token(public_token: str) -> str:
    """
    Exchange a Plaid public token for an access token.
    
    Args:
        public_token: Public token from Plaid Link
    
    Returns:
        Access token for API requests
    """
    configuration = Configuration(
        host=getattr(plaid_api.PlaidEnvironment, settings.plaid_env.upper()),
        api_key={
            'clientId': settings.plaid_client_id,
            'secret': settings.plaid_secret
        }
    )
    api_client = ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    
    access_token = response.access_token
    logger.info("Successfully exchanged public token for access token")
    
    return access_token


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python setup_plaid.py <public_token>")
        print("\nTo get a public token:")
        print("1. Use Plaid Link (https://plaid.com/docs/link/)")
        print("2. Complete the bank connection flow")
        print("3. Pass the public_token as an argument")
        sys.exit(1)
    
    public_token = sys.argv[1]
    access_token = exchange_public_token(public_token)
    
    print(f"\nAccess Token: {access_token}")
    print("\nYou can now use this access token with the main application:")
    print(f"python main.py {access_token}")

