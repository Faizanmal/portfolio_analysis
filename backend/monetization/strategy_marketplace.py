"""
Strategy Marketplace
====================

Marketplace for trading strategies:
- Strategy listing and discovery
- Strategy purchase and licensing
- Performance tracking
- Reviews and ratings
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging


class StrategyType(Enum):
    """Types of trading strategies"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    TREND_FOLLOWING = "trend_following"
    MARKET_MAKING = "market_making"
    QUANTITATIVE = "quantitative"
    FACTOR_BASED = "factor_based"
    ML_BASED = "ml_based"
    HYBRID = "hybrid"


class StrategyStatus(Enum):
    """Strategy listing status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class LicenseType(Enum):
    """Strategy license types"""
    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    PERFORMANCE_FEE = "performance_fee"
    FREE = "free"


@dataclass
class StrategyMetrics:
    """Performance metrics for a strategy"""
    # Returns
    total_return: float = 0.0
    annualized_return: float = 0.0
    monthly_return: float = 0.0
    
    # Risk metrics
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    volatility: float = 0.0
    calmar_ratio: float = 0.0
    
    # Trade statistics
    total_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    avg_holding_period: float = 0.0
    
    # Benchmark comparison
    alpha: float = 0.0
    beta: float = 0.0
    correlation_to_market: float = 0.0
    
    # Time period
    backtest_start: Optional[datetime] = None
    backtest_end: Optional[datetime] = None
    live_start: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'returns': {
                'total': self.total_return,
                'annualized': self.annualized_return,
                'monthly': self.monthly_return
            },
            'risk': {
                'sharpe_ratio': self.sharpe_ratio,
                'sortino_ratio': self.sortino_ratio,
                'max_drawdown': self.max_drawdown,
                'volatility': self.volatility,
                'calmar_ratio': self.calmar_ratio
            },
            'trades': {
                'total': self.total_trades,
                'win_rate': self.win_rate,
                'profit_factor': self.profit_factor
            },
            'benchmark': {
                'alpha': self.alpha,
                'beta': self.beta
            }
        }


@dataclass
class StrategyReview:
    """User review of a strategy"""
    review_id: str
    strategy_id: str
    user_id: str
    
    rating: int  # 1-5
    title: str
    content: str
    
    # Detailed ratings
    accuracy_rating: int = 0
    documentation_rating: int = 0
    value_rating: int = 0
    support_rating: int = 0
    
    # Review metadata
    verified_purchase: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    helpful_votes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'review_id': self.review_id,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'detailed_ratings': {
                'accuracy': self.accuracy_rating,
                'documentation': self.documentation_rating,
                'value': self.value_rating,
                'support': self.support_rating
            },
            'verified_purchase': self.verified_purchase,
            'helpful_votes': self.helpful_votes,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class TradingStrategy:
    """Trading strategy definition"""
    strategy_id: str
    name: str
    description: str
    author_id: str
    
    # Classification
    strategy_type: StrategyType
    asset_classes: List[str] = field(default_factory=list)
    markets: List[str] = field(default_factory=list)
    
    # Strategy details
    timeframe: str = "daily"  # intraday, daily, weekly, monthly
    min_capital: float = 1000.0
    max_positions: int = 10
    leverage_allowed: bool = False
    
    # Code/Logic
    strategy_code: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Documentation
    documentation: str = ""
    setup_instructions: str = ""
    
    # Performance
    metrics: Optional[StrategyMetrics] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'strategy_id': self.strategy_id,
            'name': self.name,
            'description': self.description,
            'strategy_type': self.strategy_type.value,
            'asset_classes': self.asset_classes,
            'timeframe': self.timeframe,
            'min_capital': self.min_capital,
            'metrics': self.metrics.to_dict() if self.metrics else None
        }


@dataclass
class StrategyListing:
    """Marketplace listing for a strategy"""
    listing_id: str
    strategy: TradingStrategy
    
    # Pricing
    license_type: LicenseType
    price: float
    performance_fee_percent: float = 0.0
    
    # Status
    status: StrategyStatus = StrategyStatus.DRAFT
    featured: bool = False
    
    # Listing metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Stats
    views: int = 0
    purchases: int = 0
    subscribers: int = 0
    
    # Reviews
    reviews: List[StrategyReview] = field(default_factory=list)
    avg_rating: float = 0.0
    
    # Tags for discovery
    tags: List[str] = field(default_factory=list)
    
    def calculate_rating(self):
        """Calculate average rating from reviews"""
        if not self.reviews:
            self.avg_rating = 0.0
        else:
            self.avg_rating = sum(r.rating for r in self.reviews) / len(self.reviews)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'listing_id': self.listing_id,
            'strategy': self.strategy.to_dict(),
            'pricing': {
                'license_type': self.license_type.value,
                'price': self.price,
                'performance_fee_percent': self.performance_fee_percent
            },
            'status': self.status.value,
            'featured': self.featured,
            'stats': {
                'views': self.views,
                'purchases': self.purchases,
                'subscribers': self.subscribers,
                'avg_rating': self.avg_rating,
                'review_count': len(self.reviews)
            },
            'tags': self.tags,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class StrategyPurchase:
    """Record of a strategy purchase"""
    purchase_id: str
    listing_id: str
    buyer_id: str
    seller_id: str
    
    # Purchase details
    license_type: LicenseType
    price_paid: float
    payment_method: str
    
    # License period
    purchase_date: datetime = field(default_factory=datetime.now)
    license_start: datetime = field(default_factory=datetime.now)
    license_end: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    refunded: bool = False
    
    # Usage
    times_deployed: int = 0
    total_returns: float = 0.0
    performance_fees_paid: float = 0.0
    
    def is_expired(self) -> bool:
        if self.license_end is None:
            return False
        return datetime.now() > self.license_end
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'purchase_id': self.purchase_id,
            'listing_id': self.listing_id,
            'price_paid': self.price_paid,
            'license_type': self.license_type.value,
            'purchase_date': self.purchase_date.isoformat(),
            'is_active': self.is_active and not self.is_expired(),
            'usage': {
                'times_deployed': self.times_deployed,
                'total_returns': self.total_returns
            }
        }


class StrategyMarketplace:
    """
    Marketplace for trading strategies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("strategy_marketplace")
        self.listings: Dict[str, StrategyListing] = {}
        self.purchases: Dict[str, StrategyPurchase] = {}
        self.user_purchases: Dict[str, List[str]] = {}  # user_id -> purchase_ids
        self.seller_listings: Dict[str, List[str]] = {}  # seller_id -> listing_ids
        
        # Platform settings
        self.platform_fee_percent: float = 15.0  # Platform takes 15%
        self.min_price: float = 0.0
        self.max_price: float = 100000.0
    
    def create_listing(
        self,
        strategy: TradingStrategy,
        license_type: LicenseType,
        price: float,
        tags: List[str] = None,
        performance_fee_percent: float = 0.0
    ) -> StrategyListing:
        """Create a new strategy listing"""
        listing_id = str(uuid.uuid4())
        
        listing = StrategyListing(
            listing_id=listing_id,
            strategy=strategy,
            license_type=license_type,
            price=price,
            performance_fee_percent=performance_fee_percent,
            tags=tags or [],
            status=StrategyStatus.DRAFT
        )
        
        self.listings[listing_id] = listing
        
        # Track seller's listings
        seller_id = strategy.author_id
        if seller_id not in self.seller_listings:
            self.seller_listings[seller_id] = []
        self.seller_listings[seller_id].append(listing_id)
        
        self.logger.info(f"Created listing {listing_id} for strategy {strategy.name}")
        
        return listing
    
    def publish_listing(self, listing_id: str) -> bool:
        """Publish a listing (make it visible)"""
        listing = self.listings.get(listing_id)
        
        if not listing:
            return False
        
        # Validation
        if listing.status not in [StrategyStatus.DRAFT, StrategyStatus.PENDING_REVIEW]:
            return False
        
        # Check strategy has required fields
        strategy = listing.strategy
        if not strategy.name or not strategy.description:
            self.logger.warning("Strategy missing required fields")
            return False
        
        # Check for performance metrics
        if not strategy.metrics:
            self.logger.warning("Strategy missing performance metrics")
            return False
        
        listing.status = StrategyStatus.PUBLISHED
        listing.published_at = datetime.now()
        listing.updated_at = datetime.now()
        
        self.logger.info(f"Published listing {listing_id}")
        
        return True
    
    def purchase_strategy(
        self,
        listing_id: str,
        buyer_id: str,
        payment_method: str = "card"
    ) -> Optional[StrategyPurchase]:
        """Purchase a strategy"""
        listing = self.listings.get(listing_id)
        
        if not listing or listing.status != StrategyStatus.PUBLISHED:
            return None
        
        # Check buyer doesn't already own it
        existing = self._get_user_purchase(buyer_id, listing_id)
        if existing and not existing.is_expired():
            self.logger.warning(f"User {buyer_id} already owns this strategy")
            return existing
        
        # Create purchase record
        purchase_id = str(uuid.uuid4())
        
        # Calculate license end date
        license_end = None
        if listing.license_type == LicenseType.MONTHLY:
            license_end = datetime.now() + timedelta(days=30)
        elif listing.license_type == LicenseType.ANNUAL:
            license_end = datetime.now() + timedelta(days=365)
        
        purchase = StrategyPurchase(
            purchase_id=purchase_id,
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=listing.strategy.author_id,
            license_type=listing.license_type,
            price_paid=listing.price,
            payment_method=payment_method,
            license_end=license_end
        )
        
        self.purchases[purchase_id] = purchase
        
        # Track user's purchases
        if buyer_id not in self.user_purchases:
            self.user_purchases[buyer_id] = []
        self.user_purchases[buyer_id].append(purchase_id)
        
        # Update listing stats
        listing.purchases += 1
        if listing.license_type in [LicenseType.MONTHLY, LicenseType.ANNUAL]:
            listing.subscribers += 1
        
        self.logger.info(f"User {buyer_id} purchased strategy {listing_id}")
        
        return purchase
    
    def _get_user_purchase(
        self,
        user_id: str,
        listing_id: str
    ) -> Optional[StrategyPurchase]:
        """Get user's purchase of a specific listing"""
        purchase_ids = self.user_purchases.get(user_id, [])
        
        for pid in purchase_ids:
            purchase = self.purchases.get(pid)
            if purchase and purchase.listing_id == listing_id:
                return purchase
        
        return None
    
    def add_review(
        self,
        listing_id: str,
        user_id: str,
        rating: int,
        title: str,
        content: str,
        detailed_ratings: Dict[str, int] = None
    ) -> Optional[StrategyReview]:
        """Add a review to a strategy"""
        listing = self.listings.get(listing_id)
        
        if not listing:
            return None
        
        # Check if user purchased the strategy
        purchase = self._get_user_purchase(user_id, listing_id)
        verified = purchase is not None
        
        review_id = str(uuid.uuid4())
        
        review = StrategyReview(
            review_id=review_id,
            strategy_id=listing.strategy.strategy_id,
            user_id=user_id,
            rating=max(1, min(5, rating)),
            title=title,
            content=content,
            accuracy_rating=detailed_ratings.get('accuracy', 0) if detailed_ratings else 0,
            documentation_rating=detailed_ratings.get('documentation', 0) if detailed_ratings else 0,
            value_rating=detailed_ratings.get('value', 0) if detailed_ratings else 0,
            support_rating=detailed_ratings.get('support', 0) if detailed_ratings else 0,
            verified_purchase=verified
        )
        
        listing.reviews.append(review)
        listing.calculate_rating()
        listing.updated_at = datetime.now()
        
        self.logger.info(f"Added review to listing {listing_id}")
        
        return review
    
    def search_strategies(
        self,
        query: str = None,
        strategy_type: StrategyType = None,
        asset_classes: List[str] = None,
        min_sharpe: float = None,
        max_drawdown: float = None,
        price_range: Tuple[Any, Any] = None,
        min_rating: float = None,
        tags: List[str] = None,
        sort_by: str = "popularity"
    ) -> List[StrategyListing]:
        """Search for strategies"""
        results = []
        
        for listing in self.listings.values():
            if listing.status != StrategyStatus.PUBLISHED:
                continue
            
            strategy = listing.strategy
            
            # Text search
            if query:
                query_lower = query.lower()
                if (query_lower not in strategy.name.lower() and
                    query_lower not in strategy.description.lower() and
                    not any(query_lower in tag.lower() for tag in listing.tags)):
                    continue
            
            # Strategy type filter
            if strategy_type and strategy.strategy_type != strategy_type:
                continue
            
            # Asset class filter
            if asset_classes:
                if not any(ac in strategy.asset_classes for ac in asset_classes):
                    continue
            
            # Performance filters
            if strategy.metrics:
                if min_sharpe and strategy.metrics.sharpe_ratio < min_sharpe:
                    continue
                if max_drawdown and abs(strategy.metrics.max_drawdown) > max_drawdown:
                    continue
            
            # Price filter
            if price_range:
                min_price, max_price = price_range
                if listing.price < min_price or listing.price > max_price:
                    continue
            
            # Rating filter
            if min_rating and listing.avg_rating < min_rating:
                continue
            
            # Tags filter
            if tags:
                if not any(tag in listing.tags for tag in tags):
                    continue
            
            results.append(listing)
        
        # Sort results
        if sort_by == "popularity":
            results.sort(key=lambda x: x.purchases, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda x: x.avg_rating, reverse=True)
        elif sort_by == "price_low":
            results.sort(key=lambda x: x.price)
        elif sort_by == "price_high":
            results.sort(key=lambda x: x.price, reverse=True)
        elif sort_by == "newest":
            results.sort(key=lambda x: x.published_at or x.created_at, reverse=True)
        elif sort_by == "sharpe":
            results.sort(
                key=lambda x: x.strategy.metrics.sharpe_ratio if x.strategy.metrics else 0,
                reverse=True
            )
        
        return results
    
    def get_featured_strategies(self, limit: int = 10) -> List[StrategyListing]:
        """Get featured strategies"""
        featured = [listing for listing in self.listings.values() 
                   if listing.featured and listing.status == StrategyStatus.PUBLISHED]
        
        # Sort by some criteria (rating, sales, etc.)
        featured.sort(key=lambda x: (x.avg_rating * x.purchases), reverse=True)
        
        return featured[:limit]
    
    def get_top_performers(self, limit: int = 10) -> List[StrategyListing]:
        """Get top performing strategies"""
        published = [listing for listing in self.listings.values() 
                    if listing.status == StrategyStatus.PUBLISHED and listing.strategy.metrics]
        
        published.sort(
            key=lambda x: x.strategy.metrics.sharpe_ratio if x.strategy.metrics else 0,
            reverse=True
        )
        
        return published[:limit]
    
    def get_seller_earnings(self, seller_id: str) -> Dict[str, Any]:
        """Get earnings for a seller"""
        listing_ids = self.seller_listings.get(seller_id, [])
        
        total_sales = 0
        total_revenue = 0.0
        total_subscribers = 0
        performance_fees = 0.0
        
        for listing_id in listing_ids:
            listing = self.listings.get(listing_id)
            if not listing:
                continue
            
            total_sales += listing.purchases
            total_subscribers += listing.subscribers
        
        # Calculate from purchases
        for purchase in self.purchases.values():
            if purchase.seller_id == seller_id and not purchase.refunded:
                total_revenue += purchase.price_paid
                performance_fees += purchase.performance_fees_paid
        
        # Platform fee
        platform_fee = total_revenue * (self.platform_fee_percent / 100)
        net_revenue = total_revenue - platform_fee
        
        return {
            'seller_id': seller_id,
            'total_sales': total_sales,
            'total_subscribers': total_subscribers,
            'gross_revenue': total_revenue,
            'platform_fee': platform_fee,
            'performance_fees': performance_fees,
            'net_revenue': net_revenue + performance_fees,
            'listing_count': len(listing_ids)
        }
    
    def get_user_library(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's purchased strategies"""
        purchase_ids = self.user_purchases.get(user_id, [])
        library = []
        
        for pid in purchase_ids:
            purchase = self.purchases.get(pid)
            if not purchase:
                continue
            
            listing = self.listings.get(purchase.listing_id)
            if not listing:
                continue
            
            library.append({
                'purchase': purchase.to_dict(),
                'strategy': listing.strategy.to_dict(),
                'is_active': purchase.is_active and not purchase.is_expired(),
                'days_remaining': (purchase.license_end - datetime.now()).days if purchase.license_end else None
            })
        
        return library
    
    def track_strategy_performance(
        self,
        purchase_id: str,
        returns: float
    ) -> float:
        """Track strategy performance and calculate fees"""
        purchase = self.purchases.get(purchase_id)
        
        if not purchase or not purchase.is_active:
            return 0.0
        
        listing = self.listings.get(purchase.listing_id)
        
        if not listing:
            return 0.0
        
        purchase.total_returns += returns
        purchase.times_deployed += 1
        
        # Calculate performance fee if applicable
        performance_fee = 0.0
        if listing.license_type == LicenseType.PERFORMANCE_FEE and returns > 0:
            performance_fee = returns * (listing.performance_fee_percent / 100)
            purchase.performance_fees_paid += performance_fee
        
        return performance_fee
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        published = [listing for listing in self.listings.values() 
                    if listing.status == StrategyStatus.PUBLISHED]
        
        total_revenue = sum(p.price_paid for p in self.purchases.values() if not p.refunded)
        
        return {
            'total_listings': len(self.listings),
            'published_listings': len(published),
            'total_purchases': len(self.purchases),
            'total_revenue': total_revenue,
            'platform_earnings': total_revenue * (self.platform_fee_percent / 100),
            'unique_sellers': len(self.seller_listings),
            'unique_buyers': len(self.user_purchases),
            'avg_strategy_price': sum(listing.price for listing in published) / len(published) if published else 0,
            'avg_rating': sum(listing.avg_rating for listing in published) / len(published) if published else 0
        }


# Convenience type alias
