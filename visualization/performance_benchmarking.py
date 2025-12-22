"""
Performance Benchmarking Engine
==============================

Real-time performance benchmarking against:
- Market indices (S&P 500, NASDAQ, etc.)
- Peer portfolios and strategies
- Custom benchmarks
- Risk-adjusted metrics comparison
- Attribution analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from scipy import stats


class BenchmarkType(Enum):
    """Types of benchmarks supported"""
    INDEX = "index"
    PEER_PORTFOLIO = "peer_portfolio"
    CUSTOM = "custom"
    RISK_FREE = "risk_free"
    BLENDED = "blended"


class TimeHorizon(Enum):
    """Standard time horizons for performance measurement"""
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    ONE_MONTH = "1M"
    THREE_MONTHS = "3M"
    SIX_MONTHS = "6M"
    ONE_YEAR = "1Y"
    THREE_YEARS = "3Y"
    FIVE_YEARS = "5Y"
    SINCE_INCEPTION = "SI"


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    beta: float
    alpha: float
    treynor_ratio: float
    information_ratio: float
    tracking_error: float
    up_capture: float
    down_capture: float
    hit_ratio: float
    avg_win: float
    avg_loss: float
    win_loss_ratio: float
    var_95: float
    cvar_95: float
    skewness: float
    kurtosis: float


@dataclass
class BenchmarkComparison:
    """Comparison between portfolio and benchmark"""
    portfolio_id: str
    benchmark_id: str
    benchmark_name: str
    benchmark_type: BenchmarkType
    time_horizon: TimeHorizon
    as_of_date: datetime
    
    # Performance comparison
    portfolio_metrics: PerformanceMetrics
    benchmark_metrics: PerformanceMetrics
    
    # Relative metrics
    excess_return: float
    relative_sharpe: float
    active_return: float
    
    # Percentile rankings
    return_percentile: float
    risk_percentile: float
    sharpe_percentile: float
    
    # Attribution
    sector_attribution: Dict[str, float] = field(default_factory=dict)
    factor_attribution: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'portfolio_id': self.portfolio_id,
            'benchmark_id': self.benchmark_id,
            'benchmark_name': self.benchmark_name,
            'time_horizon': self.time_horizon.value,
            'as_of_date': self.as_of_date.isoformat(),
            'portfolio': {
                'return': self.portfolio_metrics.total_return,
                'sharpe': self.portfolio_metrics.sharpe_ratio,
                'volatility': self.portfolio_metrics.volatility,
                'max_drawdown': self.portfolio_metrics.max_drawdown,
                'alpha': self.portfolio_metrics.alpha,
                'beta': self.portfolio_metrics.beta
            },
            'benchmark': {
                'return': self.benchmark_metrics.total_return,
                'sharpe': self.benchmark_metrics.sharpe_ratio,
                'volatility': self.benchmark_metrics.volatility,
                'max_drawdown': self.benchmark_metrics.max_drawdown
            },
            'relative': {
                'excess_return': self.excess_return,
                'information_ratio': self.portfolio_metrics.information_ratio,
                'tracking_error': self.portfolio_metrics.tracking_error
            },
            'rankings': {
                'return_percentile': self.return_percentile,
                'risk_percentile': self.risk_percentile,
                'sharpe_percentile': self.sharpe_percentile
            },
            'attribution': {
                'sector': self.sector_attribution,
                'factor': self.factor_attribution
            }
        }


@dataclass
class PeerGroup:
    """Peer group for comparison"""
    group_id: str
    name: str
    description: str
    portfolios: List[str]
    category: str
    aum_range: Tuple[float, float]
    style: str  # growth, value, blend
    
    # Aggregate statistics
    median_return: float = 0.0
    median_sharpe: float = 0.0
    median_volatility: float = 0.0
    top_quartile_return: float = 0.0
    bottom_quartile_return: float = 0.0


class PerformanceBenchmark:
    """
    Calculates comprehensive performance metrics and benchmarking.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger("performance_benchmark")
        
        # Standard benchmarks
        self.standard_benchmarks = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ 100',
            'IWM': 'Russell 2000',
            'EFA': 'MSCI EAFE',
            'EEM': 'MSCI Emerging Markets',
            'AGG': 'US Aggregate Bond',
            'TLT': '20+ Year Treasury',
            'GLD': 'Gold',
            'DBC': 'Commodities',
            'VT': 'Total World Stock'
        }
    
    def calculate_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None
    ) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            returns: Portfolio returns series
            benchmark_returns: Optional benchmark returns for relative metrics
        """
        # Clean data
        returns = returns.dropna()
        n_periods = len(returns)
        
        if n_periods < 2:
            return self._empty_metrics()
        
        # Basic metrics
        total_return = (1 + returns).prod() - 1
        ann_factor = 252  # Assuming daily returns
        annualized_return = (1 + total_return) ** (ann_factor / n_periods) - 1
        volatility = returns.std() * np.sqrt(ann_factor)
        
        # Risk-adjusted returns
        excess_returns = returns - self.risk_free_rate / ann_factor
        sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility if volatility > 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(ann_factor) if len(downside_returns) > 0 else 0.001
        sortino_ratio = (annualized_return - self.risk_free_rate) / downside_std if downside_std > 0 else 0
        
        # Drawdown analysis
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdowns = cumulative / rolling_max - 1
        max_drawdown = drawdowns.min()
        
        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Benchmark-relative metrics
        beta = 0
        alpha = 0
        treynor_ratio = 0
        information_ratio = 0
        tracking_error = 0
        up_capture = 0
        down_capture = 0
        
        if benchmark_returns is not None:
            benchmark_returns = benchmark_returns.dropna()
            # Align dates
            common_dates = returns.index.intersection(benchmark_returns.index)
            if len(common_dates) > 10:
                port_aligned = returns.loc[common_dates]
                bench_aligned = benchmark_returns.loc[common_dates]
                
                # Beta and Alpha
                covariance = np.cov(port_aligned, bench_aligned)[0, 1]
                bench_var = bench_aligned.var()
                beta = covariance / bench_var if bench_var > 0 else 0
                
                bench_ann_return = (1 + bench_aligned).prod() ** (ann_factor / len(bench_aligned)) - 1
                alpha = annualized_return - (self.risk_free_rate + beta * (bench_ann_return - self.risk_free_rate))
                
                # Treynor ratio
                treynor_ratio = (annualized_return - self.risk_free_rate) / beta if beta > 0 else 0
                
                # Tracking error and Information ratio
                active_returns = port_aligned - bench_aligned
                tracking_error = active_returns.std() * np.sqrt(ann_factor)
                active_return_ann = active_returns.mean() * ann_factor
                information_ratio = active_return_ann / tracking_error if tracking_error > 0 else 0
                
                # Capture ratios
                up_periods = bench_aligned > 0
                down_periods = bench_aligned < 0
                
                if up_periods.sum() > 0:
                    up_capture = (port_aligned[up_periods].mean() / bench_aligned[up_periods].mean()) * 100
                if down_periods.sum() > 0:
                    down_capture = (port_aligned[down_periods].mean() / bench_aligned[down_periods].mean()) * 100
        
        # Win/Loss statistics
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        hit_ratio = len(positive_returns) / n_periods if n_periods > 0 else 0
        avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0
        avg_loss = abs(negative_returns.mean()) if len(negative_returns) > 0 else 0.001
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Risk metrics
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else var_95
        
        # Distribution metrics
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            beta=beta,
            alpha=alpha,
            treynor_ratio=treynor_ratio,
            information_ratio=information_ratio,
            tracking_error=tracking_error,
            up_capture=up_capture,
            down_capture=down_capture,
            hit_ratio=hit_ratio,
            avg_win=avg_win,
            avg_loss=avg_loss,
            win_loss_ratio=win_loss_ratio,
            var_95=var_95,
            cvar_95=cvar_95,
            skewness=skewness,
            kurtosis=kurtosis
        )
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics object"""
        return PerformanceMetrics(
            total_return=0, annualized_return=0, volatility=0,
            sharpe_ratio=0, sortino_ratio=0, max_drawdown=0,
            calmar_ratio=0, beta=0, alpha=0, treynor_ratio=0,
            information_ratio=0, tracking_error=0, up_capture=0,
            down_capture=0, hit_ratio=0, avg_win=0, avg_loss=0,
            win_loss_ratio=0, var_95=0, cvar_95=0, skewness=0, kurtosis=0
        )
    
    def compare_to_benchmark(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
        portfolio_id: str,
        benchmark_id: str,
        benchmark_name: str,
        time_horizon: TimeHorizon = TimeHorizon.ONE_YEAR
    ) -> BenchmarkComparison:
        """
        Compare portfolio to a specific benchmark.
        """
        portfolio_metrics = self.calculate_metrics(portfolio_returns, benchmark_returns)
        benchmark_metrics = self.calculate_metrics(benchmark_returns)
        
        excess_return = portfolio_metrics.total_return - benchmark_metrics.total_return
        relative_sharpe = portfolio_metrics.sharpe_ratio - benchmark_metrics.sharpe_ratio
        
        active_returns = portfolio_returns - benchmark_returns
        active_return = active_returns.mean() * 252
        
        return BenchmarkComparison(
            portfolio_id=portfolio_id,
            benchmark_id=benchmark_id,
            benchmark_name=benchmark_name,
            benchmark_type=BenchmarkType.INDEX,
            time_horizon=time_horizon,
            as_of_date=datetime.now(),
            portfolio_metrics=portfolio_metrics,
            benchmark_metrics=benchmark_metrics,
            excess_return=excess_return,
            relative_sharpe=relative_sharpe,
            active_return=active_return,
            return_percentile=0,  # Calculated in peer comparison
            risk_percentile=0,
            sharpe_percentile=0
        )
    
    def multi_benchmark_comparison(
        self,
        portfolio_returns: pd.Series,
        benchmark_data: Dict[str, pd.Series],
        portfolio_id: str
    ) -> List[BenchmarkComparison]:
        """
        Compare portfolio to multiple benchmarks simultaneously.
        """
        comparisons = []
        
        for benchmark_id, benchmark_returns in benchmark_data.items():
            benchmark_name = self.standard_benchmarks.get(benchmark_id, benchmark_id)
            comparison = self.compare_to_benchmark(
                portfolio_returns,
                benchmark_returns,
                portfolio_id,
                benchmark_id,
                benchmark_name
            )
            comparisons.append(comparison)
        
        return comparisons
    
    def rolling_performance(
        self,
        returns: pd.Series,
        window: int = 252
    ) -> pd.DataFrame:
        """
        Calculate rolling performance metrics.
        """
        ann_factor = 252
        
        rolling_return = returns.rolling(window=window).apply(
            lambda x: (1 + x).prod() ** (ann_factor / len(x)) - 1
        )
        
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(ann_factor)
        
        rolling_sharpe = (rolling_return - self.risk_free_rate) / rolling_vol
        
        # Rolling max drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.rolling(window=window).max()
        drawdowns = cumulative / rolling_max - 1
        rolling_max_dd = drawdowns.rolling(window=window).min()
        
        return pd.DataFrame({
            'rolling_return': rolling_return,
            'rolling_volatility': rolling_vol,
            'rolling_sharpe': rolling_sharpe,
            'rolling_max_drawdown': rolling_max_dd
        })


