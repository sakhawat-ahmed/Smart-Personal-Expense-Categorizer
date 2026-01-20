import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import warnings
import os
warnings.filterwarnings('ignore')

def train_model():
    print("🚀 Starting model training...")
    
    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)
    
    # Load data
    try:
        df = pd.read_csv('data/raw/transactions.csv')
        print(f"📊 Loaded {len(df)} transactions")
    except Exception as e:
        print(f"❌ Could not load data: {e}")
        print("Make sure to generate data first by running: python data/synthetic_data_generator.py")
        return
    
    # Feature engineering
    df['description'] = df['description'].str.lower()
    df['description_length'] = df['description'].str.len()
    df['word_count'] = df['description'].str.split().str.len()
    df['has_digits'] = df['description'].str.contains(r'\d').astype(int)
    df['amount_log'] = np.log1p(df['amount'])
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    
    # Keywords
    keywords = ['uber', 'amazon', 'netflix', 'starbucks', 'mcdonalds', 'walmart', 
                'target', 'gas', 'groceries', 'restaurant']
    for keyword in keywords:
        df[f'has_{keyword}'] = df['description'].str.contains(keyword).astype(int)
    
    # Prepare features
    X = df.drop(['category', 'date', 'user_id', 'payment_method'], axis=1, errors='ignore')
    y = df['category']
    
    # Text and numeric features
    text_features = ['description']
    numeric_features = ['amount', 'description_length', 'word_count', 
                       'has_digits', 'amount_log', 'month', 'day_of_week'] + \
                      [f'has_{k}' for k in keywords]
    
    # Preprocessor
    preprocessor = ColumnTransformer([
        ('text', TfidfVectorizer(max_features=500, ngram_range=(1, 2)), 'description'),
        ('num', StandardScaler(), numeric_features)
    ])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Train
    print("🤖 Training model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    train_score = pipeline.score(X_train, y_train)
    test_score = pipeline.score(X_test, y_test)
    
    print(f"✅ Training accuracy: {train_score:.3f}")
    print(f"✅ Test accuracy: {test_score:.3f}")
    
    # Save model
    joblib.dump(pipeline, 'models/expense_classifier.pkl')
    print("💾 Model saved as 'models/expense_classifier.pkl'")
    
    # Show sample predictions
    print("\n🎯 Sample predictions:")
    sample = X_test.head(3)
    predictions = pipeline.predict(sample)
    for i, (idx, row) in enumerate(sample.iterrows()):
        desc = row['description'][:50] + "..." if len(row['description']) > 50 else row['description']
        print(f"  {desc} → {predictions[i]}")
    
    return pipeline

if __name__ == "__main__":
    train_model()
