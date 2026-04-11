"""
Real Estate Investment Tracking
===============================

Comprehensive real estate portfolio management:
- REIT analysis and tracking
- Direct property valuation
- Rental income tracking
- Real estate market analytics
- Property comparables analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging


class PropertyType(Enum):
    """Types of real estate properties"""
    RESIDENTIAL_SINGLE = "residential_single_family"
    RESIDENTIAL_MULTI = "residential_multi_family"
    COMMERCIAL_OFFICE = "commercial_office"
    COMMERCIAL_RETAIL = "commercial_retail"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    LAND = "land"
    HOTEL = "hotel"
    DATA_CENTER = "data_center"
    HEALTHCARE = "healthcare"
    SELF_STORAGE = "self_storage"


class REITSector(Enum):
    """REIT sectors"""
    RESIDENTIAL = "residential"
    OFFICE = "office"
    RETAIL = "retail"
    INDUSTRIAL = "industrial"
    HEALTHCARE = "healthcare"
    HOTEL = "hotel"
    DATA_CENTER = "data_center"
    INFRASTRUCTURE = "infrastructure"
    SPECIALTY = "specialty"
    DIVERSIFIED = "diversified"


@dataclass
class Property:
    """Direct real estate property"""
    property_id: str
    name: str
    property_type: PropertyType
    address: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    
    # Valuation
    purchase_price: float = 0.0
    purchase_date: Optional[datetime] = None
    current_value: float = 0.0
    last_appraisal_date: Optional[datetime] = None
    
    # Property details
    square_feet: float = 0.0
    lot_size: float = 0.0
    year_built: int = 0
    bedrooms: int = 0
    bathrooms: float = 0.0
    units: int = 1
    
    # Income
    monthly_rent: float = 0.0
    vacancy_rate: float = 0.05
    annual_gross_income: float = 0.0
    annual_operating_expenses: float = 0.0
    annual_noi: float = 0.0
    
    # Financing
    mortgage_balance: float = 0.0
    mortgage_rate: float = 0.0
    monthly_payment: float = 0.0
    
    # Returns
    cap_rate: float = 0.0
    cash_on_cash_return: float = 0.0
    equity: float = 0.0
    ltv_ratio: float = 0.0
    
    def calculate_metrics(self):
        """Calculate derived metrics"""
        # Annual income
        self.annual_gross_income = self.monthly_rent * 12 * self.units * (1 - self.vacancy_rate)
        
        # NOI
        self.annual_noi = self.annual_gross_income - self.annual_operating_expenses
        
        # Cap rate
        if self.current_value > 0:
            self.cap_rate = self.annual_noi / self.current_value
        
        # Equity
        self.equity = self.current_value - self.mortgage_balance
        
        # LTV
        if self.current_value > 0:
            self.ltv_ratio = self.mortgage_balance / self.current_value
        
        # Cash on cash return
        annual_debt_service = self.monthly_payment * 12
        annual_cash_flow = self.annual_noi - annual_debt_service
        down_payment = self.purchase_price - self.mortgage_balance
        if down_payment > 0:
            self.cash_on_cash_return = annual_cash_flow / down_payment
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'property_id': self.property_id,
            'name': self.name,
            'type': self.property_type.value,
            'location': {
                'address': self.address,
                'city': self.city,
                'state': self.state,
                'zip': self.zip_code
            },
            'valuation': {
                'purchase_price': self.purchase_price,
                'current_value': self.current_value,
                'appreciation': (self.current_value - self.purchase_price) / self.purchase_price if self.purchase_price > 0 else 0
            },
            'income': {
                'monthly_rent': self.monthly_rent,
                'annual_gross': self.annual_gross_income,
                'annual_noi': self.annual_noi,
                'vacancy_rate': self.vacancy_rate
            },
            'metrics': {
                'cap_rate': self.cap_rate,
                'cash_on_cash': self.cash_on_cash_return,
                'equity': self.equity,
                'ltv': self.ltv_ratio
            },
            'details': {
                'sqft': self.square_feet,
                'units': self.units,
                'year_built': self.year_built
            }
        }


@dataclass
class REIT:
    """Real Estate Investment Trust"""
    symbol: str
    name: str
    sector: REITSector
    
    # Price data
    current_price: float = 0.0
    shares_held: float = 0.0
    value: float = 0.0
    
    # Dividend info
    dividend_yield: float = 0.0
    annual_dividend: float = 0.0
    dividend_frequency: str = "quarterly"
    ex_dividend_date: Optional[datetime] = None
    
    # Fundamentals
    ffo_per_share: float = 0.0  # Funds From Operations
    affo_per_share: float = 0.0  # Adjusted FFO
    nav_per_share: float = 0.0  # Net Asset Value
    price_to_ffo: float = 0.0
    price_to_nav: float = 0.0
    
    # Portfolio info
    property_count: int = 0
    total_sqft: float = 0.0
    occupancy_rate: float = 0.0
    avg_lease_term: float = 0.0
    
    # Debt metrics
    debt_to_ebitda: float = 0.0
    interest_coverage: float = 0.0
    
    def calculate_metrics(self):
        """Calculate derived metrics"""
        self.value = self.current_price * self.shares_held
        
        if self.ffo_per_share > 0:
            self.price_to_ffo = self.current_price / self.ffo_per_share
        
        if self.nav_per_share > 0:
            self.price_to_nav = self.current_price / self.nav_per_share
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'sector': self.sector.value,
            'holdings': {
                'shares': self.shares_held,
                'value': self.value,
                'price': self.current_price
            },
            'dividend': {
                'yield': self.dividend_yield,
                'annual': self.annual_dividend,
                'frequency': self.dividend_frequency
            },
            'valuation': {
                'price_to_ffo': self.price_to_ffo,
                'price_to_nav': self.price_to_nav,
                'nav_discount': (self.nav_per_share - self.current_price) / self.nav_per_share if self.nav_per_share > 0 else 0
            },
            'fundamentals': {
                'ffo_per_share': self.ffo_per_share,
                'affo_per_share': self.affo_per_share,
                'occupancy': self.occupancy_rate,
                'property_count': self.property_count
            }
        }


class RealEstateTracker:
    """
    Tracks real estate investments including REITs and direct properties.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("real_estate_tracker")
        self.properties: Dict[str, Property] = {}
        self.reits: Dict[str, REIT] = {}
    
    def add_property(self, property: Property) -> str:
        """Add a property to the portfolio"""
        property.calculate_metrics()
        self.properties[property.property_id] = property
        self.logger.info(f"Added property: {property.name}")
        return property.property_id
    
    def add_reit(self, reit: REIT) -> str:
        """Add a REIT holding to the portfolio"""
        reit.calculate_metrics()
        self.reits[reit.symbol] = reit
        self.logger.info(f"Added REIT: {reit.symbol}")
        return reit.symbol
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get summary of real estate portfolio"""
        # Properties summary
        total_property_value = sum(p.current_value for p in self.properties.values())
        total_property_equity = sum(p.equity for p in self.properties.values())
        total_annual_noi = sum(p.annual_noi for p in self.properties.values())
        weighted_cap_rate = sum(p.cap_rate * p.current_value for p in self.properties.values()) / total_property_value if total_property_value > 0 else 0
        
        # REITs summary
        total_reit_value = sum(r.value for r in self.reits.values())
        total_annual_dividends = sum(r.annual_dividend * r.shares_held for r in self.reits.values())
        weighted_yield = sum(r.dividend_yield * r.value for r in self.reits.values()) / total_reit_value if total_reit_value > 0 else 0
        
        return {
            'total_value': total_property_value + total_reit_value,
            'direct_properties': {
                'count': len(self.properties),
                'total_value': total_property_value,
                'total_equity': total_property_equity,
                'annual_noi': total_annual_noi,
                'weighted_cap_rate': weighted_cap_rate
            },
            'reits': {
                'count': len(self.reits),
                'total_value': total_reit_value,
                'annual_dividends': total_annual_dividends,
                'weighted_yield': weighted_yield
            },
            'allocation': {
                'direct': total_property_value / (total_property_value + total_reit_value) if (total_property_value + total_reit_value) > 0 else 0,
                'reits': total_reit_value / (total_property_value + total_reit_value) if (total_property_value + total_reit_value) > 0 else 0
            }
        }
    
    def get_income_summary(self) -> Dict[str, Any]:
        """Get income summary from real estate"""
        property_income = {}
        for prop in self.properties.values():
            property_income[prop.property_id] = {
                'name': prop.name,
                'monthly_gross': prop.monthly_rent * prop.units,
                'monthly_net': prop.annual_noi / 12,
                'cash_flow': (prop.annual_noi - prop.monthly_payment * 12) / 12
            }
        
        reit_income = {}
        for reit in self.reits.values():
            reit_income[reit.symbol] = {
                'name': reit.name,
                'quarterly_dividend': reit.annual_dividend * reit.shares_held / 4,
                'annual_dividend': reit.annual_dividend * reit.shares_held
            }
        
        total_monthly_property = sum(v['cash_flow'] for v in property_income.values())
        total_annual_reit = sum(v['annual_dividend'] for v in reit_income.values())
        
        return {
            'property_income': property_income,
            'reit_income': reit_income,
            'totals': {
                'monthly_property_cash_flow': total_monthly_property,
                'annual_reit_dividends': total_annual_reit,
                'total_annual_income': total_monthly_property * 12 + total_annual_reit
            }
        }


class REITAnalyzer:
    """
    Advanced REIT analysis and screening.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("reit_analyzer")
        
        # Sector benchmarks
        self.sector_benchmarks = {
            REITSector.RESIDENTIAL: {'avg_cap_rate': 0.05, 'avg_yield': 0.035, 'avg_occupancy': 0.95},
            REITSector.OFFICE: {'avg_cap_rate': 0.065, 'avg_yield': 0.045, 'avg_occupancy': 0.88},
            REITSector.RETAIL: {'avg_cap_rate': 0.06, 'avg_yield': 0.05, 'avg_occupancy': 0.92},
            REITSector.INDUSTRIAL: {'avg_cap_rate': 0.045, 'avg_yield': 0.025, 'avg_occupancy': 0.97},
            REITSector.DATA_CENTER: {'avg_cap_rate': 0.04, 'avg_yield': 0.02, 'avg_occupancy': 0.98},
            REITSector.HEALTHCARE: {'avg_cap_rate': 0.055, 'avg_yield': 0.055, 'avg_occupancy': 0.90},
        }
    
    def analyze_reit(self, reit: REIT) -> Dict[str, Any]:
        """Comprehensive REIT analysis"""
        sector_bench = self.sector_benchmarks.get(reit.sector, {})
        
        # Valuation analysis
        nav_discount = (reit.nav_per_share - reit.current_price) / reit.nav_per_share if reit.nav_per_share > 0 else 0
        
        valuation_score = 0
        if nav_discount > 0.1:  # Trading at > 10% discount to NAV
            valuation_score += 2
        elif nav_discount > 0:
            valuation_score += 1
        
        if reit.price_to_ffo < 15:
            valuation_score += 2
        elif reit.price_to_ffo < 20:
            valuation_score += 1
        
        # Quality analysis
        quality_score = 0
        if reit.occupancy_rate > sector_bench.get('avg_occupancy', 0.9):
            quality_score += 2
        
        if reit.interest_coverage > 3:
            quality_score += 2
        elif reit.interest_coverage > 2:
            quality_score += 1
        
        if reit.debt_to_ebitda < 6:
            quality_score += 1
        
        # Income analysis
        income_score = 0
        if reit.dividend_yield > sector_bench.get('avg_yield', 0.04):
            income_score += 2
        
        # AFFO payout ratio (lower is more sustainable)
        affo_payout = reit.annual_dividend / reit.affo_per_share if reit.affo_per_share > 0 else 1
        if affo_payout < 0.75:
            income_score += 2
        elif affo_payout < 0.90:
            income_score += 1
        
        total_score = valuation_score + quality_score + income_score
        
        return {
            'symbol': reit.symbol,
            'sector': reit.sector.value,
            'scores': {
                'valuation': valuation_score,
                'quality': quality_score,
                'income': income_score,
                'total': total_score,
                'rating': 'Strong Buy' if total_score >= 8 else 'Buy' if total_score >= 6 else 'Hold' if total_score >= 4 else 'Sell'
            },
            'valuation': {
                'nav_discount': nav_discount,
                'price_to_ffo': reit.price_to_ffo,
                'vs_sector_yield': reit.dividend_yield - sector_bench.get('avg_yield', 0)
            },
            'quality': {
                'occupancy': reit.occupancy_rate,
                'vs_sector_occupancy': reit.occupancy_rate - sector_bench.get('avg_occupancy', 0),
                'interest_coverage': reit.interest_coverage,
                'debt_to_ebitda': reit.debt_to_ebitda
            },
            'income': {
                'yield': reit.dividend_yield,
                'affo_payout': affo_payout,
                'dividend_safety': 'Safe' if affo_payout < 0.75 else 'Moderate' if affo_payout < 0.90 else 'At Risk'
            }
        }
    
    def screen_reits(
        self,
        reits: List[REIT],
        min_yield: float = 0.0,
        max_price_to_ffo: float = 100.0,
        min_occupancy: float = 0.0,
        sectors: Optional[List[REITSector]] = None
    ) -> List[Dict[str, Any]]:
        """Screen REITs based on criteria"""
        results = []
        
        for reit in reits:
            # Apply filters
            if reit.dividend_yield < min_yield:
                continue
            if reit.price_to_ffo > max_price_to_ffo:
                continue
            if reit.occupancy_rate < min_occupancy:
                continue
            if sectors and reit.sector not in sectors:
                continue
            
            analysis = self.analyze_reit(reit)
            results.append(analysis)
        
        # Sort by total score
        results.sort(key=lambda x: x['scores']['total'], reverse=True)
        
        return results
    
    def get_sector_allocation(self, reits: List[REIT]) -> Dict[str, float]:
        """Get allocation by REIT sector"""
        total_value = sum(r.value for r in reits)
        
        if total_value == 0:
            return {}
        
        allocation = {}
        for reit in reits:
            sector = reit.sector.value
            if sector not in allocation:
                allocation[sector] = 0
            allocation[sector] += reit.value / total_value
        
        return allocation