class PeerComparisonEngine:
    """
    Engine for comparing portfolio performance against peer groups.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("peer_comparison")
        self.benchmark = PerformanceBenchmark()
        self.peer_groups: Dict[str, PeerGroup] = {}
        self.peer_performance: Dict[str, Dict[str, PerformanceMetrics]] = {}
    
    def create_peer_group(
        self,
        group_id: str,
        name: str,
        portfolios: List[str],
        category: str,
        style: str = "blend"
    ) -> PeerGroup:
        """Create a new peer group"""
        peer_group = PeerGroup(
            group_id=group_id,
            name=name,
            description=f"{category} - {style} portfolios",
            portfolios=portfolios,
            category=category,
            aum_range=(0, float('inf')),
            style=style
        )
        
        self.peer_groups[group_id] = peer_group
        return peer_group
    
    def update_peer_performance(
        self,
        group_id: str,
        portfolio_returns: Dict[str, pd.Series]
    ):
        """
        Update performance metrics for all portfolios in a peer group.
        """
        if group_id not in self.peer_groups:
            return
        
        group = self.peer_groups[group_id]
        self.peer_performance[group_id] = {}
        
        returns_list = []
        sharpe_list = []
        vol_list = []
        
        for portfolio_id in group.portfolios:
            if portfolio_id in portfolio_returns:
                returns = portfolio_returns[portfolio_id]
                metrics = self.benchmark.calculate_metrics(returns)
                self.peer_performance[group_id][portfolio_id] = metrics
                
                returns_list.append(metrics.annualized_return)
                sharpe_list.append(metrics.sharpe_ratio)
                vol_list.append(metrics.volatility)
        
        if returns_list:
            group.median_return = np.median(returns_list)
            group.median_sharpe = np.median(sharpe_list)
            group.median_volatility = np.median(vol_list)
            group.top_quartile_return = np.percentile(returns_list, 75)
            group.bottom_quartile_return = np.percentile(returns_list, 25)
    
    def get_percentile_rankings(
        self,
        portfolio_id: str,
        group_id: str,
        portfolio_returns: pd.Series
    ) -> Dict[str, float]:
        """
        Get percentile rankings for a portfolio within its peer group.
        """
        if group_id not in self.peer_performance:
            return {'return': 50, 'sharpe': 50, 'risk': 50}
        
        portfolio_metrics = self.benchmark.calculate_metrics(portfolio_returns)
        
        returns = [m.annualized_return for m in self.peer_performance[group_id].values()]
        sharpes = [m.sharpe_ratio for m in self.peer_performance[group_id].values()]
        vols = [m.volatility for m in self.peer_performance[group_id].values()]
        
        return_percentile = stats.percentileofscore(returns, portfolio_metrics.annualized_return)
        sharpe_percentile = stats.percentileofscore(sharpes, portfolio_metrics.sharpe_ratio)
        risk_percentile = 100 - stats.percentileofscore(vols, portfolio_metrics.volatility)  # Lower vol = better
        
        return {
            'return': return_percentile,
            'sharpe': sharpe_percentile,
            'risk': risk_percentile
        }
    
    def generate_peer_comparison_report(
        self,
        portfolio_id: str,
        portfolio_returns: pd.Series,
        group_id: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive peer comparison report.
        """
        if group_id not in self.peer_groups:
            return {'error': 'Peer group not found'}
        
        group = self.peer_groups[group_id]
        rankings = self.get_percentile_rankings(portfolio_id, group_id, portfolio_returns)
        metrics = self.benchmark.calculate_metrics(portfolio_returns)
        
        # Determine quartile
        if rankings['return'] >= 75:
            quartile = "Top Quartile"
        elif rankings['return'] >= 50:
            quartile = "Second Quartile"
        elif rankings['return'] >= 25:
            quartile = "Third Quartile"
        else:
            quartile = "Bottom Quartile"
        
        return {
            'portfolio_id': portfolio_id,
            'peer_group': {
                'id': group_id,
                'name': group.name,
                'size': len(group.portfolios),
                'category': group.category
            },
            'performance': {
                'annualized_return': metrics.annualized_return,
                'sharpe_ratio': metrics.sharpe_ratio,
                'volatility': metrics.volatility,
                'max_drawdown': metrics.max_drawdown
            },
            'rankings': rankings,
            'quartile': quartile,
            'vs_median': {
                'return_diff': metrics.annualized_return - group.median_return,
                'sharpe_diff': metrics.sharpe_ratio - group.median_sharpe,
                'vol_diff': metrics.volatility - group.median_volatility
            },
            'insights': self._generate_ranking_insights(rankings, metrics, group)
        }
    
    def _generate_ranking_insights(
        self,
        rankings: Dict[str, float],
        metrics: PerformanceMetrics,
        group: PeerGroup
    ) -> List[str]:
        """Generate textual insights based on rankings"""
        insights = []
        
        if rankings['return'] >= 90:
            insights.append(f"Outstanding performance - top 10% of {group.name}")
        elif rankings['return'] >= 75:
            insights.append(f"Strong performance - outperforming 75% of peers")
        elif rankings['return'] < 25:
            insights.append(f"Performance lagging - in bottom quartile of peers")
        
        if rankings['sharpe'] >= 80:
            insights.append("Excellent risk-adjusted returns relative to peers")
        elif rankings['sharpe'] < 30:
            insights.append("Risk-adjusted returns below most peers - review strategy")
        
        if rankings['risk'] >= 80:
            insights.append("Lower volatility than most peers - conservative positioning")
        elif rankings['risk'] < 20:
            insights.append("Higher volatility than peers - consider risk reduction")
        
        if metrics.max_drawdown < -0.20:
            insights.append(f"Significant drawdown ({metrics.max_drawdown:.1%}) - review risk management")
        
        return insights
    
    def get_performance_distribution(
        self,
        group_id: str,
        metric: str = 'return'
    ) -> Dict[str, Any]:
        """
        Get distribution of a metric across the peer group.
        """
        if group_id not in self.peer_performance:
            return {}
        
        values = []
        for portfolio_id, metrics in self.peer_performance[group_id].items():
            if metric == 'return':
                values.append((portfolio_id, metrics.annualized_return))
            elif metric == 'sharpe':
                values.append((portfolio_id, metrics.sharpe_ratio))
            elif metric == 'volatility':
                values.append((portfolio_id, metrics.volatility))
            elif metric == 'drawdown':
                values.append((portfolio_id, metrics.max_drawdown))
        
        values.sort(key=lambda x: x[1], reverse=True)
        metric_values = [v[1] for v in values]
        
        return {
            'ranking': values,
            'statistics': {
                'mean': np.mean(metric_values),
                'median': np.median(metric_values),
                'std': np.std(metric_values),
                'min': np.min(metric_values),
                'max': np.max(metric_values),
                'p25': np.percentile(metric_values, 25),
                'p75': np.percentile(metric_values, 75)
            },
            'histogram': np.histogram(metric_values, bins=10)
        }
    
    def generate_leaderboard(
        self,
        group_id: str,
        metric: str = 'sharpe',
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate leaderboard for a peer group.
        """
        distribution = self.get_performance_distribution(group_id, metric)
        
        if not distribution:
            return []
        
        leaderboard = []
        for rank, (portfolio_id, value) in enumerate(distribution['ranking'][:top_n], 1):
            metrics = self.peer_performance[group_id][portfolio_id]
            leaderboard.append({
                'rank': rank,
                'portfolio_id': portfolio_id,
                metric: value,
                'return': metrics.annualized_return,
                'sharpe': metrics.sharpe_ratio,
                'volatility': metrics.volatility,
                'max_drawdown': metrics.max_drawdown
            })
        
        return leaderboard


class AttributionAnalyzer:
    """
    Performance attribution analysis - sector and factor attribution.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("attribution_analyzer")
    
    def sector_attribution(
        self,
        portfolio_weights: Dict[str, float],
        portfolio_returns: Dict[str, float],
        benchmark_weights: Dict[str, float],
        benchmark_returns: Dict[str, float],
        asset_sectors: Dict[str, str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Brinson-style sector attribution analysis.
        
        Decomposes excess return into:
        - Allocation effect: Over/underweight decisions
        - Selection effect: Stock picking within sectors
        - Interaction effect: Combined effect
        """
        sectors = set(asset_sectors.values())
        attribution = {}
        
        for sector in sectors:
            # Get sector weights and returns
            port_sector_weight = sum(
                w for a, w in portfolio_weights.items() 
                if asset_sectors.get(a) == sector
            )
            bench_sector_weight = sum(
                w for a, w in benchmark_weights.items() 
                if asset_sectors.get(a) == sector
            )
            
            # Weighted returns within sector
            port_sector_assets = [a for a in portfolio_weights if asset_sectors.get(a) == sector]
            bench_sector_assets = [a for a in benchmark_weights if asset_sectors.get(a) == sector]
            
            if port_sector_weight > 0:
                port_sector_return = sum(
                    portfolio_returns.get(a, 0) * portfolio_weights.get(a, 0)
                    for a in port_sector_assets
                ) / port_sector_weight
            else:
                port_sector_return = 0
            
            if bench_sector_weight > 0:
                bench_sector_return = sum(
                    benchmark_returns.get(a, 0) * benchmark_weights.get(a, 0)
                    for a in bench_sector_assets
                ) / bench_sector_weight
            else:
                bench_sector_return = 0
            
            # Total benchmark return
            total_bench_return = sum(
                benchmark_returns.get(a, 0) * benchmark_weights.get(a, 0)
                for a in benchmark_weights
            )
            
            # Attribution effects
            allocation_effect = (port_sector_weight - bench_sector_weight) * (bench_sector_return - total_bench_return)
            selection_effect = bench_sector_weight * (port_sector_return - bench_sector_return)
            interaction_effect = (port_sector_weight - bench_sector_weight) * (port_sector_return - bench_sector_return)
            
            attribution[sector] = {
                'allocation': allocation_effect,
                'selection': selection_effect,
                'interaction': interaction_effect,
                'total': allocation_effect + selection_effect + interaction_effect,
                'portfolio_weight': port_sector_weight,
                'benchmark_weight': bench_sector_weight,
                'active_weight': port_sector_weight - bench_sector_weight,
                'portfolio_return': port_sector_return,
                'benchmark_return': bench_sector_return
            }
        
        return attribution
    
    def factor_attribution(
        self,
        portfolio_returns: pd.Series,
        factor_returns: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Factor attribution using regression.
        
        Args:
            portfolio_returns: Portfolio return series
            factor_returns: DataFrame with factor returns (e.g., size, value, momentum)
        """
        # Align data
        common_index = portfolio_returns.index.intersection(factor_returns.index)
        y = portfolio_returns.loc[common_index]
        X = factor_returns.loc[common_index]
        
        # Add constant for alpha
        X = X.copy()
        X['const'] = 1
        
        # OLS regression
        coeffs = np.linalg.lstsq(X.values, y.values, rcond=None)[0]
        
        # Factor exposures and attribution
        factor_names = list(factor_returns.columns) + ['alpha']
        exposures = dict(zip(factor_names, coeffs))
        
        # Attribution: exposure * average factor return
        attribution = {}
        for factor in factor_returns.columns:
            attribution[factor] = exposures[factor] * factor_returns[factor].mean() * 252
        
        attribution['alpha'] = exposures['alpha'] * 252  # Annualize
        attribution['residual'] = (y - X @ coeffs).std() * np.sqrt(252)  # Tracking error from factors
        
        return attribution
