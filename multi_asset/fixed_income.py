"""
Fixed Income Analytics
=====================

Comprehensive fixed income portfolio management:
- Bond portfolio analytics
- Yield curve analysis
- Duration and convexity calculations
- Credit risk assessment
- Interest rate scenario analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy.optimize import brentq
from scipy.interpolate import CubicSpline


class BondType(Enum):
    """Types of bonds"""
    TREASURY = "treasury"
    CORPORATE = "corporate"
    MUNICIPAL = "municipal"
    AGENCY = "agency"
    MORTGAGE_BACKED = "mbs"
    ASSET_BACKED = "abs"
    CONVERTIBLE = "convertible"
    HIGH_YIELD = "high_yield"
    EMERGING_MARKET = "emerging_market"
    TIPS = "tips"  # Treasury Inflation Protected


class CreditRating(Enum):
    """Credit ratings"""
    AAA = "AAA"
    AA_PLUS = "AA+"
    AA = "AA"
    AA_MINUS = "AA-"
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    BBB_PLUS = "BBB+"
    BBB = "BBB"
    BBB_MINUS = "BBB-"
    BB_PLUS = "BB+"
    BB = "BB"
    BB_MINUS = "BB-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"


@dataclass
class Bond:
    """Fixed income security representation"""
    bond_id: str
    name: str
    bond_type: BondType
    issuer: str
    
    # Bond terms
    face_value: float = 1000.0
    coupon_rate: float = 0.0  # Annual coupon rate
    coupon_frequency: int = 2  # Payments per year
    maturity_date: datetime = None
    issue_date: datetime = None
    
    # Holdings
    quantity: int = 0
    purchase_price: float = 0.0
    current_price: float = 0.0
    
    # Yield metrics
    ytm: float = 0.0  # Yield to maturity
    current_yield: float = 0.0
    yield_to_call: float = 0.0
    
    # Risk metrics
    duration: float = 0.0  # Modified duration
    macaulay_duration: float = 0.0
    convexity: float = 0.0
    
    # Credit
    credit_rating: CreditRating = CreditRating.BBB
    spread_to_treasury: float = 0.0
    
    # Optionality
    is_callable: bool = False
    call_date: Optional[datetime] = None
    call_price: float = 0.0
    is_putable: bool = False
    
    def years_to_maturity(self) -> float:
        """Calculate years to maturity"""
        if self.maturity_date is None:
            return 0.0
        days = (self.maturity_date - datetime.now()).days
        return max(0, days / 365.25)
    
    def accrued_interest(self) -> float:
        """Calculate accrued interest"""
        if self.coupon_rate == 0:
            return 0.0
        
        coupon_payment = self.face_value * self.coupon_rate / self.coupon_frequency
        days_in_period = 365.25 / self.coupon_frequency
        
        # Simplified - assume we're halfway through current period
        days_since_coupon = days_in_period / 2
        
        return coupon_payment * (days_since_coupon / days_in_period)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'bond_id': self.bond_id,
            'name': self.name,
            'type': self.bond_type.value,
            'issuer': self.issuer,
            'terms': {
                'face_value': self.face_value,
                'coupon_rate': self.coupon_rate,
                'coupon_frequency': self.coupon_frequency,
                'maturity_date': self.maturity_date.isoformat() if self.maturity_date else None,
                'years_to_maturity': self.years_to_maturity()
            },
            'holdings': {
                'quantity': self.quantity,
                'purchase_price': self.purchase_price,
                'current_price': self.current_price,
                'market_value': self.current_price * self.quantity / 100 * self.face_value
            },
            'yield': {
                'ytm': self.ytm,
                'current_yield': self.current_yield,
                'spread_to_treasury': self.spread_to_treasury
            },
            'risk': {
                'duration': self.duration,
                'convexity': self.convexity,
                'credit_rating': self.credit_rating.value
            }
        }


@dataclass
class YieldCurvePoint:
    """Point on the yield curve"""
    maturity_years: float
    yield_rate: float
    security_type: str = "treasury"


class FixedIncomeAnalytics:
    """
    Core fixed income analytics calculations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("fixed_income_analytics")
    
    def calculate_ytm(
        self,
        price: float,
        face_value: float,
        coupon_rate: float,
        years_to_maturity: float,
        frequency: int = 2
    ) -> float:
        """
        Calculate yield to maturity using numerical methods.
        """
        if years_to_maturity <= 0:
            return 0.0
        
        coupon = face_value * coupon_rate / frequency
        n_periods = int(years_to_maturity * frequency)
        
        def bond_price(ytm):
            periods = range(1, n_periods + 1)
            pv_coupons = sum(coupon / (1 + ytm/frequency) ** t for t in periods)
            pv_face = face_value / (1 + ytm/frequency) ** n_periods
            return pv_coupons + pv_face - price
        
        try:
            ytm = brentq(bond_price, 0.0001, 0.5)
            return ytm
        except ValueError:
            # If brentq fails, use approximation
            annual_coupon = face_value * coupon_rate
            avg_price = (price + face_value) / 2
            return (annual_coupon + (face_value - price) / years_to_maturity) / avg_price
    
    def calculate_duration(
        self,
        ytm: float,
        coupon_rate: float,
        years_to_maturity: float,
        face_value: float = 1000,
        frequency: int = 2
    ) -> Dict[str, float]:
        """
        Calculate Macaulay and Modified duration.
        """
        if years_to_maturity <= 0:
            return {'macaulay': 0, 'modified': 0}
        
        coupon = face_value * coupon_rate / frequency
        n_periods = int(years_to_maturity * frequency)
        y = ytm / frequency
        
        # Calculate price
        price = sum(coupon / (1 + y) ** t for t in range(1, n_periods + 1))
        price += face_value / (1 + y) ** n_periods
        
        # Macaulay duration
        weighted_cf = sum((t/frequency) * coupon / (1 + y) ** t for t in range(1, n_periods + 1))
        weighted_cf += (n_periods/frequency) * face_value / (1 + y) ** n_periods
        
        macaulay = weighted_cf / price
        modified = macaulay / (1 + ytm/frequency)
        
        return {
            'macaulay': macaulay,
            'modified': modified
        }
    
    def calculate_convexity(
        self,
        ytm: float,
        coupon_rate: float,
        years_to_maturity: float,
        face_value: float = 1000,
        frequency: int = 2
    ) -> float:
        """
        Calculate bond convexity.
        """
        if years_to_maturity <= 0:
            return 0.0
        
        coupon = face_value * coupon_rate / frequency
        n_periods = int(years_to_maturity * frequency)
        y = ytm / frequency
        
        # Calculate price
        price = sum(coupon / (1 + y) ** t for t in range(1, n_periods + 1))
        price += face_value / (1 + y) ** n_periods
        
        # Convexity
        conv_sum = sum(t * (t + 1) * coupon / (1 + y) ** (t + 2) for t in range(1, n_periods + 1))
        conv_sum += n_periods * (n_periods + 1) * face_value / (1 + y) ** (n_periods + 2)
        
        convexity = conv_sum / (price * frequency ** 2)
        
        return convexity
    
    def price_sensitivity(
        self,
        current_price: float,
        duration: float,
        convexity: float,
        yield_change: float
    ) -> Dict[str, float]:
        """
        Calculate price change for a given yield change.
        Uses duration-convexity approximation.
        """
        # First order (duration)
        duration_effect = -duration * yield_change * current_price
        
        # Second order (convexity)
        convexity_effect = 0.5 * convexity * (yield_change ** 2) * current_price
        
        new_price = current_price + duration_effect + convexity_effect
        
        return {
            'new_price': new_price,
            'price_change': new_price - current_price,
            'price_change_pct': (new_price - current_price) / current_price,
            'duration_effect': duration_effect,
            'convexity_effect': convexity_effect
        }
    
    def calculate_spread(
        self,
        bond_ytm: float,
        treasury_ytm: float
    ) -> Dict[str, float]:
        """Calculate spread metrics"""
        nominal_spread = bond_ytm - treasury_ytm
        
        return {
            'nominal_spread': nominal_spread,
            'nominal_spread_bps': nominal_spread * 10000
        }


