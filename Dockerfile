FROM python:3.10-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed models

# Expose ports for API and Streamlit
EXPOSE 8000 8501

# Run both services
CMD ["sh", "-c", "python data/synthetic_data_generator.py && python models/train.py && uvicorn app.backend.api:app --host 0.0.0.0 --port 8000 --reload & streamlit run app/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless=true"]
