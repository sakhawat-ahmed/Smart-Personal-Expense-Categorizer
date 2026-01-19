from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime
import joblib
import numpy as np
import uvicorn

app = FastAPI(title="Smart Expense Categorizer API")

# Load model
try:
    model = joblib.load('models/expense_classifier.pkl')
    print("✅ Model loaded successfully")
except:
    print("⚠️  Model not found, using fallback")
    model = None

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
    """Preprocess a single transaction"""
    if date is None:
        date = datetime.now()
    else:
        date = datetime.strptime(date, "%Y-%m-%d")
    
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

@app.get("/")
async def root():
    return {"message": "Smart Expense Categorizer API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict(transaction: Transaction):
    """Predict category for a single transaction"""
    try:
        if model is None:
            # Fallback simple categorization
            description = transaction.description.lower()
            if any(word in description for word in ['uber', 'taxi', 'lyft', 'bus']):
                category = "Transport"
            elif any(word in description for word in ['starbucks', 'mcdonalds', 'restaurant', 'food']):
                category = "Food"
            elif any(word in description for word in ['amazon', 'walmart', 'target']):
                category = "Shopping"
            else:
                category = "Other"
            confidence = 0.5
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
        df = pd.DataFrame(results)
        insights = {
            "total_spent": float(df['amount'].sum()),
            "total_transactions": len(df),
            "category_counts": df['category'].value_counts().to_dict(),
            "average_confidence": float(df['confidence'].mean())
        }
        
        return {
            "predictions": results,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
