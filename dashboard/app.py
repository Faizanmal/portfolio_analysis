"""
AI Portfolio Analysis Dashboard

Interactive Streamlit dashboard for portfolio visualization and analysis.

Features:
- Real-time portfolio performance monitoring
- Risk analysis visualization
- Interactive charts and metrics
- Model prediction interface
- Document upload and analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
from datetime import datetime

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from models.risk_predictor import RiskPredictor
from models.sentiment_analyzer import SentimentAnalyzer
from models.portfolio_optimizer import PortfolioOptimizer, generate_sample_returns
from nlp.document_analyzer import DocumentAnalyzer


# Page configuration
st.set_page_config(
    page_title="AI Portfolio Analysis Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def load_models():
    """Load all ML models."""
    try:
        risk_model = RiskPredictor()
        model_path = Path("data/models/risk_predictor.pkl")
        if model_path.exists():
            risk_model.load_model()
        
        sentiment_analyzer = SentimentAnalyzer()
        portfolio_optimizer = PortfolioOptimizer()
        
        return risk_model, sentiment_analyzer, portfolio_optimizer
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        return None, None, None


def show_overview_page():
    """Display overview page."""
    st.title("📊 Portfolio Analysis Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Portfolio Value",
            value="$2.5M",
            delta="5.2%"
        )
    
    with col2:
        st.metric(
            label="Total Return (YTD)",
            value="12.5%",
            delta="2.3%"
        )
    
    with col3:
        st.metric(
            label="Active Investments",
            value="35",
            delta="4"
        )
    
    with col4:
        st.metric(
            label="Risk Level",
            value="Medium",
            delta="-5%"
        )
    
    st.markdown("---")
    
    # Portfolio performance chart
    st.subheader("📈 Portfolio Performance")
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    portfolio_values = 1000000 + (dates - dates[0]).days * 10000 + pd.Series(range(90)).apply(lambda x: x * 100)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Asset allocation
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥧 Asset Allocation")
        
        allocation_data = pd.DataFrame({
            'Asset Class': ['Stocks', 'Bonds', 'Real Estate', 'Commodities', 'Cash'],
            'Percentage': [45, 25, 15, 10, 5]
        })
        
        fig = px.pie(
            allocation_data,
            values='Percentage',
            names='Asset Class',
            hole=0.4
        )
        
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Risk Distribution")
        
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High'],
            'Companies': [12, 18, 5]
        })
        
        fig = px.bar(
            risk_data,
            x='Risk Level',
            y='Companies',
            color='Risk Level',
            color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        )
        
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def show_risk_prediction_page(risk_model):
    """Display risk prediction page."""
    st.title("🎯 Risk Prediction")
    
    st.markdown("""
    Enter company financial data to predict risk level using our AI model.
    The model analyzes multiple financial ratios and metrics to classify risk.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Financial Inputs")
        
        revenue = st.number_input("Revenue ($)", min_value=0, value=50000000, step=1000000)
        cogs = st.number_input("Cost of Goods Sold ($)", min_value=0, value=30000000, step=1000000)
        net_income = st.number_input("Net Income ($)", value=5000000, step=100000)
        total_assets = st.number_input("Total Assets ($)", min_value=0, value=100000000, step=1000000)
        total_debt = st.number_input("Total Debt ($)", min_value=0, value=30000000, step=1000000)
        total_equity = st.number_input("Total Equity ($)", min_value=0, value=70000000, step=1000000)
    
    with col2:
        st.subheader("Additional Metrics")
        
        current_assets = st.number_input("Current Assets ($)", min_value=0, value=40000000, step=1000000)
        current_liabilities = st.number_input("Current Liabilities ($)", min_value=0, value=20000000, step=1000000)
        cash = st.number_input("Cash ($)", min_value=0, value=15000000, step=1000000)
        inventory = st.number_input("Inventory ($)", min_value=0, value=5000000, step=1000000)
    
    if st.button("🔍 Predict Risk", type="primary"):
        if risk_model and risk_model.model:
            # Create DataFrame
            data = pd.DataFrame([{
                'company_id': 1,
                'revenue': revenue,
                'cogs': cogs,
                'net_income': net_income,
                'total_assets': total_assets,
                'total_debt': total_debt,
                'total_equity': total_equity,
                'current_assets': current_assets,
                'current_liabilities': current_liabilities,
                'cash': cash,
                'inventory': inventory
            }])
            
            # Predict
            prediction = risk_model.predict(data)[0]
            probabilities = risk_model.predict_proba(data)[0]
            
            st.markdown("---")
            st.subheader("Prediction Results")
            
            # Risk level
            col1, col2, col3 = st.columns(3)
            
            with col2:
                if prediction == 'Low':
                    st.success(f"### Risk Level: {prediction}")
                elif prediction == 'Medium':
                    st.warning(f"### Risk Level: {prediction}")
                else:
                    st.error(f"### Risk Level: {prediction}")
            
            # Probabilities
            st.subheader("Confidence Scores")
            
            classes = risk_model.model.classes_
            prob_df = pd.DataFrame({
                'Risk Level': classes,
                'Probability': probabilities * 100
            })
            
            fig = px.bar(
                prob_df,
                x='Risk Level',
                y='Probability',
                color='Risk Level',
                color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'}
            )
            
            fig.update_layout(yaxis_title="Probability (%)", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("Risk model not loaded. Please train the model first.")


def show_sentiment_analysis_page(sentiment_analyzer):
    """Display sentiment analysis page."""
    st.title("💭 Sentiment Analysis")
    
    st.markdown("""
    Analyze the sentiment of financial news, reports, and documents using our AI-powered
    sentiment analyzer based on FinBERT and advanced NLP models.
    """)
    
    # Text input
    text_input = st.text_area(
        "Enter text to analyze:",
        height=200,
        placeholder="Paste financial news, earnings reports, or any text here..."
    )
    
    extract_entities = st.checkbox("Extract Named Entities", value=True)
    
    if st.button("🔍 Analyze Sentiment", type="primary"):
        if text_input and sentiment_analyzer:
            with st.spinner("Analyzing..."):
                # Analyze sentiment
                result = sentiment_analyzer.analyze_sentiment(text_input)
                
                # Extract entities
                entities = None
                if extract_entities:
                    entities = sentiment_analyzer.extract_entities(text_input)
                
                st.markdown("---")
                st.subheader("Analysis Results")
                
                # Sentiment score
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Sentiment", result['finbert_label'].upper())
                
                with col2:
                    st.metric("Confidence", f"{result['finbert_score']*100:.1f}%")
                
                with col3:
                    st.metric("Compound Score", f"{result['compound_score']:.3f}")
                
                # Sentiment gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result['compound_score'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [-1, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [-1, -0.1], 'color': "lightcoral"},
                            {'range': [-0.1, 0.1], 'color': "lightgray"},
                            {'range': [0.1, 1], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0
                        }
                    },
                    title={'text': "Sentiment Score"}
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # Entities
                if entities:
                    st.subheader("Extracted Entities")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if entities.get('organizations'):
                            st.write("**Organizations:**")
                            for org in entities['organizations']:
                                st.write(f"- {org}")
                        
                        if entities.get('people'):
                            st.write("**People:**")
                            for person in entities['people']:
                                st.write(f"- {person}")
                    
                    with col2:
                        if entities.get('money'):
                            st.write("**Monetary Values:**")
                            for money in entities['money']:
                                st.write(f"- {money}")
                        
                        if entities.get('dates'):
                            st.write("**Dates:**")
                            for date in entities['dates']:
                                st.write(f"- {date}")
        else:
            st.warning("Please enter text to analyze")


