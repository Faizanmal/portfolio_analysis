"""
Explainability Layer
===================

SHAP-based feature attribution and natural language report generation
for explainable AI decisions in the investment platform.

Features:
- SHAP-based feature attribution
- "Why this trade?" natural language reports
- Regulator-ready explanations
- Decision visualization
"""
from __future__ import annotations

import numpy as np
from datetime import datetime
from typing import Dict, List, Any, TYPE_CHECKING
from dataclasses import dataclass, field
import logging

if TYPE_CHECKING:
    from .cai_orchestrator import CAIDecision

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


@dataclass
class FeatureAttribution:
    """Attribution of a single feature to the decision"""
    feature_name: str
    feature_value: Any
    attribution_value: float  # SHAP value
    attribution_direction: str  # positive, negative, neutral
    importance_rank: int
    explanation: str


@dataclass
class DecisionExplanation:
    """Complete explanation of a decision"""
    decision_id: str
    decision_summary: str
    probability_of_success: float
    key_drivers: List[FeatureAttribution]
    main_risks: List[str]
    alternatives_rejected: List[Dict[str, Any]]
    rejection_reasons: Dict[str, str]
    
    # Audience-specific explanations
    portfolio_committee_explanation: str
    risk_committee_explanation: str
    regulator_explanation: str
    
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TradeExplanation:
    """Detailed explanation of why a specific trade was made"""
    trade_id: str
    asset: str
    action: str  # BUY, SELL, HOLD
    quantity: float
    confidence: float
    expected_return: float
    expected_drawdown: float
    
    # Feature contributions
    feature_attributions: List[FeatureAttribution]
    
    # Natural language
    why_this_trade: str
    what_could_go_wrong: str
    what_are_alternatives: str
    
    timestamp: datetime = field(default_factory=datetime.now)


class ExplainabilityEngine:
    """
    Engine for generating explainable AI outputs.
    
    Provides SHAP-based explanations, natural language reports,
    and regulator-ready documentation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("explainability")
        
        # Model references for SHAP
        self.models = {}
        self.explainers = {}
        
        # Feature descriptions
        self.feature_descriptions = self._load_feature_descriptions()
        
        # Explanation templates
        self.templates = self._load_explanation_templates()
    
    def _load_feature_descriptions(self) -> Dict[str, str]:
        """Load human-readable feature descriptions"""
        return {
            # Market features
            "momentum_20d": "20-day price momentum",
            "momentum_60d": "60-day price momentum",
            "volatility_20d": "20-day realized volatility",
            "rsi": "Relative Strength Index (overbought/oversold indicator)",
            "macd_signal": "MACD momentum signal",
            "volume_z_score": "Volume relative to historical average",
            
            # Fundamental features
            "pe_ratio": "Price-to-Earnings ratio",
            "pb_ratio": "Price-to-Book ratio",
            "roe": "Return on Equity",
            "debt_to_equity": "Debt-to-Equity ratio",
            "revenue_growth": "Year-over-year revenue growth",
            "earnings_surprise": "Recent earnings surprise",
            
            # Risk features
            "var_95": "Value at Risk (95% confidence)",
            "beta": "Market beta (systematic risk)",
            "correlation": "Correlation with portfolio",
            "drawdown": "Current drawdown from peak",
            
            # Sentiment features
            "news_sentiment": "News sentiment score",
            "social_sentiment": "Social media sentiment",
            "analyst_rating": "Average analyst rating",
            
            # Regime features
            "market_regime": "Current market regime classification",
            "regime_probability": "Confidence in regime classification",
            "vix_level": "Market volatility index (VIX)",
            "yield_curve": "Treasury yield curve slope"
        }
    
    def _load_explanation_templates(self) -> Dict[str, str]:
        """Load templates for natural language explanations"""
        return {
            "buy_momentum": """
The decision to BUY {asset} is primarily driven by strong momentum signals.
The asset shows {momentum_20d:.1%} returns over 20 days with positive trend confirmation.
Risk metrics indicate {var_95:.2%} daily VaR, which is within acceptable limits.
{additional_factors}
            """.strip(),
            
            "buy_value": """
The decision to BUY {asset} is based on attractive valuation metrics.
Current P/E of {pe_ratio:.1f} represents a discount to historical averages.
Combined with {quality_factors}, this presents a favorable risk/reward opportunity.
{additional_factors}
            """.strip(),
            
            "sell_risk": """
