import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import plotly.express as px

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
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">💰 Smart Expense Categorizer</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Single Transaction", "Batch Upload", "API Status"])

# API URL
API_URL = "http://localhost:8000"

# Page 1: Single Transaction
if page == "Single Transaction":
    st.header("🔍 Categorize Single Transaction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        description = st.text_area(
            "Transaction Description",
            value="UBER RIDE #1234",
            height=100,
            help="Enter the transaction description from your bank statement"
        )
        
        amount = st.number_input(
            "Amount ($)",
            min_value=0.01,
            value=25.00,
            step=0.01
        )
        
        date = st.date_input("Date", datetime.now())
        
        if st.button("🏷️ Categorize Transaction", type="primary", use_container_width=True):
            if description and amount:
                with st.spinner("Analyzing transaction..."):
                    try:
                        payload = {
                            "description": description,
                            "amount": float(amount),
                            "date": date.strftime("%Y-%m-%d")
                        }
                        
                        response = requests.post(f"{API_URL}/predict", json=payload)
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Display results
                            st.success(f"✅ Category: **{result['category']}**")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Category", result['category'])
                            with col2:
                                st.metric("Confidence", f"{result['confidence']:.1%}")
                            with col3:
                                st.metric("Amount", f"${amount:.2f}")
                            
                            # Show confidence indicator
                            confidence = result['confidence']
                            if confidence > 0.8:
                                st.info("High confidence prediction")
                            elif confidence > 0.6:
                                st.warning("Medium confidence prediction")
                            else:
                                st.error("Low confidence prediction")
                        else:
                            st.error(f"API Error: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter both description and amount")

# Page 2: Batch Upload
elif page == "Batch Upload":
    st.header("📁 Upload Multiple Transactions")
    
    upload_option = st.radio("Choose input method:", ["CSV File", "Manual Entry"])
    
    if upload_option == "CSV File":
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:")
            st.dataframe(df.head())
            
            if st.button("📊 Process All Transactions", type="primary"):
                with st.spinner("Processing..."):
                    transactions = []
                    for _, row in df.iterrows():
                        transactions.append({
                            "description": str(row.get('description', '')),
                            "amount": float(row.get('amount', 0)),
                            "date": row.get('date', datetime.now().strftime("%Y-%m-%d"))
                        })
                    
                    try:
                        response = requests.post(
                            f"{API_URL}/predict-batch",
                            json={"transactions": transactions}
                        )
                        
                        if response.status_code == 200:
                            results = response.json()
                            
                            # Display results
                            st.success(f"✅ Processed {len(results['predictions'])} transactions")
                            
                            # Create results dataframe
                            results_df = pd.DataFrame(results['predictions'])
                            st.dataframe(results_df)
                            
                            # Download button
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv,
                                file_name="categorized_expenses.csv",
                                mime="text/csv"
                            )
                            
                            # Show insights
                            st.subheader("📈 Insights")
                            insights = results['insights']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Spent", f"${insights['total_spent']:,.2f}")
                            with col2:
                                st.metric("Transactions", insights['total_transactions'])
                            with col3:
                                st.metric("Avg Confidence", f"{insights['average_confidence']:.1%}")
                            
                            # Category breakdown
                            if insights['category_counts']:
                                cat_df = pd.DataFrame(
                                    list(insights['category_counts'].items()),
                                    columns=['Category', 'Count']
                                )
                                fig = px.pie(cat_df, values='Count', names='Category', 
                                           title="Transaction Categories")
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error(f"API Error: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Page 3: API Status
elif page == "API Status":
    st.header("🔧 API Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Check API Health"):
            try:
                response = requests.get(f"{API_URL}/health")
                if response.status_code == 200:
                    health = response.json()
                    st.success("✅ API is healthy")
                    st.json(health)
                else:
                    st.error("❌ API is not responding")
            except:
                st.error("❌ Cannot connect to API")
    
    with col2:
        st.subheader("API Endpoints")
        st.code("""
POST /predict
POST /predict-batch
GET /health
GET /
        """)
    
    st.subheader("Test API")
    with st.form("test_form"):
        test_desc = st.text_input("Description", "STARBUCKS COFFEE")
        test_amt = st.number_input("Amount", value=5.75)
        
        if st.form_submit_button("Test Prediction"):
            try:
                payload = {
                    "description": test_desc,
                    "amount": test_amt
                }
                response = requests.post(f"{API_URL}/predict", json=payload)
                if response.status_code == 200:
                    st.success("✅ Test successful")
                    st.json(response.json())
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")

# Footer
st.markdown("---")
st.markdown("*Smart Expense Categorizer • Powered by Machine Learning*")
