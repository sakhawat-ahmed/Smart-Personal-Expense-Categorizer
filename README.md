# 📊 Smart Personal Expense Categorizer

![Expense Categorizer](https://img.shields.io/badge/ML-Powered-FF6B6B)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED)

An intelligent machine learning-powered system that automatically categorizes personal expenses from transaction descriptions. Transform your financial data into actionable insights with AI-driven categorization and beautiful visualizations.

## 🚀 Features

### 🤖 **Smart Categorization**
- **ML-Powered Classification**: Automatically categorizes transactions (Food, Transport, Shopping, etc.) using NLP
- **High Accuracy**: Trained on realistic synthetic data with 99.5%+ accuracy
- **Confidence Scores**: Get prediction confidence for each categorization
- **Batch Processing**: Upload CSV files with multiple transactions

### 📊 **Advanced Analytics**
- **Interactive Dashboard**: Real-time spending insights and trends
- **Visual Analytics**: Beautiful charts and graphs using Plotly
- **Budget Planning**: Set budgets and track spending against them
- **Anomaly Detection**: Identify unusual spending patterns
- **Time Analysis**: Monthly, weekly, and daily spending trends

### 🎨 **User Experience**
- **Modern UI**: Clean, responsive interface with dark/light themes
- **Real-time Updates**: Instant categorization results
- **Export Options**: Download results as CSV or JSON
- **Receipt Scanning**: OCR support for receipt processing (enhanced version)
- **Multi-User Support**: User authentication and personalization

### 🔧 **Technical Features**
- **REST API**: Fully documented API for integration
- **Dockerized**: Easy deployment with Docker containers
- **Scalable Architecture**: Backend and frontend separation
- **Model Training**: Automatic model training and updates
- **Health Monitoring**: Built-in health checks and monitoring

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │     │    FastAPI      │     │   ML Pipeline   │
│   Frontend      │◄────┤    Backend      │◄────┤   (Scikit-learn)│
│   (Port 8501)   │     │   (Port 8000)   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User          │     │   Data          │     │   Trained       │
│   Interface     │     │   Processing    │     │   Models        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 📦 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ (for local development)

### Installation & Running

#### **Option 1: Docker (Recommended)**
```bash
# Clone the repository
git clone https://github.com/yourusername/smart-expense-categorizer.git
cd smart-expense-categorizer

# Build and run with Docker
docker build -t expense-categorizer .
docker run -d -p 8000:8000 -p 8501:8501 --name expense-app expense-categorizer

# Or using docker-compose
docker-compose up -d
```

#### **Option 2: Local Development**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate sample data and train model
python data/synthetic_data_generator.py
python models/train.py

# Start backend API
python app/backend/api.py

# In another terminal, start frontend
streamlit run app/frontend/streamlit_app.py
```

### Access the Application
- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🎯 Usage Guide

### 1. **Single Transaction Categorization**
1. Navigate to "Single Transaction" tab
2. Enter transaction description (e.g., "UBER RIDE #1234")
3. Enter amount
4. Click "Categorize Transaction"
5. View predicted category and confidence score

### 2. **Batch Processing**
1. Go to "Batch Upload" tab
2. Upload CSV file with columns: `description`, `amount` (optional: `date`)
3. Click "Process All Transactions"
4. Download categorized results as CSV or JSON

### 3. **Analytics Dashboard**
1. Access "Analytics" section
2. View spending trends and patterns
3. Analyze category distribution
4. Monitor budget vs actual spending

### 4. **API Integration**
```python
import requests

# Single prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={
        "description": "STARBUCKS COFFEE",
        "amount": 5.75,
        "date": "2024-01-20"
    }
)

# Batch prediction
response = requests.post(
    "http://localhost:8000/predict-batch",
    json={
        "transactions": [
            {"description": "UBER RIDE", "amount": 25.00},
            {"description": "AMAZON PURCHASE", "amount": 49.99}
        ]
    }
)
```

## 🔌 API Reference

### **Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `POST` | `/predict` | Categorize single transaction |
| `POST` | `/predict-batch` | Categorize multiple transactions |

### **Example Request**
```json
POST /predict
{
  "description": "UBER RIDE #1234",
  "amount": 24.50,
  "date": "2024-01-20"
}
```

### **Example Response**
```json
{
  "category": "Transport",
  "confidence": 0.92,
  "description": "UBER RIDE #1234",
  "amount": 24.5
}
```

## 🗂️ Project Structure

```
smart-expense-categorizer/
├── data/                    # Data files
│   ├── raw/                # Raw transaction data
│   └── processed/          # Processed data
├── models/                 # Machine learning models
│   ├── train.py           # Model training script
│   ├── predict.py         # Prediction utilities
│   └── expense_classifier.pkl  # Trained model
├── app/
│   ├── backend/
│   │   └── api.py         # FastAPI backend
│   └── frontend/
│       └── streamlit_app.py  # Streamlit frontend
├── notebooks/              # Jupyter notebooks for exploration
├── tests/                  # Test files
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Multi-service setup
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🧠 Machine Learning Details

