"""
Automated Insight Generator
===========================

AI-powered insight generation for portfolio analysis:
- Natural language insights ("Your tech sector is 15% overweight")
- Anomaly detection and alerts
- Trend identification
- Risk warnings
- Opportunity detection
- Personalized recommendations
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import json


class InsightCategory(Enum):
    """Categories of insights"""
    ALLOCATION = "allocation"
    PERFORMANCE = "performance"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    ANOMALY = "anomaly"
    TREND = "trend"
    COMPLIANCE = "compliance"
    REBALANCING = "rebalancing"
    COST = "cost"
    TAX = "tax"


class InsightPriority(Enum):
    """Priority levels for insights"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


class InsightAction(Enum):
    """Recommended actions"""
    REBALANCE = "rebalance"
    REDUCE_EXPOSURE = "reduce_exposure"
    INCREASE_EXPOSURE = "increase_exposure"
    HEDGE = "hedge"
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    DIVERSIFY = "diversify"
    REVIEW = "review"
    NO_ACTION = "no_action"


@dataclass
class Insight:
    """Individual insight with natural language description"""
    insight_id: str
    category: InsightCategory
    priority: InsightPriority
    created_at: datetime
    
    # Main content
    title: str
    description: str
    natural_language: str  # Human-readable summary
    
    # Context
    affected_assets: List[str] = field(default_factory=list)
    affected_factors: List[str] = field(default_factory=list)
    
    # Metrics
    metric_name: str = ""
    current_value: float = 0.0
    threshold_value: float = 0.0
    benchmark_value: float = 0.0
    deviation_pct: float = 0.0
    
    # Action
    recommended_action: InsightAction = InsightAction.REVIEW
    action_urgency: str = "medium"
    estimated_impact: float = 0.0
    
    # Confidence
    confidence_score: float = 0.8
    data_quality: float = 1.0
    
    # Related insights
    related_insights: List[str] = field(default_factory=list)
    
    # Dismissal tracking
    is_dismissed: bool = False
    dismissed_at: Optional[datetime] = None
    dismissed_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'insight_id': self.insight_id,
            'category': self.category.value,
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat(),
            'title': self.title,
            'description': self.description,
            'natural_language': self.natural_language,
            'affected_assets': self.affected_assets,
            'metrics': {
                'name': self.metric_name,
                'current': self.current_value,
                'threshold': self.threshold_value,
                'benchmark': self.benchmark_value,
                'deviation_pct': self.deviation_pct
            },
            'action': {
                'recommended': self.recommended_action.value,
                'urgency': self.action_urgency,
                'estimated_impact': self.estimated_impact
            },
            'confidence': self.confidence_score
        }


@dataclass
class InsightSession:
    """Collection of insights for a session"""
    session_id: str
    portfolio_id: str
    created_at: datetime
    insights: List[Insight] = field(default_factory=list)
    
    # Summary stats
    total_insights: int = 0
    critical_count: int = 0
    high_count: int = 0
    categories_covered: List[str] = field(default_factory=list)
    
    def get_top_insights(self, n: int = 5) -> List[Insight]:
        """Get top N insights by priority"""
        sorted_insights = sorted(
            [i for i in self.insights if not i.is_dismissed],
            key=lambda x: x.priority.value,
            reverse=True
        )
        return sorted_insights[:n]


