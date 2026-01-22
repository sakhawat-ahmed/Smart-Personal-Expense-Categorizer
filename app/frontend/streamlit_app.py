import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import requests
import asyncio
from streamlit_option_menu import option_menu
import calendar

# Import custom components
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.analytics import render_analytics
from components.settings import render_settings
from components.upload import render_upload_section
from components.reports import render_reports

# Page config
st.set_page_config(
    page_title="Smart Expense Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open("app/frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "token" not in st.session_state:
        st.session_state.token = None
    if "transactions" not in st.session_state:
        st.session_state.transactions = []
    if "budgets" not in st.session_state:
        st.session_state.budgets = {}
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

# Main App
def main():
    load_css()
    init_session_state()
    
    # Top Navigation Bar
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        st.markdown("<h1 class='main-title'>💰 Smart Expense Manager</h1>", unsafe_allow_html=True)
    
    with col2:
        if st.button("🔔", help="Notifications"):
            st.session_state.show_notifications = True
    
    with col3:
        if st.button("⚙️", help="Settings"):
            st.session_state.page = "Settings"
    
    with col4:
        if st.button("👤", help="Profile"):
            st.session_state.page = "Profile"
    
    with col5:
        if st.button("🔄", help="Refresh Data"):
            st.rerun()
    
    # Authentication Check
    if not st.session_state.user:
        render_login()
        return
    
    # Main Navigation
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Transactions", "Analytics", "Budget", "Reports", "Upload", "Settings"],
        icons=["house", "cash-stack", "graph-up", "wallet", "file-earmark-text", "upload", "gear"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#4CAF50"},
        }
    )
    
    # Render selected page
    if selected == "Dashboard":
        render_dashboard()
    elif selected == "Transactions":
        render_transactions()
    elif selected == "Analytics":
        render_analytics()
    elif selected == "Budget":
        render_budget()
    elif selected == "Reports":
        render_reports()
    elif selected == "Upload":
        render_upload_section()
    elif selected == "Settings":
        render_settings()

def render_login():
    """Enhanced Login/Register UI"""
    st.markdown("""
    <div class='login-container'>
        <div class='login-box'>
            <h2>Welcome to Smart Expense Manager</h2>
            <p>Track, analyze, and optimize your spending</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                remember = st.checkbox("Remember me")
                
                if st.form_submit_button("Login", use_container_width=True):
                    # Mock login for demo
                    st.session_state.user = {"email": email, "name": "Demo User"}
                    st.session_state.token = "demo_token"
                    st.success("Login successful!")
                    st.rerun()
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    st.success("Account created! Please login.")

def render_transactions():
    """Enhanced Transactions View"""
    st.header("📋 Transaction History")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        start_date = st.date_input("From", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To", datetime.now())
    with col3:
        categories = st.multiselect("Categories", ["All", "Food", "Transport", "Shopping", "Entertainment", "Utilities"])
    with col4:
        min_amount, max_amount = st.slider("Amount Range", 0, 1000, (0, 500))
    
    # Mock data - replace with API call
    transactions = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=50, freq='D'),
        'Description': ['Transaction ' + str(i) for i in range(50)],
        'Amount': np.random.randint(10, 500, 50),
        'Category': np.random.choice(['Food', 'Transport', 'Shopping', 'Entertainment'], 50),
        'Status': np.random.choice(['Completed', 'Pending', 'Failed'], 50)
    })
    
    # Display transactions
    st.dataframe(
        transactions,
        column_config={
            "Date": st.column_config.DateColumn("Date"),
            "Amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
            "Category": st.column_config.SelectboxColumn("Category", options=transactions['Category'].unique()),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Export to Excel", use_container_width=True):
            st.success("Export started!")
    with col2:
        if st.button("🔄 Re-categorize All", use_container_width=True):
            st.info("Re-categorizing transactions...")
    with col3:
        if st.button("📊 Generate Summary", use_container_width=True):
            st.session_state.show_summary = True

def render_budget():
    """Enhanced Budget Planning"""
    st.header("💰 Budget Planning")
    
    # Current month budget overview
    current_month = datetime.now().strftime("%B %Y")
    st.subheader(f"Budget for {current_month}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Budget", "$2,500", delta="+5%")
    with col2:
        st.metric("Spent", "$1,850", delta="-150", delta_color="inverse")
    with col3:
        st.metric("Remaining", "$650", "+12 days")
    with col4:
        st.metric("Daily Avg", "$61.67")
    
    # Budget by category
    categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Utilities', 'Healthcare']
    budgets = [500, 300, 800, 200, 400, 300]
    spent = [450, 280, 750, 180, 350, 250]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Budget',
        x=categories,
        y=budgets,
        marker_color='lightblue'
    ))
    fig.add_trace(go.Bar(
        name='Spent',
        x=categories,
        y=spent,
        marker_color='coral'
    ))
    
    fig.update_layout(
        title="Budget vs Spent by Category",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Budget setup
    with st.expander("📝 Set Up New Budget"):
        col1, col2 = st.columns(2)
        with col1:
            budget_name = st.text_input("Budget Name", "Monthly Budget")
            total_budget = st.number_input("Total Budget", value=2500.00)
        with col2:
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        
        st.subheader("Category Breakdown")
        
        for category in categories:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(category)
            with col2:
                st.number_input(f"{category} Budget", value=400, key=f"budget_{category}")
        
        if st.button("Save Budget", type="primary"):
            st.success("Budget saved successfully!")

if __name__ == "__main__":
    main()