def show_portfolio_optimization_page(portfolio_optimizer):
    """Display portfolio optimization page."""
    st.title("⚖️ Portfolio Optimization")
    
    st.markdown("""
    Optimize your portfolio allocation using modern portfolio theory.
    Choose from multiple optimization strategies.
    """)
    
    # Sample data option
    use_sample = st.checkbox("Use Sample Data", value=True)
    
    if use_sample:
        # Generate sample returns
        returns_df = generate_sample_returns(n_assets=5, n_periods=252)
        st.success("Using sample portfolio data (5 assets, 252 trading days)")
    else:
        st.info("Upload your own returns data (CSV format)")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file:
            returns_df = pd.read_csv(uploaded_file)
        else:
            st.warning("Please upload a CSV file or use sample data")
            return
    
    # Optimization method
    opt_method = st.selectbox(
        "Optimization Method",
        ["Maximum Sharpe Ratio", "Minimum Volatility", "Risk Parity"]
    )
    
    if st.button("🎯 Optimize Portfolio", type="primary"):
        with st.spinner("Optimizing..."):
            portfolio_optimizer.load_data(returns_df)
            
            # Run optimization
            if opt_method == "Maximum Sharpe Ratio":
                result = portfolio_optimizer.optimize_max_sharpe()
            elif opt_method == "Minimum Volatility":
                result = portfolio_optimizer.optimize_min_volatility()
            else:
                result = portfolio_optimizer.risk_parity_optimization()
            
            st.markdown("---")
            st.subheader("Optimization Results")
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Expected Return", f"{result['metrics']['return']*100:.2f}%")
            
            with col2:
                st.metric("Volatility", f"{result['metrics']['volatility']*100:.2f}%")
            
            with col3:
                st.metric("Sharpe Ratio", f"{result['metrics']['sharpe_ratio']:.3f}")
            
            # Weights
            st.subheader("Optimal Allocation")
            
            weights_df = pd.DataFrame({
                'Asset': list(result['weights'].keys()),
                'Weight': [v * 100 for v in result['weights'].values()]
            })
            
            fig = px.bar(
                weights_df,
                x='Asset',
                y='Weight',
                color='Weight',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(yaxis_title="Weight (%)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show table
            st.dataframe(weights_df.style.format({'Weight': '{:.2f}%'}))


def show_document_analysis_page():
    """Display document analysis page."""
    st.title("📄 Document Analysis")
    
    st.markdown("""
    Upload financial documents for AI-powered analysis and insights extraction.
    Supports PDF, DOCX, and TXT formats.
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'docx', 'txt']
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Save uploaded file
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / uploaded_file.name
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("🔍 Analyze Document", type="primary"):
            with st.spinner("Analyzing document..."):
                analyzer = DocumentAnalyzer()
                
                # Load document
                text = analyzer.load_document(str(file_path))
                
                st.subheader("Document Summary")
                summary = analyzer.summarize_document(text, max_length=300)
                st.info(summary)
                
                # Extract metrics
                st.subheader("Financial Metrics")
                metrics = analyzer.extract_financial_metrics(text)
                st.json(metrics)
                
                # Q&A
                st.subheader("Ask Questions")
                question = st.text_input("Enter your question about the document:")
                
                if question:
                    answer = analyzer.answer_question(text, question)
                    st.write(f"**Answer:** {answer}")


def main():
    """Main dashboard function."""
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["📊 Overview", "🎯 Risk Prediction", "💭 Sentiment Analysis", 
         "⚖️ Portfolio Optimization", "📄 Document Analysis"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **AI Portfolio Analysis Platform**
    
    This dashboard demonstrates:
    - ML-powered risk prediction
    - Sentiment analysis
    - Portfolio optimization
    - Document analysis with LLMs
    """)
    
    # Load models
    risk_model, sentiment_analyzer, portfolio_optimizer = load_models()
    
    # Route to pages
    if page == "📊 Overview":
        show_overview_page()
    elif page == "🎯 Risk Prediction":
        show_risk_prediction_page(risk_model)
    elif page == "💭 Sentiment Analysis":
        show_sentiment_analysis_page(sentiment_analyzer)
    elif page == "⚖️ Portfolio Optimization":
        show_portfolio_optimization_page(portfolio_optimizer)
    elif page == "📄 Document Analysis":
        show_document_analysis_page()


if __name__ == "__main__":
    main()
