import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def render_analytics():
    """Advanced Analytics Dashboard"""
    
    st.header("📈 Advanced Analytics")
    
    # Tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Time Analysis", 
        "💰 Spending Patterns", 
        "📊 Comparative Analysis",
        "🔮 Predictive Insights"
    ])
    
    with tab1:
        render_time_analysis()
    
    with tab2:
        render_spending_patterns()
    
    with tab3:
        render_comparative_analysis()
    
    with tab4:
        render_predictive_insights()

def render_time_analysis():
    """Time-based spending analysis"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Generate sample time series data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        daily_spending = np.random.normal(50, 20, len(dates))
        
        df_time = pd.DataFrame({
            'Date': dates,
            'Spending': daily_spending,
            '7_day_avg': pd.Series(daily_spending).rolling(7).mean(),
            '30_day_avg': pd.Series(daily_spending).rolling(30).mean()
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_time['Date'],
            y=df_time['Spending'],
            mode='lines',
            name='Daily Spending',
            line=dict(color='lightblue', width=1)
        ))
        fig.add_trace(go.Scatter(
            x=df_time['Date'],
            y=df_time['7_day_avg'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='orange', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df_time['Date'],
            y=df_time['30_day_avg'],
            mode='lines',
            name='30-Day Average',
            line=dict(color='green', width=2)
        ))
        
        fig.update_layout(
            title="Daily Spending Trend",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Key Metrics")
        
        metrics = {
            "Avg Daily Spend": "$52.34",
            "Peak Spending Day": "Friday",
            "Lowest Spending Day": "Tuesday",
            "Monthly Growth": "+2.3%",
            "Weekend vs Weekday": "35% higher"
        }
        
        for metric, value in metrics.items():
            st.metric(metric, value)

def render_spending_patterns():
    """Spending pattern analysis"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Heatmap of spending by day and hour
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        
        # Generate sample data
        data = np.random.rand(len(days), len(hours)) * 100
        
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=hours,
            y=days,
            colorscale='Viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Spending Heatmap (Day vs Hour)",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Spending by location (mock data)
        locations = ['Home', 'Work', 'Shopping Mall', 'Restaurant', 'Online', 'Travel']
        spending = [1200, 800, 2500, 1800, 3200, 1500]
        
        fig = go.Figure(data=[go.Pie(
            labels=locations,
            values=spending,
            hole=.3,
            marker=dict(colors=px.colors.sequential.Viridis)
        )])
        
        fig.update_layout(
            title="Spending by Location",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_comparative_analysis():
    """Comparative analysis"""
    st.subheader("Comparative Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly comparison
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        current_year = [1200, 1500, 1300, 1800, 1600, 1700]
        last_year = [1100, 1400, 1250, 1600, 1550, 1650]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Current Year',
            x=months,
            y=current_year,
            marker_color='rgb(55, 83, 109)'
        ))
        fig.add_trace(go.Bar(
            name='Last Year',
            x=months,
            y=last_year,
            marker_color='rgb(26, 118, 255)'
        ))
        
        fig.update_layout(
            title="Monthly Spending Comparison",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category comparison
        categories = ['Food', 'Transport', 'Shopping', 'Entertainment']
        user_avg = [450, 300, 600, 200]
        peer_avg = [400, 350, 550, 250]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Your Avg',
            x=categories,
            y=user_avg,
            marker_color='lightcoral'
        ))
        fig.add_trace(go.Bar(
            name='Peer Avg',
            x=categories,
            y=peer_avg,
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title="Category Spending vs Peers",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_predictive_insights():
    """Predictive analytics and insights"""
    st.subheader("🔮 Predictive Insights")
    
    # Next month prediction
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Predicted Spending (Next Month)", "$2,850", delta="+5.2%")
    with col2:
        st.metric("Savings Potential", "$320", "+12%")
    with col3:
        st.metric("Risk of Overspending", "Medium", "-8%")
    
    # Spending forecast
    future_dates = pd.date_range(start='2024-07-01', end='2024-12-31', freq='M')
    forecast = [2800, 2900, 3100, 3200, 3300, 3400]
    lower_bound = [f * 0.9 for f in forecast]
    upper_bound = [f * 1.1 for f in forecast]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=forecast,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='royalblue', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=future_dates.tolist() + future_dates.tolist()[::-1],
        y=upper_bound + lower_bound[::-1],
        fill='toself',
        fillcolor='rgba(65, 105, 225, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Interval'
    ))
    
    fig.update_layout(
        title="6-Month Spending Forecast",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        hovermode='x',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    with st.expander("💡 Personalized Recommendations"):
        recommendations = [
            "Reduce food delivery by 20% to save $80/month",
            "Switch to public transport 2 days/week to save $60/month",
            "Cancel unused subscriptions (potential savings: $45/month)",
            "Shop during sales to save 15% on shopping",
            "Use cashback apps for online purchases"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")