class YieldCurveAnalyzer:
    """
    Yield curve analysis and modeling.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("yield_curve")
        self.current_curve: List[YieldCurvePoint] = []
    
    def build_curve(self, points: List[YieldCurvePoint]):
        """Build yield curve from points"""
        self.current_curve = sorted(points, key=lambda x: x.maturity_years)
    
    def interpolate(self, maturity: float) -> float:
        """Interpolate yield at given maturity using cubic spline"""
        if not self.current_curve:
            return 0.0
        
        maturities = [p.maturity_years for p in self.current_curve]
        yields = [p.yield_rate for p in self.current_curve]
        
        if maturity <= maturities[0]:
            return yields[0]
        if maturity >= maturities[-1]:
            return yields[-1]
        
        spline = CubicSpline(maturities, yields)
        return float(spline(maturity))
    
    def get_forward_rate(
        self,
        start_years: float,
        end_years: float
    ) -> float:
        """Calculate implied forward rate"""
        r1 = self.interpolate(start_years)
        r2 = self.interpolate(end_years)
        
        if start_years == 0:
            return r2
        
        # Forward rate formula
        forward = ((1 + r2) ** end_years / (1 + r1) ** start_years) ** (1 / (end_years - start_years)) - 1
        
        return forward
    
    def curve_shape_analysis(self) -> Dict[str, Any]:
        """Analyze yield curve shape and provide insights"""
        if len(self.current_curve) < 3:
            return {'error': 'Insufficient curve points'}
        
        short_yield = self.interpolate(2)
        medium_yield = self.interpolate(5)
        long_yield = self.interpolate(10)
        
        # Slopes
        slope_2_10 = long_yield - short_yield
        slope_2_5 = medium_yield - short_yield
        slope_5_10 = long_yield - medium_yield
        
        # Curvature (butterfly)
        curvature = 2 * medium_yield - short_yield - long_yield
        
        # Determine shape
        if slope_2_10 > 0.01:
            shape = "normal_upward"
            outlook = "Economic expansion expected"
        elif slope_2_10 < -0.01:
            shape = "inverted"
            outlook = "Recession risk elevated"
        else:
            shape = "flat"
            outlook = "Economic uncertainty"
        
        return {
            'shape': shape,
            'outlook': outlook,
            'slopes': {
                '2y_10y': slope_2_10,
                '2y_5y': slope_2_5,
                '5y_10y': slope_5_10
            },
            'curvature': curvature,
            'key_rates': {
                '2y': short_yield,
                '5y': medium_yield,
                '10y': long_yield
            },
            'forward_rates': {
                '1y_1y': self.get_forward_rate(1, 2),
                '2y_3y': self.get_forward_rate(2, 5),
                '5y_5y': self.get_forward_rate(5, 10)
            }
        }
    
    def scenario_analysis(
        self,
        scenarios: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze yield curve under different scenarios.
        
        Args:
            scenarios: Dict of scenario_name -> {maturity: yield_change}
        """
        results = {}
        
        for scenario_name, changes in scenarios.items():
            new_curve = []
            for point in self.current_curve:
                change = changes.get(str(int(point.maturity_years)), 0)
                new_yield = point.yield_rate + change
                new_curve.append(YieldCurvePoint(
                    maturity_years=point.maturity_years,
                    yield_rate=new_yield
                ))
            
            # Analyze new curve shape
            temp_analyzer = YieldCurveAnalyzer()
            temp_analyzer.build_curve(new_curve)
            
            results[scenario_name] = temp_analyzer.curve_shape_analysis()
        
        return results


