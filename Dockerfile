FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including OCR tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p data/raw data/processed models uploads exports

# Create non-root user
RUN useradd -m -u 1000 user && \
    chown -R user:user /app
USER user

EXPOSE 8000 8501

CMD ["sh", "-c", "python scripts/init_db.py && python models/train.py && uvicorn app.backend.api:app --host 0.0.0.0 --port 8000 --reload & streamlit run app/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]