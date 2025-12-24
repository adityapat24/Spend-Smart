"""Main application entry point for SpendSmart."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session

from database import init_db, get_db, Transaction, TransactionCreate
from plaid_client import PlaidClient
from gemini_client import GeminiClient
from sheets_client import SheetsClient
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpendSmart:
    """Main application class for SpendSmart expense tracker."""
    
    def __init__(self, plaid_access_token: str):
        """
        Initialize SpendSmart application.
        
        Args:
            plaid_access_token: Plaid access token for authenticated requests
        """
        self.plaid_client = PlaidClient()
        self.plaid_client.set_access_token(plaid_access_token)
        self.gemini_client = GeminiClient()
        self.sheets_client = SheetsClient()
        
        # Initialize database
        init_db()
        logger.info("SpendSmart application initialized")
    
    def fetch_and_process_transactions(
        self,
        days: int = 30,
        sync_to_sheets: bool = True
    ) -> Dict:
        """
        Main pipeline: Fetch transactions, categorize, store, and sync.
        
        Args:
            days: Number of days to fetch transactions for
            sync_to_sheets: Whether to sync to Google Sheets
        
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Starting transaction processing for last {days} days")
        
        # Step 1: Fetch transactions from Plaid
        logger.info("Fetching transactions from Plaid...")
        transactions = self.plaid_client.get_all_transactions_since(days=days)
        logger.info(f"Fetched {len(transactions)} transactions from Plaid")
        
        if not transactions:
            logger.warning("No transactions found")
            return {
                'total_fetched': 0,
                'new_transactions': 0,
                'categorized': 0,
                'synced_to_sheets': 0
            }
        
        # Get database session
        db = next(get_db())
        
        try:
            # Step 2: Check which transactions are new
            existing_ids = {
                tx.transaction_id
                for tx in db.query(Transaction).all()
            }
        
        new_transactions = [
            tx for tx in transactions
            if tx['transaction_id'] not in existing_ids
        ]
        
        logger.info(f"Found {len(new_transactions)} new transactions")
        
        if not new_transactions:
            logger.info("No new transactions to process")
            return {
                'total_fetched': len(transactions),
                'new_transactions': 0,
                'categorized': 0,
                'synced_to_sheets': 0
            }
        
        # Step 3: Categorize transactions using Gemini AI
        logger.info("Categorizing transactions with Gemini AI...")
        categorized_transactions = self.gemini_client.categorize_batch(new_transactions)
        
        # Calculate average confidence
        avg_confidence = sum(
            tx.get('confidence', 0) for tx in categorized_transactions
        ) / len(categorized_transactions) if categorized_transactions else 0
        
        logger.info(
            f"Categorized {len(categorized_transactions)} transactions "
            f"(avg confidence: {avg_confidence:.2%})"
        )
        
            # Step 4: Store transactions in database
            logger.info("Storing transactions in database...")
            stored_count = 0
            for tx in categorized_transactions:
                try:
                    db_transaction = Transaction(
                        transaction_id=tx['transaction_id'],
                        account_id=tx['account_id'],
                        amount=tx['amount'],
                        date=tx['date'],
                        name=tx['name'],
                        merchant_name=tx.get('merchant_name'),
                        description=tx.get('description'),
                        is_pending=tx.get('is_pending', False),
                        category=f"{tx.get('primary_category', 'Other')} - {tx.get('subcategory', '')}",
                        primary_category=tx.get('primary_category', 'Other'),
                        subcategory=tx.get('subcategory', ''),
                        category_confidence=tx.get('confidence', 0.0),
                        synced_to_sheets=False
                    )
                    db.add(db_transaction)
                    stored_count += 1
                except Exception as e:
                    logger.error(f"Error storing transaction {tx.get('transaction_id')}: {e}")
            
            db.commit()
            logger.info(f"Stored {stored_count} transactions in database")
        
        # Step 5: Sync to Google Sheets if enabled
        synced_count = 0
        if sync_to_sheets and categorized_transactions:
            logger.info("Syncing transactions to Google Sheets...")
            try:
                # Get all unsynced transactions
                unsynced = db.query(Transaction).filter(
                    Transaction.synced_to_sheets == False
                ).all()
                
                if unsynced:
                    # Convert to dict format for sheets
                    sheets_data = []
                    for tx in unsynced:
                        sheets_data.append({
                            'date': tx.date,
                            'name': tx.name,
                            'merchant_name': tx.merchant_name,
                            'amount': tx.amount,
                            'primary_category': tx.primary_category,
                            'subcategory': tx.subcategory,
                            'description': tx.description,
                            'category_confidence': tx.category_confidence,
                            'transaction_id': tx.transaction_id
                        })
                    
                    # Sync to sheets
                    self.sheets_client.sync_transactions(sheets_data)
                    
                    # Mark as synced
                    for tx in unsynced:
                        tx.synced_to_sheets = True
                    db.commit()
                    synced_count = len(unsynced)
                    
                    logger.info(f"Synced {synced_count} transactions to Google Sheets")
            except Exception as e:
                logger.error(f"Error syncing to Google Sheets: {e}")
        
        finally:
            db.close()
        
        # Step 6: Generate statistics
        stats = {
            'total_fetched': len(transactions),
            'new_transactions': len(new_transactions),
            'categorized': len(categorized_transactions),
            'average_confidence': avg_confidence,
            'synced_to_sheets': synced_count,
            'categories_used': len(set(
                tx.get('primary_category', 'Other')
                for tx in categorized_transactions
            ))
        }
        
        logger.info("Transaction processing completed")
        logger.info(f"Statistics: {stats}")
        
        return stats
    
    def get_category_summary(self) -> Dict:
        """Get summary of spending by category."""
        db = next(get_db())
        try:
            transactions = db.query(Transaction).all()
            
            category_totals = {}
            for tx in transactions:
                category = tx.primary_category or 'Other'
                if category not in category_totals:
                    category_totals[category] = {'count': 0, 'total': 0.0}
                category_totals[category]['count'] += 1
                category_totals[category]['total'] += abs(tx.amount)
            
            return category_totals
        finally:
            db.close()


def main():
    """Main entry point."""
    import sys
    
    # Check for Plaid access token
    if len(sys.argv) < 2:
        print("Usage: python main.py <plaid_access_token>")
        print("\nTo get a Plaid access token:")
        print("1. Use Plaid Link to connect your bank account")
        print("2. Exchange the public_token for an access_token")
        print("3. Pass the access_token as an argument")
        sys.exit(1)
    
    plaid_access_token = sys.argv[1]
    
    # Initialize application
    app = SpendSmart(plaid_access_token)
    
    try:
        # Process transactions
        stats = app.fetch_and_process_transactions(days=30, sync_to_sheets=True)
        
        # Print summary
        print("\n" + "="*50)
        print("SpendSmart Processing Summary")
        print("="*50)
        print(f"Total transactions fetched: {stats['total_fetched']}")
        print(f"New transactions processed: {stats['new_transactions']}")
        print(f"Categorized: {stats['categorized']}")
        print(f"Average confidence: {stats['average_confidence']:.2%}")
        print(f"Categories used: {stats['categories_used']}")
        print(f"Synced to Google Sheets: {stats['synced_to_sheets']}")
        print("="*50)
        
        # Print category summary
        category_summary = app.get_category_summary()
        if category_summary:
            print("\nSpending by Category:")
            print("-" * 50)
            for category, data in sorted(
                category_summary.items(),
                key=lambda x: x[1]['total'],
                reverse=True
            ):
                print(f"{category:25s} ${data['total']:>10.2f} ({data['count']} transactions)")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