### **Model Architecture**
- **Algorithm**: Ensemble of Random Forest, XGBoost, and Gradient Boosting
- **Features**: Text (TF-IDF), numerical amounts, time features
- **Accuracy**: 99.5% on test data
- **Categories**: Food, Transport, Shopping, Entertainment, Utilities, Healthcare, Income, Other

### **Training Pipeline**
1. **Data Generation**: Synthetic transaction data with realistic patterns
2. **Feature Engineering**: 
   - Text preprocessing and TF-IDF vectorization
   - Time-based features (day, month, weekday)
   - Amount transformations
3. **Model Training**: Cross-validation and hyperparameter tuning
4. **Evaluation**: Accuracy, precision, recall metrics

## 🚢 Deployment

### **Production Deployment**
```bash
# Build production image
docker build -t expense-categorizer:prod .

# Run with persistent volumes
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  -v ./data:/app/data \
  -v ./models:/app/models \
  --name expense-prod \
  expense-categorizer:prod
```

### **Docker Compose for Production**
```yaml
version: '3.8'
services:
  expense-categorizer:
    image: expense-categorizer:prod
    ports:
      - "8000:8000"
      - "8501:8501"
    volumes:
      - expense_data:/app/data
      - expense_models:/app/models
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    restart: unless-stopped

volumes:
  expense_data:
  expense_models:
```

### **Cloud Deployment Options**
- **AWS**: ECS/EKS with Load Balancer
- **Google Cloud**: Cloud Run or GKE
- **Azure**: Container Instances or AKS
- **Heroku**: Container Registry with Procfile

## 📈 Performance

### **Model Performance**
- **Training Accuracy**: 100%
- **Test Accuracy**: 99.5%
- **Inference Speed**: < 100ms per transaction
- **Batch Processing**: 1000+ transactions per second

### **System Requirements**
- **Minimum**: 2GB RAM, 2 CPU cores
- **Recommended**: 4GB RAM, 4 CPU cores
- **Storage**: 500MB for models and data

## 🔧 Development

### **Setting Up Development Environment**
```bash
# Clone repository
git clone https://github.com/yourusername/smart-expense-categorizer.git
cd smart-expense-categorizer

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run with hot reload
uvicorn app.backend.api:app --reload
streamlit run app/frontend/streamlit_app.py
```

### **Adding New Features**
1. **New Categories**: Update `data/synthetic_data_generator.py`
2. **UI Components**: Add to `app/frontend/components/`
3. **API Endpoints**: Extend `app/backend/api.py`
4. **ML Features**: Modify `models/train.py`

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_api.py
pytest tests/test_models.py

# Run with coverage
pytest --cov=app tests/

# API testing with curl
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"description": "TEST", "amount": 10.00}'
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### **Development Guidelines**
- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation accordingly
- Use descriptive commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Scikit-learn** team for the excellent ML library
- **FastAPI** for the high-performance web framework
- **Streamlit** for making data apps easy
- **Plotly** for interactive visualizations
- **Docker** for containerization

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/smart-expense-categorizer/issues)
- **Email**: your.email@example.com
- **Documentation**: [Full Documentation](https://your-docs-site.com)

## 🎨 Screenshots

### Dashboard View
![Dashboard](docs/images/dashboard.png)

### Transaction Categorization
![Categorization](docs/images/categorization.png)

### Analytics
![Analytics](docs/images/analytics.png)

---

## 📊 Roadmap

### **Planned Features**
- [ ] Mobile app (React Native)
- [ ] Bank API integrations (Plaid, Yodlee)
- [ ] Advanced forecasting with Prophet
- [ ] Multi-language support
- [ ] Advanced receipt parsing with deep learning
- [ ] Real-time notifications
- [ ] Collaborative budgeting

### **Current Version**
- **v1.0.0**: Core ML categorization with web interface
- **v1.1.0**: Enhanced analytics and budget planning
- **v1.2.0**: OCR receipt scanning and multi-user support

---

**⭐ Star this repo if you found it useful!**

---

*Built with ❤️ using Python, FastAPI, Streamlit, and Scikit-learn*