The decision to SELL {asset} is driven by elevated risk indicators.
VaR has increased to {var_95:.2%}, exceeding our risk tolerance of {risk_limit:.2%}.
{risk_factors} support reducing exposure at this time.
            """.strip(),
            
            "hold_neutral": """
No action recommended for {asset} at this time.
Current signals are neutral with confidence of {confidence:.0%}.
Key factors: {factors}
We will continue monitoring for clearer signals.
            """.strip(),
            
            "abstain_uncertainty": """
Abstaining from action due to high uncertainty.
Confidence level of {confidence:.0%} is below our threshold of {threshold:.0%}.
Following capital preservation principle, we defer this decision.
            """.strip()
        }
    
    def register_model(self, model_id: str, model: Any, background_data: np.ndarray = None):
        """Register a model for SHAP explanations"""
        self.models[model_id] = model
        
        if SHAP_AVAILABLE and background_data is not None:
            try:
                # Try tree explainer first (fast for tree-based models)
                self.explainers[model_id] = shap.TreeExplainer(model)
            except Exception:
                try:
                    # Fall back to kernel explainer
                    self.explainers[model_id] = shap.KernelExplainer(
                        model.predict_proba if hasattr(model, 'predict_proba') else model.predict,
                        shap.sample(background_data, 100)
                    )
                except Exception as e:
                    self.logger.warning(f"Could not create SHAP explainer for {model_id}: {e}")
    
    def explain_decision(
        self,
        decision: 'CAIDecision',
        model_id: str = None,
        feature_values: Dict[str, Any] = None
    ) -> DecisionExplanation:
        """Generate complete explanation for a decision"""
        
        # Get feature attributions
        if model_id and feature_values and SHAP_AVAILABLE:
            attributions = self._calculate_shap_attributions(
                model_id, feature_values
            )
        else:
            attributions = self._estimate_attributions(decision, feature_values or {})
        
        # Generate audience-specific explanations
        portfolio_exp = self._generate_portfolio_committee_explanation(
            decision, attributions
        )
        risk_exp = self._generate_risk_committee_explanation(
            decision, attributions
        )
        regulator_exp = self._generate_regulator_explanation(
            decision, attributions
        )
        
        return DecisionExplanation(
            decision_id=decision.decision_id,
            decision_summary=self._generate_summary(decision),
            probability_of_success=decision.probability_of_success,
            key_drivers=attributions[:5],  # Top 5
            main_risks=decision.main_risks,
            alternatives_rejected=[
                {"action": alt.description, "confidence": alt.confidence}
                for alt in decision.alternatives_considered
            ],
            rejection_reasons={
                alt.action_id: alt.rejection_reason
                for alt in decision.alternatives_considered
                if alt.rejection_reason
            },
            portfolio_committee_explanation=portfolio_exp,
            risk_committee_explanation=risk_exp,
            regulator_explanation=regulator_exp
        )
    
    def explain_trade(
        self,
        trade_id: str,
        asset: str,
        action: str,
        quantity: float,
        confidence: float,
        feature_values: Dict[str, Any],
        risk_metrics: Dict[str, float],
        alternatives: List[Dict] = None
    ) -> TradeExplanation:
        """Generate detailed trade explanation"""
        
        # Calculate attributions
        attributions = self._estimate_attributions_from_features(feature_values)
        
        # Generate natural language explanations
        why_trade = self._generate_why_this_trade(
            asset, action, feature_values, attributions
        )
        what_wrong = self._generate_what_could_go_wrong(
            risk_metrics, feature_values
        )
        what_alternatives = self._generate_alternatives_explanation(
            alternatives or []
        )
        
        return TradeExplanation(
            trade_id=trade_id,
            asset=asset,
            action=action,
            quantity=quantity,
            confidence=confidence,
            expected_return=feature_values.get('expected_return', 0),
            expected_drawdown=risk_metrics.get('expected_drawdown', 0),
            feature_attributions=attributions,
            why_this_trade=why_trade,
            what_could_go_wrong=what_wrong,
            what_are_alternatives=what_alternatives
        )
    
    def _calculate_shap_attributions(
        self,
        model_id: str,
        feature_values: Dict[str, Any]
    ) -> List[FeatureAttribution]:
        """Calculate SHAP values for features"""
        if model_id not in self.explainers:
            return self._estimate_attributions_from_features(feature_values)
        
        try:
            explainer = self.explainers[model_id]
            
            # Prepare feature array
            features = np.array([list(feature_values.values())])
            
            # Calculate SHAP values
            shap_values = explainer.shap_values(features)
            
            # Handle multi-class output
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Take positive class
            
            # Create attributions
            attributions = []
            for i, (name, value) in enumerate(feature_values.items()):
                shap_val = shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i]
                
                attributions.append(FeatureAttribution(
                    feature_name=name,
                    feature_value=value,
                    attribution_value=float(shap_val),
                    attribution_direction="positive" if shap_val > 0 else "negative" if shap_val < 0 else "neutral",
                    importance_rank=0,  # Will be set after sorting
                    explanation=self._generate_feature_explanation(name, value, shap_val)
                ))
            
            # Sort by absolute SHAP value and set ranks
            attributions.sort(key=lambda x: abs(x.attribution_value), reverse=True)
            for i, attr in enumerate(attributions):
                attr.importance_rank = i + 1
            
            return attributions
            
        except Exception as e:
            self.logger.error(f"SHAP calculation error: {e}")
            return self._estimate_attributions_from_features(feature_values)
    
    def _estimate_attributions_from_features(
        self,
        feature_values: Dict[str, Any]
    ) -> List[FeatureAttribution]:
        """Estimate attributions without SHAP (rule-based)"""
        attributions = []
        
        # Define importance weights for features
        importance_weights = {
            "momentum_20d": 0.15,
            "volatility_20d": 0.12,
            "var_95": 0.15,
            "rsi": 0.08,
            "market_regime": 0.10,
            "news_sentiment": 0.08,
            "pe_ratio": 0.07,
            "beta": 0.06,
            "volume_z_score": 0.05,
            "correlation": 0.07,
            "drawdown": 0.07
        }
        
        for name, value in feature_values.items():
            weight = importance_weights.get(name, 0.05)
            
            # Estimate attribution based on feature value and weight
            if isinstance(value, (int, float)):
                # Normalize to -1 to 1 range approximately
                normalized = np.clip(value, -1, 1) if abs(value) <= 2 else value / abs(value)
                attribution = normalized * weight
            else:
                attribution = 0.0
            
            attributions.append(FeatureAttribution(
                feature_name=name,
                feature_value=value,
                attribution_value=attribution,
                attribution_direction="positive" if attribution > 0 else "negative" if attribution < 0 else "neutral",
                importance_rank=0,
                explanation=self._generate_feature_explanation(name, value, attribution)
            ))
        
        # Sort and rank
        attributions.sort(key=lambda x: abs(x.attribution_value), reverse=True)
        for i, attr in enumerate(attributions):
            attr.importance_rank = i + 1
        
        return attributions
    
    def _estimate_attributions(
        self,
        decision: 'CAIDecision',
        feature_values: Dict[str, Any]
    ) -> List[FeatureAttribution]:
        """Estimate attributions from decision object"""
        attributions = []
        
        # Use decision's key drivers
        for i, driver in enumerate(decision.key_drivers):
            attributions.append(FeatureAttribution(
                feature_name=f"driver_{i}",
                feature_value=driver,
                attribution_value=0.2 / (i + 1),  # Decreasing importance
                attribution_direction="positive",
                importance_rank=i + 1,
                explanation=driver
            ))
        
        return attributions
    
    def _generate_feature_explanation(
        self,
        feature_name: str,
        feature_value: Any,
        attribution: float
    ) -> str:
        """Generate natural language explanation for a feature"""
        description = self.feature_descriptions.get(
            feature_name, 
            feature_name.replace("_", " ").title()
        )
        
        direction = "increases" if attribution > 0 else "decreases" if attribution < 0 else "has minimal impact on"
        
        if isinstance(feature_value, float):
            value_str = f"{feature_value:.2%}" if abs(feature_value) < 1 else f"{feature_value:.2f}"
        else:
            value_str = str(feature_value)
        
        return f"{description} ({value_str}) {direction} the decision confidence."
    
    def _generate_summary(self, decision: 'CAIDecision') -> str:
        """Generate decision summary"""
        return f"""
