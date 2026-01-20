import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import json

# Page configuration
st.set_page_config(
    page_title="Smart Expense Categorizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 5px solid #3B82F6;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1E40AF, #2563EB);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">💰 Smart Expense Categorizer</h1>', unsafe_allow_html=True)
st.markdown("### Automatically categorize your expenses using Machine Learning")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("Navigation")
    page = st.radio(
        "Choose a page:",
        ["🏠 Dashboard", "🔍 Single Transaction", "📁 Batch Upload", "📊 Insights", "🔧 API Tools"]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("""
    This tool uses machine learning to automatically 
    categorize your expenses based on transaction 
    descriptions and amounts.
    """)

# API Configuration
API_URL = "http://localhost:8000"  # Change this if your API is hosted elsewhere

# Helper functions
def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def predict_single(description, amount, date=None):
    """Predict category for a single transaction"""
    try:
        payload = {
            "description": description,
            "amount": float(amount),
            "date": date.strftime("%Y-%m-%d") if date else None
        }
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

# Main content based on selected page
if page == "🏠 Dashboard":
    st.header("Welcome to Smart Expense Categorizer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API Status", "✅ Online" if check_api_health()[0] else "❌ Offline")
    
    with col2:
        st.metric("Model Type", "ML Model" if check_api_health()[1] and check_api_health()[1].get('model_loaded') else "Rule-based")
    
    with col3:
        st.metric("Transactions Processed", "Ready")
    
    st.markdown("---")
    
    # Quick start
    st.subheader("Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 🔍 Single Transaction")
            st.write("Categorize one transaction at a time")
            if st.button("Go to Single Transaction", key="quick_single"):
                st.session_state.page = "🔍 Single Transaction"
                st.rerun()
    
    with col2:
        with st.container(border=True):
            st.markdown("### 📁 Batch Upload")
            st.write("Upload CSV file with multiple transactions")
            if st.button("Go to Batch Upload", key="quick_batch"):
                st.session_state.page = "📁 Batch Upload"
                st.rerun()

elif page == "🔍 Single Transaction":
    st.header("Categorize Single Transaction")
    
    # Check API health
    api_healthy, health_info = check_api_health()
    if not api_healthy:
        st.error("⚠️ API is not responding. Please make sure the backend server is running.")
        st.info("Start the API with: `python app/backend/api.py`")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        description = st.text_area(
            "Transaction Description",
            value="UBER RIDE #1234",
            height=120,
            placeholder="Enter transaction description from your bank statement...",
            help="Example: STARBUCKS COFFEE, AMAZON PURCHASE, NETFLIX SUBSCRIPTION"
        )
        
        amount = st.number_input(
            "Amount ($)",
            min_value=0.01,
            value=25.00,
            step=0.01,
            format="%.2f"
        )
        
        date = st.date_input("Date", datetime.now())
        
        if st.button("🏷️ Categorize Transaction", type="primary", use_container_width=True):
            if description and amount > 0:
                with st.spinner("Analyzing transaction..."):
                    success, result = predict_single(description, amount, date)
                    
                    if success:
                        # Display results
                        st.success(f"✅ Categorized as: **{result['category']}**")
                        
                        # Results in columns
                        cols = st.columns(4)
                        with cols[0]:
                            st.metric("Category", result['category'])
                        with cols[1]:
                            confidence_color = "green" if result['confidence'] > 0.8 else "orange" if result['confidence'] > 0.6 else "red"
                            st.metric("Confidence", f"{result['confidence']:.1%}")
                        with cols[2]:
                            st.metric("Amount", f"${amount:.2f}")
                        with cols[3]:
                            st.metric("Method", "ML Model" if health_info and health_info.get('model_loaded') else "Rule-based")
                        
                        # Confidence bar
                        st.progress(float(result['confidence']))
                        st.caption(f"Prediction confidence: {result['confidence']:.1%}")
                        
                        # Show raw response
                        with st.expander("View raw response"):
                            st.json(result)
                    else:
                        st.error(f"❌ Error: {result}")
            else:
                st.warning("Please enter both description and amount")

elif page == "📁 Batch Upload":
    st.header("Upload Multiple Transactions")
    
    upload_method = st.radio(
        "Choose upload method:",
        ["CSV File", "JSON Data", "Manual Entry"]
    )
    
    if upload_method == "CSV File":
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="CSV should have columns: description, amount (optional: date)"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(df)} transactions")
                
                # Show preview
                with st.expander("Preview data"):
                    st.dataframe(df.head(), use_container_width=True)
                
                # Validate required columns
                if 'description' not in df.columns or 'amount' not in df.columns:
                    st.error("CSV must contain 'description' and 'amount' columns")
                else:
                    if st.button("📊 Process All Transactions", type="primary"):
                        with st.spinner(f"Processing {len(df)} transactions..."):
                            transactions = []
                            for _, row in df.iterrows():
                                transactions.append({
                                    "description": str(row['description']),
                                    "amount": float(row['amount']),
                                    "date": row.get('date', datetime.now().strftime("%Y-%m-%d"))
                                })
                            
                            try:
                                response = requests.post(
                                    f"{API_URL}/predict-batch",
                                    json={"transactions": transactions},
                                    timeout=30
                                )
                                
                                if response.status_code == 200:
                                    results = response.json()
                                    st.success(f"✅ Successfully processed {len(results['predictions'])} transactions")
                                    
                                    # Display results
                                    results_df = pd.DataFrame(results['predictions'])
                                    
                                    tab1, tab2, tab3 = st.tabs(["Results", "Insights", "Download"])
                                    
                                    with tab1:
                                        st.dataframe(results_df, use_container_width=True)
                                    
                                    with tab2:
                                        insights = results['insights']
                                        if insights:
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric("Total Spent", f"${insights['total_spent']:,.2f}")
                                            with col2:
                                                st.metric("Avg Amount", f"${insights['average_amount']:.2f}")
                                            with col3:
                                                st.metric("Avg Confidence", f"{insights['average_confidence']:.1%}")
                                            
                                            # Category distribution
                                            if insights['category_counts']:
                                                cat_df = pd.DataFrame(
                                                    list(insights['category_counts'].items()),
                                                    columns=['Category', 'Count']
                                                )
                                                fig = px.pie(cat_df, values='Count', names='Category', 
                                                           title="Transaction Categories Distribution")
                                                st.plotly_chart(fig, use_container_width=True)
                                    
                                    with tab3:
                                        csv = results_df.to_csv(index=False)
                                        st.download_button(
                                            label="📥 Download Results as CSV",
                                            data=csv,
                                            file_name="categorized_expenses.csv",
                                            mime="text/csv",
                                            type="primary"
                                        )
                                        
                                        json_data = json.dumps(results, indent=2)
                                        st.download_button(
                                            label="📥 Download Results as JSON",
                                            data=json_data,
                                            file_name="categorized_expenses.json",
                                            mime="application/json"
                                        )
                                else:
                                    st.error(f"API Error: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

elif page == "📊 Insights":
    st.header("Expense Insights")
    
    # Sample data for demonstration
    st.info("This section shows sample insights. Connect to your actual transaction data for real insights.")
    
    # Generate sample data
    categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Utilities', 'Healthcare']
    monthly_data = []
    
    for month in range(1, 13):
        for category in categories:
            monthly_data.append({
                'Month': f'2023-{month:02d}',
                'Category': category,
                'Amount': np.random.randint(100, 1000)
            })
    
    df_sample = pd.DataFrame(monthly_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Spending Trend")
        fig = px.line(
            df_sample.groupby(['Month', 'Category'])['Amount'].sum().reset_index(),
            x='Month', y='Amount', color='Category',
            title="Spending Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Category Breakdown")
        total_by_category = df_sample.groupby('Category')['Amount'].sum().reset_index()
        fig = px.pie(
            total_by_category, 
            values='Amount', 
            names='Category',
            title="Total Spending by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Budget planning
    st.subheader("💰 Budget Planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_budget = st.number_input(
            "Set your monthly budget ($)",
            min_value=100,
            value=2000,
            step=100
        )
    
    with col2:
        # Calculate sample spending
        current_month = datetime.now().month
        current_spending = df_sample[df_sample['Month'] == f'2023-{current_month:02d}']['Amount'].sum()
        remaining = monthly_budget - current_spending
        
        st.metric(
            "Sample Current Month",
            f"${current_spending:.2f}",
            delta=f"${remaining:.2f} remaining",
            delta_color="normal" if remaining >= 0 else "inverse"
        )

elif page == "🔧 API Tools":
    st.header("API Development Tools")
    
    # API Status
    st.subheader("API Status")
    
    if st.button("Check API Health", key="health_check"):
        api_healthy, health_info = check_api_health()
        
        if api_healthy:
            st.success("✅ API is healthy and running")
            st.json(health_info)
        else:
            st.error("❌ API is not responding")
    
    # API Documentation
    st.subheader("API Documentation")
    
    with st.expander("View API Endpoints"):
        st.markdown("""
        ### Available Endpoints
        
        #### `GET /`
        **Description**: API root endpoint
        **Response**: API information
        
        #### `GET /health`
        **Description**: Health check endpoint
        **Response**: API health status
        
        #### `POST /predict`
        **Description**: Predict category for single transaction
        
        **Request Body**:
        ```json
        {
            "description": "UBER RIDE #1234",
            "amount": 24.50,
            "date": "2024-01-15"
        }
        ```
        
        **Response**:
        ```json
        {
            "category": "Transport",
            "confidence": 0.92,
            "description": "UBER RIDE #1234",
            "amount": 24.5
        }
        ```
        
        #### `POST /predict-batch`
        **Description**: Predict categories for multiple transactions
        """)
    
    # Test API
    st.subheader("Test API")
    
    with st.form("test_api_form"):
        test_endpoint = st.selectbox(
            "Select endpoint",
            ["/predict", "/predict-batch", "/health"]
        )
        
        if test_endpoint == "/predict":
            col1, col2 = st.columns(2)
            with col1:
                test_desc = st.text_input("Description", "STARBUCKS COFFEE")
            with col2:
                test_amount = st.number_input("Amount", value=5.75, step=0.01)
        
        if st.form_submit_button("Test Endpoint", type="primary"):
            try:
                if test_endpoint == "/predict":
                    payload = {
                        "description": test_desc,
                        "amount": test_amount
                    }
                    response = requests.post(f"{API_URL}{test_endpoint}", json=payload)
                elif test_endpoint == "/predict-batch":
                    payload = {
                        "transactions": [
                            {"description": "UBER RIDE", "amount": 25.00},
                            {"description": "AMAZON PURCHASE", "amount": 49.99}
                        ]
                    }
                    response = requests.post(f"{API_URL}{test_endpoint}", json=payload)
                else:
                    response = requests.get(f"{API_URL}{test_endpoint}")
                
                if response.status_code == 200:
                    st.success("✅ Request successful")
                    st.json(response.json())
                else:
                    st.error(f"❌ Error {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Smart Expense Categorizer • Powered by Machine Learning • "
    f"© {datetime.now().year}"
    "</div>",
    unsafe_allow_html=True
)
