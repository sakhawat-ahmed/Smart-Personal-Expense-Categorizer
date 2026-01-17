# models/predict.py
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

class ExpensePredictor:
    def __init__(self, model_path='models/expense_classifier.pkl'):
        self.model = joblib.load(model_path)
        self.categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 
                          'Utilities', 'Healthcare', 'Income', 'Other']
        
    def preprocess_input(self, description, amount, date=None):
        """Preprocess single transaction"""
        if date is None:
            date = datetime.now()
        
        # Create feature dictionary
        desc_lower = description.lower()
        
        features = {
            'description': desc_lower,
            'amount': float(amount),
            'description_length': len(description),
            'word_count': len(description.split()),
            'has_digits': int(bool(any(char.isdigit() for char in description))),
            'amount_log': np.log1p(float(amount)),
            'month': date.month,
            'day_of_week': date.weekday(),
            'payment_method': 'Unknown'  # Default
        }
        
        # Add keyword features
        keywords = ['uber', 'amazon', 'netflix', 'starbucks', 'mcdonalds', 
                   'walmart', 'target', 'gas', 'groceries', 'restaurant']
        for keyword in keywords:
            features[f'has_{keyword}'] = int(keyword in desc_lower)
        
        return pd.DataFrame([features])
    
    def predict(self, description, amount, date=None):
        """Predict category for a transaction"""
        try:
            # Preprocess
            X = self.preprocess_input(description, amount, date)
            
            # Predict
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            # Get confidence scores
            confidences = {cat: prob for cat, prob in zip(self.categories, probabilities)}
            
            return {
                'category': prediction,
                'confidence': float(np.max(probabilities)),
                'all_probabilities': confidences,
                'description': description,
                'amount': amount
            }
        except Exception as e:
            print(f"Error in prediction: {e}")
            return {
                'category': 'Other',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def predict_batch(self, transactions):
        """Predict categories for multiple transactions"""
        results = []
        for transaction in transactions:
            result = self.predict(
                transaction['description'],
                transaction['amount'],
                transaction.get('date')
            )
            results.append(result)
        return results

# Test the predictor
if __name__ == "__main__":
    predictor = ExpensePredictor()
    
    # Test cases
    test_transactions = [
        {"description": "UBER RIDE #1234", "amount": 24.50},
        {"description": "STARBUCKS COFFEE", "amount": 5.75},
        {"description": "AMAZON.COM PURCHASE", "amount": 89.99},
        {"description": "CON EDISON ELECTRIC BILL", "amount": 120.00}
    ]
    
    for transaction in test_transactions:
        result = predictor.predict(transaction["description"], transaction["amount"])
        print(f"{transaction['description']} → {result['category']} ({result['confidence']:.2f})")