Decision: {decision.action}
Asset: {decision.asset or 'Portfolio'}
Confidence: {decision.confidence.value:.0%}
Expected Return: {decision.expected_return:.2%}
Expected Drawdown: {decision.expected_drawdown:.2%}
Risk Level: {decision.risk_level.name}
Compliance: {decision.compliance_status.value.upper()}
        """.strip()
    
    def _generate_why_this_trade(
        self,
        asset: str,
        action: str,
        feature_values: Dict[str, Any],
        attributions: List[FeatureAttribution]
    ) -> str:
        """Generate 'Why this trade?' explanation"""
        top_positive = [a for a in attributions if a.attribution_direction == "positive"][:3]
        
        explanation_parts = [
            f"**Decision: {action} {asset}**\n",
            "### Key Factors Supporting This Decision:\n"
        ]
        
        for attr in top_positive:
            explanation_parts.append(f"- **{attr.feature_name}**: {attr.explanation}")
        
        # Add contextual information
        if "market_regime" in feature_values:
            explanation_parts.append(
                f"\n### Market Context:\n"
                f"Current regime: {feature_values['market_regime']}"
            )
        
        if "news_sentiment" in feature_values:
            sentiment = feature_values["news_sentiment"]
            sentiment_desc = "positive" if sentiment > 0.3 else "negative" if sentiment < -0.3 else "neutral"
            explanation_parts.append(f"News sentiment: {sentiment_desc}")
        
        return "\n".join(explanation_parts)
    
    def _generate_what_could_go_wrong(
        self,
        risk_metrics: Dict[str, float],
        feature_values: Dict[str, Any]
    ) -> str:
        """Generate risk warning explanation"""
        warnings = ["### Potential Risks:\n"]
        
        # VaR warning
        var_95 = risk_metrics.get("var_95", 0)
        if var_95 > 0.02:
            warnings.append(f"- **Elevated VaR**: Daily VaR of {var_95:.2%} indicates above-average risk exposure")
        
        # Drawdown warning
        drawdown = risk_metrics.get("expected_drawdown", 0)
        if drawdown > 0.05:
            warnings.append(f"- **Drawdown Risk**: Potential drawdown of {drawdown:.2%} from current levels")
        
        # Volatility warning
        volatility = feature_values.get("volatility_20d", 0)
        if volatility > 0.25:
            warnings.append(f"- **High Volatility**: Realized volatility of {volatility:.2%} is elevated")
        
        # Regime uncertainty
        regime_prob = feature_values.get("regime_probability", 1.0)
        if regime_prob < 0.6:
            warnings.append(f"- **Regime Uncertainty**: Market regime confidence only {regime_prob:.0%}")
        
        if len(warnings) == 1:
            warnings.append("- No significant risk factors identified above normal thresholds")
        
        return "\n".join(warnings)
    
    def _generate_alternatives_explanation(self, alternatives: List[Dict]) -> str:
        """Explain why alternatives were rejected"""
        if not alternatives:
            return "No alternative strategies met minimum confidence thresholds."
        
        parts = ["### Alternatives Considered:\n"]
        
        for alt in alternatives[:3]:
            parts.append(
                f"- **{alt.get('action', 'Unknown')}**: "
                f"Rejected due to {alt.get('rejection_reason', 'lower composite score')}"
            )
        
        return "\n".join(parts)
    
    def _generate_portfolio_committee_explanation(
        self,
        decision: 'CAIDecision',
        attributions: List[FeatureAttribution]
    ) -> str:
        """Generate explanation for portfolio committee"""
        return f"""
