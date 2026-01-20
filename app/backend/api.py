from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime
import joblib
import numpy as np
import uvicorn
import os

app = FastAPI(
    title="Smart Expense Categorizer API",
    description="API for automatic expense categorization using machine learning",
    version="1.0.0"
)

# Load model
model = None
model_path = 'models/expense_classifier.pkl'

try:
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print("✅ Model loaded successfully from", model_path)
    else:
        print(f"⚠️  Model not found at {model_path}, using fallback categorization")
except Exception as e:
    print(f"⚠️  Error loading model: {e}, using fallback categorization")

class Transaction(BaseModel):
    description: str
    amount: float
    date: Optional[str] = None
    user_id: Optional[str] = None

class BatchRequest(BaseModel):
    transactions: List[Transaction]

class PredictionResponse(BaseModel):
    category: str
    confidence: float
    description: str
    amount: float

def preprocess_for_prediction(description, amount, date=None):
    """Preprocess a single transaction for prediction"""
    if date is None:
        date = datetime.now()
    else:
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
        except:
            date = datetime.now()
    
    desc_lower = description.lower()
    
    # Feature engineering (must match training)
    features = {
        'description': desc_lower,
        'amount': float(amount),
        'description_length': len(description),
        'word_count': len(description.split()),
        'has_digits': int(bool(any(char.isdigit() for char in description))),
        'amount_log': np.log1p(float(amount)),
        'month': date.month,
        'day_of_week': date.weekday(),
    }
    
    # Add keyword features
    keywords = ['uber', 'amazon', 'netflix', 'starbucks', 'mcdonalds', 
                'walmart', 'target', 'gas', 'groceries', 'restaurant']
    for keyword in keywords:
        features[f'has_{keyword}'] = int(keyword in desc_lower)
    
    return pd.DataFrame([features])

def fallback_categorization(description, amount):
    """Fallback simple categorization if model is not available"""
    description = description.lower()
    
    if any(word in description for word in ['uber', 'taxi', 'lyft', 'bus', 'metro', 'train']):
        category = "Transport"
    elif any(word in description for word in ['starbucks', 'mcdonalds', 'restaurant', 'food', 'coffee', 'lunch', 'dinner']):
        category = "Food"
    elif any(word in description for word in ['amazon', 'walmart', 'target', 'shop', 'store', 'best buy']):
        category = "Shopping"
    elif any(word in description for word in ['netflix', 'spotify', 'cinema', 'movie', 'theater']):
        category = "Entertainment"
    elif any(word in description for word in ['electric', 'water', 'internet', 'phone', 'bill', 'utility']):
        category = "Utilities"
    elif amount >= 1000:
        category = "Income"
    else:
        category = "Other"
    
    return category, 0.7  # Medium confidence for fallback

@app.get("/")
async def root():
    return {
        "message": "Smart Expense Categorizer API",
        "status": "running",
        "model_loaded": model is not None,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "predict": "/predict",
            "predict_batch": "/predict-batch"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(transaction: Transaction):
    """Predict category for a single transaction"""
    try:
        if model is None:
            # Use fallback categorization
            category, confidence = fallback_categorization(
                transaction.description, 
                transaction.amount
            )
        else:
            # Use ML model
            X = preprocess_for_prediction(
                transaction.description,
                transaction.amount,
                transaction.date
            )
            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            category = prediction
            confidence = float(np.max(probabilities))
        
        return PredictionResponse(
            category=category,
            confidence=confidence,
            description=transaction.description,
            amount=transaction.amount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict-batch")
async def predict_batch(batch: BatchRequest):
    """Predict categories for multiple transactions"""
    try:
        results = []
        for transaction in batch.transactions:
            result = await predict(transaction)
            results.append(result.dict())
        
        # Generate insights
        if results:
            df = pd.DataFrame(results)
            insights = {
                "total_spent": float(df['amount'].sum()),
                "total_transactions": len(df),
                "category_counts": df['category'].value_counts().to_dict(),
                "average_confidence": float(df['confidence'].mean()),
                "average_amount": float(df['amount'].mean()),
                "max_amount": float(df['amount'].max()),
                "min_amount": float(df['amount'].min())
            }
        else:
            insights = {}
        
        return {
            "predictions": results,
            "insights": insights,
            "model_used": "ml_model" if model is not None else "fallback"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Expense Categorizer API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
