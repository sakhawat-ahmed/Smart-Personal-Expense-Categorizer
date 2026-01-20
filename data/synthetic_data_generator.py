import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_transaction_data(num_samples=2000):
    """Generate realistic synthetic transaction data"""
    
    print("Generating synthetic transaction data...")
    
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
        category = random.choice(list(categories.keys()))
        
        if random.random() < 0.7:
            merchant = random.choice(merchants[category])
            desc = f"{merchant} #{random.randint(1000, 9999)}"
        else:
            base_desc = random.choice(categories[category])
            desc = f"{base_desc.upper()} {random.choice(['PAYMENT', 'PURCHASE', 'CHARGE', ''])}"
        
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
        
        days_offset = random.randint(0, 365)
        date = start_date + timedelta(days=days_offset)
        
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
    
    # Ensure data directory exists
    os.makedirs('data/raw', exist_ok=True)
    
    df.to_csv('data/raw/transactions.csv', index=False)
    print(f"✅ Generated {num_samples} transactions to data/raw/transactions.csv")
    print(df.head())
    return df

if __name__ == "__main__":
    generate_transaction_data(2000)