class PropertyValuation:
    """
    Property valuation and comparables analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("property_valuation")
    
    def income_approach(
        self,
        annual_noi: float,
        cap_rate: float
    ) -> float:
        """Value property using income approach"""
        if cap_rate <= 0:
            return 0
        return annual_noi / cap_rate
    
    def sales_comparison_approach(
        self,
        comparables: List[Dict[str, Any]],
        subject_property: Property
    ) -> Dict[str, Any]:
        """Value property using sales comparison approach"""
        if not comparables:
            return {'error': 'No comparables provided'}
        
        # Calculate price per sqft from comparables
        prices_per_sqft = []
        for comp in comparables:
            if comp.get('sqft', 0) > 0:
                price_per_sqft = comp.get('sale_price', 0) / comp['sqft']
                prices_per_sqft.append(price_per_sqft)
        
        if not prices_per_sqft:
            return {'error': 'Invalid comparable data'}
        
        avg_price_per_sqft = np.mean(prices_per_sqft)
        median_price_per_sqft = np.median(prices_per_sqft)
        
        # Apply adjustments based on property characteristics
        adjustment_factor = 1.0
        
        # Age adjustment
        avg_comp_age = np.mean([datetime.now().year - c.get('year_built', 2000) for c in comparables])
        subject_age = datetime.now().year - subject_property.year_built if subject_property.year_built > 0 else avg_comp_age
        
        if subject_age < avg_comp_age:
            adjustment_factor += 0.01 * (avg_comp_age - subject_age)  # Newer = premium
        else:
            adjustment_factor -= 0.01 * (subject_age - avg_comp_age)  # Older = discount
        
        estimated_value = subject_property.square_feet * avg_price_per_sqft * adjustment_factor
        
        return {
            'estimated_value': estimated_value,
            'avg_price_per_sqft': avg_price_per_sqft,
            'median_price_per_sqft': median_price_per_sqft,
            'adjustment_factor': adjustment_factor,
            'comparable_count': len(comparables),
            'value_range': {
                'low': subject_property.square_feet * min(prices_per_sqft),
                'high': subject_property.square_feet * max(prices_per_sqft)
            }
        }
    
    def gross_rent_multiplier(
        self,
        monthly_gross_rent: float,
        market_grm: float
    ) -> float:
        """Value property using GRM approach"""
        return monthly_gross_rent * 12 * market_grm
    
    def calculate_roi_metrics(
        self,
        property: Property,
        holding_period_years: int = 5,
        appreciation_rate: float = 0.03,
        rent_growth_rate: float = 0.02
    ) -> Dict[str, Any]:
        """Calculate projected ROI metrics"""
        # Initial investment
        down_payment = property.purchase_price - property.mortgage_balance
        closing_costs = property.purchase_price * 0.03
        initial_investment = down_payment + closing_costs
        
        # Project cash flows
        annual_cash_flows = []
        current_noi = property.annual_noi
        annual_debt_service = property.monthly_payment * 12
        
        for year in range(1, holding_period_years + 1):
            if year > 1:
                current_noi *= (1 + rent_growth_rate)
            
            cash_flow = current_noi - annual_debt_service
            annual_cash_flows.append(cash_flow)
        
        # Terminal value
        future_value = property.current_value * ((1 + appreciation_rate) ** holding_period_years)
        selling_costs = future_value * 0.06  # Agent fees, etc.
        
        # Approximate remaining mortgage (simplified)
        mortgage_paydown_rate = 0.02  # ~2% of balance per year
        remaining_mortgage = property.mortgage_balance * ((1 - mortgage_paydown_rate) ** holding_period_years)
        
        terminal_equity = future_value - remaining_mortgage - selling_costs
        
        # Total return
        total_cash_flow = sum(annual_cash_flows)
        equity_gain = terminal_equity - down_payment
        total_profit = total_cash_flow + equity_gain
        
        # IRR calculation (simplified)
        cash_flows_for_irr = [-initial_investment] + annual_cash_flows[:-1] + [annual_cash_flows[-1] + terminal_equity]
        irr = np.irr(cash_flows_for_irr) if all(cf != 0 for cf in cash_flows_for_irr) else 0
        
        return {
            'initial_investment': initial_investment,
            'holding_period_years': holding_period_years,
            'annual_cash_flows': annual_cash_flows,
            'total_cash_flow': total_cash_flow,
            'future_property_value': future_value,
            'terminal_equity': terminal_equity,
            'equity_gain': equity_gain,
            'total_profit': total_profit,
            'total_return_pct': total_profit / initial_investment,
            'annualized_return': (1 + total_profit / initial_investment) ** (1/holding_period_years) - 1,
            'irr': irr
        }
