from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime
from models.predict import ExpensePredictor
import uvicorn

app = FastAPI(title="Smart Expense Categorizer API", 
              description="API for automatic expense categorization")

# Initialize predictor
predictor = ExpensePredictor()

class Transaction(BaseModel):
    description: str
    amount: float
    date: Optional[str] = None
    user_id: Optional[str] = None

class BatchRequest(BaseModel):
    transactions: List[Transaction]

class CategorizationResponse(BaseModel):
    category: str
    confidence: float
    description: str
    amount: float
    probabilities: dict

@app.get("/")
async def root():
    return {"message": "Smart Expense Categorizer API", "status": "running"}

@app.post("/predict", response_model=CategorizationResponse)
async def predict_single(transaction: Transaction):
    """Predict category for a single transaction"""
    try:
        # Parse date if provided
        date_obj = None
        if transaction.date:
            date_obj = datetime.strptime(transaction.date, "%Y-%m-%d")
        
        result = predictor.predict(
            transaction.description,
            transaction.amount,
            date_obj
        )
        
        return CategorizationResponse(
            category=result['category'],
            confidence=result['confidence'],
            description=transaction.description,
            amount=transaction.amount,
            probabilities=result.get('all_probabilities', {})
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict-batch")
async def predict_batch(batch: BatchRequest):
    """Predict categories for multiple transactions"""
    try:
        results = []
        for transaction in batch.transactions:
            date_obj = None
            if transaction.date:
                date_obj = datetime.strptime(transaction.date, "%Y-%m-%d")
            
            result = predictor.predict(
                transaction.description,
                transaction.amount,
                date_obj
            )
            
            results.append({
                "description": transaction.description,
                "amount": transaction.amount,
                "predicted_category": result['category'],
                "confidence": result['confidence'],
                "user_id": transaction.user_id
            })
        
        # Generate insights
        insights = generate_insights(results)
        
        return {
            "predictions": results,
            "insights": insights,
            "total_transactions": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def generate_insights(predictions):
    """Generate spending insights from predictions"""
    df = pd.DataFrame(predictions)
    
    if len(df) == 0:
        return {}
    
    insights = {
        "total_spent": float(df['amount'].sum()),
        "category_summary": {},
        "top_categories": []
    }
    
    # Calculate by category
    category_totals = df.groupby('predicted_category')['amount'].sum().to_dict()
    insights['category_summary'] = category_totals
    
    # Top categories by spending
    top_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]
    insights['top_categories'] = [
        {"category": cat, "total": float(total)} for cat, total in top_cats
    ]
    
    # Average transaction size
    insights['average_transaction'] = float(df['amount'].mean())
    
    return insights

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)