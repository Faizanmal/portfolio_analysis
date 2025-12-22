"""
Alternative Investments
=======================

Portfolio management for alternative investments:
- Private equity tracking
- Commodities analytics
- Hedge fund monitoring
- Collectibles and art
- Infrastructure investments
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging


class AlternativeType(Enum):
    """Types of alternative investments"""
    PRIVATE_EQUITY = "private_equity"
    VENTURE_CAPITAL = "venture_capital"
    HEDGE_FUND = "hedge_fund"
    COMMODITIES = "commodities"
    REAL_ASSETS = "real_assets"
    INFRASTRUCTURE = "infrastructure"
    ART = "art"
    COLLECTIBLES = "collectibles"
    WINE = "wine"
    CRYPTOCURRENCY = "cryptocurrency"  # Sometimes classified as alternative


class PrivateEquityStage(Enum):
    """Private equity investment stages"""
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    GROWTH = "growth"
    LATE_STAGE = "late_stage"
    BUYOUT = "buyout"
    DISTRESSED = "distressed"
    SECONDARY = "secondary"


class CommodityType(Enum):
    """Types of commodities"""
    PRECIOUS_METALS = "precious_metals"
    INDUSTRIAL_METALS = "industrial_metals"
    ENERGY = "energy"
    AGRICULTURE = "agriculture"
    LIVESTOCK = "livestock"
    SOFTS = "softs"


class HedgeFundStrategy(Enum):
    """Hedge fund strategies"""
    LONG_SHORT_EQUITY = "long_short_equity"
    MARKET_NEUTRAL = "market_neutral"
    EVENT_DRIVEN = "event_driven"
    MERGER_ARB = "merger_arbitrage"
    DISTRESSED = "distressed"
    GLOBAL_MACRO = "global_macro"
    CTA_MANAGED_FUTURES = "managed_futures"
    FIXED_INCOME_ARB = "fixed_income_arb"
    MULTI_STRATEGY = "multi_strategy"
    QUANTITATIVE = "quantitative"


@dataclass
class PrivateEquityInvestment:
    """Private equity investment"""
    investment_id: str
    fund_name: str
    vintage_year: int
    stage: PrivateEquityStage
    
    # Commitment and funding
    committed_capital: float = 0.0
    called_capital: float = 0.0
    remaining_commitment: float = 0.0
    distributions: float = 0.0
    
    # Valuation
    nav: float = 0.0  # Net Asset Value
    last_valuation_date: Optional[datetime] = None
    
    # Performance
    irr: float = 0.0  # Internal Rate of Return
    tvpi: float = 0.0  # Total Value to Paid-In
    dpi: float = 0.0  # Distributions to Paid-In
    rvpi: float = 0.0  # Residual Value to Paid-In
    
    # Details
    sector: str = ""
    geography: str = ""
    gp_name: str = ""  # General Partner
    
    def calculate_metrics(self):
        """Calculate performance metrics"""
        self.remaining_commitment = self.committed_capital - self.called_capital
        
        if self.called_capital > 0:
            self.dpi = self.distributions / self.called_capital
            self.rvpi = self.nav / self.called_capital
            self.tvpi = self.dpi + self.rvpi
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'investment_id': self.investment_id,
            'fund_name': self.fund_name,
            'vintage_year': self.vintage_year,
            'stage': self.stage.value,
            'commitment': {
                'committed': self.committed_capital,
                'called': self.called_capital,
                'remaining': self.remaining_commitment,
                'pct_called': self.called_capital / self.committed_capital if self.committed_capital > 0 else 0
            },
            'valuation': {
                'nav': self.nav,
                'distributions': self.distributions,
                'total_value': self.nav + self.distributions
            },
            'performance': {
                'irr': self.irr,
                'tvpi': self.tvpi,
                'dpi': self.dpi,
                'rvpi': self.rvpi
            }
        }


@dataclass
class CommodityPosition:
    """Commodity investment position"""
    position_id: str
    commodity: str
    commodity_type: CommodityType
    
    # Position details
    quantity: float = 0.0
    unit: str = "oz"  # oz, barrels, bushels, etc.
    
    # Pricing
    entry_price: float = 0.0
    current_price: float = 0.0
    market_value: float = 0.0
    
    # For futures
    is_futures: bool = False
    contract_symbol: str = ""
    expiration_date: Optional[datetime] = None
    contract_size: float = 0.0
    
    # Storage (for physical)
    is_physical: bool = False
    storage_cost_annual: float = 0.0
    storage_location: str = ""
    
    def calculate_value(self):
        """Calculate market value"""
        self.market_value = self.quantity * self.current_price
    
    def unrealized_pnl(self) -> float:
        """Calculate unrealized P&L"""
        return (self.current_price - self.entry_price) * self.quantity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'position_id': self.position_id,
            'commodity': self.commodity,
            'type': self.commodity_type.value,
            'quantity': self.quantity,
            'unit': self.unit,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'market_value': self.market_value,
            'unrealized_pnl': self.unrealized_pnl(),
            'return_pct': (self.current_price - self.entry_price) / self.entry_price if self.entry_price > 0 else 0,
            'is_physical': self.is_physical,
            'is_futures': self.is_futures
        }


@dataclass
class HedgeFundInvestment:
    """Hedge fund investment"""
    investment_id: str
    fund_name: str
    strategy: HedgeFundStrategy
    
    # Investment
    investment_amount: float = 0.0
    current_value: float = 0.0
    investment_date: Optional[datetime] = None
    
    # Terms
    management_fee: float = 0.02  # 2%
    performance_fee: float = 0.20  # 20%
    hurdle_rate: float = 0.0
    high_water_mark: float = 0.0
    
    # Liquidity
    lock_up_period_months: int = 12
    redemption_notice_days: int = 90
    redemption_frequency: str = "quarterly"
    gate_provision: float = 0.0
    
    # Performance
    ytd_return: float = 0.0
    one_year_return: float = 0.0
    since_inception_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    
    # Risk
    beta_to_market: float = 0.0
    correlation_to_sp500: float = 0.0
    
    def is_locked(self) -> bool:
        """Check if investment is still in lock-up"""
        if self.investment_date is None:
            return False
        lock_up_end = self.investment_date + timedelta(days=self.lock_up_period_months * 30)
        return datetime.now() < lock_up_end
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'investment_id': self.investment_id,
            'fund_name': self.fund_name,
            'strategy': self.strategy.value,
            'investment': {
                'initial': self.investment_amount,
                'current': self.current_value,
                'gain_loss': self.current_value - self.investment_amount
            },
            'terms': {
                'management_fee': self.management_fee,
                'performance_fee': self.performance_fee,
                'lock_up_months': self.lock_up_period_months,
                'is_locked': self.is_locked()
            },
            'performance': {
                'ytd': self.ytd_return,
                '1y': self.one_year_return,
                'since_inception': self.since_inception_return,
                'sharpe': self.sharpe_ratio,
                'max_drawdown': self.max_drawdown
            },
            'risk': {
                'volatility': self.volatility,
                'beta': self.beta_to_market,
                'correlation': self.correlation_to_sp500
            }
        }


@dataclass
class Collectible:
    """Art, wine, or other collectible investment"""
    item_id: str
    name: str
    category: str  # art, wine, watches, cars, etc.
    
    # Details
    artist_maker: str = ""
    year: int = 0
    medium: str = ""
    dimensions: str = ""
    provenance: str = ""
    condition: str = ""
    
    # Valuation
    purchase_price: float = 0.0
    purchase_date: Optional[datetime] = None
    current_value: float = 0.0
    last_appraisal_date: Optional[datetime] = None
    appraiser: str = ""
    
    # Insurance and storage
    insured_value: float = 0.0
    annual_insurance_cost: float = 0.0
    storage_location: str = ""
    annual_storage_cost: float = 0.0
    
    def appreciation(self) -> float:
        """Calculate appreciation"""
        if self.purchase_price <= 0:
            return 0
        return (self.current_value - self.purchase_price) / self.purchase_price
    
    def annual_return(self) -> float:
        """Calculate annualized return"""
        if self.purchase_date is None or self.purchase_price <= 0:
            return 0
        
        years = (datetime.now() - self.purchase_date).days / 365.25
        if years <= 0:
            return 0
        
        return (self.current_value / self.purchase_price) ** (1/years) - 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'item_id': self.item_id,
            'name': self.name,
            'category': self.category,
            'details': {
                'artist_maker': self.artist_maker,
                'year': self.year,
                'medium': self.medium,
                'condition': self.condition
            },
            'valuation': {
                'purchase_price': self.purchase_price,
                'current_value': self.current_value,
                'appreciation': self.appreciation(),
                'annual_return': self.annual_return()
            },
            'costs': {
                'annual_insurance': self.annual_insurance_cost,
                'annual_storage': self.annual_storage_cost,
                'total_annual': self.annual_insurance_cost + self.annual_storage_cost
            }
        }


class PrivateEquityTracker:
    """
    Tracks private equity and venture capital investments.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("pe_tracker")
        self.investments: Dict[str, PrivateEquityInvestment] = {}
    
    def add_investment(self, investment: PrivateEquityInvestment):
        """Add PE investment"""
        investment.calculate_metrics()
        self.investments[investment.investment_id] = investment
        self.logger.info(f"Added PE investment: {investment.fund_name}")
    
    def record_capital_call(
        self,
        investment_id: str,
        amount: float,
        call_date: datetime = None
    ):
        """Record a capital call"""
        if investment_id not in self.investments:
            self.logger.error(f"Investment not found: {investment_id}")
            return
        
        inv = self.investments[investment_id]
        inv.called_capital += amount
        inv.calculate_metrics()
        self.logger.info(f"Recorded capital call: ${amount:,.2f} for {inv.fund_name}")
    
    def record_distribution(
        self,
        investment_id: str,
        amount: float,
        dist_date: datetime = None
    ):
        """Record a distribution"""
        if investment_id not in self.investments:
            self.logger.error(f"Investment not found: {investment_id}")
            return
        
        inv = self.investments[investment_id]
        inv.distributions += amount
        inv.calculate_metrics()
        self.logger.info(f"Recorded distribution: ${amount:,.2f} from {inv.fund_name}")
    
    def update_nav(
        self,
        investment_id: str,
        nav: float,
        valuation_date: datetime = None
    ):
        """Update NAV"""
        if investment_id not in self.investments:
            return
        
        inv = self.investments[investment_id]
        inv.nav = nav
        inv.last_valuation_date = valuation_date or datetime.now()
        inv.calculate_metrics()
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get PE portfolio summary"""
        total_committed = sum(i.committed_capital for i in self.investments.values())
        total_called = sum(i.called_capital for i in self.investments.values())
        total_remaining = sum(i.remaining_commitment for i in self.investments.values())
        total_nav = sum(i.nav for i in self.investments.values())
        total_distributions = sum(i.distributions for i in self.investments.values())
        
        # Weighted metrics
        weighted_irr = 0
        weighted_tvpi = 0
        if total_called > 0:
            for inv in self.investments.values():
                weight = inv.called_capital / total_called
                weighted_irr += inv.irr * weight
                weighted_tvpi += inv.tvpi * weight
        
        # By stage
        by_stage = {}
        for inv in self.investments.values():
            stage = inv.stage.value
            if stage not in by_stage:
                by_stage[stage] = {'nav': 0, 'count': 0}
            by_stage[stage]['nav'] += inv.nav
            by_stage[stage]['count'] += 1
        
        # By vintage
        by_vintage = {}
        for inv in self.investments.values():
            year = str(inv.vintage_year)
            if year not in by_vintage:
                by_vintage[year] = {'nav': 0, 'count': 0}
            by_vintage[year]['nav'] += inv.nav
            by_vintage[year]['count'] += 1
        
        return {
            'total_committed': total_committed,
            'total_called': total_called,
            'remaining_commitment': total_remaining,
            'total_nav': total_nav,
            'total_distributions': total_distributions,
            'total_value': total_nav + total_distributions,
            'portfolio_tvpi': (total_nav + total_distributions) / total_called if total_called > 0 else 0,
            'portfolio_dpi': total_distributions / total_called if total_called > 0 else 0,
            'weighted_irr': weighted_irr,
            'weighted_tvpi': weighted_tvpi,
            'investment_count': len(self.investments),
            'by_stage': by_stage,
            'by_vintage': by_vintage
        }
    
    def get_cash_flow_forecast(self, quarters: int = 8) -> Dict[str, Any]:
        """Forecast future capital calls and distributions"""
        # Simplified J-curve based forecast
        forecast = []
        remaining = sum(i.remaining_commitment for i in self.investments.values())
        
        avg_call_rate = 0.10  # 10% of remaining per quarter
        avg_dist_rate = 0.05  # 5% of NAV per quarter
        
        for q in range(1, quarters + 1):
            expected_calls = remaining * avg_call_rate
            remaining -= expected_calls
            
            current_nav = sum(i.nav for i in self.investments.values())
            expected_distributions = current_nav * avg_dist_rate * (q / 4)  # Increase over time
            
            net_cash_flow = expected_distributions - expected_calls
            
            forecast.append({
                'quarter': q,
                'expected_calls': expected_calls,
                'expected_distributions': expected_distributions,
                'net_cash_flow': net_cash_flow
            })
        
        return {
            'forecast': forecast,
            'total_expected_calls': sum(f['expected_calls'] for f in forecast),
            'total_expected_distributions': sum(f['expected_distributions'] for f in forecast)
        }


class CommodityAnalytics:
    """
    Commodity portfolio analytics.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("commodity_analytics")
        self.positions: Dict[str, CommodityPosition] = {}
        
        # Commodity benchmarks
        self.benchmarks = {
            'gold': {'volatility': 0.15, 'correlation_stocks': -0.1},
            'silver': {'volatility': 0.25, 'correlation_stocks': 0.1},
            'oil': {'volatility': 0.35, 'correlation_stocks': 0.3},
            'natural_gas': {'volatility': 0.45, 'correlation_stocks': 0.1},
            'copper': {'volatility': 0.25, 'correlation_stocks': 0.4},
            'corn': {'volatility': 0.25, 'correlation_stocks': 0.1},
            'wheat': {'volatility': 0.30, 'correlation_stocks': 0.1},
        }
    
    def add_position(self, position: CommodityPosition):
        """Add commodity position"""
        position.calculate_value()
        self.positions[position.position_id] = position
        self.logger.info(f"Added commodity position: {position.commodity}")
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get commodity portfolio summary"""
        total_value = sum(p.market_value for p in self.positions.values())
        total_pnl = sum(p.unrealized_pnl() for p in self.positions.values())
        
        by_type = {}
        for pos in self.positions.values():
            ctype = pos.commodity_type.value
            if ctype not in by_type:
                by_type[ctype] = {'value': 0, 'pnl': 0}
            by_type[ctype]['value'] += pos.market_value
            by_type[ctype]['pnl'] += pos.unrealized_pnl()
        
        return {
            'total_value': total_value,
            'total_unrealized_pnl': total_pnl,
            'total_return_pct': total_pnl / (total_value - total_pnl) if (total_value - total_pnl) != 0 else 0,
            'position_count': len(self.positions),
            'by_type': by_type
        }
    
    def calculate_portfolio_volatility(self) -> float:
        """Estimate portfolio volatility based on commodity mix"""
        total_value = sum(p.market_value for p in self.positions.values())
        if total_value == 0:
            return 0
        
        weighted_vol = 0
        for pos in self.positions.values():
            commodity_lower = pos.commodity.lower()
            vol = self.benchmarks.get(commodity_lower, {}).get('volatility', 0.25)
            weight = pos.market_value / total_value
            weighted_vol += vol * weight
        
        return weighted_vol
    
    def get_expiration_calendar(self) -> List[Dict[str, Any]]:
        """Get futures expiration calendar"""
        futures_positions = [p for p in self.positions.values() if p.is_futures and p.expiration_date]
        futures_positions.sort(key=lambda x: x.expiration_date)
        
        calendar = []
        for pos in futures_positions:
            days_to_expiry = (pos.expiration_date - datetime.now()).days
            calendar.append({
                'commodity': pos.commodity,
                'contract': pos.contract_symbol,
                'expiration': pos.expiration_date.isoformat(),
                'days_to_expiry': days_to_expiry,
                'value': pos.market_value,
                'needs_rollover': days_to_expiry < 30
            })
        
        return calendar


class AlternativeInvestments:
    """
    Unified alternative investments manager.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("alternatives")
        self.pe_tracker = PrivateEquityTracker()
        self.commodity_analytics = CommodityAnalytics()
        self.hedge_funds: Dict[str, HedgeFundInvestment] = {}
        self.collectibles: Dict[str, Collectible] = {}
    
    def add_hedge_fund(self, investment: HedgeFundInvestment):
        """Add hedge fund investment"""
        self.hedge_funds[investment.investment_id] = investment
    
    def add_collectible(self, item: Collectible):
        """Add collectible"""
        self.collectibles[item.item_id] = item
    
    def get_total_alternatives_value(self) -> Dict[str, float]:
        """Get total value across all alternative investments"""
        pe_value = sum(i.nav for i in self.pe_tracker.investments.values())
        commodity_value = sum(p.market_value for p in self.commodity_analytics.positions.values())
        hf_value = sum(h.current_value for h in self.hedge_funds.values())
        collectibles_value = sum(c.current_value for c in self.collectibles.values())
        
        total = pe_value + commodity_value + hf_value + collectibles_value
        
        return {
            'total': total,
            'private_equity': pe_value,
            'commodities': commodity_value,
            'hedge_funds': hf_value,
            'collectibles': collectibles_value,
            'allocation': {
                'private_equity': pe_value / total if total > 0 else 0,
                'commodities': commodity_value / total if total > 0 else 0,
                'hedge_funds': hf_value / total if total > 0 else 0,
                'collectibles': collectibles_value / total if total > 0 else 0
            }
        }
    
    def get_liquidity_analysis(self) -> Dict[str, Any]:
        """Analyze liquidity across alternative investments"""
        # Highly liquid (< 1 week)
        liquid = sum(p.market_value for p in self.commodity_analytics.positions.values() if not p.is_physical)
        
        # Moderate liquidity (1-3 months)
        moderate = sum(h.current_value for h in self.hedge_funds.values() 
                      if not h.is_locked() and h.redemption_notice_days <= 90)
        
        # Low liquidity (> 3 months)
        low_liquidity = sum(h.current_value for h in self.hedge_funds.values() 
                           if h.is_locked() or h.redemption_notice_days > 90)
        
        # Illiquid
        illiquid = (
            sum(i.nav for i in self.pe_tracker.investments.values()) +
            sum(c.current_value for c in self.collectibles.values()) +
            sum(p.market_value for p in self.commodity_analytics.positions.values() if p.is_physical)
        )
        
        total = liquid + moderate + low_liquidity + illiquid
        
        return {
            'liquid': {'value': liquid, 'pct': liquid/total if total > 0 else 0, 'timeframe': '< 1 week'},
            'moderate': {'value': moderate, 'pct': moderate/total if total > 0 else 0, 'timeframe': '1-3 months'},
            'low': {'value': low_liquidity, 'pct': low_liquidity/total if total > 0 else 0, 'timeframe': '> 3 months'},
            'illiquid': {'value': illiquid, 'pct': illiquid/total if total > 0 else 0, 'timeframe': 'years'},
            'total': total,
            'weighted_avg_liquidity_days': (
                liquid * 3 + moderate * 60 + low_liquidity * 180 + illiquid * 730
            ) / total if total > 0 else 0
        }
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive alternatives report"""
        return {
            'summary': self.get_total_alternatives_value(),
            'liquidity': self.get_liquidity_analysis(),
            'private_equity': self.pe_tracker.get_portfolio_summary(),
            'commodities': self.commodity_analytics.get_portfolio_summary(),
            'hedge_funds': {
                'count': len(self.hedge_funds),
                'total_value': sum(h.current_value for h in self.hedge_funds.values()),
                'by_strategy': self._get_hf_by_strategy()
            },
            'collectibles': {
                'count': len(self.collectibles),
                'total_value': sum(c.current_value for c in self.collectibles.values()),
                'by_category': self._get_collectibles_by_category()
            }
        }
    
    def _get_hf_by_strategy(self) -> Dict[str, Dict]:
        """Group hedge funds by strategy"""
        by_strategy = {}
        for hf in self.hedge_funds.values():
            strategy = hf.strategy.value
            if strategy not in by_strategy:
                by_strategy[strategy] = {'value': 0, 'count': 0, 'avg_return': 0}
            by_strategy[strategy]['value'] += hf.current_value
            by_strategy[strategy]['count'] += 1
            by_strategy[strategy]['avg_return'] += hf.ytd_return
        
        # Calculate averages
        for strategy in by_strategy:
            if by_strategy[strategy]['count'] > 0:
                by_strategy[strategy]['avg_return'] /= by_strategy[strategy]['count']
        
        return by_strategy
    
    def _get_collectibles_by_category(self) -> Dict[str, Dict]:
        """Group collectibles by category"""
        by_category = {}
        for item in self.collectibles.values():
            cat = item.category
            if cat not in by_category:
                by_category[cat] = {'value': 0, 'count': 0, 'total_appreciation': 0}
            by_category[cat]['value'] += item.current_value
            by_category[cat]['count'] += 1
            by_category[cat]['total_appreciation'] += item.appreciation() * item.current_value
        
        return by_category
