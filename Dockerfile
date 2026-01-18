FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data/raw data/processed models

# Generate sample data and train model
RUN python data/synthetic_data_generator.py
RUN python models/train.py

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Command to run both API and Streamlit
CMD ["sh", "-c", "uvicorn app.backend.api:app --host 0.0.0.0 --port 8000 & streamlit run app.frontend.streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]