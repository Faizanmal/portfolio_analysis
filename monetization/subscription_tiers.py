"""
Subscription Tiers
==================

Multi-tier subscription system:
- Free tier with limited features
- Basic tier for retail investors
- Professional tier with advanced analytics
- Enterprise tier with full features
- Custom tier for institutional clients
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging


class SubscriptionTier(Enum):
    """Subscription tier levels"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    LIFETIME = "lifetime"


class TierFeature(Enum):
    """Features available by tier"""
    # Basic features
    PORTFOLIO_TRACKING = "portfolio_tracking"
    BASIC_CHARTS = "basic_charts"
    MARKET_NEWS = "market_news"
    WATCHLISTS = "watchlists"
    
    # Advanced features
    ADVANCED_ANALYTICS = "advanced_analytics"
    REAL_TIME_DATA = "real_time_data"
    CUSTOM_ALERTS = "custom_alerts"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    RISK_ANALYSIS = "risk_analysis"
    
    # Professional features
    AI_INSIGHTS = "ai_insights"
    BACKTESTING = "backtesting"
    OPTIONS_ANALYSIS = "options_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    STRATEGY_BUILDER = "strategy_builder"
    
    # Enterprise features
    API_ACCESS = "api_access"
    WHITE_LABEL = "white_label"
    MULTI_TENANT = "multi_tenant"
    CUSTOM_INTEGRATIONS = "custom_integrations"
    DEDICATED_SUPPORT = "dedicated_support"
    COMPLIANCE_REPORTS = "compliance_reports"
    FEDERATED_LEARNING = "federated_learning"


@dataclass
class TierConfiguration:
    """Configuration for a subscription tier"""
    tier: SubscriptionTier
    name: str
    description: str
    
    # Pricing
    monthly_price: float
    annual_price: float  # Usually discounted
    
    # Limits
    max_portfolios: int
    max_positions: int
    max_watchlists: int
    max_alerts: int
    api_calls_per_day: int
    data_retention_days: int
    
    # Features
    features: Set[TierFeature] = field(default_factory=set)
    
    # Support
    support_level: str = "community"  # community, email, priority, dedicated
    response_time_hours: int = 72
    
    def has_feature(self, feature: TierFeature) -> bool:
        return feature in self.features
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tier': self.tier.value,
            'name': self.name,
            'description': self.description,
            'pricing': {
                'monthly': self.monthly_price,
                'annual': self.annual_price,
                'annual_savings': (self.monthly_price * 12) - self.annual_price
            },
            'limits': {
                'portfolios': self.max_portfolios,
                'positions': self.max_positions,
                'watchlists': self.max_watchlists,
                'alerts': self.max_alerts,
                'api_calls_per_day': self.api_calls_per_day,
                'data_retention_days': self.data_retention_days
            },
            'features': [f.value for f in self.features],
            'support': {
                'level': self.support_level,
                'response_time_hours': self.response_time_hours
            }
        }


@dataclass
class UserSubscription:
    """User's subscription details"""
    subscription_id: str
    user_id: str
    tier: SubscriptionTier
    billing_cycle: BillingCycle
    
    # Dates
    start_date: datetime
    end_date: datetime
    trial_end_date: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    is_trial: bool = False
    auto_renew: bool = True
    
    # Billing
    payment_method_id: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    amount_paid: float = 0.0
    
    # Usage
    api_calls_today: int = 0
    api_calls_reset_time: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        return datetime.now() > self.end_date
    
    def days_remaining(self) -> int:
        delta = self.end_date - datetime.now()
        return max(0, delta.days)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subscription_id': self.subscription_id,
            'user_id': self.user_id,
            'tier': self.tier.value,
            'billing_cycle': self.billing_cycle.value,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_active': self.is_active,
            'is_trial': self.is_trial,
            'auto_renew': self.auto_renew,
            'days_remaining': self.days_remaining()
        }


@dataclass
class FeatureAccess:
    """Feature access check result"""
    allowed: bool
    feature: TierFeature
    current_tier: SubscriptionTier
    required_tier: Optional[SubscriptionTier] = None
    message: str = ""
    upgrade_url: Optional[str] = None