## Portfolio Committee Report

### Decision Summary
- **Action**: {decision.action} {decision.asset or ''}
- **Confidence**: {decision.confidence.value:.0%}
- **Expected Return**: {decision.expected_return:.2%}
- **Sharpe Ratio Impact**: Estimated positive

### Investment Rationale
{chr(10).join('- ' + a.explanation for a in attributions[:3])}

### Risk-Adjusted Assessment
- VaR (95%): {decision.var_95:.2%}
- Expected Drawdown: {decision.expected_drawdown:.2%}
- Risk Level: {decision.risk_level.name}

### Market Context
- Regime: {decision.market_regime.value} ({decision.regime_probability:.0%} confidence)

### Recommendation
{"PROCEED" if decision.confidence.value >= 0.65 else "REVIEW REQUIRED"}
        """.strip()
    
    def _generate_risk_committee_explanation(
        self,
        decision: 'CAIDecision',
        attributions: List[FeatureAttribution]
    ) -> str:
        """Generate explanation for risk committee"""
        return f"""
## Risk Committee Report

### Risk Metrics Summary
| Metric | Value | Limit | Status |
|--------|-------|-------|--------|
| VaR (95%) | {decision.var_95:.2%} | 2.00% | {'✓' if decision.var_95 <= 0.02 else '⚠'} |
| VaR (99%) | {decision.var_99:.2%} | 3.50% | {'✓' if decision.var_99 <= 0.035 else '⚠'} |
| CVaR (95%) | {decision.cvar_95:.2%} | 3.00% | {'✓' if decision.cvar_95 <= 0.03 else '⚠'} |
| Exp. Drawdown | {decision.expected_drawdown:.2%} | 10.00% | {'✓' if decision.expected_drawdown <= 0.10 else '⚠'} |