class BondPortfolioManager:
    """
    Fixed income portfolio management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("bond_portfolio")
        self.bonds: Dict[str, Bond] = {}
        self.analytics = FixedIncomeAnalytics()
        self.curve_analyzer = YieldCurveAnalyzer()
    
    def add_bond(self, bond: Bond):
        """Add bond to portfolio"""
        # Calculate metrics
        bond.ytm = self.analytics.calculate_ytm(
            bond.current_price,
            bond.face_value,
            bond.coupon_rate,
            bond.years_to_maturity(),
            bond.coupon_frequency
        )
        
        duration = self.analytics.calculate_duration(
            bond.ytm,
            bond.coupon_rate,
            bond.years_to_maturity(),
            bond.face_value,
            bond.coupon_frequency
        )
        bond.duration = duration['modified']
        bond.macaulay_duration = duration['macaulay']
        
        bond.convexity = self.analytics.calculate_convexity(
            bond.ytm,
            bond.coupon_rate,
            bond.years_to_maturity(),
            bond.face_value,
            bond.coupon_frequency
        )
        
        bond.current_yield = (bond.coupon_rate * bond.face_value) / bond.current_price if bond.current_price > 0 else 0
        
        self.bonds[bond.bond_id] = bond
        self.logger.info(f"Added bond: {bond.name}, Duration: {bond.duration:.2f}")
    
    def get_portfolio_metrics(self) -> Dict[str, Any]:
        """Calculate portfolio-level metrics"""
        if not self.bonds:
            return {}
        
        total_value = 0
        weighted_duration = 0
        weighted_convexity = 0
        weighted_yield = 0
        total_annual_income = 0
        
        by_type = {}
        by_rating = {}
        by_maturity = {'short': 0, 'medium': 0, 'long': 0}
        
        for bond in self.bonds.values():
            market_value = bond.current_price * bond.quantity / 100 * bond.face_value
            total_value += market_value
            
            weighted_duration += bond.duration * market_value
            weighted_convexity += bond.convexity * market_value
            weighted_yield += bond.ytm * market_value
            
            annual_income = bond.coupon_rate * bond.face_value * bond.quantity
            total_annual_income += annual_income
            
            # By type
            bond_type = bond.bond_type.value
            if bond_type not in by_type:
                by_type[bond_type] = 0
            by_type[bond_type] += market_value
            
            # By rating
            rating = bond.credit_rating.value
            if rating not in by_rating:
                by_rating[rating] = 0
            by_rating[rating] += market_value
            
            # By maturity bucket
            ytm = bond.years_to_maturity()
            if ytm <= 3:
                by_maturity['short'] += market_value
            elif ytm <= 7:
                by_maturity['medium'] += market_value
            else:
                by_maturity['long'] += market_value
        
        # Convert to percentages
        by_type = {k: v/total_value for k, v in by_type.items()}
        by_rating = {k: v/total_value for k, v in by_rating.items()}
        by_maturity = {k: v/total_value for k, v in by_maturity.items()}
        
        return {
            'total_market_value': total_value,
            'portfolio_duration': weighted_duration / total_value if total_value > 0 else 0,
            'portfolio_convexity': weighted_convexity / total_value if total_value > 0 else 0,
            'portfolio_yield': weighted_yield / total_value if total_value > 0 else 0,
            'annual_income': total_annual_income,
            'income_yield': total_annual_income / total_value if total_value > 0 else 0,
            'bond_count': len(self.bonds),
            'allocation_by_type': by_type,
            'allocation_by_rating': by_rating,
            'allocation_by_maturity': by_maturity
        }
    
    def scenario_impact(
        self,
        yield_change: float
    ) -> Dict[str, Any]:
        """Calculate portfolio impact of yield change"""
        metrics = self.get_portfolio_metrics()
        
        duration = metrics['portfolio_duration']
        convexity = metrics['portfolio_convexity']
        value = metrics['total_market_value']
        
        impact = self.analytics.price_sensitivity(
            value,
            duration,
            convexity,
            yield_change
        )
        
        # Per-bond impact
        bond_impacts = {}
        for bond_id, bond in self.bonds.items():
            bond_value = bond.current_price * bond.quantity / 100 * bond.face_value
            bond_impact = self.analytics.price_sensitivity(
                bond_value,
                bond.duration,
                bond.convexity,
                yield_change
            )
            bond_impacts[bond_id] = {
                'name': bond.name,
                'current_value': bond_value,
                'new_value': bond_impact['new_price'],
                'change': bond_impact['price_change'],
                'change_pct': bond_impact['price_change_pct']
            }
        
        return {
            'yield_change_bps': yield_change * 10000,
            'portfolio_impact': impact,
            'bond_impacts': bond_impacts
        }
    
    def get_income_schedule(self, months: int = 12) -> Dict[str, Any]:
        """Generate income schedule for next N months"""
        schedule = {}
        today = datetime.now()
        
        for i in range(months):
            month_date = today + timedelta(days=30 * i)
            month_key = month_date.strftime('%Y-%m')
            schedule[month_key] = {
                'coupon_payments': [],
                'total': 0
            }
        
        for bond in self.bonds.values():
            coupon_payment = bond.coupon_rate * bond.face_value * bond.quantity / bond.coupon_frequency
            payment_interval = 12 / bond.coupon_frequency
            
            for i in range(months):
                # Simplified: assume payments fall in certain months
                if i % payment_interval == 0:
                    month_date = today + timedelta(days=30 * i)
                    month_key = month_date.strftime('%Y-%m')
                    if month_key in schedule:
                        schedule[month_key]['coupon_payments'].append({
                            'bond': bond.name,
                            'amount': coupon_payment
                        })
                        schedule[month_key]['total'] += coupon_payment
        
        total_income = sum(m['total'] for m in schedule.values())
        
        return {
            'schedule': schedule,
            'total_expected_income': total_income,
            'average_monthly': total_income / months
        }
    
    def rebalancing_recommendations(
        self,
        target_duration: float,
        target_allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate rebalancing recommendations"""
        metrics = self.get_portfolio_metrics()
        current_duration = metrics['portfolio_duration']
        
        recommendations = []
        
        # Duration adjustment
        duration_diff = target_duration - current_duration
        if abs(duration_diff) > 0.5:
            if duration_diff > 0:
                recommendations.append({
                    'type': 'duration',
                    'action': 'extend',
                    'current': current_duration,
                    'target': target_duration,
                    'suggestion': 'Consider adding longer-dated bonds to extend duration'
                })
            else:
                recommendations.append({
                    'type': 'duration',
                    'action': 'shorten',
                    'current': current_duration,
                    'target': target_duration,
                    'suggestion': 'Consider shorter-dated bonds or selling long-dated positions'
                })
        
        # Allocation adjustments
        current_allocation = metrics['allocation_by_type']
        for asset_type, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_type, 0)
            diff = target_pct - current_pct
            
            if abs(diff) > 0.05:  # 5% threshold
                recommendations.append({
                    'type': 'allocation',
                    'asset_type': asset_type,
                    'current': current_pct,
                    'target': target_pct,
                    'action': 'increase' if diff > 0 else 'decrease',
                    'suggestion': f"{'Buy' if diff > 0 else 'Sell'} {asset_type} bonds"
                })
        
        return {
            'current_metrics': metrics,
            'recommendations': recommendations,
            'recommendation_count': len(recommendations)
        }