class InsightGenerator:
    """
    Main engine for generating automated insights.
    
    Analyzes portfolio data and generates actionable insights
    in natural language.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("insight_generator")
        self.insight_templates = self._load_templates()
        
        # Thresholds for various checks
        self.thresholds = {
            'sector_overweight': 0.15,  # 15% overweight triggers alert
            'sector_underweight': -0.10,  # 10% underweight
            'position_concentration': 0.10,  # Single position > 10%
            'correlation_high': 0.8,
            'volatility_spike': 0.5,  # 50% above average
            'drawdown_warning': -0.10,  # 10% drawdown
            'drawdown_critical': -0.20,  # 20% drawdown
            'tracking_error': 0.05,  # 5% tracking error
            'beta_deviation': 0.3,  # Beta more than 0.3 from 1
            'rebalance_drift': 0.05,  # 5% drift triggers rebalance
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """Load natural language templates for insights"""
        return {
            'sector_overweight': "Your {sector} sector allocation is {deviation:.1%} overweight relative to benchmark. Current: {current:.1%}, Target: {target:.1%}.",
            'sector_underweight': "Your {sector} sector allocation is {deviation:.1%} underweight. Consider increasing exposure for better diversification.",
            'position_concentration': "{asset} represents {weight:.1%} of your portfolio. Consider reducing concentration risk.",
            'high_correlation': "{asset1} and {asset2} have a correlation of {correlation:.2f}. This reduces diversification benefits.",
            'volatility_increase': "Portfolio volatility has increased by {change:.1%} over the past {period}. Current: {current:.1%}.",
            'drawdown_warning': "Portfolio is experiencing a {drawdown:.1%} drawdown from recent highs. {days} days since peak.",
            'strong_performance': "{asset} has gained {return:.1%} over the past {period}. Consider taking partial profits.",
            'weak_performance': "{asset} has declined {return:.1%} over the past {period}. Review thesis or consider exit.",
            'rebalance_needed': "Portfolio has drifted from target allocation. {n_assets} assets need rebalancing.",
            'beta_high': "Portfolio beta of {beta:.2f} indicates higher market sensitivity. Consider defensive positions.",
            'opportunity_detected': "Potential opportunity: {asset} is trading at {discount:.1%} below fair value estimate.",
            'risk_budget_exceeded': "Risk budget for {factor} has been exceeded by {excess:.1%}.",
            'tax_harvest': "Tax-loss harvesting opportunity: {asset} has unrealized loss of {loss:.1%}.",
        }
    
    def generate_insight(
        self,
        template_key: str,
        category: InsightCategory,
        priority: InsightPriority,
        params: Dict[str, Any],
        action: InsightAction = InsightAction.REVIEW
    ) -> Insight:
        """Generate a single insight from template"""
        import uuid
        
        template = self.insight_templates.get(template_key, "{description}")
        natural_language = template.format(**params)
        
        return Insight(
            insight_id=str(uuid.uuid4()),
            category=category,
            priority=priority,
            created_at=datetime.now(),
            title=template_key.replace('_', ' ').title(),
            description=json.dumps(params),
            natural_language=natural_language,
            affected_assets=params.get('affected_assets', []),
            metric_name=params.get('metric_name', ''),
            current_value=params.get('current', 0),
            threshold_value=params.get('threshold', 0),
            deviation_pct=params.get('deviation', 0),
            recommended_action=action,
            confidence_score=params.get('confidence', 0.8)
        )
    
    def analyze_sector_allocation(
        self,
        portfolio_weights: Dict[str, float],
        benchmark_weights: Dict[str, float],
        asset_sectors: Dict[str, str]
    ) -> List[Insight]:
        """Analyze sector allocation vs benchmark"""
        insights = []
        
        # Aggregate by sector
        portfolio_sectors = {}
        for asset, weight in portfolio_weights.items():
            sector = asset_sectors.get(asset, 'Other')
            portfolio_sectors[sector] = portfolio_sectors.get(sector, 0) + weight
        
        benchmark_sectors = {}
        for asset, weight in benchmark_weights.items():
            sector = asset_sectors.get(asset, 'Other')
            benchmark_sectors[sector] = benchmark_sectors.get(sector, 0) + weight
        
        # Check each sector
        all_sectors = set(portfolio_sectors.keys()) | set(benchmark_sectors.keys())
        
        for sector in all_sectors:
            port_weight = portfolio_sectors.get(sector, 0)
            bench_weight = benchmark_sectors.get(sector, 0)
            deviation = port_weight - bench_weight
            
            if deviation > self.thresholds['sector_overweight']:
                insight = self.generate_insight(
                    'sector_overweight',
                    InsightCategory.ALLOCATION,
                    InsightPriority.HIGH if deviation > 0.25 else InsightPriority.MEDIUM,
                    {
                        'sector': sector,
                        'deviation': deviation,
                        'current': port_weight,
                        'target': bench_weight,
                        'affected_assets': [a for a, s in asset_sectors.items() if s == sector]
                    },
                    InsightAction.REDUCE_EXPOSURE
                )
                insights.append(insight)
            
            elif deviation < self.thresholds['sector_underweight']:
                insight = self.generate_insight(
                    'sector_underweight',
                    InsightCategory.ALLOCATION,
                    InsightPriority.MEDIUM,
                    {
                        'sector': sector,
                        'deviation': abs(deviation),
                        'current': port_weight,
                        'target': bench_weight
                    },
                    InsightAction.INCREASE_EXPOSURE
                )
                insights.append(insight)
        
        return insights
    
    def analyze_concentration(
        self,
        portfolio_weights: Dict[str, float]
    ) -> List[Insight]:
        """Analyze position concentration risk"""
        insights = []
        
        for asset, weight in portfolio_weights.items():
            if weight > self.thresholds['position_concentration']:
                priority = InsightPriority.HIGH if weight > 0.15 else InsightPriority.MEDIUM
                
                insight = self.generate_insight(
                    'position_concentration',
                    InsightCategory.RISK,
                    priority,
                    {
                        'asset': asset,
                        'weight': weight,
                        'affected_assets': [asset]
                    },
                    InsightAction.REDUCE_EXPOSURE
                )
                insights.append(insight)
        
        return insights
    
    def analyze_correlation(
        self,
        correlation_matrix: pd.DataFrame,
        portfolio_weights: Dict[str, float]
    ) -> List[Insight]:
        """Analyze correlation risks"""
        insights = []
        
        assets = list(portfolio_weights.keys())
        seen_pairs = set()
        
        for i, asset1 in enumerate(assets):
            for asset2 in assets[i+1:]:
                if asset1 in correlation_matrix.index and asset2 in correlation_matrix.columns:
                    corr = correlation_matrix.loc[asset1, asset2]
                    pair = tuple(sorted([asset1, asset2]))
                    
                    if pair not in seen_pairs and corr > self.thresholds['correlation_high']:
                        combined_weight = portfolio_weights.get(asset1, 0) + portfolio_weights.get(asset2, 0)
                        
                        if combined_weight > 0.15:  # Only flag if meaningful exposure
                            insight = self.generate_insight(
                                'high_correlation',
                                InsightCategory.RISK,
                                InsightPriority.MEDIUM,
                                {
                                    'asset1': asset1,
                                    'asset2': asset2,
                                    'correlation': corr,
                                    'combined_weight': combined_weight,
                                    'affected_assets': [asset1, asset2]
                                },
                                InsightAction.DIVERSIFY
                            )
                            insights.append(insight)
                        
                        seen_pairs.add(pair)
        
        return insights
    
    def analyze_volatility(
        self,
        returns: pd.DataFrame,
        lookback: int = 21,
        comparison_period: int = 252
    ) -> List[Insight]:
        """Analyze volatility changes"""
        insights = []
        
        recent_vol = returns.iloc[-lookback:].std() * np.sqrt(252)
        historical_vol = returns.iloc[-comparison_period:-lookback].std() * np.sqrt(252)
        
        for asset in returns.columns:
            if historical_vol[asset] > 0:
                vol_change = (recent_vol[asset] - historical_vol[asset]) / historical_vol[asset]
                
                if vol_change > self.thresholds['volatility_spike']:
                    insight = self.generate_insight(
                        'volatility_increase',
                        InsightCategory.RISK,
                        InsightPriority.HIGH if vol_change > 0.75 else InsightPriority.MEDIUM,
                        {
                            'asset': asset,
                            'change': vol_change,
                            'current': recent_vol[asset],
                            'historical': historical_vol[asset],
                            'period': f"{lookback} days",
                            'affected_assets': [asset]
                        },
                        InsightAction.REVIEW
                    )
                    insights.append(insight)
        
        return insights
    
    def analyze_drawdowns(
        self,
        returns: pd.Series,
        asset_name: str = "Portfolio"
    ) -> List[Insight]:
        """Analyze current drawdown"""
        insights = []
        
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = cumulative / rolling_max - 1
        current_dd = drawdown.iloc[-1]
        
        if current_dd < self.thresholds['drawdown_critical']:
            # Find peak date
            peak_idx = cumulative.idxmax()
            days_since_peak = (returns.index[-1] - peak_idx).days
            
            insight = self.generate_insight(
                'drawdown_warning',
                InsightCategory.RISK,
                InsightPriority.CRITICAL,
                {
                    'asset': asset_name,
                    'drawdown': current_dd,
                    'days': days_since_peak,
                    'affected_assets': [asset_name]
                },
                InsightAction.HEDGE
            )
            insights.append(insight)
        
        elif current_dd < self.thresholds['drawdown_warning']:
            peak_idx = cumulative.idxmax()
            days_since_peak = (returns.index[-1] - peak_idx).days
            
            insight = self.generate_insight(
                'drawdown_warning',
                InsightCategory.RISK,
                InsightPriority.HIGH,
                {
                    'asset': asset_name,
                    'drawdown': current_dd,
                    'days': days_since_peak,
                    'affected_assets': [asset_name]
                },
                InsightAction.REVIEW
            )
            insights.append(insight)
        
        return insights
    
    def analyze_performance_outliers(
        self,
        returns: pd.DataFrame,
        lookback: int = 21
    ) -> List[Insight]:
        """Identify strong and weak performers"""
        insights = []
        
        period_returns = (1 + returns.iloc[-lookback:]).prod() - 1
        
        for asset, ret in period_returns.items():
            if ret > 0.15:  # > 15% gain
                insight = self.generate_insight(
                    'strong_performance',
                    InsightCategory.OPPORTUNITY,
                    InsightPriority.MEDIUM,
                    {
                        'asset': asset,
                        'return': ret,
                        'period': f"{lookback} days",
                        'affected_assets': [asset]
                    },
                    InsightAction.TAKE_PROFIT
                )
                insights.append(insight)
            
            elif ret < -0.15:  # > 15% loss
                insight = self.generate_insight(
                    'weak_performance',
                    InsightCategory.RISK,
                    InsightPriority.HIGH,
                    {
                        'asset': asset,
                        'return': abs(ret),
                        'period': f"{lookback} days",
                        'affected_assets': [asset]
                    },
                    InsightAction.STOP_LOSS
                )
                insights.append(insight)
        
        return insights
    
    def analyze_rebalancing_needs(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float]
    ) -> List[Insight]:
        """Check if rebalancing is needed"""
        insights = []
        assets_needing_rebalance = []
        
        for asset in set(current_weights.keys()) | set(target_weights.keys()):
            current = current_weights.get(asset, 0)
            target = target_weights.get(asset, 0)
            drift = abs(current - target)
            
            if drift > self.thresholds['rebalance_drift']:
                assets_needing_rebalance.append({
                    'asset': asset,
                    'current': current,
                    'target': target,
                    'drift': drift
                })
        
        if assets_needing_rebalance:
            insight = self.generate_insight(
                'rebalance_needed',
                InsightCategory.REBALANCING,
                InsightPriority.MEDIUM,
                {
                    'n_assets': len(assets_needing_rebalance),
                    'assets': assets_needing_rebalance,
                    'affected_assets': [a['asset'] for a in assets_needing_rebalance]
                },
                InsightAction.REBALANCE
            )
            insights.append(insight)
        
        return insights
    
    def analyze_tax_opportunities(
        self,
        positions: Dict[str, Dict[str, float]],
        tax_rate: float = 0.20
    ) -> List[Insight]:
        """Identify tax-loss harvesting opportunities"""
        insights = []
        
        for asset, position in positions.items():
            unrealized_gain = position.get('unrealized_gain_pct', 0)
            value = position.get('value', 0)
            
            if unrealized_gain < -0.10 and value > 1000:  # > 10% loss, > $1000 value
                potential_savings = abs(unrealized_gain * value * tax_rate)
                
                insight = self.generate_insight(
                    'tax_harvest',
                    InsightCategory.TAX,
                    InsightPriority.LOW,
                    {
                        'asset': asset,
                        'loss': unrealized_gain,
                        'value': value,
                        'potential_savings': potential_savings,
                        'affected_assets': [asset]
                    },
                    InsightAction.REVIEW
                )
                insights.append(insight)
        
        return insights


class AutomatedInsights:
    """
    High-level interface for generating comprehensive portfolio insights.
    """
    
    def __init__(self):
        self.generator = InsightGenerator()
        self.logger = logging.getLogger("automated_insights")
        self.sessions: Dict[str, InsightSession] = {}
    
    def generate_full_analysis(
        self,
        portfolio_id: str,
        portfolio_weights: Dict[str, float],
        returns: pd.DataFrame,
        benchmark_weights: Optional[Dict[str, float]] = None,
        correlation_matrix: Optional[pd.DataFrame] = None,
        asset_sectors: Optional[Dict[str, str]] = None,
        target_weights: Optional[Dict[str, float]] = None,
        positions: Optional[Dict[str, Dict]] = None
    ) -> InsightSession:
        """
        Generate comprehensive insights for a portfolio.
        """
        import uuid
        
        session = InsightSession(
            session_id=str(uuid.uuid4()),
            portfolio_id=portfolio_id,
            created_at=datetime.now()
        )
        
        # Sector allocation analysis
        if benchmark_weights and asset_sectors:
            sector_insights = self.generator.analyze_sector_allocation(
                portfolio_weights, benchmark_weights, asset_sectors
            )
            session.insights.extend(sector_insights)
        
        # Concentration analysis
        concentration_insights = self.generator.analyze_concentration(portfolio_weights)
        session.insights.extend(concentration_insights)
        
        # Correlation analysis
        if correlation_matrix is not None:
            correlation_insights = self.generator.analyze_correlation(
                correlation_matrix, portfolio_weights
            )
            session.insights.extend(correlation_insights)
        
        # Volatility analysis
        if len(returns) > 60:
            volatility_insights = self.generator.analyze_volatility(returns)
            session.insights.extend(volatility_insights)
        
        # Drawdown analysis
        portfolio_returns = (returns * pd.Series(portfolio_weights)).sum(axis=1)
        drawdown_insights = self.generator.analyze_drawdowns(portfolio_returns)
        session.insights.extend(drawdown_insights)
        
        # Performance outliers
        performance_insights = self.generator.analyze_performance_outliers(returns)
        session.insights.extend(performance_insights)
        
        # Rebalancing needs
        if target_weights:
            rebalance_insights = self.generator.analyze_rebalancing_needs(
                portfolio_weights, target_weights
            )
            session.insights.extend(rebalance_insights)
        
        # Tax opportunities
        if positions:
            tax_insights = self.generator.analyze_tax_opportunities(positions)
            session.insights.extend(tax_insights)
        
        # Update session stats
        session.total_insights = len(session.insights)
        session.critical_count = len([i for i in session.insights if i.priority == InsightPriority.CRITICAL])
        session.high_count = len([i for i in session.insights if i.priority == InsightPriority.HIGH])
        session.categories_covered = list(set(i.category.value for i in session.insights))
        
        self.sessions[session.session_id] = session
        
        self.logger.info(
            f"Generated {session.total_insights} insights for portfolio {portfolio_id}. "
            f"Critical: {session.critical_count}, High: {session.high_count}"
        )
        
        return session
    
    def get_executive_summary(self, session: InsightSession) -> str:
        """Generate executive summary of insights"""
        top_insights = session.get_top_insights(5)
        
        summary_parts = [
            f"Portfolio Analysis Summary - {session.created_at.strftime('%Y-%m-%d %H:%M')}\n",
            f"Total Insights: {session.total_insights}\n",
            f"Critical: {session.critical_count} | High Priority: {session.high_count}\n",
            "\nTop Insights:\n"
        ]
        
        for i, insight in enumerate(top_insights, 1):
            summary_parts.append(
                f"{i}. [{insight.priority.name}] {insight.natural_language}\n"
            )
        
        return "".join(summary_parts)
    
    def get_actionable_items(self, session: InsightSession) -> List[Dict[str, Any]]:
        """Get list of actionable items from insights"""
        actionable = []
        
        for insight in session.insights:
            if insight.recommended_action != InsightAction.NO_ACTION:
                actionable.append({
                    'insight_id': insight.insight_id,
                    'action': insight.recommended_action.value,
                    'priority': insight.priority.name,
                    'description': insight.natural_language,
                    'affected_assets': insight.affected_assets,
                    'estimated_impact': insight.estimated_impact
                })
        
        # Sort by priority
        actionable.sort(key=lambda x: InsightPriority[x['priority']].value, reverse=True)
        
        return actionable
    
    def dismiss_insight(
        self,
        session_id: str,
        insight_id: str,
        reason: str
    ) -> bool:
        """Dismiss an insight with reason"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        for insight in session.insights:
            if insight.insight_id == insight_id:
                insight.is_dismissed = True
                insight.dismissed_at = datetime.now()
                insight.dismissed_reason = reason
                return True
        
        return False
    
    def export_insights_json(self, session: InsightSession) -> str:
        """Export insights to JSON"""
        return json.dumps({
            'session_id': session.session_id,
            'portfolio_id': session.portfolio_id,
            'created_at': session.created_at.isoformat(),
            'summary': {
                'total': session.total_insights,
                'critical': session.critical_count,
                'high': session.high_count,
                'categories': session.categories_covered
            },
            'insights': [i.to_dict() for i in session.insights]
        }, indent=2)
