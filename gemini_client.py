"""Gemini API client for AI-powered transaction categorization."""
import google.generativeai as genai
from typing import Dict, List, Optional
from config import settings
import logging
import json

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Gemini API for transaction categorization."""
    
    # Define spending categories
    CATEGORIES = [
        "Food & Dining",
        "Shopping",
        "Transportation",
        "Bills & Utilities",
        "Entertainment",
        "Healthcare",
        "Travel",
        "Education",
        "Personal Care",
        "Home & Garden",
        "Gifts & Donations",
        "Business Expenses",
        "Other"
    ]
    
    def __init__(self):
        """Initialize Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self._build_prompt_template()
    
    def _build_prompt_template(self):
        """Build the prompt template for categorization."""
        categories_str = ", ".join(self.CATEGORIES)
        self.prompt_template = f"""You are an expert financial transaction categorizer. 
Analyze the following transaction and categorize it accurately.

Available categories: {categories_str}

For each transaction, provide:
1. Primary category (one of the categories above)
2. Subcategory (more specific, e.g., "Groceries" under "Food & Dining")
3. Confidence score (0.0 to 1.0)

Return your response as a JSON object with this exact format:
{{
    "primary_category": "category name",
    "subcategory": "specific subcategory",
    "confidence": 0.95
}}

Transaction details:
"""
    
    def categorize_transaction(self, transaction: Dict) -> Dict:
        """
        Categorize a single transaction using Gemini AI.
        
        Args:
            transaction: Transaction dictionary with name, amount, merchant_name, etc.
        
        Returns:
            Dictionary with primary_category, subcategory, and confidence
        """
        try:
            # Build transaction description
            transaction_desc = f"""
Name: {transaction.get('name', 'Unknown')}
Amount: ${abs(transaction.get('amount', 0)):.2f}
Merchant: {transaction.get('merchant_name', 'N/A')}
Description: {transaction.get('description', 'N/A')}
Date: {transaction.get('date', 'N/A')}
"""
            
            prompt = self.prompt_template + transaction_desc
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks if present)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from text if parsing fails
                import re
                json_match = re.search(r'\{[^}]+\}', response_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from Gemini response")
            
            # Validate and normalize result
            primary_category = result.get('primary_category', 'Other')
            if primary_category not in self.CATEGORIES:
                # Find closest match or default to Other
                primary_category = self._find_closest_category(primary_category) or 'Other'
            
            return {
                'primary_category': primary_category,
                'subcategory': result.get('subcategory', ''),
                'confidence': float(result.get('confidence', 0.5))
            }
            
        except Exception as e:
            logger.error(f"Error categorizing transaction {transaction.get('transaction_id')}: {str(e)}")
            # Return default category on error
            return {
                'primary_category': 'Other',
                'subcategory': 'Uncategorized',
                'confidence': 0.0
            }
    
    def categorize_batch(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize multiple transactions in batch.
        
        Args:
            transactions: List of transaction dictionaries
        
        Returns:
            List of categorization results
        """
        results = []
        for transaction in transactions:
            categorization = self.categorize_transaction(transaction)
            results.append({
                **transaction,
                **categorization
            })
        return results
    
    def _find_closest_category(self, category: str) -> Optional[str]:
        """Find the closest matching category from the predefined list."""
        category_lower = category.lower()
        for cat in self.CATEGORIES:
            if category_lower in cat.lower() or cat.lower() in category_lower:
                return cat
        return None

