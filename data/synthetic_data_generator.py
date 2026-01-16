import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_transaction_data(num_samples=5000):
    """Generate realistic synthetic transaction data"""
    
    # Categories and their descriptions
    categories = {
        'Food': ['mcdonalds', 'starbucks', 'groceries', 'restaurant', 'pizza', 'coffee', 'lunch', 'dinner'],
        'Transport': ['uber', 'lyft', 'gas station', 'metro', 'parking', 'taxi', 'bus fare'],
        'Shopping': ['amazon', 'target', 'walmart', 'clothing', 'electronics', 'home depot'],
        'Entertainment': ['netflix', 'spotify', 'cinema', 'concert', 'theater'],
        'Utilities': ['electric bill', 'water bill', 'internet', 'phone bill'],
        'Healthcare': ['pharmacy', 'hospital', 'doctor', 'dentist', 'insurance'],
        'Income': ['salary', 'transfer', 'refund', 'deposit'],
        'Other': ['atm withdrawal', 'bank fee', 'unknown']
    }
    
    # Common merchant names and patterns
    merchants = {
        'Food': ['MCDONALDS', 'STARBUCKS', 'WHOLE FOODS', 'CHIPOTLE', 'DOMINOS', 'SUBWAY'],
        'Transport': ['UBER *RIDE', 'LYFT *TRIP', 'SHELL OIL', 'EXXONMOBIL', 'CITY METRO'],
        'Shopping': ['AMAZON.COM', 'TARGET', 'WALMART', 'BEST BUY', 'APPLE STORE'],
        'Entertainment': ['NETFLIX', 'SPOTIFY', 'AMC THEATRES', 'TICKETMASTER'],
        'Utilities': ['CON EDISON', 'VERIZON WIRELESS', 'COMCAST', 'AT&T'],
        'Healthcare': ['CVS PHARMACY', 'WALGREENS', 'HOSPITAL', 'MEDICAL CENTER'],
        'Income': ['DIRECT DEPOSIT', 'BANK TRANSFER', 'PAYPAL', 'VENMO'],
        'Other': ['ATM WITHDRAWAL', 'BANK FEE', 'MISC CHARGE']
    }
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_samples):
        # Random category
        category = random.choice(list(categories.keys()))
        
        # Generate description
        if random.random() < 0.7:
            merchant = random.choice(merchants[category])
            desc = f"{merchant} #{random.randint(1000, 9999)}"
        else:
            # More varied descriptions
            base_desc = random.choice(categories[category])
            desc = f"{base_desc.upper()} {random.choice(['PAYMENT', 'PURCHASE', 'CHARGE', ''])}"
        
        # Generate amount based on category
        amount_ranges = {
            'Food': (5, 100),
            'Transport': (10, 150),
            'Shopping': (20, 500),
            'Entertainment': (10, 200),
            'Utilities': (50, 300),
            'Healthcare': (20, 1000),
            'Income': (1000, 5000),
            'Other': (2, 50)
        }
        min_amt, max_amt = amount_ranges[category]
        amount = round(random.uniform(min_amt, max_amt), 2)
        
        # Random date
        days_offset = random.randint(0, 365)
        date = start_date + timedelta(days=days_offset)
        
        # Payment method
        payment_method = random.choice(['Credit Card', 'Debit Card', 'Cash', 'Bank Transfer'])
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'description': desc,
            'amount': amount,
            'category': category,
            'payment_method': payment_method,
            'user_id': random.choice(['user_001', 'user_002', 'user_003'])
        })
    
    df = pd.DataFrame(data)
    df.to_csv('data/raw/transactions.csv', index=False)
    print(f"Generated {num_samples} transactions")
    return df

if __name__ == "__main__":
    df = generate_transaction_data(10000)
    print(df.head())