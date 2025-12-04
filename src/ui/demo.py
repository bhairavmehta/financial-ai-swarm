"""
Streamlit Demo UI
Interactive demo for Financial AI Swarm
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
sys.path.append('/home/claude/financial-ai-swarm/src')

# Page configuration
st.set_page_config(
    page_title="Financial AI Swarm",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
    <style>
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    st.title("🤖 Financial AI Swarm")
    st.markdown("### Multi-Agent System for Financial Operations")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["🏠 Dashboard", "💳 Transaction Analysis", "📄 Document Processing", 
         "📊 Spend Analytics", "⚙️ System Status"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "💳 Transaction Analysis":
        show_transaction_analysis()
    elif page == "📄 Document Processing":
        show_document_processing()
    elif page == "📊 Spend Analytics":
        show_spend_analytics()
    elif page == "⚙️ System Status":
        show_system_status()


def show_dashboard():
    """Show main dashboard"""
    st.header("Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Transactions Processed", "1,234", "+12%")
    with col2:
        st.metric("Fraud Detected", "23", "+5%")
    with col3:
        st.metric("Compliance Flags", "8", "-15%")
    with col4:
        st.metric("Budget Utilization", "67%", "+3%")
    
    # Quick stats
    st.subheader("Recent Activity")
    
    # Mock recent transactions
    recent_data = pd.DataFrame({
        'Time': [(datetime.now() - timedelta(hours=i)).strftime('%H:%M') for i in range(10)],
        'Transaction': [f'TXN-{1000+i}' for i in range(10)],
        'Amount': [150, 2500, 75, 500, 12000, 250, 800, 1500, 350, 600],
        'Status': ['Approved', 'Approved', 'Approved', 'Flagged', 'Review', 'Approved', 'Approved', 'Approved', 'Approved', 'Approved']
    })
    
    st.dataframe(recent_data, use_container_width=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Transaction Volume")
        chart_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            'Count': [45, 62, 58, 71, 53]
        })
        fig = px.bar(chart_data, x='Day', y='Count', color='Count')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Distribution")
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High', 'Critical'],
            'Count': [180, 45, 12, 3]
        })
        fig = px.pie(risk_data, values='Count', names='Risk Level', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)


def show_transaction_analysis():
    """Show transaction analysis page"""
    st.header("💳 Transaction Analysis")
    
    # Input form
    with st.form("transaction_form"):
        st.subheader("Enter Transaction Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_id = st.text_input("Transaction ID", value=f"TXN-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            amount = st.number_input("Amount ($)", min_value=0.01, value=150.00, step=0.01)
            merchant = st.text_input("Merchant", value="Tech Store")
            
        with col2:
            category = st.selectbox(
                "Category",
                ["IT Services", "Travel", "Entertainment", "Consulting", "Supplies", "Training"]
            )
            user_id = st.text_input("User ID", value="EMP-001")
            location = st.text_input("Location", value="New York, NY")
        
        submitted = st.form_submit_button("Analyze Transaction", type="primary")
    
    if submitted:
        with st.spinner("Processing transaction through AI agents..."):
            # Prepare transaction data
            transaction = {
                "transaction_id": transaction_id,
                "amount": amount,
                "merchant": merchant,
                "category": category,
                "user_id": user_id,
                "location": location,
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                # Call API
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/process-transaction",
                    json=transaction,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Overall status
                    status = result['overall_status']
                    if status == "APPROVED":
                        st.success(f"✅ Transaction {status}")
                    elif status == "REJECTED":
                        st.error(f"❌ Transaction {status}")
                    else:
                        st.warning(f"⚠️ Transaction {status}")
                    
                    # Create tabs for detailed results
                    tab1, tab2, tab3 = st.tabs(["🔍 Fraud Analysis", "✓ Compliance Check", "💰 Spend Impact"])
                    
                    with tab1:
                        fraud = result['fraud_analysis']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Risk Level", fraud['risk_level'])
                        with col2:
                            st.metric("Fraud Score", f"{fraud['score']:.3f}")
                        with col3:
                            st.metric("Confidence", f"{fraud['confidence']:.2%}")
                        
                        if fraud['risk_factors']:
                            st.subheader("Risk Factors")
                            for factor in fraud['risk_factors']:
                                st.warning(f"⚠️ {factor}")
                    
                    with tab2:
                        compliance = result['compliance_check']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Status", compliance['status'])
                            st.metric("Risk Score", f"{compliance['risk_score']:.2f}")
                        with col2:
                            if compliance['sanctions_hit']:
                                st.error("🚨 SANCTIONS HIT")
                            else:
                                st.success("✅ No Sanctions")
                            
                            if compliance['pep_hit']:
                                st.warning("⚠️ PEP Match")
                            else:
                                st.success("✅ No PEP")
                        
                        if compliance['violations']:
                            st.subheader("Policy Violations")
                            for violation in compliance['violations']:
                                st.error(f"❌ {violation}")
                    
                    with tab3:
                        spend = result['spend_analysis']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Budget Utilization", f"{spend['budget_utilization']:.1%}")
                        with col2:
                            st.metric("Category", spend['category'])
                    
                    # JSON response
                    with st.expander("View Raw Response"):
                        st.json(result)
                
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"Error processing transaction: {str(e)}")
                st.info("Make sure the API server is running: `uvicorn src.api.main:app --reload`")


def show_document_processing():
    """Show document processing page"""
    st.header("📄 Document Processing")
    
    st.markdown("Upload receipts or invoices for automated processing")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        help="Upload receipt or invoice image"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Document", use_container_width=True)
        
        with col2:
            if st.button("Process Document", type="primary"):
                with st.spinner("Processing document..."):
                    try:
                        files = {"file": uploaded_file.getvalue()}
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/upload-document",
                            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.success("✅ Document processed successfully!")
                            
                            # Display extracted fields
                            st.subheader("Extracted Information")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Document Type", result.get('document_type', 'Unknown'))
                                st.metric("Merchant", result.get('merchant_name', 'Not found'))
                                st.metric("Date", result.get('date', 'Not found'))
                            
                            with col_b:
                                st.metric("Total Amount", f"${result.get('total_amount', 0):.2f}" if result.get('total_amount') else 'Not found')
                                st.metric("Tax Amount", f"${result.get('tax_amount', 0):.2f}" if result.get('tax_amount') else 'Not found')
                                st.metric("Confidence", f"{result.get('confidence_score', 0):.1%}")
                            
                            # Items table
                            if result.get('items'):
                                st.subheader("Line Items")
                                items_df = pd.DataFrame(result['items'])
                                st.dataframe(items_df, use_container_width=True)
                            
                            # Raw response
                            with st.expander("View Raw Response"):
                                st.json(result)
                        else:
                            st.error(f"Processing failed: {response.status_code}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.info("Make sure the API server is running")


def show_spend_analytics():
    """Show spend analytics page"""
    st.header("📊 Spend Analytics")
    
    # Generate sample transactions
    st.subheader("Generate Sample Data")
    
    col1, col2 = st.columns(2)
    with col1:
        num_transactions = st.slider("Number of Transactions", 10, 100, 30)
    with col2:
        period = st.selectbox("Period", ["Daily", "Weekly", "Monthly", "Quarterly"])
    
    if st.button("Generate & Analyze", type="primary"):
        with st.spinner("Analyzing spending patterns..."):
            # Generate sample transactions
            import random
            categories = ["IT Services", "Travel", "Entertainment", "Consulting", "Supplies"]
            
            transactions = []
            for i in range(num_transactions):
                transactions.append({
                    "transaction_id": f"TXN-{i:04d}",
                    "amount": random.uniform(50, 5000),
                    "merchant": f"Merchant {random.randint(1, 20)}",
                    "category": random.choice(categories),
                    "user_id": f"EMP-{random.randint(1, 50):03d}",
                    "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                })
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/spend-analysis",
                    json={"transactions": transactions},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Key metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Spend", f"${result['total_spend']:,.2f}")
                    with col2:
                        st.metric("Budget Utilization", f"{result['budget_utilization']:.1%}")
                    with col3:
                        st.metric("Anomalies Detected", len(result['anomalies']))
                    
                    # Category breakdown
                    st.subheader("Category Breakdown")
                    category_df = pd.DataFrame([
                        {"Category": k, "Amount": v}
                        for k, v in result['category_breakdown'].items()
                    ])
                    fig = px.bar(category_df, x="Category", y="Amount", color="Amount")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Trends
                    st.subheader("Spending Trends")
                    trend_info = result['trends']
                    
                    trend_emoji = "📈" if trend_info.get('trend') == 'increasing' else "📉" if trend_info.get('trend') == 'decreasing' else "➡️"
                    st.info(f"{trend_emoji} Trend: **{trend_info.get('trend', 'unknown').upper()}** ({trend_info.get('change_percentage', 0):.1f}% change)")
                    
                    # Recommendations
                    if result['recommendations']:
                        st.subheader("Recommendations")
                        for rec in result['recommendations']:
                            st.info(rec)
                    
                    # Risk areas
                    if result['risk_areas']:
                        st.subheader("Risk Areas")
                        for risk in result['risk_areas']:
                            st.warning(f"⚠️ {risk}")
                    
                    # Anomalies
                    if result['anomalies']:
                        st.subheader("Detected Anomalies")
                        anomalies_df = pd.DataFrame(result['anomalies'])
                        st.dataframe(anomalies_df, use_container_width=True)
                
                else:
                    st.error(f"Analysis failed: {response.status_code}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_system_status():
    """Show system status page"""
    st.header("⚙️ System Status")
    
    if st.button("Refresh Status", type="primary"):
        with st.spinner("Checking system status..."):
            try:
                response = requests.get(f"{API_BASE_URL}/api/v1/system/status", timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ System is operational")
                    
                    # Agent status
                    st.subheader("Agent Status")
                    
                    agents = result.get('agents', {})
                    for agent_name, agent_info in agents.items():
                        with st.expander(f"🤖 {agent_name.replace('_', ' ').title()}", expanded=True):
                            status = agent_info.get('status', 'unknown')
                            if status == 'active':
                                st.success(f"Status: {status.upper()}")
                            else:
                                st.warning(f"Status: {status.upper()}")
                            
                            # Additional info
                            for key, value in agent_info.items():
                                if key != 'status':
                                    st.write(f"**{key}:** {value}")
                    
                    # Raw response
                    with st.expander("View Raw Response"):
                        st.json(result)
                
                else:
                    st.error(f"Status check failed: {response.status_code}")
            
            except Exception as e:
                st.error(f"Cannot connect to API server: {str(e)}")
                st.info("Make sure the API server is running: `uvicorn src.api.main:app --reload --port 8000`")


# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 About")
st.sidebar.info(
    "Financial AI Swarm is a multi-agent system that combines fraud detection, "
    "compliance checking, document processing, and spend analysis."
)

st.sidebar.markdown("### 🔗 Quick Links")
st.sidebar.markdown("- [API Docs](http://localhost:8000/docs)")
st.sidebar.markdown("- [GitHub](#)")
st.sidebar.markdown("- [Documentation](#)")


if __name__ == "__main__":
    main()
