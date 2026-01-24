#!/bin/bash

echo "🚀 Setting up Expense Categorizer (Simplified Version)..."

# Create directory structure if it doesn't exist
mkdir -p data/raw data/processed models app/backend app/frontend

# Create essential files if missing
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt..."
    cat > requirements.txt << 'REQ'
fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.1
pandas==2.1.3
numpy==1.24.3
scikit-learn==1.3.2
plotly==5.17.0
requests==2.31.0
joblib==1.3.2
python-multipart==0.0.6
pydantic==2.5.0
REQ
fi

# Create minimal synthetic data generator if missing
if [ ! -f "data/synthetic_data_generator.py" ]; then
    echo "Creating data generator..."
    mkdir -p data
    cat > data/synthetic_data_generator.py << 'PY'
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_transaction_data(num_samples=2000):
    categories = {
        'Food': ['mcdonalds', 'starbucks', 'groceries', 'restaurant', 'pizza', 'coffee'],
        'Transport': ['uber', 'lyft', 'gas station', 'metro', 'parking', 'taxi'],
        'Shopping': ['amazon', 'target', 'walmart', 'clothing', 'electronics'],
        'Entertainment': ['netflix', 'spotify', 'cinema', 'concert', 'theater'],
        'Utilities': ['electric bill', 'water bill', 'internet', 'phone bill'],
        'Income': ['salary', 'transfer', 'refund', 'deposit'],
        'Other': ['atm withdrawal', 'bank fee', 'unknown']
    }
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_samples):
        category = random.choice(list(categories.keys()))
        desc = f"{random.choice(categories[category]).upper()} #{random.randint(1000, 9999)}"
        
        amount_ranges = {'Food': (5, 100), 'Transport': (10, 150), 'Shopping': (20, 500),
                        'Entertainment': (10, 200), 'Utilities': (50, 300), 
                        'Income': (1000, 5000), 'Other': (2, 50)}
        min_amt, max_amt = amount_ranges[category]
        amount = round(random.uniform(min_amt, max_amt), 2)
        
        days_offset = random.randint(0, 365)
        date = start_date + timedelta(days=days_offset)
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'description': desc,
            'amount': amount,
            'category': category,
            'user_id': f'user_{random.randint(1, 3):03d}'
        })
    
    df = pd.DataFrame(data)
    df.to_csv('data/raw/transactions.csv', index=False)
    print(f"✅ Generated {num_samples} transactions")
    return df

if __name__ == "__main__":
    generate_transaction_data(2000)
PY
fi

# Create minimal model training if missing
if [ ! -f "models/train.py" ]; then
    echo "Creating model training..."
    mkdir -p models
    cat > models/train.py << 'PY'
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_model():
    print("🚀 Training model...")
    
    # Load data
    df = pd.read_csv('data/raw/transactions.csv')
    
    # Feature engineering
    df['description'] = df['description'].str.lower()
    df['description_length'] = df['description'].str.len()
    df['word_count'] = df['description'].str.split().str.len()
    df['amount_log'] = np.log1p(df['amount'])
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    
    # Prepare features
    X = df.drop(['category', 'date', 'user_id'], axis=1)
    y = df['category']
    
    # Preprocessor
    preprocessor = ColumnTransformer([
        ('text', TfidfVectorizer(max_features=500), 'description'),
        ('num', StandardScaler(), ['amount', 'description_length', 'word_count', 'amount_log', 'month', 'day_of_week'])
    ])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Train
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    train_score = pipeline.score(X_train, y_train)
    test_score = pipeline.score(X_test, y_test)
    
    print(f"✅ Training accuracy: {train_score:.3f}")
    print(f"✅ Test accuracy: {test_score:.3f}")
    
    # Save model
    joblib.dump(pipeline, 'models/expense_classifier.pkl')
    print("💾 Model saved as 'models/expense_classifier.pkl'")
    
    return pipeline

if __name__ == "__main__":
    train_model()
PY
fi

# Build Docker image
echo "📦 Building Docker image..."
docker build -t expense-categorizer .

# Stop and remove any existing container
docker stop expense-app 2>/dev/null || true
docker rm expense-app 2>/dev/null || true

# Run container
echo "🚀 Starting container..."
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  --name expense-app \
  expense-categorizer

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:8501"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Check status with:"
echo "   docker logs expense-app"
echo "   docker ps"
