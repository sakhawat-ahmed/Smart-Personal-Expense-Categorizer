import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
from transformers import AutoTokenizer, AutoModel
import torch
import joblib

class AdvancedExpenseClassifier:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.label_encoder = None
        self.embedding_model = None
        
    def create_features(self, df):
        """Create advanced features"""
        df = df.copy()
        
        # Text features
        df['description_lower'] = df['description'].str.lower()
        df['description_length'] = df['description'].str.len()
        df['word_count'] = df['description'].str.split().str.len()
        df['has_digits'] = df['description'].str.contains(r'\d').astype(int)
        df['has_special'] = df['description'].str.contains(r'[^\w\s]').astype(int)
        
        # Amount features
        df['amount_log'] = np.log1p(df['amount'])
        df['amount_bin'] = pd.qcut(df['amount'], q=5, labels=False)
        
        # Time features
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['day_of_month'] = df['date'].dt.day
        df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        
        # Merchant patterns
        common_merchants = ['uber', 'lyft', 'amazon', 'walmart', 'target', 
                           'starbucks', 'mcdonalds', 'netflix', 'spotify']
        for merchant in common_merchants:
            df[f'has_{merchant}'] = df['description_lower'].str.contains(merchant).astype(int)
        
        # Frequency features (requires user history)
        if 'user_id' in df.columns:
            df['user_transaction_count'] = df.groupby('user_id')['amount'].transform('count')
            df['user_avg_amount'] = df.groupby('user_id')['amount'].transform('mean')
        
        return df
    
    def build_model(self, use_bert=False):
        """Build advanced model pipeline"""
        
        # Define column types
        text_features = ['description']
        numeric_features = ['amount', 'description_length', 'word_count', 
                           'has_digits', 'amount_log', 'month', 'day', 
                           'day_of_week', 'is_weekend']
        categorical_features = ['amount_bin', 'is_month_end', 'is_month_start']
        
        # Create preprocessor
        if use_bert:
            # For BERT embeddings (requires GPU for training)
            from transformers import pipeline
            text_transformer = pipeline('feature-extraction', 
                                       model='bert-base-uncased')
        else:
            text_transformer = TfidfVectorizer(max_features=1000, 
                                              ngram_range=(1, 3))
        
        preprocessor = ColumnTransformer([
            ('text', text_transformer, 'description'),
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
        
        # Create ensemble model
        models = [
            ('rf', RandomForestClassifier(n_estimators=200, random_state=42)),
            ('xgb', xgb.XGBClassifier(n_estimators=100, learning_rate=0.1)),
            ('gb', GradientBoostingClassifier(n_estimators=100))
        ]
        
        from sklearn.ensemble import VotingClassifier
        ensemble = VotingClassifier(estimators=models, voting='soft')
        
        # Create final pipeline
        self.model = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', ensemble)
        ])
        
        return self.model
    
    def train(self, X_train, y_train):
        """Train model with early stopping"""
        self.model.fit(X_train, y_train)
        return self
    
    def predict_with_confidence(self, X):
        """Predict with confidence scores"""
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        confidence = np.max(probabilities, axis=1)
        
        return predictions, confidence, probabilities
    
    def explain_prediction(self, X, feature_names):
        """Explain predictions using SHAP"""
        try:
            import shap
            explainer = shap.TreeExplainer(self.model.named_steps['classifier'])
            shap_values = explainer.shap_values(X)
            return shap_values
        except:
            return None