"""
Cross-Asset Analytics
====================

Cross-asset class analysis and optimization:
- Multi-asset correlation analysis
- Hedging recommendations
- Asset class rotation signals
- Risk parity allocation
- Macro regime detection
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging


class AssetClass(Enum):
    """Asset classes"""
    EQUITIES = "equities"
    FIXED_INCOME = "fixed_income"
    REAL_ESTATE = "real_estate"
    COMMODITIES = "commodities"
    CRYPTOCURRENCY = "cryptocurrency"
    PRIVATE_EQUITY = "private_equity"
    HEDGE_FUNDS = "hedge_funds"
    CASH = "cash"
    ALTERNATIVES = "alternatives"


class MacroRegime(Enum):
    """Macroeconomic regimes"""
    GROWTH = "growth"
    RECESSION = "recession"
    RECOVERY = "recovery"
    STAGFLATION = "stagflation"
    GOLDILOCKS = "goldilocks"
    RISK_OFF = "risk_off"


class RiskProfile(Enum):
    """Investor risk profiles"""
    CONSERVATIVE = "conservative"
    MODERATE_CONSERVATIVE = "moderate_conservative"
    MODERATE = "moderate"
    MODERATE_AGGRESSIVE = "moderate_aggressive"
    AGGRESSIVE = "aggressive"


@dataclass
class AssetClassAllocation:
    """Allocation to an asset class"""
    asset_class: AssetClass
    current_value: float
    target_weight: float
    current_weight: float = 0.0
    expected_return: float = 0.0
    expected_volatility: float = 0.0
    liquidity_score: float = 1.0  # 0-1, higher is more liquid


@dataclass
class CorrelationPair:
    """Correlation between two assets/asset classes"""
    asset1: str
    asset2: str
    correlation: float
    rolling_30d: float = 0.0
    rolling_90d: float = 0.0
    crisis_correlation: float = 0.0  # Correlation during market stress


@dataclass
class HedgeRecommendation:
    """Hedging recommendation"""
    exposure: str
    hedge_instrument: str
    hedge_ratio: float
    cost_estimate: float
    effectiveness: float
    recommendation: str
    priority: str  # high, medium, low


class CrossAssetAnalyzer:
    """
    Analyzes relationships and provides insights across asset classes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("cross_asset")
        self.allocations: Dict[AssetClass, AssetClassAllocation] = {}
        
        # Historical correlation benchmarks
        self.historical_correlations = {
            ('equities', 'fixed_income'): -0.2,
            ('equities', 'commodities'): 0.3,
            ('equities', 'real_estate'): 0.6,
            ('equities', 'cryptocurrency'): 0.5,
            ('fixed_income', 'commodities'): 0.1,
            ('fixed_income', 'real_estate'): 0.2,
            ('commodities', 'cryptocurrency'): 0.3,
        }
        
        # Expected returns by regime
        self.regime_returns = {
            MacroRegime.GROWTH: {
                AssetClass.EQUITIES: 0.12,
                AssetClass.FIXED_INCOME: 0.02,
                AssetClass.REAL_ESTATE: 0.08,
                AssetClass.COMMODITIES: 0.06,
                AssetClass.CRYPTOCURRENCY: 0.25,
            },
            MacroRegime.RECESSION: {
                AssetClass.EQUITIES: -0.15,
                AssetClass.FIXED_INCOME: 0.06,
                AssetClass.REAL_ESTATE: -0.10,
                AssetClass.COMMODITIES: -0.08,
                AssetClass.CRYPTOCURRENCY: -0.30,
            },
            MacroRegime.STAGFLATION: {
                AssetClass.EQUITIES: -0.05,
                AssetClass.FIXED_INCOME: -0.03,
                AssetClass.REAL_ESTATE: 0.02,
                AssetClass.COMMODITIES: 0.15,
                AssetClass.CRYPTOCURRENCY: 0.0,
            },
            MacroRegime.GOLDILOCKS: {
                AssetClass.EQUITIES: 0.15,
                AssetClass.FIXED_INCOME: 0.04,
                AssetClass.REAL_ESTATE: 0.10,
                AssetClass.COMMODITIES: 0.05,
                AssetClass.CRYPTOCURRENCY: 0.20,
            },
        }
    
    def set_allocation(self, allocation: AssetClassAllocation):
        """Set allocation for an asset class"""
        self.allocations[allocation.asset_class] = allocation
        self._recalculate_weights()
    
    def _recalculate_weights(self):
        """Recalculate current weights"""
        total = sum(a.current_value for a in self.allocations.values())
        for alloc in self.allocations.values():
            alloc.current_weight = alloc.current_value / total if total > 0 else 0
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary across asset classes"""
        total_value = sum(a.current_value for a in self.allocations.values())
        
        weighted_return = sum(
            a.current_weight * a.expected_return 
            for a in self.allocations.values()
        )
        
        # Simplified volatility (doesn't account for correlations)
        weighted_vol = np.sqrt(sum(
            (a.current_weight ** 2) * (a.expected_volatility ** 2)
            for a in self.allocations.values()
        ))
        
        allocation_summary = {
            a.asset_class.value: {
                'value': a.current_value,
                'current_weight': a.current_weight,
                'target_weight': a.target_weight,
                'drift': a.current_weight - a.target_weight
            }
            for a in self.allocations.values()
        }
        
        return {
            'total_value': total_value,
            'expected_return': weighted_return,
            'expected_volatility': weighted_vol,
            'sharpe_estimate': (weighted_return - 0.04) / weighted_vol if weighted_vol > 0 else 0,
            'allocations': allocation_summary
        }
    
    def calculate_correlation_matrix(
        self,
        returns: Dict[str, pd.Series]
    ) -> pd.DataFrame:
        """Calculate correlation matrix from returns"""
        returns_df = pd.DataFrame(returns)
        return returns_df.corr()
    
    def detect_correlation_regime(
        self,
        short_term_corr: float,
        long_term_corr: float
    ) -> Dict[str, Any]:
        """Detect if correlations are in unusual regime"""
        diff = short_term_corr - long_term_corr
        
        if abs(diff) > 0.3:
            regime = "divergent"
            message = "Short-term correlations significantly different from historical"
        elif short_term_corr > 0.7:
            regime = "high_correlation"
            message = "Assets highly correlated, diversification benefits reduced"
        elif short_term_corr < 0.2:
            regime = "low_correlation"
            message = "Good diversification conditions"
        else:
            regime = "normal"
            message = "Correlations within normal range"
        
        return {
            'regime': regime,
            'short_term': short_term_corr,
            'long_term': long_term_corr,
            'divergence': diff,
            'message': message
        }
    
    def identify_macro_regime(
        self,
        gdp_growth: float,
        inflation: float,
        unemployment_change: float
    ) -> Dict[str, Any]:
        """Identify current macroeconomic regime"""
        if gdp_growth > 0.02 and inflation < 0.03:
            regime = MacroRegime.GOLDILOCKS
            description = "Strong growth with low inflation - ideal conditions"
        elif gdp_growth > 0.02 and inflation > 0.04:
            regime = MacroRegime.GROWTH
            description = "Strong growth but rising inflation concerns"
        elif gdp_growth < 0 and inflation > 0.04:
            regime = MacroRegime.STAGFLATION
            description = "Negative growth with high inflation - challenging environment"
        elif gdp_growth < 0:
            regime = MacroRegime.RECESSION
            description = "Economic contraction - defensive positioning recommended"
        elif gdp_growth > 0 and unemployment_change < 0:
            regime = MacroRegime.RECOVERY
            description = "Economy recovering - risk-on assets may outperform"
        else:
            regime = MacroRegime.GROWTH
            description = "Normal growth conditions"
        
        # Get expected returns for this regime
        expected_returns = self.regime_returns.get(regime, {})
        
        return {
            'regime': regime.value,
            'description': description,
            'indicators': {
                'gdp_growth': gdp_growth,
                'inflation': inflation,
                'unemployment_change': unemployment_change
            },
            'expected_returns': {k.value: v for k, v in expected_returns.items()}
        }
    
    def get_rebalancing_trades(
        self,
        min_trade_size: float = 1000
    ) -> List[Dict[str, Any]]:
        """Calculate trades needed to rebalance to targets"""
        total_value = sum(a.current_value for a in self.allocations.values())
        trades = []
        
        for alloc in self.allocations.values():
            target_value = total_value * alloc.target_weight
            current_value = alloc.current_value
            diff = target_value - current_value
            
            if abs(diff) >= min_trade_size:
                trades.append({
                    'asset_class': alloc.asset_class.value,
                    'action': 'buy' if diff > 0 else 'sell',
                    'amount': abs(diff),
                    'current_value': current_value,
                    'target_value': target_value,
                    'current_weight': alloc.current_weight,
                    'target_weight': alloc.target_weight
                })
        
        # Sort by absolute size
        trades.sort(key=lambda x: x['amount'], reverse=True)
        
        return trades


class HedgingRecommendations:
    """
    Generates hedging recommendations for portfolio risks.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("hedging")
        
        # Hedging instruments by risk type
        self.hedge_instruments = {
            'equity_market': ['SPY puts', 'VIX calls', 'inverse ETFs', 'futures shorts'],
            'interest_rate': ['treasury futures', 'interest rate swaps', 'bond puts'],
            'currency': ['FX forwards', 'currency options', 'currency ETFs'],
            'commodity': ['commodity futures', 'commodity ETFs', 'producer options'],
            'inflation': ['TIPS', 'commodity basket', 'real estate exposure'],
            'credit': ['CDS', 'high yield shorts', 'investment grade longs'],
            'crypto': ['bitcoin futures', 'stablecoin allocation', 'options'],
        }
    
    def analyze_portfolio_risks(
        self,
        allocations: Dict[str, float],
        sensitivities: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Analyze portfolio risk exposures"""
        risks = {
            'equity_beta': 0,
            'duration': 0,
            'commodity_exposure': 0,
            'crypto_exposure': 0,
            'real_estate_exposure': 0
        }
        
        for asset_class, weight in allocations.items():
            sens = sensitivities.get(asset_class, {})
            risks['equity_beta'] += weight * sens.get('equity_beta', 0)
            risks['duration'] += weight * sens.get('duration', 0)
            risks['commodity_exposure'] += weight * sens.get('commodity', 0)
            risks['crypto_exposure'] += weight * sens.get('crypto', 0)
            risks['real_estate_exposure'] += weight * sens.get('real_estate', 0)
        
        return risks
    
    def generate_recommendations(
        self,
        risks: Dict[str, float],
        risk_tolerance: RiskProfile = RiskProfile.MODERATE
    ) -> List[HedgeRecommendation]:
        """Generate hedging recommendations based on risk analysis"""
        recommendations = []
        
        # Thresholds based on risk tolerance
        thresholds = {
            RiskProfile.CONSERVATIVE: {'beta': 0.3, 'duration': 3, 'commodity': 0.05},
            RiskProfile.MODERATE: {'beta': 0.6, 'duration': 5, 'commodity': 0.10},
            RiskProfile.AGGRESSIVE: {'beta': 0.9, 'duration': 8, 'commodity': 0.20},
        }
        
        threshold = thresholds.get(risk_tolerance, thresholds[RiskProfile.MODERATE])
        
        # Check equity risk
        if risks.get('equity_beta', 0) > threshold['beta']:
            hedge_ratio = (risks['equity_beta'] - threshold['beta']) / risks['equity_beta']
            recommendations.append(HedgeRecommendation(
                exposure='equity_market',
                hedge_instrument='SPY put spread',
                hedge_ratio=hedge_ratio,
                cost_estimate=0.02 * hedge_ratio,  # ~2% for puts
                effectiveness=0.85,
                recommendation=f"Consider hedging {hedge_ratio:.0%} of equity exposure with put spreads",
                priority='high' if risks['equity_beta'] > threshold['beta'] * 1.5 else 'medium'
            ))
        
        # Check duration risk
        if risks.get('duration', 0) > threshold['duration']:
            hedge_ratio = (risks['duration'] - threshold['duration']) / risks['duration']
            recommendations.append(HedgeRecommendation(
                exposure='interest_rate',
                hedge_instrument='Treasury futures short',
                hedge_ratio=hedge_ratio,
                cost_estimate=0.001 * hedge_ratio,  # Minimal cost
                effectiveness=0.90,
                recommendation=f"Reduce duration by {hedge_ratio:.0%} using treasury futures",
                priority='high' if risks['duration'] > threshold['duration'] * 1.3 else 'medium'
            ))
        
        # Check crypto exposure
        if risks.get('crypto_exposure', 0) > 0.10:
            recommendations.append(HedgeRecommendation(
                exposure='cryptocurrency',
                hedge_instrument='Bitcoin put options or stablecoin allocation',
                hedge_ratio=0.5,
                cost_estimate=0.05,
                effectiveness=0.70,
                recommendation="Consider hedging crypto exposure due to high volatility",
                priority='medium'
            ))
        
        return recommendations
    
    def calculate_hedge_effectiveness(
        self,
        portfolio_returns: pd.Series,
        hedge_returns: pd.Series
    ) -> Dict[str, float]:
        """Calculate hedge effectiveness metrics"""
        # Correlation
        correlation = portfolio_returns.corr(hedge_returns)
        
        # Variance reduction
        combined_returns = portfolio_returns + hedge_returns
        var_reduction = 1 - (combined_returns.var() / portfolio_returns.var())
        
        # Beta
        if hedge_returns.var() > 0:
            beta = portfolio_returns.cov(hedge_returns) / hedge_returns.var()
        else:
            beta = 0
        
        # R-squared (how much variance is explained)
        r_squared = correlation ** 2
        
        return {
            'correlation': correlation,
            'variance_reduction': var_reduction,
            'beta': beta,
            'r_squared': r_squared,
            'effectiveness_rating': 'excellent' if var_reduction > 0.7 else 'good' if var_reduction > 0.5 else 'moderate' if var_reduction > 0.3 else 'poor'
        }


class RiskParityAllocator:
    """
    Risk parity allocation across asset classes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("risk_parity")
    
    def calculate_risk_parity_weights(
        self,
        volatilities: Dict[str, float],
        correlations: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """
        Calculate risk parity weights.
        Simple approach: inverse volatility weighting.
        """
        # Inverse volatility weights
        inv_vols = {k: 1/v if v > 0 else 0 for k, v in volatilities.items()}
        total_inv_vol = sum(inv_vols.values())
        
        weights = {k: v/total_inv_vol for k, v in inv_vols.items()}
        
        return weights
    
    def calculate_risk_contributions(
        self,
        weights: Dict[str, float],
        volatilities: Dict[str, float],
        correlations: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate marginal risk contributions"""
        assets = list(weights.keys())
        n = len(assets)
        
        w = np.array([weights[a] for a in assets])
        vol = np.array([volatilities[a] for a in assets])
        
        # Build covariance matrix from correlations and volatilities
        cov = np.zeros((n, n))
        for i, a1 in enumerate(assets):
            for j, a2 in enumerate(assets):
                if i == j:
                    cov[i, j] = vol[i] ** 2
                else:
                    corr = correlations.loc[a1, a2] if a1 in correlations.index and a2 in correlations.columns else 0
                    cov[i, j] = corr * vol[i] * vol[j]
        
        # Portfolio variance
        port_var = w @ cov @ w
        port_vol = np.sqrt(port_var)
        
        # Marginal contribution to risk
        mctr = (cov @ w) / port_vol
        
        # Total contribution to risk
        tctr = w * mctr
        
        # Percentage contribution
        pctr = tctr / port_vol
        
        contributions = {
            assets[i]: {
                'weight': float(w[i]),
                'marginal_contribution': float(mctr[i]),
                'total_contribution': float(tctr[i]),
                'percent_contribution': float(pctr[i])
            }
            for i in range(n)
        }
        
        return {
            'portfolio_volatility': float(port_vol),
            'contributions': contributions,
            'is_risk_parity': all(abs(pctr[i] - 1/n) < 0.05 for i in range(n))
        }


class AssetRotationSignals:
    """
    Generates asset class rotation signals.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("rotation")
        
        # Momentum lookback periods
        self.lookback_periods = [21, 63, 126, 252]  # 1m, 3m, 6m, 12m
    
    def calculate_momentum_scores(
        self,
        price_data: Dict[str, pd.Series]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate momentum scores for each asset class"""
        scores = {}
        
        for asset, prices in price_data.items():
            if len(prices) < max(self.lookback_periods):
                continue
            
            momentum = {}
            for period in self.lookback_periods:
                if len(prices) >= period:
                    ret = (prices.iloc[-1] / prices.iloc[-period]) - 1
                    momentum[f'{period}d'] = ret
            
            # Composite momentum score
            if momentum:
                avg_momentum = np.mean(list(momentum.values()))
                scores[asset] = {
                    'returns': momentum,
                    'composite_score': avg_momentum,
                    'signal': 'overweight' if avg_momentum > 0.05 else 'underweight' if avg_momentum < -0.05 else 'neutral'
                }
        
        return scores
    
    def generate_rotation_signals(
        self,
        momentum_scores: Dict[str, Dict[str, float]],
        current_allocations: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate rotation signals based on momentum"""
        # Rank by momentum
        ranked = sorted(
            momentum_scores.items(),
            key=lambda x: x[1]['composite_score'],
            reverse=True
        )
        
        signals = []
        for rank, (asset, scores) in enumerate(ranked):
            current = current_allocations.get(asset, 0)
            
            if rank < len(ranked) // 3:
                # Top third - overweight
                target_adjustment = 0.05  # Increase by 5%
                action = 'increase'
            elif rank >= len(ranked) * 2 // 3:
                # Bottom third - underweight
                target_adjustment = -0.05
                action = 'decrease'
            else:
                target_adjustment = 0
                action = 'hold'
            
            signals.append({
                'asset': asset,
                'rank': rank + 1,
                'momentum_score': scores['composite_score'],
                'current_allocation': current,
                'suggested_adjustment': target_adjustment,
                'action': action
            })
        
        return {
            'date': datetime.now().isoformat(),
            'signals': signals,
            'top_picks': [s['asset'] for s in signals if s['action'] == 'increase'],
            'avoid': [s['asset'] for s in signals if s['action'] == 'decrease']
        }
    
    def trend_following_signals(
        self,
        price_data: Dict[str, pd.Series],
        short_window: int = 50,
        long_window: int = 200
    ) -> Dict[str, Dict[str, Any]]:
        """Generate trend following signals using moving averages"""
        signals = {}
        
        for asset, prices in price_data.items():
            if len(prices) < long_window:
                continue
            
            short_ma = prices.rolling(window=short_window).mean()
            long_ma = prices.rolling(window=long_window).mean()
            
            current_price = prices.iloc[-1]
            current_short = short_ma.iloc[-1]
            current_long = long_ma.iloc[-1]
            
            # Trend direction
            if current_short > current_long * 1.02:
                trend = 'uptrend'
                signal = 'buy'
            elif current_short < current_long * 0.98:
                trend = 'downtrend'
                signal = 'sell'
            else:
                trend = 'sideways'
                signal = 'hold'
            
            # Trend strength
            trend_strength = abs(current_short - current_long) / current_long
            
            signals[asset] = {
                'price': current_price,
                'short_ma': current_short,
                'long_ma': current_long,
                'trend': trend,
                'signal': signal,
                'strength': trend_strength,
                'above_long_ma': current_price > current_long
            }
        
        return signals
