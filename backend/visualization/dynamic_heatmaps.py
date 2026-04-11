"""
Dynamic Heatmaps Engine
======================

Advanced correlation and exposure analysis with:
- Real-time correlation heatmaps with animation
- Sector/asset class exposure analysis
- Time-varying correlation matrices
- Regime-dependent correlation changes
- Interactive drill-down capabilities
- Rolling window analysis
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
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster


class HeatmapType(Enum):
    """Types of heatmaps supported"""
    CORRELATION = "correlation"
    COVARIANCE = "covariance"
    EXPOSURE = "exposure"
    RISK_CONTRIBUTION = "risk_contribution"
    DRAWDOWN = "drawdown"
    ROLLING_BETA = "rolling_beta"
    SECTOR_ROTATION = "sector_rotation"
    REGIME_CORRELATION = "regime_correlation"


class TimeFrame(Enum):
    """Time frames for analysis"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class HeatmapCell:
    """Individual cell in a heatmap"""
    row_label: str
    col_label: str
    value: float
    normalized_value: float  # 0-1 for color mapping
    color: Tuple[float, float, float]
    significance: float  # p-value for statistical significance
    tooltip: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HeatmapData:
    """Complete heatmap data structure"""
    heatmap_id: str
    title: str
    heatmap_type: HeatmapType
    created_at: datetime
    
    # Matrix data
    row_labels: List[str]
    col_labels: List[str]
    values: np.ndarray
    cells: List[HeatmapCell] = field(default_factory=list)
    
    # Metadata
    time_period: str = ""
    data_points: int = 0
    
    # Clustering (optional)
    row_dendogram: Optional[Dict] = None
    col_dendogram: Optional[Dict] = None
    clusters: Optional[Dict[int, List[str]]] = None
    
    # Animation frames for time-varying heatmaps
    animation_frames: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'heatmap_id': self.heatmap_id,
            'title': self.title,
            'type': self.heatmap_type.value,
            'created_at': self.created_at.isoformat(),
            'row_labels': self.row_labels,
            'col_labels': self.col_labels,
            'values': self.values.tolist(),
            'cells': [
                {
                    'row': c.row_label,
                    'col': c.col_label,
                    'value': c.value,
                    'color': c.color,
                    'tooltip': c.tooltip
                }
                for c in self.cells
            ],
            'time_period': self.time_period,
            'data_points': self.data_points,
            'clusters': self.clusters
        }


