#!/bin/bash
# setup_enhanced.sh

echo "🚀 Setting up Enhanced Expense Categorizer..."

# Create project structure
mkdir -p {data/{raw,processed},models,app/{backend,frontend/{components,assets},ml},notebooks,scripts,tests}

# Create all the enhanced files (copy the code from above into respective files)

echo "📦 Building Docker image..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "✅ Setup complete!"
echo ""
echo "🌐 Access your enhanced application:"
echo "   Frontend: http://localhost:8501"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Features included:"
echo "   • Multi-user authentication"
echo "   • OCR receipt scanning"
echo "   • Advanced analytics dashboard"
echo "   • Budget planning & forecasting"
echo "   • Anomaly detection"
echo "   • Multi-currency support"
echo "   • Bank integration (mock)"
echo "   • Export to Excel/PDF"
echo "   • Mobile-responsive UI"
echo "   • Real-time notifications"