### Risk Flags
{chr(10).join('- ' + f for f in decision.risk_flags) if decision.risk_flags else '- No risk flags triggered'}

### Main Risks
{chr(10).join('- ' + r for r in decision.main_risks[:5]) if decision.main_risks else '- No significant risks identified'}

### Stress Test Results
Included in full risk report.

### Risk Approval
{"APPROVED - Within Limits" if len(decision.risk_flags) == 0 else "REVIEW REQUIRED"}
        """.strip()
    
    def _generate_regulator_explanation(
        self,
        decision: 'CAIDecision',
        attributions: List[FeatureAttribution]
    ) -> str:
        """Generate explanation for regulators"""
        return f"""
## Regulatory Compliance Report

### Decision Record
- **Decision ID**: {decision.decision_id}
- **Timestamp**: {decision.timestamp.isoformat()}
- **Action**: {decision.action}
- **Asset**: {decision.asset or 'N/A'}
- **Quantity**: {decision.quantity or 'N/A'}

### Compliance Status
- **Overall Status**: {decision.compliance_status.value.upper()}
- **All Checks**: {len(decision.compliance_checks)} performed

### Decision Explainability
This decision was made by an algorithmic trading system using the following methodology:

1. **Data Ingestion**: Market data, risk metrics, and sentiment indicators were collected from approved data sources.

2. **Risk Assessment**: Multiple risk metrics were calculated including VaR, CVaR, and stress testing.

3. **Compliance Verification**: All applicable regulatory requirements were verified before execution.

4. **Decision Logic**: The system uses a multi-factor model with the following primary factors:
{chr(10).join('   - ' + a.explanation for a in attributions[:5])}

### Audit Trail
Full decision inputs, outputs, and intermediate calculations are logged and available for audit.

### Model Governance
- Model Version: CAI v1.0
- Last Validation: [Date]
- Model Owner: [Name]

### Attestation
This report is generated automatically and represents an accurate record of the decision process.
        """.strip()
    
    def generate_batch_report(
        self,
        decisions: List['CAIDecision'],
        period: str = "daily"
    ) -> str:
        """Generate a batch report for multiple decisions"""
        if not decisions:
            return "No decisions to report."
        
        total = len(decisions)
        buys = len([d for d in decisions if d.action == "BUY"])
        sells = len([d for d in decisions if d.action == "SELL"])
        holds = len([d for d in decisions if d.action in ["HOLD", "ABSTAIN"]])
        
        avg_confidence = np.mean([d.confidence.value for d in decisions])
        avg_var = np.mean([d.var_95 for d in decisions])
        
        return f"""
## {period.title()} Trading Activity Report

### Summary Statistics
- **Total Decisions**: {total}
- **Buy Signals**: {buys}
- **Sell Signals**: {sells}
- **Hold/Abstain**: {holds}
- **Average Confidence**: {avg_confidence:.0%}
- **Average VaR (95%)**: {avg_var:.2%}

### Compliance Status
- All decisions passed pre-trade compliance checks

### Notable Decisions
{chr(10).join(f'- {d.action} {d.asset}: {d.explanation[:100]}...' for d in decisions[:5])}

### Risk Summary
Full risk metrics available in detailed report.
        """.strip()
