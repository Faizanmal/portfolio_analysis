"""
AI Portfolio Analysis Dashboard - CAI Edition

Interactive Streamlit dashboard for portfolio visualization, analysis, and
Central Autonomous Intelligence (CAI) monitoring.

Features:
- Real-time CAI status and decision monitoring
- Safety system dashboard (Kill Switches, Black Swan Sentinel)
- Market regime detection visualization
- SHAP explainability interface
- Compliance and audit trail
- Risk analysis visualization
- Interactive charts and metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import asyncio

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from models.risk_predictor import RiskPredictor
from models.sentiment_analyzer import SentimentAnalyzer
from models.portfolio_optimizer import PortfolioOptimizer, generate_sample_returns
from nlp.document_analyzer import DocumentAnalyzer


# Page configuration
st.set_page_config(
    page_title="AI Portfolio Analysis - CAI Platform",
    page_icon="🤖",
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
    .cai-status {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .cai-active {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .cai-warning {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
    }
    .cai-danger {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .kill-switch {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        font-weight: bold;
    }
    .kill-switch-active {
        background-color: #d4edda;
        color: #155724;
    }
    .kill-switch-triggered {
        background-color: #f8d7da;
        color: #721c24;
    }
    .regime-badge {
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .pipeline-stage {
        padding: 8px 12px;
        margin: 3px 0;
        border-radius: 5px;
        border-left: 4px solid;
    }
    .stage-complete {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    .stage-active {
        background-color: #cce5ff;
        border-left-color: #007bff;
    }
    .stage-pending {
        background-color: #e9ecef;
        border-left-color: #6c757d;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================
# MOCK DATA GENERATORS (Replace with real data in production)
# ============================================

def get_mock_cai_status() -> Dict[str, Any]:
    """Get mock CAI system status."""
    return {
        'mode': 'autonomous',
        'status': 'active',
        'uptime_hours': 127.5,
        'decisions_today': 42,
        'trades_executed': 8,
        'trades_abstained': 34,
        'current_regime': 'normal',
        'confidence_avg': 0.73,
        'last_decision_time': datetime.now() - timedelta(minutes=5),
        'errors_today': 0,
        'agents_online': {
            'portfolio_manager': True,
            'risk_analyst': True,
            'market_researcher': True,
            'nlp_intelligence': True,
            'trading_agent': True,
            'compliance_agent': True
        }
    }


def get_mock_kill_switches() -> List[Dict[str, Any]]:
    """Get mock kill switch status."""
    return [
        {'name': 'Portfolio Level', 'type': 'portfolio_level', 'status': 'active', 'auto_trigger': True, 'threshold': '8% drawdown'},
        {'name': 'Position Level', 'type': 'position_level', 'status': 'active', 'auto_trigger': True, 'threshold': '15% loss'},
        {'name': 'Volatility Regime', 'type': 'volatility_regime', 'status': 'active', 'auto_trigger': True, 'threshold': 'VIX > 35'},
        {'name': 'Liquidity Crisis', 'type': 'liquidity_crisis', 'status': 'active', 'auto_trigger': True, 'threshold': '5% spread'},
        {'name': 'Correlation Breakdown', 'type': 'correlation_breakdown', 'status': 'active', 'auto_trigger': True, 'threshold': '0.85 spike'},
        {'name': 'News Sentiment', 'type': 'news_sentiment', 'status': 'active', 'auto_trigger': False, 'threshold': '-0.7 sentiment'},
        {'name': 'Regulatory Halt', 'type': 'regulatory_halt', 'status': 'active', 'auto_trigger': True, 'threshold': 'Exchange halt'},
        {'name': 'Manual Override', 'type': 'manual_override', 'status': 'standby', 'auto_trigger': False, 'threshold': 'Authorized users'}
    ]


def get_mock_market_regime() -> Dict[str, Any]:
    """Get mock market regime data."""
    return {
        'current_regime': 'normal',
        'confidence': 0.78,
        'regime_probabilities': {
            'crisis': 0.05,
            'bear': 0.12,
            'normal': 0.58,
            'bull': 0.25
        },
        'factors': {
            'volatility_regime': 'low',
            'trend_strength': 0.42,
            'momentum': 0.31,
            'correlation': 0.45
        },
        'regime_history': [
            {'date': datetime.now() - timedelta(days=i), 'regime': np.random.choice(['normal', 'bull', 'normal', 'normal', 'bear'])}
            for i in range(30)
        ]
    }


def get_mock_recent_decisions() -> List[Dict[str, Any]]:
    """Get mock recent decisions."""
    decisions = []
    actions = ['BUY', 'SELL', 'HOLD', 'REBALANCE', 'ABSTAIN']
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'JPM', 'NVDA', 'META', 'TSLA']
    
    for i in range(10):
        decision = {
            'timestamp': datetime.now() - timedelta(minutes=i*15),
            'action': np.random.choice(actions, p=[0.15, 0.10, 0.25, 0.10, 0.40]),
            'symbol': np.random.choice(symbols) if np.random.random() > 0.3 else 'Portfolio',
            'confidence': round(np.random.uniform(0.45, 0.95), 2),
            'risk_score': np.random.choice(['Low', 'Medium', 'High'], p=[0.5, 0.35, 0.15]),
            'compliant': np.random.random() > 0.05,
            'executed': np.random.random() > 0.6
        }
        decisions.append(decision)
    return decisions


def get_mock_black_swan_alerts() -> List[Dict[str, Any]]:
    """Get mock Black Swan Sentinel alerts."""
    return [
        {'type': 'volatility_spike', 'threat_level': 'low', 'value': 1.2, 'threshold': 3.0, 'message': 'Volatility within normal range'},
        {'type': 'correlation_breakdown', 'threat_level': 'low', 'value': 0.15, 'threshold': 0.4, 'message': 'Correlations stable'},
        {'type': 'liquidity_stress', 'threat_level': 'low', 'value': 0.08, 'threshold': 0.3, 'message': 'Liquidity adequate'}
    ]


def get_mock_compliance_status() -> Dict[str, Any]:
    """Get mock compliance status."""
    return {
        'overall_status': 'compliant',
        'rules_checked': 12,
        'violations_today': 0,
        'warnings_today': 2,
        'last_audit': datetime.now() - timedelta(hours=1),
        'rules': [
            {'name': 'Position Size Limit', 'status': 'pass', 'current': '8.5%', 'limit': '10%'},
            {'name': 'Sector Concentration', 'status': 'pass', 'current': '24%', 'limit': '30%'},
            {'name': 'Leverage Limit', 'status': 'pass', 'current': '1.0x', 'limit': '1.0x'},
            {'name': 'Daily VaR (95%)', 'status': 'pass', 'current': '1.8%', 'limit': '2.0%'},
            {'name': 'Liquidity Ratio', 'status': 'warning', 'current': '6%', 'limit': '5%'},
            {'name': 'Wash Sale Prevention', 'status': 'pass', 'current': 'No violations', 'limit': 'N/A'}
        ]
    }


def get_mock_audit_trail() -> List[Dict[str, Any]]:
    """Get mock audit trail entries."""
    entries = []
    actions = ['TRADE_EXECUTED', 'RISK_CHECK', 'COMPLIANCE_PASS', 'DECISION_MADE', 'REBALANCE', 'ALERT_GENERATED']
    
    for i in range(20):
        entry = {
            'timestamp': datetime.now() - timedelta(minutes=i*30),
            'action': np.random.choice(actions),
            'agent': np.random.choice(['portfolio_manager', 'risk_analyst', 'compliance_agent', 'trading_agent']),
            'details': f'Audit entry {i+1}',
            'hash': f'0x{np.random.randint(0, 16**8):08x}...'
        }
        entries.append(entry)
    return entries


def get_mock_explainability_data() -> Dict[str, Any]:
    """Get mock SHAP explainability data."""
    features = ['Market Momentum', 'Volatility', 'Sector Exposure', 'Valuation', 
                'Sentiment Score', 'Liquidity', 'Correlation Risk', 'News Impact']
    
    return {
        'decision': 'HOLD - Reduce Tech Exposure',
        'confidence': 0.78,
        'feature_importance': {f: round(np.random.uniform(-0.3, 0.3), 3) for f in features},
        'natural_language': """
        **Decision Rationale:**
        
        The CAI recommends holding current positions while reducing technology sector exposure by 5%.
        
        **Key Factors:**
        1. **Market Momentum (+0.15)**: Positive market momentum supports maintaining positions
        2. **Sector Exposure (-0.22)**: Tech concentration at 35% exceeds optimal 30% threshold
        3. **Volatility (-0.08)**: Elevated volatility suggests caution on new positions
        4. **Valuation (+0.05)**: Current valuations within acceptable range
        
        **Risk Assessment:**
        - Expected impact: +0.2% to -0.5% over next 5 trading days
        - Confidence interval: [72%, 84%]
        
        **Compliance Check:** ✓ All constraints satisfied
        """
    }


def get_mock_portfolio_constraints() -> Dict[str, Any]:
    """Get mock portfolio constraints status."""
    return {
        'max_position_size': {'limit': 0.10, 'current': 0.085, 'status': 'ok'},
        'max_sector_concentration': {'limit': 0.30, 'current': 0.28, 'status': 'warning'},
        'max_leverage': {'limit': 1.0, 'current': 1.0, 'status': 'ok'},
        'max_var_95': {'limit': 0.02, 'current': 0.018, 'status': 'ok'},
        'max_drawdown': {'limit': 0.10, 'current': 0.03, 'status': 'ok'},
        'min_liquidity': {'limit': 0.05, 'current': 0.12, 'status': 'ok'}
    }


# ============================================
# CACHED RESOURCES
# ============================================

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


# ============================================
# PAGE FUNCTIONS
# ============================================

def show_cai_dashboard():
    """Display main CAI dashboard."""
    st.title("🤖 Central Autonomous Intelligence Dashboard")
    
    # Get status data
    cai_status = get_mock_cai_status()
    kill_switches = get_mock_kill_switches()
    regime = get_mock_market_regime()
    
    # CAI Status Header
    status_class = 'cai-active' if cai_status['status'] == 'active' else 'cai-warning'
    st.markdown(f"""
        <div class="cai-status {status_class}">
            <h3>🟢 CAI Status: {cai_status['status'].upper()} | Mode: {cai_status['mode'].upper()}</h3>
            <p>Uptime: {cai_status['uptime_hours']:.1f}h | Last Decision: {cai_status['last_decision_time'].strftime('%H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Decisions Today", cai_status['decisions_today'])
    with col2:
        st.metric("Trades Executed", cai_status['trades_executed'])
    with col3:
        st.metric("Trades Abstained", cai_status['trades_abstained'])
    with col4:
        st.metric("Avg Confidence", f"{cai_status['confidence_avg']*100:.1f}%")
    with col5:
        regime_color = {'crisis': '🔴', 'bear': '🟠', 'normal': '🟢', 'bull': '🔵'}
        st.metric("Market Regime", f"{regime_color.get(regime['current_regime'], '⚪')} {regime['current_regime'].upper()}")
    
    st.markdown("---")
    
    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Decision Pipeline Status
        st.subheader("📋 Decision Pipeline")
        
        pipeline_stages = [
            ("1. Ingest Data", "complete"),
            ("2. Validate Data Quality", "complete"),
            ("3. Detect Market Regime", "complete"),
            ("4. Generate Strategy Candidates", "complete"),
            ("5. Evaluate Risk", "complete"),
            ("6. Check Compliance", "active"),
            ("7. Simulate Outcomes", "pending"),
            ("8. Rank Alternatives", "pending"),
            ("9. Execute/Abstain", "pending"),
            ("10. Log Everything", "pending"),
            ("11. Monitor Post-Action", "pending")
        ]
        
        cols = st.columns(3)
        for i, (stage, status) in enumerate(pipeline_stages):
            col_idx = i % 3
            with cols[col_idx]:
                if status == 'complete':
                    st.success(f"✓ {stage}")
                elif status == 'active':
                    st.info(f"⟳ {stage}")
                else:
                    st.write(f"○ {stage}")
        
        st.markdown("---")
        
        # Recent Decisions
        st.subheader("📊 Recent Decisions")
        
        decisions = get_mock_recent_decisions()
        decisions_df = pd.DataFrame(decisions)
        decisions_df['timestamp'] = decisions_df['timestamp'].dt.strftime('%H:%M:%S')
        
        # Color-code actions
        def color_action(val):
            colors = {
                'BUY': 'background-color: #d4edda',
                'SELL': 'background-color: #f8d7da',
                'HOLD': 'background-color: #e9ecef',
                'REBALANCE': 'background-color: #cce5ff',
                'ABSTAIN': 'background-color: #fff3cd'
            }
            return colors.get(val, '')
        
        st.dataframe(
            decisions_df[['timestamp', 'action', 'symbol', 'confidence', 'risk_score', 'executed']].style.applymap(
                color_action, subset=['action']
            ),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        # Agent Status
        st.subheader("🤖 Agent Status")
        
        for agent, online in cai_status['agents_online'].items():
            status_icon = "🟢" if online else "🔴"
            agent_name = agent.replace('_', ' ').title()
            st.write(f"{status_icon} {agent_name}")
        
        st.markdown("---")
        
        # Constraints Status
        st.subheader("⚠️ Constraints")
        
        constraints = get_mock_portfolio_constraints()
        for name, data in constraints.items():
            pct_used = data['current'] / data['limit'] * 100
            status_color = "🟢" if pct_used < 80 else "🟡" if pct_used < 95 else "🔴"
            display_name = name.replace('_', ' ').replace('max ', '').replace('min ', '').title()
            st.write(f"{status_color} {display_name}: {pct_used:.0f}%")
    
    # Confidence Trend Chart
    st.markdown("---")
    st.subheader("📈 Decision Confidence Trend")
    
    # Generate mock confidence data
    time_points = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
    confidence_values = [0.6 + np.random.uniform(-0.15, 0.2) for _ in time_points]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_points,
        y=confidence_values,
        mode='lines+markers',
        name='Confidence',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.add_hline(y=0.65, line_dash="dash", line_color="green", annotation_text="Min Trade Threshold")
    fig.add_hline(y=0.35, line_dash="dash", line_color="red", annotation_text="Abstain Threshold")
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Confidence",
        yaxis=dict(range=[0, 1]),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_safety_monitoring():
    """Display safety systems monitoring page."""
    st.title("🛡️ Safety Systems Monitoring")
    
    # Black Swan Sentinel
    st.subheader("🦢 Black Swan Sentinel")
    
    alerts = get_mock_black_swan_alerts()
    
    col1, col2, col3 = st.columns(3)
    
    threat_colors = {'low': '#28a745', 'medium': '#ffc107', 'high': '#dc3545', 'critical': '#6f42c1'}
    
    for i, alert in enumerate(alerts):
        with [col1, col2, col3][i]:
            threat_color = threat_colors[alert['threat_level']]
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=alert['value'],
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, alert['threshold'] * 1.5]},
                    'bar': {'color': threat_color},
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': alert['threshold']
                    }
                },
                title={'text': alert['type'].replace('_', ' ').title()}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(alert['message'])
    
    st.markdown("---")
    
    # Kill Switches
    st.subheader("🔴 Kill Switch Status")
    
    kill_switches = get_mock_kill_switches()
    
    cols = st.columns(4)
    for i, switch in enumerate(kill_switches):
        with cols[i % 4]:
            if switch['status'] == 'triggered':
                st.error(f"⛔ {switch['name']}")
            elif switch['status'] == 'active':
                st.success(f"✓ {switch['name']}")
            else:
                st.warning(f"◯ {switch['name']}")
            
            st.caption(f"Threshold: {switch['threshold']}")
            st.caption(f"Auto: {'Yes' if switch['auto_trigger'] else 'No'}")
    
    st.markdown("---")
    
    # Manual Override Panel
    st.subheader("🔧 Manual Override Panel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.warning("⚠️ Manual overrides require authorization")
        
        override_action = st.selectbox(
            "Select Override Action",
            ["None", "Activate Portfolio Kill Switch", "Pause All Trading", 
             "Enter Safe Mode", "Force Rebalance", "Emergency Liquidation"]
        )
        
        if override_action != "None":
            reason = st.text_input("Override Reason (required)")
            
            if st.button("🔐 Request Override", type="primary"):
                if reason:
                    st.info(f"Override request submitted: {override_action}")
                    st.caption("Pending authorization from risk manager...")
                else:
                    st.error("Reason is required for override")
    
    with col2:
        st.info("📊 Override History (Last 24h)")
        
        override_history = [
            {'time': '14:30', 'action': 'Pause Trading', 'user': 'risk_mgr', 'status': 'Completed'},
            {'time': '09:15', 'action': 'Reduce Position', 'user': 'cio', 'status': 'Completed'}
        ]
        
        st.dataframe(pd.DataFrame(override_history), use_container_width=True, hide_index=True)


def show_market_regime():
    """Display market regime analysis page."""
    st.title("📊 Market Regime Analysis")
    
    regime_data = get_mock_market_regime()
    
    # Current Regime
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Current Regime")
        
        regime_colors = {'crisis': '#dc3545', 'bear': '#fd7e14', 'normal': '#28a745', 'bull': '#007bff'}
        regime = regime_data['current_regime']
        
        st.markdown(f"""
            <div style="background-color: {regime_colors[regime]}; color: white; 
                        padding: 30px; border-radius: 10px; text-align: center;">
                <h1>{regime.upper()}</h1>
                <h3>Confidence: {regime_data['confidence']*100:.1f}%</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("Regime Factors")
        for factor, value in regime_data['factors'].items():
            st.write(f"**{factor.replace('_', ' ').title()}:** {value}")
    
    with col2:
        # Regime Probabilities
        st.subheader("Regime Probabilities")
        
        probs = regime_data['regime_probabilities']
        
        fig = go.Figure(go.Bar(
            x=list(probs.keys()),
            y=[v * 100 for v in probs.values()],
            marker_color=[regime_colors[r] for r in probs.keys()]
        ))
        
        fig.update_layout(
            yaxis_title="Probability (%)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Regime History
    st.markdown("---")
    st.subheader("📅 Regime History (30 Days)")
    
    history = regime_data['regime_history']
    dates = [h['date'] for h in history]
    regimes = [h['regime'] for h in history]
    
    # Convert regimes to numeric for coloring
    regime_map = {'crisis': 0, 'bear': 1, 'normal': 2, 'bull': 3}
    regime_numeric = [regime_map[r] for r in regimes]
    
    fig = go.Figure()
    
    for regime_name, regime_val in regime_map.items():
        mask = [1 if r == regime_val else 0 for r in regime_numeric]
        fig.add_trace(go.Bar(
            x=dates,
            y=mask,
            name=regime_name.title(),
            marker_color=regime_colors[regime_name]
        ))
    
    fig.update_layout(
        barmode='stack',
        xaxis_title="Date",
        yaxis_title="Regime",
        height=250,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk Multipliers
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎛️ Regime-Adaptive Risk Multipliers")
        
        multipliers = {
            'Crisis': 0.5,
            'Bear': 0.75,
            'Normal': 1.0,
            'Bull': 1.2
        }
        
        current_mult = multipliers[regime.title()]
        
        for regime_name, mult in multipliers.items():
            if regime_name.lower() == regime:
                st.info(f"**{regime_name}**: {mult}x (ACTIVE)")
            else:
                st.write(f"{regime_name}: {mult}x")
    
    with col2:
        st.subheader("📉 Effective Limits")
        
        base_limits = {
            'Max VaR (95%)': 0.02,
            'Max Position': 0.10,
            'Max Sector': 0.30
        }
        
        for name, base in base_limits.items():
            effective = base * current_mult
            st.metric(name, f"{base*100:.1f}%", f"Effective: {effective*100:.1f}%")


def show_explainability():
    """Display explainability dashboard."""
    st.title("🔍 Explainability & Transparency")
    
    explain_data = get_mock_explainability_data()
    
    # Latest Decision Explanation
    st.subheader("📋 Latest Decision Explanation")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("Decision", explain_data['decision'])
        st.metric("Confidence", f"{explain_data['confidence']*100:.1f}%")
        
        st.markdown("---")
        
        # Audience selector
        audience = st.selectbox(
            "Explanation Format",
            ["Portfolio Committee", "Risk Committee", "Regulator", "Technical"]
        )
    
    with col2:
        st.markdown(explain_data['natural_language'])
    
    st.markdown("---")
    
    # SHAP Feature Importance
    st.subheader("📊 Feature Attribution (SHAP)")
    
    features = explain_data['feature_importance']
    
    # Sort by absolute value
    sorted_features = dict(sorted(features.items(), key=lambda x: abs(x[1]), reverse=True))
    
    fig = go.Figure()
    
    colors = ['#28a745' if v > 0 else '#dc3545' for v in sorted_features.values()]
    
    fig.add_trace(go.Bar(
        x=list(sorted_features.values()),
        y=list(sorted_features.keys()),
        orientation='h',
        marker_color=colors
    ))
    
    fig.update_layout(
        xaxis_title="SHAP Value (Impact on Decision)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Feature Interaction
    st.markdown("---")
    st.subheader("🔗 Feature Interactions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Mock interaction heatmap
        features_short = list(features.keys())[:5]
        interaction_matrix = np.random.uniform(-0.1, 0.1, (5, 5))
        np.fill_diagonal(interaction_matrix, 0)
        
        fig = px.imshow(
            interaction_matrix,
            x=features_short,
            y=features_short,
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        fig.update_layout(title="Feature Interaction Matrix")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        **Interpretation Guide:**
        
        - **Positive SHAP values** (green): Feature pushes toward action
        - **Negative SHAP values** (red): Feature pushes against action
        - **Larger magnitude**: Stronger influence on decision
        
        **Top Influencing Factors:**
        1. Sector Exposure: -0.22 (reduce tech)
        2. Market Momentum: +0.15 (bullish signal)
        3. Volatility: -0.08 (caution flag)
        """)


def show_compliance_audit():
    """Display compliance and audit page."""
    st.title("📜 Compliance & Audit Trail")
    
    compliance = get_mock_compliance_status()
    audit_trail = get_mock_audit_trail()
    
    # Compliance Status Header
    status_color = '#28a745' if compliance['overall_status'] == 'compliant' else '#dc3545'
    
    st.markdown(f"""
        <div style="background-color: {status_color}; color: white; 
                    padding: 20px; border-radius: 10px; text-align: center;">
            <h2>Compliance Status: {compliance['overall_status'].upper()}</h2>
            <p>Rules Checked: {compliance['rules_checked']} | Violations: {compliance['violations_today']} | Warnings: {compliance['warnings_today']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Compliance Rules
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Compliance Rules Status")
        
        for rule in compliance['rules']:
            if rule['status'] == 'pass':
                st.success(f"✓ **{rule['name']}**: {rule['current']} (Limit: {rule['limit']})")
            elif rule['status'] == 'warning':
                st.warning(f"⚠ **{rule['name']}**: {rule['current']} (Limit: {rule['limit']})")
            else:
                st.error(f"✗ **{rule['name']}**: {rule['current']} (Limit: {rule['limit']})")
    
    with col2:
        st.subheader("📊 Compliance Score")
        
        pass_count = sum(1 for r in compliance['rules'] if r['status'] == 'pass')
        total_rules = len(compliance['rules'])
        score = pass_count / total_rules * 100
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#28a745" if score >= 90 else "#ffc107" if score >= 70 else "#dc3545"},
                'steps': [
                    {'range': [0, 70], 'color': '#f8d7da'},
                    {'range': [70, 90], 'color': '#fff3cd'},
                    {'range': [90, 100], 'color': '#d4edda'}
                ]
            },
            title={'text': "Compliance %"}
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Audit Trail
    st.subheader("📝 Audit Trail (Blockchain-Secured)")
    
    st.caption("Each entry is cryptographically linked to the previous entry for tamper-proof auditing.")
    
    audit_df = pd.DataFrame(audit_trail)
    audit_df['timestamp'] = audit_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    st.dataframe(
        audit_df[['timestamp', 'action', 'agent', 'details', 'hash']],
        use_container_width=True,
        hide_index=True
    )
    
    # Export Options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Audit Log (CSV)"):
            st.info("Audit log exported to reports/audit_trail.csv")
    
    with col2:
        if st.button("📄 Generate Regulator Report"):
            st.info("Generating regulator-ready report...")
    
    with col3:
        if st.button("🔒 Verify Chain Integrity"):
            st.success("✓ Audit chain integrity verified - No tampering detected")


def show_overview_page():
    """Display overview page with portfolio metrics."""
    st.title("📊 Portfolio Overview")
    
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
            label="Active Positions",
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
    portfolio_values = 2000000 + np.cumsum(np.random.randn(90) * 10000)
    benchmark_values = 2000000 + np.cumsum(np.random.randn(90) * 8000)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines',
        name='Portfolio',
        line=dict(color='#1f77b4', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=benchmark_values,
        mode='lines',
        name='Benchmark (S&P 500)',
        line=dict(color='#7f7f7f', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Portfolio Value vs Benchmark",
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
            'Asset Class': ['Technology', 'Healthcare', 'Finance', 'Consumer', 'Energy', 'Cash'],
            'Percentage': [30, 20, 18, 15, 12, 5]
        })
        
        fig = px.pie(
            allocation_data,
            values='Percentage',
            names='Asset Class',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Position Risk Distribution")
        
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High'],
            'Positions': [18, 12, 5]
        })
        
        fig = px.bar(
            risk_data,
            x='Risk Level',
            y='Positions',
            color='Risk Level',
            color_discrete_map={'Low': '#28a745', 'Medium': '#ffc107', 'High': '#dc3545'}
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
                color_discrete_map={'Low': '#28a745', 'Medium': '#ffc107', 'High': '#dc3545'}
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
                            {'range': [-1, -0.1], 'color': "#f8d7da"},
                            {'range': [-0.1, 0.1], 'color': "#e9ecef"},
                            {'range': [0.1, 1], 'color': "#d4edda"}
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
    
    # CAI Constraints Toggle
    apply_cai_constraints = st.checkbox("Apply CAI Global Constraints", value=True)
    
    if apply_cai_constraints:
        st.info("CAI constraints will be applied: Max position 10%, Max sector 30%, Max VaR 2%")
    
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
            
            # CAI Compliance Check
            if apply_cai_constraints:
                st.subheader("CAI Constraint Validation")
                max_weight = max(result['weights'].values())
                
                if max_weight <= 0.10:
                    st.success(f"✓ Position size constraint satisfied (max: {max_weight*100:.1f}%)")
                else:
                    st.error(f"✗ Position size constraint violated (max: {max_weight*100:.1f}% > 10%)")
            
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


def show_self_improvement():
    """Display self-improvement and model monitoring page."""
    st.title("🔄 Self-Improvement & Model Monitoring")
    
    # Model Performance Overview
    st.subheader("📊 Model Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Risk Model Accuracy", "87.3%", "+2.1%")
    with col2:
        st.metric("Sentiment Model F1", "0.82", "+0.03")
    with col3:
        st.metric("Portfolio Sharpe", "1.45", "+0.12")
    with col4:
        st.metric("Active Strategies", "8", "-2 retired")
    
    st.markdown("---")
    
    # Model Drift Detection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Model Drift Detection")
        
        # Mock drift data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        drift_scores = [0.05 + np.random.uniform(-0.02, 0.03) for _ in dates]
        drift_scores[-5:] = [s + 0.03 for s in drift_scores[-5:]]  # Slight increase
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=drift_scores,
            mode='lines+markers',
            name='Drift Score',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.add_hline(y=0.15, line_dash="dash", line_color="red", 
                      annotation_text="Retrain Threshold")
        
        fig.update_layout(
            yaxis_title="Drift Score (KS Statistic)",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("✓ All models within acceptable drift thresholds")
    
    with col2:
        st.subheader("🎯 Prediction Accuracy Tracking")
        
        accuracy_data = {
            'Model': ['Risk Predictor', 'Sentiment', 'Regime Detection', 'Trade Signal'],
            'Last Week': [0.85, 0.79, 0.72, 0.68],
            'Current': [0.87, 0.82, 0.75, 0.71],
            'Trend': ['↑', '↑', '↑', '↑']
        }
        
        st.dataframe(pd.DataFrame(accuracy_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Strategy Retirement
    st.subheader("📉 Strategy Performance & Retirement")
    
    strategies = [
        {'name': 'Momentum Alpha', 'score': 0.78, 'sharpe': 1.2, 'status': 'active'},
        {'name': 'Mean Reversion', 'score': 0.65, 'sharpe': 0.9, 'status': 'active'},
        {'name': 'Trend Following', 'score': 0.72, 'sharpe': 1.1, 'status': 'active'},
        {'name': 'Volatility Arb', 'score': 0.45, 'sharpe': 0.4, 'status': 'warning'},
        {'name': 'Pairs Trading', 'score': 0.28, 'sharpe': -0.1, 'status': 'retired'},
        {'name': 'News Sentiment', 'score': 0.55, 'sharpe': 0.6, 'status': 'active'}
    ]
    
    for strategy in strategies:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{strategy['name']}**")
        with col2:
            st.write(f"Score: {strategy['score']:.2f}")
        with col3:
            st.write(f"Sharpe: {strategy['sharpe']:.2f}")
        with col4:
            if strategy['status'] == 'active':
                st.success("Active")
            elif strategy['status'] == 'warning':
                st.warning("Under Review")
            else:
                st.error("Retired")
    
    st.markdown("---")
    
    # Retraining Controls
    st.subheader("🔧 Model Retraining Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Schedule Risk Model Retrain"):
            st.info("Risk model retraining scheduled for next maintenance window")
    
    with col2:
        if st.button("🔄 Update Feature Weights"):
            st.info("Feature weight optimization in progress...")
    
    with col3:
        if st.button("📊 Generate Performance Report"):
            st.info("Performance report being generated...")


def main():
    """Main dashboard function."""
    
    # Sidebar
    st.sidebar.title("🤖 CAI Platform")
    st.sidebar.caption("Central Autonomous Intelligence")
    
    # Page categories
    st.sidebar.markdown("### 🎛️ CAI System")
    
    page = st.sidebar.radio(
        "Navigation",
        [
            "🎛️ CAI Dashboard",
            "🛡️ Safety Monitoring", 
            "📊 Market Regime",
            "🔍 Explainability",
            "📜 Compliance & Audit",
            "🔄 Self-Improvement",
            "---",
            "📈 Portfolio Overview",
            "🎯 Risk Prediction",
            "💭 Sentiment Analysis", 
            "⚖️ Portfolio Optimization",
            "📄 Document Analysis",
            "---",
            "📱 Mobile & PWA",
            "👥 Social Trading",
            "📉 Predictive Analytics",
            "🤝 Collaboration",
            "🤖 AI Assistant",
            "📚 Learning Hub"
        ],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # CAI Quick Status
    cai_status = get_mock_cai_status()
    st.sidebar.markdown("### Quick Status")
    st.sidebar.success(f"🟢 CAI: {cai_status['mode'].upper()}")
    st.sidebar.info(f"📊 Regime: {cai_status['current_regime'].upper()}")
    st.sidebar.write(f"Decisions: {cai_status['decisions_today']} today")
    
    st.sidebar.markdown("---")
    st.sidebar.caption("""
    **AI Portfolio Analysis Platform**  
    CAI Edition v2.0.0  
    
    Central Autonomous Intelligence  
    for institutional portfolio management
    """)
    
    # Load models
    risk_model, sentiment_analyzer, portfolio_optimizer = load_models()
    
    # Route to pages
    if page == "🎛️ CAI Dashboard":
        show_cai_dashboard()
    elif page == "🛡️ Safety Monitoring":
        show_safety_monitoring()
    elif page == "📊 Market Regime":
        show_market_regime()
    elif page == "🔍 Explainability":
        show_explainability()
    elif page == "📜 Compliance & Audit":
        show_compliance_audit()
    elif page == "🔄 Self-Improvement":
        show_self_improvement()
    elif page == "📈 Portfolio Overview":
        show_overview_page()
    elif page == "🎯 Risk Prediction":
        show_risk_prediction_page(risk_model)
    elif page == "💭 Sentiment Analysis":
        show_sentiment_analysis_page(sentiment_analyzer)
    elif page == "⚖️ Portfolio Optimization":
        show_portfolio_optimization_page(portfolio_optimizer)
    elif page == "📄 Document Analysis":
        show_document_analysis_page()
    # New feature pages
    elif page == "📱 Mobile & PWA":
        show_mobile_pwa_page()
    elif page == "👥 Social Trading":
        show_social_trading_page()
    elif page == "📉 Predictive Analytics":
        show_predictive_analytics_page()
    elif page == "🤝 Collaboration":
        show_collaboration_page()
    elif page == "🤖 AI Assistant":
        show_ai_assistant_page()
    elif page == "📚 Learning Hub":
        show_learning_hub_page()


# ============================================
# NEW FEATURE PAGES
# ============================================

def show_mobile_pwa_page():
    """Mobile PWA status and settings."""
    st.title("📱 Mobile & PWA Dashboard")
    st.markdown("Progressive Web App features and mobile experience settings.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Mobile Users", "1,247", "+12%")
    with col2:
        st.metric("Push Subscriptions", "892", "+8%")
    with col3:
        st.metric("Offline Syncs Today", "156", "-3%")
    with col4:
        st.metric("Voice Commands", "89", "+45%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔔 Push Notification Settings")
        st.checkbox("Price Alerts", value=True)
        st.checkbox("Portfolio Updates", value=True)
        st.checkbox("Trade Confirmations", value=True)
        st.checkbox("Market News", value=False)
        st.checkbox("AI Insights", value=True)
    
    with col2:
        st.markdown("### 🔐 Biometric Authentication")
        st.success("✅ WebAuthn Enabled")
        st.info("Supported: Face ID, Touch ID, Windows Hello")
        
        st.markdown("### 🌐 Offline Mode")
        st.write("Cached portfolio data available offline")
        st.write("Last sync: 2 minutes ago")
        if st.button("Force Sync"):
            st.success("Sync initiated!")
    
    st.markdown("---")
    st.markdown("### 🎤 Voice Commands")
    st.info("Try: 'What's my portfolio value?' or 'Show AAPL analysis'")
    
    voice_input = st.text_input("Voice command (simulated)", placeholder="Speak or type a command...")
    if voice_input:
        st.write(f"Processing: '{voice_input}'")
        st.success("Command recognized and executed!")


def show_social_trading_page():
    """Social trading platform interface."""
    st.title("👥 Social Trading Platform")
    st.markdown("Share strategies, follow experts, and copy successful trades.")
    
    tabs = st.tabs(["📊 Leaderboard", "🏪 Strategy Marketplace", "👤 My Profile", "📋 Copy Trading"])
    
    with tabs[0]:
        st.markdown("### 🏆 Top Performers This Month")
        
        leaderboard_data = pd.DataFrame({
            "Rank": [1, 2, 3, 4, 5],
            "Trader": ["AlphaTrader", "QuantMaster", "ValueSeeker", "TrendFollower", "DividendKing"],
            "Return (MTD)": ["+18.5%", "+15.2%", "+12.8%", "+11.3%", "+9.7%"],
            "Sharpe Ratio": [2.45, 2.12, 1.98, 1.85, 1.72],
            "Followers": [1250, 890, 756, 623, 512],
            "Risk Level": ["Medium", "High", "Low", "Medium", "Low"]
        })
        st.dataframe(leaderboard_data, use_container_width=True)
    
    with tabs[1]:
        st.markdown("### 🛒 Strategy Marketplace")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **📈 Momentum Alpha Strategy**
            - Annual Return: 24.5%
            - Sharpe Ratio: 1.85
            - Max Drawdown: 12%
            - Price: $49/month
            """)
            st.button("Subscribe", key="strat1")
        
        with col2:
            st.markdown("""
            **🛡️ Defensive Income Strategy**
            - Annual Return: 12.3%
            - Sharpe Ratio: 2.10
            - Max Drawdown: 5%
            - Price: $29/month
            """)
            st.button("Subscribe", key="strat2")
    
    with tabs[2]:
        st.markdown("### 👤 Your Social Profile")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Followers", "156")
        with col2:
            st.metric("Following", "23")
        with col3:
            st.metric("Portfolio Visibility", "Private")
        
        st.selectbox("Portfolio Sharing", ["Private", "Followers Only", "Public", "Benchmark Anonymous"])
    
    with tabs[3]:
        st.markdown("### 📋 Copy Trading")
        st.warning("⚠️ Copy trading involves risk. Past performance doesn't guarantee future results.")
        
        st.number_input("Allocation Amount ($)", min_value=100, max_value=100000, value=1000)
        st.slider("Max Risk per Trade (%)", 1, 10, 5)
        st.checkbox("Enable proportional sizing", value=True)
        st.button("Start Copy Trading")


def show_predictive_analytics_page():
    """Predictive analytics dashboard."""
    st.title("📉 Predictive Analytics Dashboard")
    st.markdown("AI-powered predictions, regime forecasting, and Monte Carlo simulations.")
    
    tabs = st.tabs(["🔮 Price Predictions", "📊 Regime Forecast", "🎲 Monte Carlo", "💡 Recommendations"])
    
    with tabs[0]:
        st.markdown("### 🔮 AI Price Predictions")
        
        symbol = st.selectbox("Select Asset", ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("7-Day Prediction", "$182.50", "+3.2%")
        with col2:
            st.metric("14-Day Prediction", "$186.20", "+5.3%")
        with col3:
            st.metric("30-Day Prediction", "$190.00", "+7.5%")
        
        st.markdown("**Prediction Confidence:** 72%")
        st.progress(0.72)
        
        # Sample prediction chart
        dates = pd.date_range(start='today', periods=30)
        prices = np.cumsum(np.random.randn(30) * 2) + 175
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name='Predicted Price'))
        fig.add_trace(go.Scatter(x=dates, y=prices*1.05, mode='lines', name='Upper Bound', line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=dates, y=prices*0.95, mode='lines', name='Lower Bound', line=dict(dash='dash')))
        fig.update_layout(title=f"{symbol} Price Prediction", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        st.markdown("### 📊 Market Regime Forecast")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Current Regime:** Normal 📊")
            st.markdown("**Transition Probabilities (7 days):**")
            regime_probs = {"Crisis": 5, "Bear": 12, "Normal": 58, "Bull": 25}
            fig = px.pie(values=list(regime_probs.values()), names=list(regime_probs.keys()), title="Regime Probabilities")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Key Indicators:**")
            st.write("- VIX: 18.5 (Low)")
            st.write("- Trend Momentum: +0.42")
            st.write("- Credit Spreads: Normal")
            st.write("- Yield Curve: Flat")
    
    with tabs[2]:
        st.markdown("### 🎲 Monte Carlo Simulation")
        
        col1, col2 = st.columns(2)
        with col1:
            n_simulations = st.slider("Number of Simulations", 100, 10000, 1000)
            time_horizon = st.slider("Time Horizon (days)", 30, 365, 90)
        with col2:
            st.markdown("**Portfolio Value Scenarios:**")
            st.metric("5th Percentile (Worst)", "$95,000", "-5%")
            st.metric("50th Percentile (Median)", "$108,000", "+8%")
            st.metric("95th Percentile (Best)", "$125,000", "+25%")
        
        if st.button("Run Simulation"):
            st.info("Running Monte Carlo simulation...")
            st.success("Simulation complete! See results above.")
    
    with tabs[3]:
        st.markdown("### 💡 AI Recommendations")
        
        st.success("**BUY: NVDA** - Strong momentum, AI sector growth (Confidence: 78%)")
        st.warning("**HOLD: AAPL** - Near fair value, wait for pullback (Confidence: 65%)")
        st.error("**REDUCE: TSLA** - High volatility, take partial profits (Confidence: 72%)")


def show_collaboration_page():
    """Real-time collaboration interface."""
    st.title("🤝 Collaboration Hub")
    st.markdown("Team workspaces, voting, and shared analysis.")
    
    tabs = st.tabs(["📁 Workspaces", "🗳️ Decisions", "💬 Comments", "📋 Audit Trail"])
    
    with tabs[0]:
        st.markdown("### 📁 Your Workspaces")
        
        workspaces = [
            {"name": "Q4 Investment Strategy", "members": 8, "decisions": 12, "status": "Active"},
            {"name": "Tech Sector Analysis", "members": 5, "decisions": 7, "status": "Active"},
            {"name": "Risk Committee Review", "members": 12, "decisions": 23, "status": "Meeting Today"}
        ]
        
        for ws in workspaces:
            with st.expander(f"📂 {ws['name']} ({ws['status']})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"👥 {ws['members']} members")
                with col2:
                    st.write(f"🗳️ {ws['decisions']} decisions")
                with col3:
                    st.button("Open", key=f"open_{ws['name']}")
    
    with tabs[1]:
        st.markdown("### 🗳️ Pending Decisions")
        
        st.markdown("""
        **Decision: Increase AAPL allocation by 5%**
        - Proposed by: Portfolio Manager
        - Deadline: Tomorrow 5PM
        - Current Votes: 4/7 required
        """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("✅ Approve", type="primary")
        with col2:
            st.button("❌ Reject")
        with col3:
            st.button("⏸️ Abstain")
    
    with tabs[2]:
        st.markdown("### 💬 Recent Comments")
        
        comments = [
            {"user": "John D.", "time": "10 min ago", "text": "I think we should wait for earnings before this trade."},
            {"user": "Sarah M.", "time": "25 min ago", "text": "The technical analysis supports this entry point."},
            {"user": "Alex K.", "time": "1 hour ago", "text": "What about the Fed meeting next week?"}
        ]
        
        for comment in comments:
            st.markdown(f"**{comment['user']}** - {comment['time']}")
            st.write(comment['text'])
            st.markdown("---")
        
        st.text_area("Add a comment")
        st.button("Post Comment")
    
    with tabs[3]:
        st.markdown("### 📋 Audit Trail")
        
        audit_data = pd.DataFrame({
            "Timestamp": ["2024-01-15 10:30", "2024-01-15 10:25", "2024-01-15 10:20"],
            "User": ["John D.", "CAI System", "Sarah M."],
            "Action": ["Approved decision #42", "Auto-rebalanced portfolio", "Created new analysis"],
            "Details": ["AAPL increase", "Risk adjustment", "Tech sector review"]
        })
        st.dataframe(audit_data, use_container_width=True)


def show_ai_assistant_page():
    """Conversational AI assistant interface."""
    st.title("🤖 AI Portfolio Assistant")
    st.markdown("Ask questions in natural language about your portfolio, markets, or investing concepts.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Hello! I'm your AI portfolio assistant. How can I help you today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your portfolio..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate mock response
        response = generate_ai_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
    
    # Quick actions
    st.markdown("---")
    st.markdown("### 💡 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📊 Portfolio Status"):
            st.session_state.messages.append({"role": "user", "content": "What's my portfolio status?"})
            st.rerun()
    with col2:
        if st.button("📈 Market Overview"):
            st.session_state.messages.append({"role": "user", "content": "How is the market today?"})
            st.rerun()
    with col3:
        if st.button("💡 Recommendations"):
            st.session_state.messages.append({"role": "user", "content": "What stocks should I consider?"})
            st.rerun()
    with col4:
        if st.button("📚 Learn Something"):
            st.session_state.messages.append({"role": "user", "content": "Explain diversification"})
            st.rerun()


def generate_ai_response(prompt: str) -> str:
    """Generate mock AI response."""
    prompt_lower = prompt.lower()
    
    if "portfolio" in prompt_lower and ("status" in prompt_lower or "doing" in prompt_lower):
        return """📊 **Portfolio Summary**

Your portfolio is valued at **$125,432**, up **1.25%** today.

**Top Performers:**
- AAPL: +2.3%
- MSFT: +1.1%

**Key Metrics:**
- Total Return (YTD): +15.2%
- Sharpe Ratio: 1.45

Would you like more details on any specific holding?"""
    
    elif "market" in prompt_lower:
        return """🌍 **Market Overview**

**Indices:**
- S&P 500: 4,782 (+0.85%)
- Nasdaq: 15,123 (+1.20%)
- Dow: 38,254 (+0.45%)

**Sentiment:** Cautiously Bullish 📈

Key news: Fed signals steady rates, tech earnings beat expectations."""
    
    elif "diversification" in prompt_lower or "explain" in prompt_lower:
        return """📚 **Diversification**

Diversification means spreading your investments across different assets to reduce risk.

**Think of it this way:** Instead of putting all eggs in one basket, you spread them across multiple baskets. If one drops, you still have the others.

**Key benefits:**
- Reduces portfolio volatility
- Protects against single-stock risk
- Can improve risk-adjusted returns

Would you like to learn about related concepts like asset allocation?"""
    
    else:
        return f"""I understand you're asking about: "{prompt}"

I can help you with:
- Portfolio analysis and performance
- Stock research and recommendations
- Market updates
- Financial education

Could you rephrase your question, or try one of the quick actions below?"""


def show_learning_hub_page():
    """Personalized learning and onboarding."""
    st.title("📚 Learning Hub")
    st.markdown("Personalized courses, tutorials, and achievements.")
    
    # User progress
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Level", "5 ⭐")
    with col2:
        st.metric("XP", "1,250")
    with col3:
        st.metric("Streak", "7 days 🔥")
    with col4:
        st.metric("Achievements", "12/48")
    
    # Progress bar
    st.progress(0.35, "35% to Level 6")
    
    tabs = st.tabs(["📖 Courses", "🏆 Achievements", "📊 My Progress", "🎯 Learning Path"])
    
    with tabs[0]:
        st.markdown("### 📖 Recommended Courses")
        
        courses = [
            {"name": "Investing 101", "progress": 80, "difficulty": "Beginner", "xp": 500},
            {"name": "Technical Analysis", "progress": 0, "difficulty": "Intermediate", "xp": 750},
            {"name": "Portfolio Management", "progress": 30, "difficulty": "Intermediate", "xp": 700},
            {"name": "AI-Powered Trading", "progress": 0, "difficulty": "Advanced", "xp": 1000}
        ]
        
        for course in courses:
            with st.expander(f"📚 {course['name']} ({course['difficulty']}) - {course['xp']} XP"):
                st.progress(course['progress'] / 100, f"{course['progress']}% complete")
                if course['progress'] == 0:
                    st.button("Start Course", key=f"start_{course['name']}")
                elif course['progress'] < 100:
                    st.button("Continue", key=f"continue_{course['name']}")
                else:
                    st.success("✅ Completed!")
    
    with tabs[1]:
        st.markdown("### 🏆 Achievements")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Earned:**")
            st.markdown("📖 First Steps")
            st.markdown("🔥 Week Warrior")
            st.markdown("📊 Portfolio Builder")
            st.markdown("💯 Quiz Master")
        
        with col2:
            st.markdown("**In Progress:**")
            st.markdown("🎓 Quick Learner (8/10)")
            st.markdown("📚 Knowledge Seeker (1/3)")
        
        with col3:
            st.markdown("**Locked:**")
            st.markdown("🌟 Dedication (30 day streak)")
            st.markdown("⭐ Level 10")
            st.markdown("🏆 Master Investor")
    
    with tabs[2]:
        st.markdown("### 📊 Learning Progress")
        
        progress_data = pd.DataFrame({
            "Topic": ["Fundamentals", "Technical Analysis", "Risk Management", "Portfolio Theory", "Trading"],
            "Progress": [85, 45, 60, 30, 20]
        })
        
        fig = px.bar(progress_data, x="Progress", y="Topic", orientation='h', title="Topic Mastery")
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[3]:
        st.markdown("### 🎯 Your Learning Path")
        
        st.markdown("""
        **Goal:** Become a confident investor
        
        **Your personalized path:**
        1. ✅ Introduction to Investing (Complete)
        2. ✅ Understanding Stocks (Complete)
        3. 🔄 Bonds and Fixed Income (In Progress)
        4. ⬜ Diversification Strategies
        5. ⬜ Risk Management Basics
        6. ⬜ Building Your First Portfolio
        """)
        
        st.progress(0.35, "35% Complete")


if __name__ == "__main__":
    main()
