"""
Social Trading & Community Features
====================================

Enterprise-grade social trading platform with:
- Portfolio sharing with privacy controls
- Strategy marketplace for buying/selling AI trading strategies
- Leaderboards with risk-adjusted returns competitions
- Expert network connecting retail investors with professionals
- Copy trading with customizable risk limits

Builds network effects and user engagement.
"""

import asyncio
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class PrivacyLevel(Enum):
    """Portfolio sharing privacy levels"""
    PRIVATE = "private"
    FRIENDS_ONLY = "friends_only"
    FOLLOWERS = "followers"
    BENCHMARK_ONLY = "benchmark_only"  # Shows performance but not holdings
    PUBLIC = "public"


class StrategyStatus(Enum):
    """Strategy marketplace status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class LeaderboardType(Enum):
    """Leaderboard categories"""
    TOTAL_RETURN = "total_return"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    CONSISTENCY = "consistency"
    RISK_ADJUSTED = "risk_adjusted"
    SECTOR_SPECIFIC = "sector_specific"


class ExpertTier(Enum):
    """Expert network tiers"""
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    PROFESSIONAL = "professional"


class CopyTradingMode(Enum):
    """Copy trading modes"""
    FULL_COPY = "full_copy"
    PROPORTIONAL = "proportional"
    FIXED_AMOUNT = "fixed_amount"
    SIGNAL_ONLY = "signal_only"


@dataclass
class UserProfile:
    """Social trading user profile"""
    user_id: str
    username: str
    display_name: str
    bio: str = ""
    avatar_url: Optional[str] = None
    expert_tier: ExpertTier = ExpertTier.NOVICE
    verified: bool = False
    followers_count: int = 0
    following_count: int = 0
    portfolio_privacy: PrivacyLevel = PrivacyLevel.PRIVATE
    joined_at: datetime = field(default_factory=datetime.now)
    
    # Performance metrics (public if sharing enabled)
    total_return_pct: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    
    # Social stats
    strategies_published: int = 0
    strategies_sold: int = 0
    total_copiers: int = 0
    reputation_score: float = 0.0
    
    # Badges and achievements
    badges: List[str] = field(default_factory=list)


@dataclass
class SharedPortfolio:
    """Shared portfolio configuration"""
    portfolio_id: str
    owner_id: str
    name: str
    description: str
    privacy_level: PrivacyLevel
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # What to share
    show_holdings: bool = False
    show_allocation: bool = True
    show_performance: bool = True
    show_trades: bool = False
    show_risk_metrics: bool = True
    
    # Anonymization settings
    anonymize_positions: bool = False
    delay_trades: int = 24  # Hours to delay trade visibility
    
    # Followers
    followers: List[str] = field(default_factory=list)
    allowed_viewers: List[str] = field(default_factory=list)
    
    # Performance snapshot
    performance_snapshot: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradingStrategy:
    """Tradeable strategy in the marketplace"""
    strategy_id: str
    creator_id: str
    name: str
    description: str
    strategy_type: str  # "momentum", "value", "growth", etc.
    status: StrategyStatus = StrategyStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    
    # Pricing
    price_usd: float = 0.0
    subscription_monthly: float = 0.0
    revenue_share_pct: float = 0.0
    free_trial_days: int = 0
    
    # Performance metrics
    backtest_period: str = ""
    live_trading_days: int = 0
    total_return: float = 0.0
    annualized_return: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    
    # Risk characteristics
    risk_level: str = "moderate"  # low, moderate, high, aggressive
    recommended_capital: float = 10000.0
    max_position_size: float = 0.10
    typical_holding_period: str = "days"
    
    # Social metrics
    subscribers: int = 0
    reviews_count: int = 0
    average_rating: float = 0.0
    total_copies: int = 0
    
    # Strategy logic (encrypted)
    strategy_config: Dict[str, Any] = field(default_factory=dict)
    
    # Tags and categories
    tags: List[str] = field(default_factory=list)
    asset_classes: List[str] = field(default_factory=list)


@dataclass
class StrategyReview:
    """User review of a strategy"""
    review_id: str
    strategy_id: str
    reviewer_id: str
    rating: int  # 1-5 stars
    title: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    
    # Performance during use
    used_days: int = 0
    return_during_use: float = 0.0
    
    # Helpful votes
    helpful_count: int = 0
    not_helpful_count: int = 0
    
    # Verification
    verified_purchase: bool = False


@dataclass
class LeaderboardEntry:
    """Entry in a leaderboard"""
    rank: int
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str]
    expert_tier: ExpertTier
    
    # Metrics
    metric_value: float
    metric_name: str
    
    # Supporting metrics
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Rank change
    previous_rank: Optional[int] = None
    rank_change: int = 0
    
    # Badges
    badges: List[str] = field(default_factory=list)


@dataclass
class Competition:
    """Trading competition"""
    competition_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    
    # Rules
    metric: LeaderboardType = LeaderboardType.RISK_ADJUSTED
    min_trades: int = 10
    min_participants: int = 10
    entry_fee_usd: float = 0.0
    
    # Prizes
    prize_pool_usd: float = 0.0
    prize_distribution: Dict[int, float] = field(default_factory=dict)  # rank -> percentage
    
    # Status
    status: str = "upcoming"  # upcoming, active, ended
    participants: List[str] = field(default_factory=list)
    leaderboard: List[LeaderboardEntry] = field(default_factory=list)


@dataclass
class ExpertConsultation:
    """Expert network consultation"""
    consultation_id: str
    expert_id: str
    client_id: str
    topic: str
    description: str
    scheduled_time: datetime
    duration_minutes: int = 30
    
    # Pricing
    rate_per_hour: float = 0.0
    total_cost: float = 0.0
    
    # Status
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    
    # Feedback
    client_rating: Optional[int] = None
    client_feedback: Optional[str] = None
    expert_notes: Optional[str] = None


@dataclass
class CopyTradingSubscription:
    """Copy trading subscription"""
    subscription_id: str
    copier_id: str
    leader_id: str
    strategy_id: Optional[str] = None
    mode: CopyTradingMode = CopyTradingMode.PROPORTIONAL
    created_at: datetime = field(default_factory=datetime.now)
    
    # Configuration
    allocation_amount: float = 10000.0
    allocation_percentage: float = 0.10  # 10% of portfolio
    max_position_size: float = 0.05
    max_drawdown_limit: float = 0.10
    stop_loss_pct: float = 0.15
    
    # Risk controls
    max_trades_per_day: int = 10
    min_trade_size: float = 100.0
    max_trade_size: float = 5000.0
    excluded_symbols: List[str] = field(default_factory=list)
    allowed_asset_classes: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    is_paused: bool = False
    paused_reason: Optional[str] = None
    
    # Performance tracking
    total_copied_trades: int = 0
    successful_trades: int = 0
    total_pnl: float = 0.0
    pnl_percentage: float = 0.0


@dataclass
class SocialActivity:
    """Social activity feed item"""
    activity_id: str
    user_id: str
    activity_type: str  # trade, achievement, follow, comment, strategy_published
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Visibility
    is_public: bool = True
    
    # Engagement
    likes: int = 0
    comments: int = 0
    shares: int = 0


class PortfolioSharingService:
    """
    Service for managing portfolio sharing with privacy controls.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.shared_portfolios: Dict[str, SharedPortfolio] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.followers: Dict[str, List[str]] = {}  # user_id -> list of follower_ids
        self.following: Dict[str, List[str]] = {}  # user_id -> list of following_ids
    
    async def create_shared_portfolio(
        self,
        owner_id: str,
        name: str,
        description: str,
        privacy_level: PrivacyLevel,
        settings: Dict[str, Any]
    ) -> SharedPortfolio:
        """Create a new shared portfolio"""
        portfolio = SharedPortfolio(
            portfolio_id=secrets.token_urlsafe(16),
            owner_id=owner_id,
            name=name,
            description=description,
            privacy_level=privacy_level,
            show_holdings=settings.get("show_holdings", False),
            show_allocation=settings.get("show_allocation", True),
            show_performance=settings.get("show_performance", True),
            show_trades=settings.get("show_trades", False),
            show_risk_metrics=settings.get("show_risk_metrics", True),
            anonymize_positions=settings.get("anonymize_positions", False),
            delay_trades=settings.get("delay_trades", 24)
        )
        
        self.shared_portfolios[portfolio.portfolio_id] = portfolio
        self.logger.info(f"Created shared portfolio {portfolio.portfolio_id} for user {owner_id}")
        
        return portfolio
    
    async def update_privacy_settings(
        self,
        portfolio_id: str,
        user_id: str,
        new_privacy: PrivacyLevel,
        settings: Dict[str, Any]
    ) -> bool:
        """Update portfolio privacy settings"""
        portfolio = self.shared_portfolios.get(portfolio_id)
        if not portfolio or portfolio.owner_id != user_id:
            return False
        
        portfolio.privacy_level = new_privacy
        portfolio.show_holdings = settings.get("show_holdings", portfolio.show_holdings)
        portfolio.show_allocation = settings.get("show_allocation", portfolio.show_allocation)
        portfolio.show_performance = settings.get("show_performance", portfolio.show_performance)
        portfolio.show_trades = settings.get("show_trades", portfolio.show_trades)
        portfolio.show_risk_metrics = settings.get("show_risk_metrics", portfolio.show_risk_metrics)
        portfolio.last_updated = datetime.now()
        
        return True
    
    async def get_portfolio_view(
        self,
        portfolio_id: str,
        viewer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get portfolio view based on privacy settings"""
        portfolio = self.shared_portfolios.get(portfolio_id)
        if not portfolio:
            return None
        
        # Check access
        if not self._check_access(portfolio, viewer_id):
            return None
        
        # Build view based on settings
        view = {
            "portfolio_id": portfolio.portfolio_id,
            "name": portfolio.name,
            "description": portfolio.description,
            "owner_id": portfolio.owner_id,
            "last_updated": portfolio.last_updated.isoformat()
        }
        
        if portfolio.show_performance:
            view["performance"] = portfolio.performance_snapshot.get("performance", {})
        
        if portfolio.show_allocation:
            if portfolio.anonymize_positions:
                view["allocation"] = self._anonymize_allocation(
                    portfolio.performance_snapshot.get("allocation", {})
                )
            else:
                view["allocation"] = portfolio.performance_snapshot.get("allocation", {})
        
        if portfolio.show_holdings and not portfolio.anonymize_positions:
            view["holdings"] = portfolio.performance_snapshot.get("holdings", [])
        
        if portfolio.show_risk_metrics:
            view["risk_metrics"] = portfolio.performance_snapshot.get("risk_metrics", {})
        
        if portfolio.show_trades:
            trades = portfolio.performance_snapshot.get("trades", [])
            # Apply trade delay
            cutoff = datetime.now() - timedelta(hours=portfolio.delay_trades)
            view["trades"] = [
                t for t in trades
                if datetime.fromisoformat(t.get("timestamp", "")) < cutoff
            ]
        
        return view
    
    def _check_access(self, portfolio: SharedPortfolio, viewer_id: str) -> bool:
        """Check if viewer has access to portfolio"""
        if portfolio.owner_id == viewer_id:
            return True
        
        if portfolio.privacy_level == PrivacyLevel.PUBLIC:
            return True
        elif portfolio.privacy_level == PrivacyLevel.PRIVATE:
            return False
        elif portfolio.privacy_level == PrivacyLevel.FRIENDS_ONLY:
            return viewer_id in portfolio.allowed_viewers
        elif portfolio.privacy_level == PrivacyLevel.FOLLOWERS:
            return viewer_id in portfolio.followers
        elif portfolio.privacy_level == PrivacyLevel.BENCHMARK_ONLY:
            return True  # Performance only, checked elsewhere
        
        return False
    
    def _anonymize_allocation(self, allocation: Dict[str, float]) -> Dict[str, float]:
        """Anonymize position names while preserving allocation percentages"""
        return {
            f"Position_{i+1}": pct
            for i, (_, pct) in enumerate(sorted(allocation.items(), key=lambda x: -x[1]))
        }
    
    async def follow_user(self, follower_id: str, target_id: str) -> bool:
        """Follow a user"""
        if follower_id == target_id:
            return False
        
        if target_id not in self.followers:
            self.followers[target_id] = []
        if follower_id not in self.following:
            self.following[follower_id] = []
        
        if follower_id not in self.followers[target_id]:
            self.followers[target_id].append(follower_id)
            self.following[follower_id].append(target_id)
            
            # Update counts
            if target_id in self.user_profiles:
                self.user_profiles[target_id].followers_count += 1
            if follower_id in self.user_profiles:
                self.user_profiles[follower_id].following_count += 1
            
            return True
        return False
    
    async def unfollow_user(self, follower_id: str, target_id: str) -> bool:
        """Unfollow a user"""
        if target_id in self.followers and follower_id in self.followers[target_id]:
            self.followers[target_id].remove(follower_id)
            if follower_id in self.following:
                self.following[follower_id].remove(target_id)
            
            # Update counts
            if target_id in self.user_profiles:
                self.user_profiles[target_id].followers_count -= 1
            if follower_id in self.user_profiles:
                self.user_profiles[follower_id].following_count -= 1
            
            return True
        return False


class StrategyMarketplace:
    """
    Marketplace for buying and selling AI trading strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.strategies: Dict[str, TradingStrategy] = {}
        self.reviews: Dict[str, List[StrategyReview]] = {}
        self.purchases: Dict[str, List[str]] = {}  # user_id -> list of strategy_ids
        self.subscriptions: Dict[str, List[str]] = {}  # user_id -> list of strategy_ids
    
    async def publish_strategy(
        self,
        creator_id: str,
        name: str,
        description: str,
        strategy_type: str,
        pricing: Dict[str, float],
        config: Dict[str, Any],
        performance: Dict[str, float]
    ) -> TradingStrategy:
        """Publish a new trading strategy to the marketplace"""
        strategy = TradingStrategy(
            strategy_id=secrets.token_urlsafe(16),
            creator_id=creator_id,
            name=name,
            description=description,
            strategy_type=strategy_type,
            price_usd=pricing.get("one_time", 0.0),
            subscription_monthly=pricing.get("monthly", 0.0),
            revenue_share_pct=pricing.get("revenue_share", 0.0),
            free_trial_days=pricing.get("free_trial_days", 0),
            total_return=performance.get("total_return", 0.0),
            annualized_return=performance.get("annualized_return", 0.0),
            sharpe_ratio=performance.get("sharpe_ratio", 0.0),
            sortino_ratio=performance.get("sortino_ratio", 0.0),
            max_drawdown=performance.get("max_drawdown", 0.0),
            win_rate=performance.get("win_rate", 0.0),
            profit_factor=performance.get("profit_factor", 0.0),
            strategy_config=config,
            status=StrategyStatus.PENDING_REVIEW
        )
        
        self.strategies[strategy.strategy_id] = strategy
        self.reviews[strategy.strategy_id] = []
        
        self.logger.info(f"Strategy {strategy.strategy_id} submitted for review")
        return strategy
    
    async def search_strategies(
        self,
        filters: Dict[str, Any],
        sort_by: str = "sharpe_ratio",
        limit: int = 20,
        offset: int = 0
    ) -> List[TradingStrategy]:
        """Search strategies with filters"""
        results = []
        
        for strategy in self.strategies.values():
            if strategy.status != StrategyStatus.ACTIVE:
                continue
            
            # Apply filters
            if filters.get("strategy_type") and strategy.strategy_type != filters["strategy_type"]:
                continue
            if filters.get("min_sharpe") and strategy.sharpe_ratio < filters["min_sharpe"]:
                continue
            if filters.get("max_drawdown") and strategy.max_drawdown > filters["max_drawdown"]:
                continue
            if filters.get("risk_level") and strategy.risk_level != filters["risk_level"]:
                continue
            if filters.get("max_price") and strategy.price_usd > filters["max_price"]:
                continue
            if filters.get("asset_classes"):
                if not any(ac in strategy.asset_classes for ac in filters["asset_classes"]):
                    continue
            
            results.append(strategy)
        
        # Sort
        sort_key = {
            "sharpe_ratio": lambda x: x.sharpe_ratio,
            "total_return": lambda x: x.total_return,
            "rating": lambda x: x.average_rating,
            "subscribers": lambda x: x.subscribers,
            "price": lambda x: x.price_usd
        }.get(sort_by, lambda x: x.sharpe_ratio)
        
        results.sort(key=sort_key, reverse=True)
        
        return results[offset:offset + limit]
    
    async def purchase_strategy(
        self,
        buyer_id: str,
        strategy_id: str,
        payment_method: str = "card"
    ) -> Dict[str, Any]:
        """Purchase a strategy"""
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return {"success": False, "error": "Strategy not found"}
        
        if strategy.status != StrategyStatus.ACTIVE:
            return {"success": False, "error": "Strategy not available"}
        
        # Process payment (mock)
        payment_result = await self._process_payment(buyer_id, strategy.price_usd, payment_method)
        
        if payment_result["success"]:
            if buyer_id not in self.purchases:
                self.purchases[buyer_id] = []
            self.purchases[buyer_id].append(strategy_id)
            strategy.subscribers += 1
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "transaction_id": payment_result["transaction_id"],
                "strategy_config": strategy.strategy_config
            }
        
        return payment_result
    
    async def subscribe_to_strategy(
        self,
        subscriber_id: str,
        strategy_id: str,
        payment_method: str = "card"
    ) -> Dict[str, Any]:
        """Subscribe to a strategy monthly"""
        strategy = self.strategies.get(strategy_id)
        if not strategy or strategy.subscription_monthly == 0:
            return {"success": False, "error": "Subscription not available"}
        
        # Process subscription payment
        payment_result = await self._process_payment(
            subscriber_id,
            strategy.subscription_monthly,
            payment_method,
            is_subscription=True
        )
        
        if payment_result["success"]:
            if subscriber_id not in self.subscriptions:
                self.subscriptions[subscriber_id] = []
            self.subscriptions[subscriber_id].append(strategy_id)
            strategy.subscribers += 1
            
            return {
                "success": True,
                "subscription_id": payment_result["subscription_id"],
                "strategy_id": strategy_id,
                "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
        
        return payment_result
    
    async def add_review(
        self,
        strategy_id: str,
        reviewer_id: str,
        rating: int,
        title: str,
        content: str,
        performance: Dict[str, Any]
    ) -> StrategyReview:
        """Add a review for a strategy"""
        # Check if user has purchased/subscribed
        verified = (
            reviewer_id in self.purchases.get(reviewer_id, []) or
            reviewer_id in self.subscriptions.get(reviewer_id, [])
        )
        
        review = StrategyReview(
            review_id=secrets.token_urlsafe(16),
            strategy_id=strategy_id,
            reviewer_id=reviewer_id,
            rating=min(5, max(1, rating)),
            title=title,
            content=content,
            used_days=performance.get("used_days", 0),
            return_during_use=performance.get("return", 0.0),
            verified_purchase=verified
        )
        
        if strategy_id not in self.reviews:
            self.reviews[strategy_id] = []
        self.reviews[strategy_id].append(review)
        
        # Update average rating
        strategy = self.strategies.get(strategy_id)
        if strategy:
            all_ratings = [r.rating for r in self.reviews[strategy_id]]
            strategy.average_rating = sum(all_ratings) / len(all_ratings)
            strategy.reviews_count = len(all_ratings)
        
        return review
    
    async def _process_payment(
        self,
        user_id: str,
        amount: float,
        payment_method: str,
        is_subscription: bool = False
    ) -> Dict[str, Any]:
        """Process payment (mock implementation)"""
        # In production, integrate with Stripe, PayPal, etc.
        return {
            "success": True,
            "transaction_id": secrets.token_urlsafe(16),
            "subscription_id": secrets.token_urlsafe(16) if is_subscription else None,
            "amount": amount,
            "currency": "USD"
        }


class LeaderboardService:
    """
    Leaderboard service for competitions and rankings.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.leaderboards: Dict[str, List[LeaderboardEntry]] = {}
        self.competitions: Dict[str, Competition] = {}
        self.user_stats: Dict[str, Dict[str, float]] = {}
    
    async def update_leaderboard(
        self,
        leaderboard_type: LeaderboardType,
        period: str = "monthly"
    ) -> List[LeaderboardEntry]:
        """Update and get leaderboard for a specific metric"""
        key = f"{leaderboard_type.value}_{period}"
        
        # Calculate rankings
        entries = []
        for user_id, stats in self.user_stats.items():
            metric_value = stats.get(leaderboard_type.value, 0.0)
            
            entry = LeaderboardEntry(
                rank=0,  # Will be set after sorting
                user_id=user_id,
                username=stats.get("username", f"user_{user_id[:8]}"),
                display_name=stats.get("display_name", "Anonymous"),
                avatar_url=stats.get("avatar_url"),
                expert_tier=ExpertTier(stats.get("expert_tier", "novice")),
                metric_value=metric_value,
                metric_name=leaderboard_type.value,
                total_return=stats.get("total_return", 0.0),
                sharpe_ratio=stats.get("sharpe_ratio", 0.0),
                max_drawdown=stats.get("max_drawdown", 0.0),
                win_rate=stats.get("win_rate", 0.0),
                badges=stats.get("badges", [])
            )
            entries.append(entry)
        
        # Sort by metric (higher is better, except max_drawdown)
        reverse = leaderboard_type != LeaderboardType.MAX_DRAWDOWN
        entries.sort(key=lambda x: x.metric_value, reverse=reverse)
        
        # Assign ranks and calculate changes
        previous_leaderboard = self.leaderboards.get(key, [])
        previous_ranks = {e.user_id: e.rank for e in previous_leaderboard}
        
        for i, entry in enumerate(entries):
            entry.rank = i + 1
            entry.previous_rank = previous_ranks.get(entry.user_id)
            if entry.previous_rank:
                entry.rank_change = entry.previous_rank - entry.rank
        
        self.leaderboards[key] = entries
        return entries[:100]  # Top 100
    
    async def create_competition(
        self,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        metric: LeaderboardType,
        entry_fee: float = 0.0,
        prize_pool: float = 0.0,
        prize_distribution: Dict[int, float] = None
    ) -> Competition:
        """Create a new trading competition"""
        competition = Competition(
            competition_id=secrets.token_urlsafe(16),
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            metric=metric,
            entry_fee_usd=entry_fee,
            prize_pool_usd=prize_pool,
            prize_distribution=prize_distribution or {1: 0.5, 2: 0.3, 3: 0.2}
        )
        
        self.competitions[competition.competition_id] = competition
        return competition
    
    async def join_competition(
        self,
        competition_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Join a competition"""
        competition = self.competitions.get(competition_id)
        if not competition:
            return {"success": False, "error": "Competition not found"}
        
        if competition.status != "upcoming" and competition.status != "active":
            return {"success": False, "error": "Competition not accepting participants"}
        
        if user_id in competition.participants:
            return {"success": False, "error": "Already joined"}
        
        # Process entry fee if applicable
        if competition.entry_fee_usd > 0:
            # Process payment
            pass
        
        competition.participants.append(user_id)
        
        return {
            "success": True,
            "competition_id": competition_id,
            "participant_number": len(competition.participants)
        }
    
    async def get_competition_leaderboard(
        self,
        competition_id: str
    ) -> List[LeaderboardEntry]:
        """Get current competition leaderboard"""
        competition = self.competitions.get(competition_id)
        if not competition:
            return []
        
        # Calculate rankings for participants only
        entries = []
        for user_id in competition.participants:
            stats = self.user_stats.get(user_id, {})
            metric_value = stats.get(competition.metric.value, 0.0)
            
            entry = LeaderboardEntry(
                rank=0,
                user_id=user_id,
                username=stats.get("username", f"user_{user_id[:8]}"),
                display_name=stats.get("display_name", "Anonymous"),
                avatar_url=stats.get("avatar_url"),
                expert_tier=ExpertTier(stats.get("expert_tier", "novice")),
                metric_value=metric_value,
                metric_name=competition.metric.value,
                period_start=competition.start_date,
                period_end=competition.end_date
            )
            entries.append(entry)
        
        # Sort
        reverse = competition.metric != LeaderboardType.MAX_DRAWDOWN
        entries.sort(key=lambda x: x.metric_value, reverse=reverse)
        
        for i, entry in enumerate(entries):
            entry.rank = i + 1
        
        competition.leaderboard = entries
        return entries
    
    async def award_badges(self, user_id: str, badge_type: str) -> bool:
        """Award a badge to a user"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {}
        
        if "badges" not in self.user_stats[user_id]:
            self.user_stats[user_id]["badges"] = []
        
        if badge_type not in self.user_stats[user_id]["badges"]:
            self.user_stats[user_id]["badges"].append(badge_type)
            return True
        return False


class ExpertNetworkService:
    """
    Expert network connecting retail investors with professionals.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.experts: Dict[str, Dict[str, Any]] = {}
        self.consultations: Dict[str, ExpertConsultation] = {}
        self.availability: Dict[str, List[Dict[str, Any]]] = {}
    
    async def register_expert(
        self,
        user_id: str,
        credentials: Dict[str, Any],
        specializations: List[str],
        rate_per_hour: float,
        availability: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Register as an expert"""
        # Verification would happen here
        self.experts[user_id] = {
            "user_id": user_id,
            "credentials": credentials,
            "specializations": specializations,
            "rate_per_hour": rate_per_hour,
            "verified": False,  # Pending verification
            "rating": 0.0,
            "consultations_count": 0,
            "registered_at": datetime.now().isoformat()
        }
        
        self.availability[user_id] = availability
        
        return {"success": True, "status": "pending_verification"}
    
    async def search_experts(
        self,
        specialization: Optional[str] = None,
        min_rating: float = 0.0,
        max_rate: Optional[float] = None,
        available_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Search for experts"""
        results = []
        
        for expert_id, expert in self.experts.items():
            if not expert.get("verified"):
                continue
            
            if specialization and specialization not in expert.get("specializations", []):
                continue
            
            if expert.get("rating", 0) < min_rating:
                continue
            
            if max_rate and expert.get("rate_per_hour", 0) > max_rate:
                continue
            
            # Check availability
            if available_date:
                if not self._check_availability(expert_id, available_date):
                    continue
            
            results.append(expert)
        
        # Sort by rating
        results.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return results
    
    async def book_consultation(
        self,
        client_id: str,
        expert_id: str,
        topic: str,
        description: str,
        scheduled_time: datetime,
        duration_minutes: int = 30
    ) -> ExpertConsultation:
        """Book a consultation with an expert"""
        expert = self.experts.get(expert_id)
        if not expert:
            raise ValueError("Expert not found")
        
        rate = expert.get("rate_per_hour", 0)
        total_cost = rate * (duration_minutes / 60)
        
        consultation = ExpertConsultation(
            consultation_id=secrets.token_urlsafe(16),
            expert_id=expert_id,
            client_id=client_id,
            topic=topic,
            description=description,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            rate_per_hour=rate,
            total_cost=total_cost
        )
        
        self.consultations[consultation.consultation_id] = consultation
        
        return consultation
    
    async def complete_consultation(
        self,
        consultation_id: str,
        client_rating: int,
        client_feedback: str,
        expert_notes: str
    ) -> bool:
        """Complete a consultation and leave feedback"""
        consultation = self.consultations.get(consultation_id)
        if not consultation:
            return False
        
        consultation.status = "completed"
        consultation.client_rating = client_rating
        consultation.client_feedback = client_feedback
        consultation.expert_notes = expert_notes
        
        # Update expert rating
        expert = self.experts.get(consultation.expert_id)
        if expert:
            total_ratings = expert.get("consultations_count", 0)
            current_rating = expert.get("rating", 0)
            new_rating = (current_rating * total_ratings + client_rating) / (total_ratings + 1)
            expert["rating"] = new_rating
            expert["consultations_count"] = total_ratings + 1
        
        return True
    
    def _check_availability(self, expert_id: str, requested_time: datetime) -> bool:
        """Check if expert is available at requested time"""
        slots = self.availability.get(expert_id, [])
        for slot in slots:
            start = datetime.fromisoformat(slot.get("start", ""))
            end = datetime.fromisoformat(slot.get("end", ""))
            if start <= requested_time <= end:
                return True
        return False


class CopyTradingService:
    """
    Copy trading service with customizable risk limits.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.subscriptions: Dict[str, CopyTradingSubscription] = {}
        self.leaders: Dict[str, Dict[str, Any]] = {}
        self.trade_queue: asyncio.Queue = asyncio.Queue()
    
    async def start_copy_trading(
        self,
        copier_id: str,
        leader_id: str,
        mode: CopyTradingMode,
        settings: Dict[str, Any]
    ) -> CopyTradingSubscription:
        """Start copying a trader"""
        subscription = CopyTradingSubscription(
            subscription_id=secrets.token_urlsafe(16),
            copier_id=copier_id,
            leader_id=leader_id,
            mode=mode,
            allocation_amount=settings.get("allocation_amount", 10000.0),
            allocation_percentage=settings.get("allocation_percentage", 0.10),
            max_position_size=settings.get("max_position_size", 0.05),
            max_drawdown_limit=settings.get("max_drawdown_limit", 0.10),
            stop_loss_pct=settings.get("stop_loss_pct", 0.15),
            max_trades_per_day=settings.get("max_trades_per_day", 10),
            min_trade_size=settings.get("min_trade_size", 100.0),
            max_trade_size=settings.get("max_trade_size", 5000.0),
            excluded_symbols=settings.get("excluded_symbols", []),
            allowed_asset_classes=settings.get("allowed_asset_classes", ["equity"])
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        
        # Update leader stats
        if leader_id not in self.leaders:
            self.leaders[leader_id] = {"copiers": 0, "aum": 0.0}
        self.leaders[leader_id]["copiers"] += 1
        self.leaders[leader_id]["aum"] += subscription.allocation_amount
        
        self.logger.info(f"User {copier_id} started copying {leader_id}")
        return subscription
    
    async def process_leader_trade(
        self,
        leader_id: str,
        trade: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process a leader's trade and execute copies"""
        copied_trades = []
        
        for sub_id, subscription in self.subscriptions.items():
            if subscription.leader_id != leader_id:
                continue
            
            if not subscription.is_active or subscription.is_paused:
                continue
            
            # Check trade limits
            if not self._validate_trade_for_copier(subscription, trade):
                continue
            
            # Calculate copy parameters
            copy_trade = self._calculate_copy_trade(subscription, trade)
            
            if copy_trade:
                copied_trades.append({
                    "subscription_id": sub_id,
                    "copier_id": subscription.copier_id,
                    "trade": copy_trade
                })
                
                subscription.total_copied_trades += 1
        
        return copied_trades
    
    def _validate_trade_for_copier(
        self,
        subscription: CopyTradingSubscription,
        trade: Dict[str, Any]
    ) -> bool:
        """Validate if trade should be copied for this subscriber"""
        symbol = trade.get("symbol", "")
        
        # Check excluded symbols
        if symbol in subscription.excluded_symbols:
            return False
        
        # Check asset class
        asset_class = trade.get("asset_class", "equity")
        if subscription.allowed_asset_classes and asset_class not in subscription.allowed_asset_classes:
            return False
        
        # Check daily trade limit (simplified)
        # In production, track actual daily trades
        
        return True
    
    def _calculate_copy_trade(
        self,
        subscription: CopyTradingSubscription,
        leader_trade: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Calculate the copy trade based on mode and settings"""
        if subscription.mode == CopyTradingMode.SIGNAL_ONLY:
            return {
                "type": "signal",
                "symbol": leader_trade["symbol"],
                "action": leader_trade["action"],
                "recommendation": True
            }
        
        leader_position_pct = leader_trade.get("position_percentage", 0.05)
        trade_amount = 0.0
        
        if subscription.mode == CopyTradingMode.FULL_COPY:
            trade_amount = subscription.allocation_amount * leader_position_pct
        elif subscription.mode == CopyTradingMode.PROPORTIONAL:
            trade_amount = subscription.allocation_amount * leader_position_pct * subscription.allocation_percentage
        elif subscription.mode == CopyTradingMode.FIXED_AMOUNT:
            trade_amount = min(subscription.max_trade_size, subscription.allocation_amount * 0.02)
        
        # Apply limits
        trade_amount = max(subscription.min_trade_size, min(subscription.max_trade_size, trade_amount))
        
        # Check max position size
        max_position = subscription.allocation_amount * subscription.max_position_size
        if trade_amount > max_position:
            trade_amount = max_position
        
        return {
            "type": "copy",
            "symbol": leader_trade["symbol"],
            "action": leader_trade["action"],
            "amount": trade_amount,
            "price": leader_trade.get("price"),
            "original_trade_id": leader_trade.get("trade_id")
        }
    
    async def pause_copy_trading(
        self,
        subscription_id: str,
        reason: str
    ) -> bool:
        """Pause copy trading subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if subscription:
            subscription.is_paused = True
            subscription.paused_reason = reason
            return True
        return False
    
    async def stop_copy_trading(
        self,
        subscription_id: str
    ) -> bool:
        """Stop and remove copy trading subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if subscription:
            # Update leader stats
            if subscription.leader_id in self.leaders:
                self.leaders[subscription.leader_id]["copiers"] -= 1
                self.leaders[subscription.leader_id]["aum"] -= subscription.allocation_amount
            
            subscription.is_active = False
            return True
        return False
    
    async def get_performance_summary(
        self,
        subscription_id: str
    ) -> Dict[str, Any]:
        """Get performance summary for a copy trading subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return {}
        
        return {
            "subscription_id": subscription_id,
            "leader_id": subscription.leader_id,
            "mode": subscription.mode.value,
            "allocation": subscription.allocation_amount,
            "total_trades": subscription.total_copied_trades,
            "successful_trades": subscription.successful_trades,
            "win_rate": subscription.successful_trades / max(1, subscription.total_copied_trades),
            "total_pnl": subscription.total_pnl,
            "pnl_percentage": subscription.pnl_percentage,
            "is_active": subscription.is_active,
            "is_paused": subscription.is_paused
        }


class SocialTradingPlatform:
    """
    Main social trading platform integrating all social features.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize all services
        self.portfolio_sharing = PortfolioSharingService(config)
        self.marketplace = StrategyMarketplace(config)
        self.leaderboard = LeaderboardService(config)
        self.expert_network = ExpertNetworkService(config)
        self.copy_trading = CopyTradingService(config)
        
        # Activity feed
        self.activities: List[SocialActivity] = []
    
    async def post_activity(
        self,
        user_id: str,
        activity_type: str,
        content: Dict[str, Any],
        is_public: bool = True
    ) -> SocialActivity:
        """Post a social activity"""
        activity = SocialActivity(
            activity_id=secrets.token_urlsafe(16),
            user_id=user_id,
            activity_type=activity_type,
            content=content,
            is_public=is_public
        )
        
        self.activities.insert(0, activity)
        
        # Keep last 10000 activities
        if len(self.activities) > 10000:
            self.activities = self.activities[:10000]
        
        return activity
    
    async def get_activity_feed(
        self,
        user_id: str,
        following_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[SocialActivity]:
        """Get activity feed for user"""
        if following_only:
            following = self.portfolio_sharing.following.get(user_id, [])
            activities = [
                a for a in self.activities
                if a.user_id in following and a.is_public
            ]
        else:
            activities = [a for a in self.activities if a.is_public]
        
        return activities[offset:offset + limit]
    
    def get_api_routes(self):
        """Get FastAPI routes for social trading endpoints"""
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
        
        router = APIRouter(prefix="/social", tags=["Social Trading"])
        
        class SharePortfolioRequest(BaseModel):
            name: str
            description: str
            privacy_level: str
            settings: Dict[str, Any]
        
        class StrategyRequest(BaseModel):
            name: str
            description: str
            strategy_type: str
            pricing: Dict[str, float]
            config: Dict[str, Any]
            performance: Dict[str, float]
        
        class CopyTradingRequest(BaseModel):
            leader_id: str
            mode: str
            settings: Dict[str, Any]
        
        @router.post("/portfolio/share")
        async def share_portfolio(request: SharePortfolioRequest, user_id: str = "demo_user"):
            portfolio = await self.portfolio_sharing.create_shared_portfolio(
                owner_id=user_id,
                name=request.name,
                description=request.description,
                privacy_level=PrivacyLevel(request.privacy_level),
                settings=request.settings
            )
            return {"portfolio_id": portfolio.portfolio_id, "status": "shared"}
        
        @router.get("/portfolio/{portfolio_id}")
        async def view_portfolio(portfolio_id: str, viewer_id: str = "demo_user"):
            view = await self.portfolio_sharing.get_portfolio_view(portfolio_id, viewer_id)
            if not view:
                raise HTTPException(status_code=404, detail="Portfolio not found or access denied")
            return view
        
        @router.post("/strategy/publish")
        async def publish_strategy(request: StrategyRequest, user_id: str = "demo_user"):
            strategy = await self.marketplace.publish_strategy(
                creator_id=user_id,
                name=request.name,
                description=request.description,
                strategy_type=request.strategy_type,
                pricing=request.pricing,
                config=request.config,
                performance=request.performance
            )
            return {"strategy_id": strategy.strategy_id, "status": strategy.status.value}
        
        @router.get("/strategies")
        async def search_strategies(
            strategy_type: str = None,
            min_sharpe: float = None,
            max_drawdown: float = None,
            limit: int = 20
        ):
            filters = {}
            if strategy_type:
                filters["strategy_type"] = strategy_type
            if min_sharpe:
                filters["min_sharpe"] = min_sharpe
            if max_drawdown:
                filters["max_drawdown"] = max_drawdown
            
            strategies = await self.marketplace.search_strategies(filters, limit=limit)
            return {"strategies": [s.__dict__ for s in strategies]}
        
        @router.get("/leaderboard/{leaderboard_type}")
        async def get_leaderboard(leaderboard_type: str, period: str = "monthly"):
            entries = await self.leaderboard.update_leaderboard(
                LeaderboardType(leaderboard_type),
                period
            )
            return {"entries": [e.__dict__ for e in entries[:50]]}
        
        @router.post("/copy-trading/start")
        async def start_copy_trading(request: CopyTradingRequest, user_id: str = "demo_user"):
            subscription = await self.copy_trading.start_copy_trading(
                copier_id=user_id,
                leader_id=request.leader_id,
                mode=CopyTradingMode(request.mode),
                settings=request.settings
            )
            return {"subscription_id": subscription.subscription_id, "status": "active"}
        
        @router.post("/follow/{target_id}")
        async def follow_user(target_id: str, user_id: str = "demo_user"):
            success = await self.portfolio_sharing.follow_user(user_id, target_id)
            return {"success": success}
        
        @router.delete("/follow/{target_id}")
        async def unfollow_user(target_id: str, user_id: str = "demo_user"):
            success = await self.portfolio_sharing.unfollow_user(user_id, target_id)
            return {"success": success}
        
        @router.get("/feed")
        async def get_feed(following_only: bool = False, limit: int = 50, user_id: str = "demo_user"):
            activities = await self.get_activity_feed(user_id, following_only, limit)
            return {"activities": [a.__dict__ for a in activities]}
        
        return router


# Export main components
__all__ = [
    'SocialTradingPlatform',
    'PortfolioSharingService',
    'StrategyMarketplace',
    'LeaderboardService',
    'ExpertNetworkService',
    'CopyTradingService',
    'PrivacyLevel',
    'StrategyStatus',
    'LeaderboardType',
    'ExpertTier',
    'CopyTradingMode'
]
