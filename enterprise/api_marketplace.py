"""
API Marketplace
===============

Enterprise API marketplace for monetization:
- API product catalog
- Usage tracking and billing
- Rate limiting and quotas
- API key management
- Revenue analytics
"""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from collections import defaultdict


class PricingModel(Enum):
    """API pricing models"""
    FREE = "free"
    PAY_PER_USE = "pay_per_use"
    SUBSCRIPTION = "subscription"
    TIERED = "tiered"
    ENTERPRISE = "enterprise"


class APICategory(Enum):
    """API categories"""
    PORTFOLIO = "portfolio"
    RISK = "risk"
    TRADING = "trading"
    MARKET_DATA = "market_data"
    AI_INSIGHTS = "ai_insights"
    REPORTING = "reporting"
    COMPLIANCE = "compliance"
    ANALYTICS = "analytics"


class RateLimitPeriod(Enum):
    """Rate limit time periods"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"


@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests: int
    period: RateLimitPeriod
    burst_allowance: int = 0  # Extra requests allowed in burst


@dataclass
class PricingTier:
    """Pricing tier for tiered billing"""
    name: str
    min_usage: int
    max_usage: int
    price_per_unit: float
    included_units: int = 0


@dataclass
class APIProduct:
    """API product definition"""
    product_id: str
    name: str
    description: str
    category: APICategory
    version: str = "v1"
    
    # Pricing
    pricing_model: PricingModel = PricingModel.PAY_PER_USE
    base_price: float = 0.0  # Monthly for subscription, per call for pay-per-use
    pricing_tiers: List[PricingTier] = field(default_factory=list)
    
    # Limits
    rate_limit: RateLimit = field(default_factory=lambda: RateLimit(1000, RateLimitPeriod.MINUTE))
    daily_limit: int = 100000
    monthly_limit: int = 3000000
    
    # Features
    endpoints: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    documentation_url: str = ""
    
    # Status
    is_active: bool = True
    is_beta: bool = False
    requires_approval: bool = False
    
    def calculate_cost(self, usage: int) -> float:
        """Calculate cost for given usage"""
        if self.pricing_model == PricingModel.FREE:
            return 0.0
        
        if self.pricing_model == PricingModel.PAY_PER_USE:
            return usage * self.base_price
        
        if self.pricing_model == PricingModel.SUBSCRIPTION:
            return self.base_price  # Fixed monthly
        
        if self.pricing_model == PricingModel.TIERED:
            total = 0.0
            remaining = usage
            for tier in sorted(self.pricing_tiers, key=lambda t: t.min_usage):
                if remaining <= 0:
                    break
                tier_usage = min(remaining, tier.max_usage - tier.min_usage + 1)
                billable = max(0, tier_usage - tier.included_units)
                total += billable * tier.price_per_unit
                remaining -= tier_usage
            return total
        
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'version': self.version,
            'pricing': {
                'model': self.pricing_model.value,
                'base_price': self.base_price
            },
            'limits': {
                'rate_limit': f"{self.rate_limit.requests}/{self.rate_limit.period.value}",
                'daily': self.daily_limit,
                'monthly': self.monthly_limit
            },
            'endpoints': self.endpoints,
            'is_active': self.is_active,
            'is_beta': self.is_beta
        }


@dataclass
class APIKey:
    """API key for authentication"""
    key_id: str
    key_hash: str  # Store hash, not actual key
    client_id: str
    name: str
    
    # Permissions
    products: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    
    # Limits (override product defaults)
    custom_rate_limit: Optional[RateLimit] = None
    custom_daily_limit: Optional[int] = None
    
    # Status
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    # Metadata
    ip_whitelist: List[str] = field(default_factory=list)
    environment: str = "production"  # production, sandbox


@dataclass
class UsageRecord:
    """API usage record"""
    record_id: str
    key_id: str
    client_id: str
    product_id: str
    endpoint: str
    
    timestamp: datetime
    response_time_ms: int
    status_code: int
    request_size_bytes: int
    response_size_bytes: int
    
    # Billing
    billable_units: int = 1
    cost: float = 0.0


class APIUsageTracker:
    """
    Tracks API usage for billing and analytics.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("api_usage")
        self.usage_records: List[UsageRecord] = []
        self.rate_limit_counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def record_usage(
        self,
        key_id: str,
        client_id: str,
        product_id: str,
        endpoint: str,
        response_time_ms: int,
        status_code: int,
        request_size: int = 0,
        response_size: int = 0,
        billable_units: int = 1,
        cost: float = 0.0
    ) -> UsageRecord:
        """Record API usage"""
        record = UsageRecord(
            record_id=str(uuid.uuid4()),
            key_id=key_id,
            client_id=client_id,
            product_id=product_id,
            endpoint=endpoint,
            timestamp=datetime.now(),
            response_time_ms=response_time_ms,
            status_code=status_code,
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            billable_units=billable_units,
            cost=cost
        )
        
        self.usage_records.append(record)
        return record
    
    def check_rate_limit(
        self,
        key_id: str,
        rate_limit: RateLimit
    ) -> Dict[str, Any]:
        """Check if request is within rate limit"""
        now = datetime.now()
        
        # Get period key
        if rate_limit.period == RateLimitPeriod.SECOND:
            period_key = now.strftime("%Y%m%d%H%M%S")
        elif rate_limit.period == RateLimitPeriod.MINUTE:
            period_key = now.strftime("%Y%m%d%H%M")
        elif rate_limit.period == RateLimitPeriod.HOUR:
            period_key = now.strftime("%Y%m%d%H")
        elif rate_limit.period == RateLimitPeriod.DAY:
            period_key = now.strftime("%Y%m%d")
        else:
            period_key = now.strftime("%Y%m")
        
        counter_key = f"{key_id}:{period_key}"
        current_count = self.rate_limit_counters[key_id][period_key]
        
        allowed = current_count < (rate_limit.requests + rate_limit.burst_allowance)
        
        if allowed:
            self.rate_limit_counters[key_id][period_key] += 1
        
        return {
            'allowed': allowed,
            'current_count': current_count,
            'limit': rate_limit.requests,
            'remaining': max(0, rate_limit.requests - current_count - 1),
            'reset_at': self._get_reset_time(rate_limit.period)
        }
    
    def _get_reset_time(self, period: RateLimitPeriod) -> datetime:
        """Get next rate limit reset time"""
        now = datetime.now()
        
        if period == RateLimitPeriod.SECOND:
            return now.replace(microsecond=0) + timedelta(seconds=1)
        elif period == RateLimitPeriod.MINUTE:
            return now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        elif period == RateLimitPeriod.HOUR:
            return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif period == RateLimitPeriod.DAY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:  # MONTH
            next_month = now.replace(day=1) + timedelta(days=32)
            return next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def get_usage_summary(
        self,
        client_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get usage summary for billing"""
        client_records = [
            r for r in self.usage_records
            if r.client_id == client_id and start_date <= r.timestamp <= end_date
        ]
        
        by_product = defaultdict(lambda: {
            'calls': 0,
            'billable_units': 0,
            'cost': 0,
            'avg_response_time': 0,
            'error_count': 0
        })
        
        for record in client_records:
            by_product[record.product_id]['calls'] += 1
            by_product[record.product_id]['billable_units'] += record.billable_units
            by_product[record.product_id]['cost'] += record.cost
            by_product[record.product_id]['avg_response_time'] += record.response_time_ms
            if record.status_code >= 400:
                by_product[record.product_id]['error_count'] += 1
        
        # Calculate averages
        for product in by_product:
            if by_product[product]['calls'] > 0:
                by_product[product]['avg_response_time'] /= by_product[product]['calls']
        
        total_calls = sum(p['calls'] for p in by_product.values())
        total_cost = sum(p['cost'] for p in by_product.values())
        
        return {
            'client_id': client_id,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_calls': total_calls,
            'total_cost': total_cost,
            'by_product': dict(by_product)
        }
    
    def get_daily_usage(
        self,
        client_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get daily usage for charting"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily = defaultdict(lambda: {'calls': 0, 'cost': 0})
        
        for record in self.usage_records:
            if record.client_id == client_id and start_date <= record.timestamp <= end_date:
                day_key = record.timestamp.strftime("%Y-%m-%d")
                daily[day_key]['calls'] += 1
                daily[day_key]['cost'] += record.cost
        
        result = []
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            result.append({
                'date': date,
                'calls': daily[date]['calls'],
                'cost': daily[date]['cost']
            })
        
        return result


class APIMarketplace:
    """
    Complete API marketplace for enterprise monetization.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("api_marketplace")
        self.products: Dict[str, APIProduct] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.usage_tracker = APIUsageTracker()
        self._initialize_products()
    
    def _initialize_products(self):
        """Initialize default API products"""
        products = [
            APIProduct(
                product_id="portfolio-api",
                name="Portfolio Management API",
                description="Complete portfolio management capabilities",
                category=APICategory.PORTFOLIO,
                pricing_model=PricingModel.TIERED,
                base_price=0.001,
                endpoints=[
                    "/api/v1/portfolios",
                    "/api/v1/portfolios/{id}",
                    "/api/v1/portfolios/{id}/holdings",
                    "/api/v1/portfolios/{id}/performance",
                    "/api/v1/portfolios/{id}/rebalance"
                ],
                features=["Create portfolios", "Track holdings", "Performance analytics"]
            ),
            APIProduct(
                product_id="risk-api",
                name="Risk Analytics API",
                description="Advanced risk analysis and VaR calculations",
                category=APICategory.RISK,
                pricing_model=PricingModel.PAY_PER_USE,
                base_price=0.005,
                endpoints=[
                    "/api/v1/risk/var",
                    "/api/v1/risk/stress-test",
                    "/api/v1/risk/correlation",
                    "/api/v1/risk/factor-analysis"
                ],
                features=["VaR calculations", "Stress testing", "Correlation analysis"]
            ),
            APIProduct(
                product_id="ai-insights-api",
                name="AI Insights API",
                description="AI-powered investment insights and recommendations",
                category=APICategory.AI_INSIGHTS,
                pricing_model=PricingModel.PAY_PER_USE,
                base_price=0.01,
                is_beta=True,
                endpoints=[
                    "/api/v1/ai/insights",
                    "/api/v1/ai/recommendations",
                    "/api/v1/ai/sentiment",
                    "/api/v1/ai/predictions"
                ],
                features=["AI insights", "Recommendations", "Sentiment analysis"]
            ),
            APIProduct(
                product_id="market-data-api",
                name="Market Data API",
                description="Real-time and historical market data",
                category=APICategory.MARKET_DATA,
                pricing_model=PricingModel.SUBSCRIPTION,
                base_price=99.0,  # Monthly
                rate_limit=RateLimit(10000, RateLimitPeriod.MINUTE),
                endpoints=[
                    "/api/v1/market/quotes",
                    "/api/v1/market/history",
                    "/api/v1/market/news",
                    "/api/v1/market/fundamentals"
                ],
                features=["Real-time quotes", "Historical data", "News feeds"]
            )
        ]
        
        for product in products:
            self.products[product.product_id] = product
    
    def create_api_key(
        self,
        client_id: str,
        name: str,
        products: List[str],
        scopes: List[str] = None,
        expires_days: int = None,
        environment: str = "production"
    ) -> Tuple[str, APIKey]:
        """Create a new API key"""
        # Generate secure key
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_id = str(uuid.uuid4())[:8]
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            client_id=client_id,
            name=name,
            products=products,
            scopes=scopes or ['read'],
            expires_at=datetime.now() + timedelta(days=expires_days) if expires_days else None,
            environment=environment
        )
        
        self.api_keys[key_id] = api_key
        self.logger.info(f"Created API key for client {client_id}: {key_id}")
        
        # Return full key only once
        return f"pa_{key_id}_{raw_key}", api_key
    
    def validate_api_key(
        self,
        key: str
    ) -> Optional[APIKey]:
        """Validate an API key"""
        try:
            parts = key.split('_')
            if len(parts) != 3 or parts[0] != 'pa':
                return None
            
            key_id = parts[1]
            raw_key = parts[2]
            
            if key_id not in self.api_keys:
                return None
            
            api_key = self.api_keys[key_id]
            
            # Check hash
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
            if key_hash != api_key.key_hash:
                return None
            
            # Check if active
            if not api_key.is_active:
                return None
            
            # Check expiration
            if api_key.expires_at and datetime.now() > api_key.expires_at:
                return None
            
            # Update last used
            api_key.last_used_at = datetime.now()
            
            return api_key
            
        except Exception:
            return None
    
    def revoke_api_key(self, key_id: str):
        """Revoke an API key"""
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            self.logger.info(f"Revoked API key: {key_id}")
    
    def get_product_catalog(
        self,
        category: APICategory = None,
        include_beta: bool = False
    ) -> List[Dict[str, Any]]:
        """Get product catalog"""
        products = []
        
        for product in self.products.values():
            if not product.is_active:
                continue
            if product.is_beta and not include_beta:
                continue
            if category and product.category != category:
                continue
            
            products.append(product.to_dict())
        
        return products
    
    def process_request(
        self,
        api_key: str,
        product_id: str,
        endpoint: str,
        response_time_ms: int,
        status_code: int
    ) -> Dict[str, Any]:
        """Process an API request"""
        # Validate key
        key = self.validate_api_key(api_key)
        if not key:
            return {'error': 'Invalid API key', 'status': 401}
        
        # Check product access
        if product_id not in key.products:
            return {'error': 'Product not authorized', 'status': 403}
        
        product = self.products.get(product_id)
        if not product:
            return {'error': 'Product not found', 'status': 404}
        
        # Check rate limit
        rate_limit = key.custom_rate_limit or product.rate_limit
        limit_check = self.usage_tracker.check_rate_limit(key.key_id, rate_limit)
        
        if not limit_check['allowed']:
            return {
                'error': 'Rate limit exceeded',
                'status': 429,
                'retry_after': limit_check['reset_at'].isoformat()
            }
        
        # Calculate cost
        cost = product.calculate_cost(1)
        
        # Record usage
        self.usage_tracker.record_usage(
            key_id=key.key_id,
            client_id=key.client_id,
            product_id=product_id,
            endpoint=endpoint,
            response_time_ms=response_time_ms,
            status_code=status_code,
            cost=cost
        )
        
        return {
            'allowed': True,
            'remaining': limit_check['remaining'],
            'cost': cost
        }
    
    def generate_invoice(
        self,
        client_id: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Generate monthly invoice"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        usage = self.usage_tracker.get_usage_summary(client_id, start_date, end_date)
        
        line_items = []
        for product_id, product_usage in usage['by_product'].items():
            product = self.products.get(product_id)
            if product:
                line_items.append({
                    'product': product.name,
                    'quantity': product_usage['billable_units'],
                    'unit_price': product.base_price,
                    'total': product_usage['cost']
                })
        
        return {
            'invoice_id': f"INV-{year}{month:02d}-{client_id[:8]}",
            'client_id': client_id,
            'period': f"{year}-{month:02d}",
            'generated_at': datetime.now().isoformat(),
            'line_items': line_items,
            'subtotal': usage['total_cost'],
            'tax': usage['total_cost'] * 0.0,  # Placeholder for tax calculation
            'total': usage['total_cost'],
            'usage_summary': usage
        }
    
    def get_revenue_analytics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get revenue analytics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        total_revenue = 0
        total_calls = 0
        by_product = defaultdict(float)
        by_client = defaultdict(float)
        
        for record in self.usage_tracker.usage_records:
            if start_date <= record.timestamp <= end_date:
                total_revenue += record.cost
                total_calls += 1
                by_product[record.product_id] += record.cost
                by_client[record.client_id] += record.cost
        
        # Top products
        top_products = sorted(by_product.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Top clients
        top_clients = sorted(by_client.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'period_days': days,
            'total_revenue': total_revenue,
            'total_api_calls': total_calls,
            'avg_revenue_per_call': total_revenue / total_calls if total_calls > 0 else 0,
            'top_products': [{'product': p, 'revenue': r} for p, r in top_products],
            'top_clients': [{'client': c, 'revenue': r} for c, r in top_clients],
            'daily_revenue': self._calculate_daily_revenue(start_date, end_date)
        }
    
    def _calculate_daily_revenue(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Calculate daily revenue"""
        daily = defaultdict(float)
        
        for record in self.usage_tracker.usage_records:
            if start_date <= record.timestamp <= end_date:
                day_key = record.timestamp.strftime("%Y-%m-%d")
                daily[day_key] += record.cost
        
        result = []
        current = start_date
        while current <= end_date:
            day_key = current.strftime("%Y-%m-%d")
            result.append({
                'date': day_key,
                'revenue': daily[day_key]
            })
            current += timedelta(days=1)
        
        return result