class CorrelationAnalyzer:
    """Advanced correlation analysis with statistical testing"""
    
    def __init__(self):
        self.logger = logging.getLogger("correlation_analyzer")
    
    def pearson_correlation(
        self,
        returns: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calculate Pearson correlation with p-values.
        
        Returns:
            Tuple of (correlation_matrix, p_value_matrix)
        """
        n = len(returns.columns)
        corr_matrix = returns.corr()
        p_matrix = pd.DataFrame(
            np.zeros((n, n)),
            index=returns.columns,
            columns=returns.columns
        )
        
        for i, col1 in enumerate(returns.columns):
            for j, col2 in enumerate(returns.columns):
                if i != j:
                    valid_data = returns[[col1, col2]].dropna()
                    if len(valid_data) > 2:
                        _, p_value = stats.pearsonr(valid_data[col1], valid_data[col2])
                        p_matrix.loc[col1, col2] = p_value
        
        return corr_matrix, p_matrix
    
    def spearman_correlation(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Calculate Spearman rank correlation"""
        return returns.corr(method='spearman')
    
    def kendall_correlation(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Calculate Kendall tau correlation"""
        return returns.corr(method='kendall')
    
    def rolling_correlation(
        self,
        returns: pd.DataFrame,
        window: int = 60,
        pair: Optional[Tuple[str, str]] = None
    ) -> pd.DataFrame:
        """
        Calculate rolling correlation over time.
        
        Args:
            returns: Asset returns DataFrame
            window: Rolling window size
            pair: Optional specific pair to calculate
            
        Returns:
            Rolling correlation DataFrame
        """
        if pair:
            return returns[list(pair)].rolling(window=window).corr().unstack()[pair[0]][pair[1]]
        else:
            # Calculate pairwise rolling correlations
            result = {}
            columns = returns.columns
            for i, col1 in enumerate(columns):
                for col2 in columns[i+1:]:
                    rolling_corr = returns[[col1, col2]].rolling(window=window).corr()
                    result[f"{col1}_{col2}"] = rolling_corr.unstack()[col1][col2]
            return pd.DataFrame(result)
    
    def conditional_correlation(
        self,
        returns: pd.DataFrame,
        condition_asset: str,
        threshold_percentile: float = 10
    ) -> Dict[str, pd.DataFrame]:
        """
        Calculate correlation conditional on market conditions.
        
        Returns correlations during:
        - Normal periods
        - Market stress (bottom percentile)
        - Market euphoria (top percentile)
        """
        condition_returns = returns[condition_asset]
        
        bottom_threshold = np.percentile(condition_returns, threshold_percentile)
        top_threshold = np.percentile(condition_returns, 100 - threshold_percentile)
        
        stress_mask = condition_returns <= bottom_threshold
        euphoria_mask = condition_returns >= top_threshold
        normal_mask = ~stress_mask & ~euphoria_mask
        
        return {
            'normal': returns[normal_mask].corr(),
            'stress': returns[stress_mask].corr(),
            'euphoria': returns[euphoria_mask].corr()
        }
    
    def regime_correlation(
        self,
        returns: pd.DataFrame,
        regimes: pd.Series
    ) -> Dict[str, pd.DataFrame]:
        """Calculate correlation for each market regime"""
        regime_corrs = {}
        
        for regime in regimes.unique():
            regime_mask = regimes == regime
            regime_returns = returns[regime_mask]
            if len(regime_returns) > 10:
                regime_corrs[regime] = regime_returns.corr()
        
        return regime_corrs
    
    def dynamic_conditional_correlation(
        self,
        returns: pd.DataFrame,
        decay_factor: float = 0.94
    ) -> Dict[str, pd.DataFrame]:
        """
        Calculate Dynamic Conditional Correlation (DCC) model.
        Uses exponentially weighted approach for simplicity.
        """
        n_assets = len(returns.columns)
        n_periods = len(returns)
        
        # Initialize
        ewma_cov = returns.cov()
        dcc_series = []
        
        for t in range(1, n_periods):
            # Update covariance with decay
            returns_t = returns.iloc[t].values.reshape(-1, 1)
            outer_product = np.outer(returns_t, returns_t)
            ewma_cov = decay_factor * ewma_cov + (1 - decay_factor) * outer_product
            
            # Convert to correlation
            std = np.sqrt(np.diag(ewma_cov))
            corr = ewma_cov / np.outer(std, std)
            
            dcc_series.append({
                'date': returns.index[t],
                'correlation': pd.DataFrame(corr, index=returns.columns, columns=returns.columns)
            })
        
        return {
            'series': dcc_series,
            'latest': dcc_series[-1]['correlation'] if dcc_series else returns.corr()
        }


class DynamicHeatmapEngine:
    """
    Main engine for generating dynamic, interactive heatmaps.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("heatmap_engine")
        self.correlation_analyzer = CorrelationAnalyzer()
        
        # Color palettes
        self.diverging_palette = {
            'negative': (0.8, 0.2, 0.2),  # Red
            'neutral': (0.95, 0.95, 0.95),  # White
            'positive': (0.2, 0.6, 0.8)  # Blue
        }
        
        self.sequential_palette = {
            'low': (0.98, 0.98, 0.82),  # Light yellow
            'high': (0.8, 0.1, 0.1)  # Dark red
        }
    
    def value_to_color(
        self,
        value: float,
        min_val: float,
        max_val: float,
        palette: str = 'diverging'
    ) -> Tuple[float, float, float]:
        """Map a value to a color based on palette"""
        if palette == 'diverging':
            # For correlations: -1 to 1
            if value >= 0:
                t = value / max(max_val, 0.001)
                return self._lerp_color(
                    self.diverging_palette['neutral'],
                    self.diverging_palette['positive'],
                    t
                )
            else:
                t = abs(value) / max(abs(min_val), 0.001)
                return self._lerp_color(
                    self.diverging_palette['neutral'],
                    self.diverging_palette['negative'],
                    t
                )
        else:
            # Sequential
            t = (value - min_val) / max(max_val - min_val, 0.001)
            return self._lerp_color(
                self.sequential_palette['low'],
                self.sequential_palette['high'],
                t
            )
    
    def _lerp_color(
        self,
        c1: Tuple[float, float, float],
        c2: Tuple[float, float, float],
        t: float
    ) -> Tuple[float, float, float]:
        """Linear interpolation between colors"""
        t = max(0, min(1, t))
        return (
            c1[0] + (c2[0] - c1[0]) * t,
            c1[1] + (c2[1] - c1[1]) * t,
            c1[2] + (c2[2] - c1[2]) * t
        )
    
    def generate_correlation_heatmap(
        self,
        returns: pd.DataFrame,
        method: str = 'pearson',
        cluster: bool = True
    ) -> HeatmapData:
        """
        Generate correlation heatmap with optional hierarchical clustering.
        
        Args:
            returns: DataFrame of asset returns
            method: Correlation method ('pearson', 'spearman', 'kendall')
            cluster: Whether to apply hierarchical clustering
            
        Returns:
            HeatmapData object
        """
        import uuid
        
        # Calculate correlation
        if method == 'pearson':
            corr_matrix, p_values = self.correlation_analyzer.pearson_correlation(returns)
        elif method == 'spearman':
            corr_matrix = self.correlation_analyzer.spearman_correlation(returns)
            p_values = pd.DataFrame(0, index=returns.columns, columns=returns.columns)
        else:
            corr_matrix = self.correlation_analyzer.kendall_correlation(returns)
            p_values = pd.DataFrame(0, index=returns.columns, columns=returns.columns)
        
        row_labels = list(corr_matrix.index)
        col_labels = list(corr_matrix.columns)
        
        # Apply clustering if requested
        row_dendogram = None
        clusters = None
        
        if cluster and len(row_labels) > 2:
            # Hierarchical clustering
            linkage_matrix = linkage(corr_matrix, method='ward')
            cluster_labels = fcluster(linkage_matrix, t=3, criterion='maxclust')
            
            # Reorder by cluster
            order = np.argsort(cluster_labels)
            corr_matrix = corr_matrix.iloc[order, order]
            row_labels = [row_labels[i] for i in order]
            col_labels = [col_labels[i] for i in order]
            
            clusters = {}
            for i, label in enumerate(cluster_labels[order]):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(row_labels[i])
        
        # Generate cells
        cells = []
        min_val = corr_matrix.values.min()
        max_val = corr_matrix.values.max()
        
        for i, row in enumerate(row_labels):
            for j, col in enumerate(col_labels):
                value = corr_matrix.loc[row, col]
                p_value = p_values.loc[row, col] if row in p_values.index and col in p_values.columns else 0
                
                color = self.value_to_color(value, min_val, max_val, 'diverging')
                normalized = (value + 1) / 2  # Normalize to 0-1
                
                tooltip = f"{row} vs {col}: {value:.3f}"
                if p_value > 0:
                    tooltip += f" (p={p_value:.4f})"
                
                cell = HeatmapCell(
                    row_label=row,
                    col_label=col,
                    value=value,
                    normalized_value=normalized,
                    color=color,
                    significance=p_value,
                    tooltip=tooltip
                )
                cells.append(cell)
        
        return HeatmapData(
            heatmap_id=str(uuid.uuid4()),
            title=f"{method.capitalize()} Correlation Matrix",
            heatmap_type=HeatmapType.CORRELATION,
            created_at=datetime.now(),
            row_labels=row_labels,
            col_labels=col_labels,
            values=corr_matrix.values,
            cells=cells,
            time_period=f"{returns.index[0].strftime('%Y-%m-%d')} to {returns.index[-1].strftime('%Y-%m-%d')}",
            data_points=len(returns),
            clusters=clusters
        )
    
    def generate_exposure_heatmap(
        self,
        portfolio_weights: Dict[str, float],
        asset_exposures: pd.DataFrame
    ) -> HeatmapData:
        """
        Generate exposure analysis heatmap.
        
        Args:
            portfolio_weights: Dict of {asset: weight}
            asset_exposures: DataFrame with columns as exposure factors
                            (sector, region, style, etc.)
        """
        import uuid
        
        # Calculate weighted exposures
        factors = asset_exposures.columns.tolist()
        assets = list(portfolio_weights.keys())
        
        exposure_matrix = pd.DataFrame(
            index=assets,
            columns=factors,
            dtype=float
        )
        
        for asset in assets:
            if asset in asset_exposures.index:
                for factor in factors:
                    exposure_matrix.loc[asset, factor] = (
                        asset_exposures.loc[asset, factor] * portfolio_weights[asset]
                    )
        
        # Generate cells
        cells = []
        min_val = exposure_matrix.values.min()
        max_val = exposure_matrix.values.max()
        
        for asset in assets:
            for factor in factors:
                value = exposure_matrix.loc[asset, factor]
                color = self.value_to_color(value, min_val, max_val, 'sequential')
                
                cell = HeatmapCell(
                    row_label=asset,
                    col_label=factor,
                    value=value,
                    normalized_value=(value - min_val) / (max_val - min_val) if max_val > min_val else 0,
                    color=color,
                    significance=0,
                    tooltip=f"{asset} {factor} exposure: {value:.2%}"
                )
                cells.append(cell)
        
        return HeatmapData(
            heatmap_id=str(uuid.uuid4()),
            title="Portfolio Factor Exposure",
            heatmap_type=HeatmapType.EXPOSURE,
            created_at=datetime.now(),
            row_labels=assets,
            col_labels=factors,
            values=exposure_matrix.values,
            cells=cells
        )
    
    def generate_risk_contribution_heatmap(
        self,
        portfolio_weights: Dict[str, float],
        covariance_matrix: pd.DataFrame
    ) -> HeatmapData:
        """Generate risk contribution heatmap"""
        import uuid
        
        assets = list(portfolio_weights.keys())
        weights = np.array([portfolio_weights[a] for a in assets])
        
        # Calculate marginal risk contributions
        cov = covariance_matrix.loc[assets, assets].values
        portfolio_var = weights @ cov @ weights
        portfolio_std = np.sqrt(portfolio_var)
        
        marginal_contrib = cov @ weights / portfolio_std
        risk_contrib = weights * marginal_contrib
        risk_contrib_pct = risk_contrib / risk_contrib.sum()
        
        # Create matrix showing pairwise risk interactions
        risk_matrix = np.outer(risk_contrib, risk_contrib)
        
        cells = []
        min_val = risk_matrix.min()
        max_val = risk_matrix.max()
        
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets):
                value = risk_matrix[i, j]
                color = self.value_to_color(value, min_val, max_val, 'sequential')
                
                cell = HeatmapCell(
                    row_label=asset1,
                    col_label=asset2,
                    value=value,
                    normalized_value=(value - min_val) / (max_val - min_val),
                    color=color,
                    significance=0,
                    tooltip=f"{asset1} × {asset2} risk: {value:.4f}"
                )
                cells.append(cell)
        
        return HeatmapData(
            heatmap_id=str(uuid.uuid4()),
            title="Risk Contribution Matrix",
            heatmap_type=HeatmapType.RISK_CONTRIBUTION,
            created_at=datetime.now(),
            row_labels=assets,
            col_labels=assets,
            values=risk_matrix,
            cells=cells,
            metadata={'risk_contrib_pct': dict(zip(assets, risk_contrib_pct.tolist()))}
        )
    
    def generate_animated_correlation_heatmap(
        self,
        returns: pd.DataFrame,
        window: int = 60,
        step: int = 5
    ) -> HeatmapData:
        """
        Generate animated heatmap showing correlation evolution over time.
        
        Args:
            returns: Asset returns DataFrame
            window: Rolling window size
            step: Step size for animation frames
        """
        import uuid
        
        frames = []
        
        for i in range(window, len(returns), step):
            window_returns = returns.iloc[i-window:i]
            corr = window_returns.corr()
            
            frame = {
                'date': returns.index[i].strftime('%Y-%m-%d'),
                'values': corr.values.tolist(),
                'row_labels': list(corr.index),
                'col_labels': list(corr.columns)
            }
            frames.append(frame)
        
        # Use last frame as base
        last_corr = returns.iloc[-window:].corr()
        
        cells = []
        for i, row in enumerate(last_corr.index):
            for j, col in enumerate(last_corr.columns):
                value = last_corr.loc[row, col]
                color = self.value_to_color(value, -1, 1, 'diverging')
                
                cell = HeatmapCell(
                    row_label=row,
                    col_label=col,
                    value=value,
                    normalized_value=(value + 1) / 2,
                    color=color,
                    significance=0,
                    tooltip=f"{row} vs {col}: {value:.3f}"
                )
                cells.append(cell)
        
        return HeatmapData(
            heatmap_id=str(uuid.uuid4()),
            title="Rolling Correlation Evolution",
            heatmap_type=HeatmapType.CORRELATION,
            created_at=datetime.now(),
            row_labels=list(last_corr.index),
            col_labels=list(last_corr.columns),
            values=last_corr.values,
            cells=cells,
            time_period=f"Rolling {window}-day correlation",
            data_points=len(returns),
            animation_frames=frames
        )
    
    def generate_sector_rotation_heatmap(
        self,
        sector_returns: pd.DataFrame,
        lookback_periods: List[int] = [5, 21, 63, 126, 252]
    ) -> HeatmapData:
        """
        Generate sector rotation heatmap showing momentum across timeframes.
        
        Args:
            sector_returns: DataFrame with sector returns
            lookback_periods: List of lookback periods in days
        """
        import uuid
        
        sectors = sector_returns.columns.tolist()
        period_labels = [f"{p}D" for p in lookback_periods]
        
        momentum_matrix = pd.DataFrame(
            index=sectors,
            columns=period_labels,
            dtype=float
        )
        
        for sector in sectors:
            for period, label in zip(lookback_periods, period_labels):
                if len(sector_returns) >= period:
                    cumulative_return = (1 + sector_returns[sector].iloc[-period:]).prod() - 1
                    momentum_matrix.loc[sector, label] = cumulative_return
        
        # Sort by longest period momentum
        momentum_matrix = momentum_matrix.sort_values(period_labels[-1], ascending=False)
        
        cells = []
        min_val = momentum_matrix.values.min()
        max_val = momentum_matrix.values.max()
        
        for sector in momentum_matrix.index:
            for period in period_labels:
                value = momentum_matrix.loc[sector, period]
                color = self.value_to_color(value, min_val, max_val, 'diverging')
                
                cell = HeatmapCell(
                    row_label=sector,
                    col_label=period,
                    value=value,
                    normalized_value=(value - min_val) / (max_val - min_val) if max_val > min_val else 0.5,
                    color=color,
                    significance=0,
                    tooltip=f"{sector} {period} return: {value:.2%}"
                )
                cells.append(cell)
        
        return HeatmapData(
            heatmap_id=str(uuid.uuid4()),
            title="Sector Rotation Momentum",
            heatmap_type=HeatmapType.SECTOR_ROTATION,
            created_at=datetime.now(),
            row_labels=list(momentum_matrix.index),
            col_labels=period_labels,
            values=momentum_matrix.values,
            cells=cells
        )
    
    def generate_drawdown_heatmap(
        self,
        portfolio_returns: pd.DataFrame,
        rolling_periods: List[int] = [21, 63, 126, 252]
    ) -> HeatmapData:
        """
        Generate drawdown analysis heatmap across timeframes.
        """
        import uuid
        
        assets = portfolio_returns.columns.tolist()
        period_labels = [f"{p}D Max DD" for p in rolling_periods]
        
        drawdown_matrix = pd.DataFrame(
            index=assets,
            columns=period_labels,
            dtype=float
        )
        
        for asset in assets:
            prices = (1 + portfolio_returns[asset]).cumprod()
            
            for period, label in zip(rolling_periods, period_labels):
                rolling_max = prices.rolling(window=period, min_periods=1).max()
                drawdowns = prices / rolling_max - 1
                max_dd = drawdowns.min()
                drawdown_matrix.loc[asset, label] = max_dd
        
        cells = []
        min_val = drawdown_matrix.values.min()
        max_val = 0  # Drawdowns are always negative
        
        for asset in assets:
            for period in period_labels:
                value = drawdown_matrix.loc[asset, period]
                # Use sequential palette for drawdowns (more red = worse)
                normalized = abs(value) / abs(min_val) if min_val != 0 else 0
                color = self.value_to_color(normalized, 0, 1, 'sequential')
                
                cell = HeatmapCell(
                    row_label=asset,
                    col_label=period,
                    value=value,
                    normalized_value=normalized,
                    color=color,
                    significance=0,
                    tooltip=f"{asset} {period}: {value:.2%}"
                )
                cells.append(cell)
        
        return HeatmapData(
            heatmap_id=str(uuid.uuid4()),
            title="Maximum Drawdown Analysis",
            heatmap_type=HeatmapType.DRAWDOWN,
            created_at=datetime.now(),
            row_labels=assets,
            col_labels=period_labels,
            values=drawdown_matrix.values,
            cells=cells
        )
    
    def render_plotly_heatmap(self, heatmap: HeatmapData) -> Dict[str, Any]:
        """Generate Plotly figure configuration for heatmap"""
        # Color scale based on heatmap type
        if heatmap.heatmap_type in [HeatmapType.CORRELATION, HeatmapType.SECTOR_ROTATION]:
            colorscale = [
                [0, 'rgb(180, 50, 50)'],
                [0.5, 'rgb(245, 245, 245)'],
                [1, 'rgb(50, 120, 180)']
            ]
        else:
            colorscale = [
                [0, 'rgb(255, 255, 220)'],
                [1, 'rgb(180, 30, 30)']
            ]
        
        figure = {
            'data': [{
                'type': 'heatmap',
                'z': heatmap.values.tolist(),
                'x': heatmap.col_labels,
                'y': heatmap.row_labels,
                'colorscale': colorscale,
                'hovertemplate': '%{y} vs %{x}: %{z:.3f}<extra></extra>',
                'colorbar': {
                    'title': heatmap.title
                }
            }],
            'layout': {
                'title': heatmap.title,
                'xaxis': {
                    'tickangle': -45,
                    'tickfont': {'size': 10}
                },
                'yaxis': {
                    'tickfont': {'size': 10}
                },
                'height': max(400, len(heatmap.row_labels) * 30),
                'width': max(500, len(heatmap.col_labels) * 30)
            }
        }
        
        # Add animation if available
        if heatmap.animation_frames:
            figure['frames'] = [
                {
                    'data': [{
                        'type': 'heatmap',
                        'z': frame['values'],
                        'x': frame['col_labels'],
                        'y': frame['row_labels']
                    }],
                    'name': frame['date']
                }
                for frame in heatmap.animation_frames
            ]
            figure['layout']['updatemenus'] = [{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 200, 'redraw': True},
                            'fromcurrent': True
                        }]
                    },
                    {
                        'label': 'Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate'
                        }]
                    }
                ]
            }]
            figure['layout']['sliders'] = [{
                'steps': [
                    {'label': frame['date'], 'method': 'animate', 
                     'args': [[frame['date']], {'frame': {'duration': 200}, 'mode': 'immediate'}]}
                    for frame in heatmap.animation_frames
                ]
            }]
        
        return figure
    
    def get_correlation_insights(
        self,
        heatmap: HeatmapData
    ) -> List[Dict[str, Any]]:
        """Extract key insights from correlation heatmap"""
        insights = []
        
        # Find highest positive correlations (excluding diagonal)
        high_corrs = []
        low_corrs = []
        
        for cell in heatmap.cells:
            if cell.row_label != cell.col_label:
                if cell.value > 0.7:
                    high_corrs.append(cell)
                elif cell.value < -0.3:
                    low_corrs.append(cell)
        
        high_corrs.sort(key=lambda x: x.value, reverse=True)
        low_corrs.sort(key=lambda x: x.value)
        
        if high_corrs:
            insights.append({
                'type': 'high_correlation',
                'severity': 'warning',
                'message': f"High correlation detected between {high_corrs[0].row_label} and {high_corrs[0].col_label} ({high_corrs[0].value:.2f})",
                'recommendation': "Consider reducing allocation to one of these assets for better diversification"
            })
        
        if low_corrs:
            insights.append({
                'type': 'diversification',
                'severity': 'info',
                'message': f"Good diversification: {low_corrs[0].row_label} and {low_corrs[0].col_label} are negatively correlated ({low_corrs[0].value:.2f})",
                'recommendation': "This pair provides portfolio hedging benefits"
            })
        
        # Cluster insights
        if heatmap.clusters:
            for cluster_id, assets in heatmap.clusters.items():
                if len(assets) > 1:
                    insights.append({
                        'type': 'cluster',
                        'severity': 'info',
                        'message': f"Assets {', '.join(assets)} form a correlation cluster",
                        'recommendation': f"These {len(assets)} assets move together - consider as single risk factor"
                    })
        
        return insights
