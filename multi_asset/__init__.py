"""
Multi-Asset Class Module
========================

Comprehensive multi-asset class support including:
- Cryptocurrency and DeFi integration
- Real estate investment tracking
- Fixed income analytics
- Alternative investments
- Cross-asset correlation analysis
"""

from .crypto_defi import CryptoPortfolioManager, DeFiYieldOptimizer, CryptoAnalytics
from .real_estate import RealEstateTracker, REITAnalyzer, PropertyValuation
from .fixed_income import FixedIncomeAnalytics, YieldCurveAnalyzer, BondPortfolioManager
from .alternatives import AlternativeInvestments, PrivateEquityTracker, CommodityAnalytics
from .cross_asset import CrossAssetAnalyzer, HedgingRecommendations, RiskParityAllocator, AssetRotationSignals

__all__ = [
    'CryptoPortfolioManager',
    'DeFiYieldOptimizer', 
    'CryptoAnalytics',
    'RealEstateTracker',
    'REITAnalyzer',
    'PropertyValuation',
    'FixedIncomeAnalytics',
    'YieldCurveAnalyzer',
    'BondPortfolioManager',
    'AlternativeInvestments',
    'PrivateEquityTracker',
    'CommodityAnalytics',
    'CrossAssetAnalyzer',
    'HedgingRecommendations',
    'RiskParityAllocator',
    'AssetRotationSignals'
]
