import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class ExpenseClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.scaler = None
        self.preprocessor = None
        
    def load_data(self, filepath='data/raw/transactions.csv'):
        """Load and prepare data"""
        df = pd.read_csv(filepath)
        
        # Feature engineering
        df['description'] = df['description'].str.lower()
        df['description_length'] = df['description'].str.len()
        df['word_count'] = df['description'].str.split().str.len()
        df['has_digits'] = df['description'].str.contains(r'\d').astype(int)
        df['amount_log'] = np.log1p(df['amount'])
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # Extract common keywords
        keywords = ['uber', 'amazon', 'netflix', 'starbucks', 'mcdonalds', 'walmart', 
                   'target', 'gas', 'groceries', 'restaurant']
        for keyword in keywords:
            df[f'has_{keyword}'] = df['description'].str.contains(keyword).astype(int)
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for training"""
        X = df.drop(['category', 'date', 'user_id'], axis=1)
        y = df['category']
        
        # Split text and numerical features
        text_features = ['description']
        numeric_features = ['amount', 'description_length', 'word_count', 
                           'has_digits', 'amount_log', 'month', 'day_of_week'] + \
                          [f'has_{k}' for k in keywords]
        
        # Create preprocessing pipeline
        self.preprocessor = ColumnTransformer([
            ('text', TfidfVectorizer(max_features=1000, ngram_range=(1, 2)), 'description'),
            ('num', StandardScaler(), numeric_features)
        ])
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        return X_train, X_test, y_train, y_test
    
    def train_models(self, X_train, y_train):
        """Train and compare multiple models"""
        models = {
            'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = 0
        
        for name, model in models.items():
            # Create pipeline
            pipeline = Pipeline([
                ('preprocessor', self.preprocessor),
                ('classifier', model)
            ])
            
            # Train
            pipeline.fit(X_train, y_train)
            
            # Evaluate on training (cross-validation would be better)
            score = pipeline.score(X_train, y_train)
            print(f"{name}: Training Accuracy = {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_model = pipeline
        
        self.model = best_model
        print(f"\nSelected model with accuracy: {best_score:.3f}")
        
        return best_model
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        y_pred = self.model.predict(X_test)
        
        print("Test Set Performance:")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return y_pred
    
    def save_model(self, path='models/expense_classifier.pkl'):
        """Save trained model"""
        joblib.dump(self.model, path)
        print(f"Model saved to {path}")
    
    def train_full_pipeline(self):
        """Complete training pipeline"""
        print("Loading data...")
        df = self.load_data()
        
        print("Preparing features...")
        X_train, X_test, y_train, y_test = self.prepare_features(df)
        
        print("Training models...")
        self.train_models(X_train, y_train)
        
        print("Evaluating...")
        self.evaluate(X_test, y_test)
        
        self.save_model()

if __name__ == "__main__":
    classifier = ExpenseClassifier()
    classifier.train_full_pipeline()