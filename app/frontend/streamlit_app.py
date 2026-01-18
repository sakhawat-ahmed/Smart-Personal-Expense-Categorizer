import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Smart Expense Categorizer",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .category-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .high-confidence { border-left: 5px solid #10B981; }
    .medium-confidence { border-left: 5px solid #F59E0B; }
    .low-confidence { border-left: 5px solid #EF4444; }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">💰 Smart Expense Categorizer</h1>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Single Transaction", "Batch Upload", "Spending Insights", "API Documentation"])

# API endpoint
API_URL = "http://localhost:8000"  # Change if deployed

# Function to make API calls
def predict_transaction(description, amount, date=None):
    """Call prediction API"""
    try:
        payload = {
            "description": description,
            "amount": float(amount),
            "date": date
        }
        
        response = requests.post(f"{API_URL}/predict", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def predict_batch(transactions):
    """Call batch prediction API"""
    try:
        payload = {"transactions": transactions}
        response = requests.post(f"{API_URL}/predict-batch", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

# Page 1: Single Transaction
if page == "Single Transaction":
    st.header("🔍 Categorize Single Transaction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        description = st.text_area(
            "Transaction Description",
            placeholder="e.g., UBER RIDE #1234, STARBUCKS COFFEE, AMAZON.COM PURCHASE",
            height=100
        )
        
        amount = st.number_input("Amount ($)", min_value=0.01, value=25.00, step=0.01)
        
        date = st.date_input("Date", datetime.now())
        
        if st.button("🏷️ Categorize Transaction", type="primary", use_container_width=True):
            if description and amount:
                with st.spinner("Analyzing transaction..."):
                    result = predict_transaction(
                        description, 
                        amount, 
                        date.strftime("%Y-%m-%d")
                    )
                    
                    if result:
                        # Display result
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Predicted Category", result['category'])
                        
                        with col2:
                            confidence_color = "green" if result['confidence'] > 0.7 else \
                                             "orange" if result['confidence'] > 0.5 else "red"
                            st.metric("Confidence", f"{result['confidence']:.1%}")
                        
                        with col3:
                            st.metric("Amount", f"${amount:.2f}")
                        
                        # Confidence indicator
                        confidence_level = "high" if result['confidence'] > 0.7 else \
                                         "medium" if result['confidence'] > 0.5 else "low"
                        
                        st.markdown(f"""
                        <div class="category-card {confidence_level}-confidence">
                            <h4>📋 Transaction Details</h4>
                            <p><strong>Description:</strong> {description}</p>
                            <p><strong>Category Probability Breakdown:</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show probabilities as bar chart
                        prob_df = pd.DataFrame(list(result['probabilities'].items()), 
                                             columns=['Category', 'Probability'])
                        fig = px.bar(prob_df, x='Category', y='Probability',
                                   color='Probability', color_continuous_scale='Viridis')
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Please enter both description and amount")

# Page 2: Batch Upload
elif page == "Batch Upload":
    st.header("📁 Upload Multiple Transactions")
    
    upload_option = st.radio("Upload method", 
                           ["CSV File", "Manual Entry", "Paste JSON"])
    
    if upload_option == "CSV File":
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            # Check required columns
            required_cols = ['description', 'amount']
            if all(col in df.columns for col in required_cols):
                if st.button("📊 Categorize All Transactions", type="primary"):
                    # Convert to list of dictionaries
                    transactions = []
                    for _, row in df.iterrows():
                        transactions.append({
                            "description": str(row['description']),
                            "amount": float(row['amount']),
                            "date": row.get('date', datetime.now().strftime("%Y-%m-%d"))
                        })
                    
                    with st.spinner("Processing transactions..."):
                        result = predict_batch(transactions)
                        
                        if result:
                            # Display results
                            results_df = pd.DataFrame(result['predictions'])
                            
                            st.success(f"✅ Processed {len(results_df)} transactions")
                            
                            # Show results table
                            st.dataframe(results_df)
                            
                            # Download button
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=csv,
                                file_name="categorized_expenses.csv",
                                mime="text/csv"
                            )
                            
                            # Show insights
                            st.subheader("📈 Spending Insights")
                            insights = result['insights']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Spent", f"${insights['total_spent']:,.2f}")
                            with col2:
                                st.metric("Average Transaction", f"${insights['average_transaction']:.2f}")
                            with col3:
                                st.metric("Transactions Processed", len(results_df))
                            
                            # Category breakdown chart
                            cat_df = pd.DataFrame(list(insights['category_summary'].items()),
                                                columns=['Category', 'Total'])
                            fig = px.pie(cat_df, values='Total', names='Category',
                                       title="Spending by Category")
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"CSV must contain columns: {required_cols}")

# Page 3: Spending Insights (mock data for now)
elif page == "Spending Insights":
    st.header("📈 Spending Analysis & Trends")
    
    # Generate sample data
    categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Utilities']
    monthly_data = []
    
    for month in range(1, 13):
        for category in categories:
            monthly_data.append({
                'Month': month,
                'Category': category,
                'Amount': np.random.randint(100, 1000)
            })
    
    df = pd.DataFrame(monthly_data)
    
    # Interactive charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Spending Trend")
        fig = px.line(df, x='Month', y='Amount', color='Category',
                     title="Spending Over Time")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Category Breakdown")
        fig = px.pie(df.groupby('Category')['Amount'].sum().reset_index(),
                    values='Amount', names='Category',
                    title="Total Spending by Category")
        st.plotly_chart(fig, use_container_width=True)
    
    # Budget planning section
    st.subheader("📅 Budget Planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        budget = st.number_input("Set monthly budget ($)", min_value=100, value=2000)
    
    with col2:
        current_spending = df[df['Month'] == datetime.now().month]['Amount'].sum()
        st.metric("Current Month Spending", f"${current_spending:.2f}",
                 delta=f"${budget - current_spending:.2f}")

# Page 4: API Documentation
elif page == "API Documentation":
    st.header("🔧 API Documentation")
    
    st.markdown("""
    ### API Endpoints
    
    #### `POST /predict`
    Predict category for a single transaction.
    
    **Request Body:**
    ```json
    {
        "description": "UBER RIDE #1234",
        "amount": 24.50,
        "date": "2024-01-15",
        "user_id": "user_001"
    }
    ```
    
    **Response:**
    ```json
    {
        "category": "Transport",
        "confidence": 0.92,
        "description": "UBER RIDE #1234",
        "amount": 24.5,
        "probabilities": {
            "Food": 0.01,
            "Transport": 0.92,
            "Shopping": 0.02,
            ...
        }
    }
    ```
    
    #### `POST /predict-batch`
    Predict categories for multiple transactions.
    
    #### `GET /health`
    Health check endpoint.
    
    ### Quick Test
    """)
    
    # API tester
    with st.expander("🔍 Test API Endpoints"):
        endpoint = st.selectbox("Select endpoint", ["/predict", "/predict-batch", "/health"])
        
        if endpoint == "/predict":
            with st.form("test_predict"):
                test_desc = st.text_input("Description", "STARBUCKS COFFEE")
                test_amt = st.number_input("Amount", value=5.75)
                if st.form_submit_button("Test Endpoint"):
                    response = predict_transaction(test_desc, test_amt)
                    st.json(response)
        
        elif endpoint == "/health":
            if st.button("Check Health"):
                try:
                    response = requests.get(f"{API_URL}/health")
                    st.json(response.json())
                except:
                    st.error("Cannot connect to API")

# Footer
st.markdown("---")
st.markdown("*Smart Expense Categorizer v1.0 • Powered by Machine Learning*")