class SubscriptionManager:
    """
    Manages user subscriptions and feature access.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("subscription_manager")
        self.tier_configs = self._create_tier_configs()
        self.subscriptions: Dict[str, UserSubscription] = {}
        
        # Usage tracking
        self.usage_counters: Dict[str, Dict[str, int]] = {}
    
    def _create_tier_configs(self) -> Dict[SubscriptionTier, TierConfiguration]:
        """Create tier configurations"""
        return {
            SubscriptionTier.FREE: TierConfiguration(
                tier=SubscriptionTier.FREE,
                name="Free",
                description="Basic portfolio tracking for individual investors",
                monthly_price=0.0,
                annual_price=0.0,
                max_portfolios=1,
                max_positions=10,
                max_watchlists=2,
                max_alerts=5,
                api_calls_per_day=100,
                data_retention_days=30,
                features={
                    TierFeature.PORTFOLIO_TRACKING,
                    TierFeature.BASIC_CHARTS,
                    TierFeature.MARKET_NEWS,
                    TierFeature.WATCHLISTS
                },
                support_level="community",
                response_time_hours=168
            ),
            
            SubscriptionTier.BASIC: TierConfiguration(
                tier=SubscriptionTier.BASIC,
                name="Basic",
                description="Enhanced features for active investors",
                monthly_price=9.99,
                annual_price=99.99,
                max_portfolios=3,
                max_positions=50,
                max_watchlists=10,
                max_alerts=25,
                api_calls_per_day=1000,
                data_retention_days=365,
                features={
                    TierFeature.PORTFOLIO_TRACKING,
                    TierFeature.BASIC_CHARTS,
                    TierFeature.MARKET_NEWS,
                    TierFeature.WATCHLISTS,
                    TierFeature.ADVANCED_ANALYTICS,
                    TierFeature.REAL_TIME_DATA,
                    TierFeature.CUSTOM_ALERTS,
                    TierFeature.PORTFOLIO_OPTIMIZATION,
                    TierFeature.RISK_ANALYSIS
                },
                support_level="email",
                response_time_hours=48
            ),
            
            SubscriptionTier.PROFESSIONAL: TierConfiguration(
                tier=SubscriptionTier.PROFESSIONAL,
                name="Professional",
                description="Full analytics suite for serious traders",
                monthly_price=49.99,
                annual_price=499.99,
                max_portfolios=10,
                max_positions=500,
                max_watchlists=50,
                max_alerts=100,
                api_calls_per_day=10000,
                data_retention_days=1825,  # 5 years
                features={
                    # All Basic features
                    TierFeature.PORTFOLIO_TRACKING,
                    TierFeature.BASIC_CHARTS,
                    TierFeature.MARKET_NEWS,
                    TierFeature.WATCHLISTS,
                    TierFeature.ADVANCED_ANALYTICS,
                    TierFeature.REAL_TIME_DATA,
                    TierFeature.CUSTOM_ALERTS,
                    TierFeature.PORTFOLIO_OPTIMIZATION,
                    TierFeature.RISK_ANALYSIS,
                    # Professional features
                    TierFeature.AI_INSIGHTS,
                    TierFeature.BACKTESTING,
                    TierFeature.OPTIONS_ANALYSIS,
                    TierFeature.SENTIMENT_ANALYSIS,
                    TierFeature.STRATEGY_BUILDER,
                    TierFeature.API_ACCESS
                },
                support_level="priority",
                response_time_hours=24
            ),
            
            SubscriptionTier.ENTERPRISE: TierConfiguration(
                tier=SubscriptionTier.ENTERPRISE,
                name="Enterprise",
                description="Complete solution for institutions",
                monthly_price=499.99,
                annual_price=4999.99,
                max_portfolios=-1,  # Unlimited
                max_positions=-1,
                max_watchlists=-1,
                max_alerts=-1,
                api_calls_per_day=1000000,
                data_retention_days=-1,  # Unlimited
                features=set(TierFeature),  # All features
                support_level="dedicated",
                response_time_hours=4
            )
        }
    
    def create_subscription(
        self,
        user_id: str,
        tier: SubscriptionTier,
        billing_cycle: BillingCycle,
        payment_method_id: Optional[str] = None,
        trial_days: int = 0
    ) -> UserSubscription:
        """Create a new subscription"""
        subscription_id = str(uuid.uuid4())
        
        now = datetime.now()
        
        # Calculate end date based on billing cycle
        if billing_cycle == BillingCycle.MONTHLY:
            end_date = now + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            end_date = now + timedelta(days=90)
        elif billing_cycle == BillingCycle.ANNUAL:
            end_date = now + timedelta(days=365)
        else:
            end_date = now + timedelta(days=36500)  # 100 years for lifetime
        
        # Handle trial
        trial_end_date = None
        if trial_days > 0:
            trial_end_date = now + timedelta(days=trial_days)
            end_date = trial_end_date
        
        subscription = UserSubscription(
            subscription_id=subscription_id,
            user_id=user_id,
            tier=tier,
            billing_cycle=billing_cycle,
            start_date=now,
            end_date=end_date,
            trial_end_date=trial_end_date,
            is_trial=trial_days > 0,
            payment_method_id=payment_method_id,
            next_billing_date=end_date if not trial_days else trial_end_date
        )
        
        self.subscriptions[user_id] = subscription
        
        self.logger.info(f"Created {tier.value} subscription for user {user_id}")
        
        return subscription
    
    def get_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Get user's subscription"""
        return self.subscriptions.get(user_id)
    
    def upgrade_subscription(
        self,
        user_id: str,
        new_tier: SubscriptionTier
    ) -> UserSubscription:
        """Upgrade user's subscription"""
        current = self.subscriptions.get(user_id)
        
        if not current:
            return self.create_subscription(user_id, new_tier, BillingCycle.MONTHLY)
        
        # Calculate prorated credit
        days_remaining = current.days_remaining()
        old_config = self.tier_configs.get(current.tier)
        new_config = self.tier_configs.get(new_tier)
        
        if old_config and new_config and days_remaining > 0:
            daily_old = old_config.monthly_price / 30
            prorated_credit = daily_old * days_remaining
            
            self.logger.info(f"Prorated credit: ${prorated_credit:.2f}")
        
        # Update subscription
        current.tier = new_tier
        current.start_date = datetime.now()
        
        self.logger.info(f"Upgraded user {user_id} to {new_tier.value}")
        
        return current
    
    def cancel_subscription(
        self,
        user_id: str,
        immediate: bool = False
    ) -> bool:
        """Cancel user's subscription"""
        subscription = self.subscriptions.get(user_id)
        
        if not subscription:
            return False
        
        subscription.auto_renew = False
        
        if immediate:
            subscription.is_active = False
            subscription.end_date = datetime.now()
        
        self.logger.info(f"Cancelled subscription for user {user_id}")
        
        return True
    
    def check_feature_access(
        self,
        user_id: str,
        feature: TierFeature
    ) -> FeatureAccess:
        """Check if user has access to a feature"""
        subscription = self.subscriptions.get(user_id)
        
        # Default to free tier if no subscription
        if not subscription:
            current_tier = SubscriptionTier.FREE
        elif not subscription.is_active or subscription.is_expired():
            current_tier = SubscriptionTier.FREE
        else:
            current_tier = subscription.tier
        
        tier_config = self.tier_configs.get(current_tier)
        
        if tier_config and tier_config.has_feature(feature):
            return FeatureAccess(
                allowed=True,
                feature=feature,
                current_tier=current_tier,
                message="Feature access granted"
            )
        
        # Find minimum tier required
        required_tier = None
        for tier in [SubscriptionTier.BASIC, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            config = self.tier_configs.get(tier)
            if config and config.has_feature(feature):
                required_tier = tier
                break
        
        return FeatureAccess(
            allowed=False,
            feature=feature,
            current_tier=current_tier,
            required_tier=required_tier,
            message=f"Upgrade to {required_tier.value if required_tier else 'higher'} tier required",
            upgrade_url=f"/upgrade/{required_tier.value if required_tier else 'professional'}"
        )
    
    def check_limit(
        self,
        user_id: str,
        limit_type: str,
        current_value: int
    ) -> bool:
        """Check if user is within limits"""
        subscription = self.subscriptions.get(user_id)
        
        if not subscription:
            tier = SubscriptionTier.FREE
        else:
            tier = subscription.tier
        
        config = self.tier_configs.get(tier)
        
        if not config:
            return False
        
        limit_map = {
            'portfolios': config.max_portfolios,
            'positions': config.max_positions,
            'watchlists': config.max_watchlists,
            'alerts': config.max_alerts,
            'api_calls': config.api_calls_per_day
        }
        
        limit = limit_map.get(limit_type, 0)
        
        if limit == -1:  # Unlimited
            return True
        
        return current_value < limit
    
    def track_api_usage(self, user_id: str) -> bool:
        """Track API call and check if within limit"""
        subscription = self.subscriptions.get(user_id)
        
        if not subscription:
            tier = SubscriptionTier.FREE
        else:
            tier = subscription.tier
        
        config = self.tier_configs.get(tier)
        
        if not config:
            return False
        
        # Initialize counters
        if user_id not in self.usage_counters:
            self.usage_counters[user_id] = {
                'api_calls': 0,
                'reset_time': datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            }
        
        counters = self.usage_counters[user_id]
        
        # Reset if new day
        if datetime.now() > counters['reset_time']:
            counters['api_calls'] = 0
            counters['reset_time'] = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        
        # Check limit
        if config.api_calls_per_day != -1 and counters['api_calls'] >= config.api_calls_per_day:
            return False
        
        counters['api_calls'] += 1
        return True
    
    def get_tier_comparison(self) -> List[Dict[str, Any]]:
        """Get comparison of all tiers"""
        return [config.to_dict() for config in self.tier_configs.values()]
    
    def get_usage_report(self, user_id: str) -> Dict[str, Any]:
        """Get usage report for user"""
        subscription = self.subscriptions.get(user_id)
        
        if not subscription:
            tier = SubscriptionTier.FREE
        else:
            tier = subscription.tier
        
        config = self.tier_configs.get(tier)
        counters = self.usage_counters.get(user_id, {'api_calls': 0})
        
        return {
            'user_id': user_id,
            'tier': tier.value,
            'subscription': subscription.to_dict() if subscription else None,
            'usage': {
                'api_calls_today': counters.get('api_calls', 0),
                'api_calls_limit': config.api_calls_per_day if config else 0,
                'api_usage_percent': (counters.get('api_calls', 0) / config.api_calls_per_day * 100) if config and config.api_calls_per_day > 0 else 0
            },
            'limits': {
                'portfolios': config.max_portfolios if config else 0,
                'positions': config.max_positions if config else 0,
                'watchlists': config.max_watchlists if config else 0,
                'alerts': config.max_alerts if config else 0
            }
        }
