"""Example usage of SpendSmart application."""
from main import SpendSmart
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Example: Process transactions
def example_process_transactions():
    """Example of processing transactions."""
    # Replace with your actual Plaid access token
    plaid_access_token = "your_plaid_access_token_here"
    
    # Initialize application
    app = SpendSmart(plaid_access_token)
    
    try:
        # Process last 30 days of transactions
        stats = app.fetch_and_process_transactions(days=30, sync_to_sheets=True)
        
        print("\nProcessing Statistics:")
        print(f"  Total fetched: {stats['total_fetched']}")
        print(f"  New transactions: {stats['new_transactions']}")
        print(f"  Categorized: {stats['categorized']}")
        print(f"  Average confidence: {stats['average_confidence']:.2%}")
        print(f"  Synced to sheets: {stats['synced_to_sheets']}")
        
        # Get category summary
        summary = app.get_category_summary()
        print("\nSpending Summary by Category:")
        for category, data in sorted(
            summary.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        ):
            print(f"  {category}: ${data['total']:.2f} ({data['count']} transactions)")
            
    finally:
        app.close()


if __name__ == "__main__":
    print("SpendSmart Example Usage")
    print("=" * 50)
    print("\nNote: Make sure to:")
    print("1. Set up your .env file with API credentials")
    print("2. Replace 'your_plaid_access_token_here' with your actual token")
    print("3. Have PostgreSQL running and database created")
    print("\nUncomment the function call below to run the example:")
    # example_process_transactions()

