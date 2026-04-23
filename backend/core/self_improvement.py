"""
Self-Improvement Module
======================

Continuous self-improvement capabilities for the CAI system:
- Model drift detection
- Strategy performance tracking
- Strategy retirement engine
- Prediction accuracy tracking
- Feature and strategy suggestions
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque
from scipy import stats


class DriftType(Enum):
    """Types of model drift"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    PERFORMANCE_DRIFT = "performance_drift"


class StrategyStatus(Enum):
    """Status of a trading strategy"""
    ACTIVE = "active"
    PROBATION = "probation"
    REDUCED = "reduced"
    RETIRED = "retired"
    ARCHIVED = "archived"


@dataclass
class DriftAlert:
    """Alert for detected drift"""
    alert_id: str
    drift_type: DriftType
    model_id: str
    severity: float  # 0-1
    description: str
    affected_features: List[str]
    recommended_action: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ModelPerformance:
    """Track model performance over time"""
    model_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    hit_rate: float
    profit_factor: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StrategyRecord:
    """Record of a trading strategy"""
    strategy_id: str
    name: str
    description: str
    status: StrategyStatus
    inception_date: datetime
    capital_allocation: float  # Percentage of capital
    
    # Performance metrics
    cumulative_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    
    # Tracking
    trades_executed: int
    profitable_trades: int
    last_trade_date: Optional[datetime]
    
    # Retirement info
    retirement_reason: Optional[str] = None
    retirement_date: Optional[datetime] = None


@dataclass
class ImprovementSuggestion:
    """Suggestion for system improvement"""
    suggestion_id: str
    category: str  # 'feature', 'strategy', 'parameter', 'model'
    title: str
    description: str
    expected_impact: str
    priority: int  # 1-5
    evidence: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class ModelDriftDetector:
    """
    Detect various types of model drift and data drift.
    
    Monitors:
    - Feature distribution changes
    - Prediction distribution changes
    - Model performance degradation
    - Concept drift in market regimes
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("drift_detector")
        
        # Baseline statistics for each model
        self.baselines: Dict[str, Dict] = {}
        
        # Recent data windows
        self.feature_windows: Dict[str, deque] = {}
        self.prediction_windows: Dict[str, deque] = {}
        
        # Alert history
        self.alerts: List[DriftAlert] = []
        
        # Thresholds
        self.thresholds = {
            'ks_statistic': 0.15,  # Kolmogorov-Smirnov threshold
            'psi': 0.20,  # Population Stability Index threshold
            'accuracy_drop': 0.10,  # 10% accuracy drop
            'sharpe_drop': 0.50,  # Sharpe ratio drop
        }
    
    def set_baseline(self, model_id: str, features: pd.DataFrame, predictions: np.ndarray):
        """Set baseline statistics for a model"""
        self.baselines[model_id] = {
            'feature_means': features.mean().to_dict(),
            'feature_stds': features.std().to_dict(),
            'feature_distributions': {
                col: features[col].values for col in features.columns
            },
            'prediction_distribution': predictions,
            'prediction_mean': np.mean(predictions),
            'prediction_std': np.std(predictions),
            'timestamp': datetime.now()
        }
        
        # Initialize windows
        self.feature_windows[model_id] = deque(maxlen=1000)
        self.prediction_windows[model_id] = deque(maxlen=1000)
        
        self.logger.info(f"Baseline set for model {model_id}")
    
    async def check_all_models(self) -> Optional[Dict]:
        """Check all registered models for drift"""
        drift_detected = {}
        
        for model_id in self.baselines.keys():
            drift = await self.check_model_drift(model_id)
            if drift:
                drift_detected[model_id] = drift
        
        return drift_detected if drift_detected else None
    
    async def check_model_drift(self, model_id: str) -> Optional[Dict]:
        """Check a specific model for drift"""
        if model_id not in self.baselines:
            return None
        
        drift_results = {
            'data_drift': await self._check_data_drift(model_id),
            'prediction_drift': await self._check_prediction_drift(model_id),
            'performance_drift': await self._check_performance_drift(model_id)
        }
        
        # Check if any drift is significant
        significant_drift = {
            k: v for k, v in drift_results.items()
            if v and v.get('is_significant', False)
        }
        
        if significant_drift:
            # Create alert
            alert = DriftAlert(
                alert_id=f"drift_{model_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                drift_type=DriftType.PERFORMANCE_DRIFT,
                model_id=model_id,
                severity=max(d.get('severity', 0) for d in significant_drift.values()),
                description=f"Drift detected in {list(significant_drift.keys())}",
                affected_features=self._get_affected_features(drift_results),
                recommended_action=self._get_drift_recommendation(drift_results)
            )
            self.alerts.append(alert)
            
            return {
                'model_id': model_id,
                'drift_types': list(significant_drift.keys()),
                'severity': alert.severity,
                'recommendation': alert.recommended_action
            }
        
        return None
    
    async def _check_data_drift(self, model_id: str) -> Dict:
        """Check for data drift using KS test and PSI"""
        baseline = self.baselines[model_id]
        window = list(self.feature_windows.get(model_id, []))
        
        if len(window) < 100:
            return {'is_significant': False, 'reason': 'Insufficient data'}
        
        # Convert window to DataFrame
        recent_df = pd.DataFrame(window)
        
        drift_features = []
        max_drift = 0
        
        for feature in baseline.get('feature_distributions', {}):
            if feature not in recent_df.columns:
                continue
            
            baseline_dist = baseline['feature_distributions'][feature]
            recent_dist = recent_df[feature].values
            
            # Kolmogorov-Smirnov test
            ks_stat, p_value = stats.ks_2samp(baseline_dist, recent_dist)
            
            if ks_stat > self.thresholds['ks_statistic']:
                drift_features.append(feature)
                max_drift = max(max_drift, ks_stat)
        
        return {
            'is_significant': len(drift_features) > 0,
            'drift_features': drift_features,
            'max_drift_score': max_drift,
            'severity': min(1.0, max_drift / 0.3)
        }
    
    async def _check_prediction_drift(self, model_id: str) -> Dict:
        """Check for drift in prediction distribution"""
        baseline = self.baselines[model_id]
        window = list(self.prediction_windows.get(model_id, []))
        
        if len(window) < 50:
            return {'is_significant': False, 'reason': 'Insufficient data'}
        
        recent_preds = np.array(window)
        baseline_preds = baseline.get('prediction_distribution', np.array([]))
        
        if len(baseline_preds) == 0:
            return {'is_significant': False, 'reason': 'No baseline'}
        
        # Compare distributions
        ks_stat, p_value = stats.ks_2samp(baseline_preds, recent_preds)
        
        # Compare means
        mean_shift = abs(np.mean(recent_preds) - baseline['prediction_mean'])
        std_units = mean_shift / max(baseline['prediction_std'], 0.001)
        
        is_significant = (ks_stat > self.thresholds['ks_statistic'] or 
                         std_units > 2.0)
        
        return {
            'is_significant': is_significant,
            'ks_statistic': ks_stat,
            'mean_shift_std_units': std_units,
            'severity': min(1.0, max(ks_stat, std_units / 3))
        }
    
    async def _check_performance_drift(self, model_id: str) -> Dict:
        """Check for degradation in model performance"""
        # This would compare recent performance to baseline
        # Placeholder implementation
        return {
            'is_significant': False,
            'accuracy_change': 0,
            'sharpe_change': 0
        }
    
    def add_observation(self, model_id: str, features: Dict, prediction: float):
        """Add a new observation to the monitoring windows"""
        if model_id in self.feature_windows:
            self.feature_windows[model_id].append(features)
        if model_id in self.prediction_windows:
            self.prediction_windows[model_id].append(prediction)
    
    def _get_affected_features(self, drift_results: Dict) -> List[str]:
        """Get list of features affected by drift"""
        features = []
        for result in drift_results.values():
            if isinstance(result, dict):
                features.extend(result.get('drift_features', []))
        return list(set(features))
    
    def _get_drift_recommendation(self, drift_results: Dict) -> str:
        """Get recommended action for detected drift"""
        if drift_results.get('data_drift', {}).get('is_significant'):
            return "Retrain model with recent data"
        elif drift_results.get('prediction_drift', {}).get('is_significant'):
            return "Review model predictions and consider recalibration"
        elif drift_results.get('performance_drift', {}).get('is_significant'):
            return "Evaluate model on recent data and consider retraining"
        return "Monitor closely"


class StrategyRetirementEngine:
    """
    Manage strategy lifecycle including:
    - Performance tracking
    - Capital allocation adjustment
    - Strategy retirement
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("strategy_retirement")
        
        # Strategy registry
        self.strategies: Dict[str, StrategyRecord] = {}
        
        # Performance history
        self.performance_history: Dict[str, List[ModelPerformance]] = {}
        
        # Thresholds
        self.thresholds = {
            'min_sharpe': 0.3,
            'max_drawdown': 0.15,
            'min_win_rate': 0.40,
            'min_profit_factor': 0.8,
            'probation_period_days': 30,
            'min_trades_for_evaluation': 20
        }
    
    def register_strategy(self, strategy: StrategyRecord):
        """Register a new strategy"""
        self.strategies[strategy.strategy_id] = strategy
        self.performance_history[strategy.strategy_id] = []
        self.logger.info(f"Strategy registered: {strategy.name}")
    
    async def identify_underperformers(self) -> List[Dict]:
        """Identify underperforming strategies"""
        underperformers = []
        
        for strategy_id, strategy in self.strategies.items():
            if strategy.status in [StrategyStatus.RETIRED, StrategyStatus.ARCHIVED]:
                continue
            
            # Check if strategy has enough data
            if strategy.trades_executed < self.thresholds['min_trades_for_evaluation']:
                continue
            
            # Calculate performance score
            score = self._calculate_performance_score(strategy)
            
            if score < 0.4:  # Underperforming threshold
                underperformers.append({
                    'id': strategy_id,
                    'name': strategy.name,
                    'performance_score': score,
                    'sharpe_ratio': strategy.sharpe_ratio,
                    'win_rate': strategy.win_rate,
                    'max_drawdown': strategy.max_drawdown,
                    'current_status': strategy.status.value,
                    'recommendation': self._get_recommendation(score, strategy)
                })
        
        return underperformers
    
    def _calculate_performance_score(self, strategy: StrategyRecord) -> float:
        """Calculate composite performance score (0-1)"""
        scores = []
        
        # Sharpe ratio score
        sharpe_score = min(1.0, max(0, strategy.sharpe_ratio / 2.0))
        scores.append(sharpe_score * 0.3)
        
        # Win rate score
        win_score = strategy.win_rate
        scores.append(win_score * 0.2)
        
        # Drawdown score (inverse - lower is better)
        dd_score = max(0, 1 - strategy.max_drawdown / 0.20)
        scores.append(dd_score * 0.2)
        
        # Profit factor score
        pf_score = min(1.0, max(0, (strategy.profit_factor - 0.5) / 1.5))
        scores.append(pf_score * 0.2)
        
        # Consistency score (based on profitable trades ratio)
        if strategy.trades_executed > 0:
            consistency = strategy.profitable_trades / strategy.trades_executed
        else:
            consistency = 0.5
        scores.append(consistency * 0.1)
        
        return sum(scores)
    
    def _get_recommendation(self, score: float, strategy: StrategyRecord) -> str:
        """Get recommendation based on performance score"""
        if score < 0.2:
            return "RETIRE - Severely underperforming"
        elif score < 0.3:
            return "ARCHIVE - Consider retirement"
        elif score < 0.4:
            return "REDUCE - Decrease capital allocation by 50%"
        elif score < 0.5:
            return "PROBATION - Monitor closely, reduce allocation by 25%"
        else:
            return "MAINTAIN - Acceptable performance"
    
    async def reduce_allocation(self, strategy_id: str, reduction_pct: float = 0.5):
        """Reduce capital allocation for a strategy"""
        if strategy_id not in self.strategies:
            return
        
        strategy = self.strategies[strategy_id]
        old_allocation = strategy.capital_allocation
        strategy.capital_allocation *= (1 - reduction_pct)
        
        if strategy.status == StrategyStatus.ACTIVE:
            strategy.status = StrategyStatus.REDUCED
        
        self.logger.info(
            f"Reduced allocation for {strategy.name}: "
            f"{old_allocation:.1%} -> {strategy.capital_allocation:.1%}"
        )
    
    async def archive_strategy(self, strategy_id: str, reason: str = None):
        """Archive a strategy (retire it)"""
        if strategy_id not in self.strategies:
            return
        
        strategy = self.strategies[strategy_id]
        strategy.status = StrategyStatus.ARCHIVED
        strategy.retirement_reason = reason or "Performance below threshold"
        strategy.retirement_date = datetime.now()
        strategy.capital_allocation = 0
        
        self.logger.info(
            f"Strategy archived: {strategy.name} - Reason: {strategy.retirement_reason}"
        )
    
    def update_strategy_performance(
        self,
        strategy_id: str,
        trade_result: Dict
    ):
        """Update strategy performance after a trade"""
        if strategy_id not in self.strategies:
            return
        
        strategy = self.strategies[strategy_id]
        
        # Update trade counts
        strategy.trades_executed += 1
        if trade_result.get('pnl', 0) > 0:
            strategy.profitable_trades += 1
        
        # Update metrics (simplified - would be more sophisticated)
        strategy.win_rate = strategy.profitable_trades / strategy.trades_executed
        strategy.last_trade_date = datetime.now()
    
    def get_allocation_recommendations(self) -> Dict[str, float]:
        """Get recommended capital allocations"""
        recommendations = {}
        total_active_allocation = 0
        
        for strategy_id, strategy in self.strategies.items():
            if strategy.status in [StrategyStatus.ACTIVE, StrategyStatus.REDUCED]:
                score = self._calculate_performance_score(strategy)
                
                # Allocate more to better performing strategies
                recommended = score * 0.20  # Max 20% per strategy
                recommendations[strategy_id] = recommended
                total_active_allocation += recommended
        
        # Normalize if over 100%
        if total_active_allocation > 1.0:
            for sid in recommendations:
                recommendations[sid] /= total_active_allocation
        
        return recommendations


class PredictionAccuracyTracker:
    """Track prediction accuracy over time"""
    
    def __init__(self):
        self.predictions: Dict[str, List[Dict]] = {}
        self.accuracy_history: Dict[str, List[float]] = {}
    
    def record_prediction(
        self,
        model_id: str,
        prediction_id: str,
        predicted_value: float,
        confidence: float,
        timestamp: datetime = None
    ):
        """Record a new prediction"""
        if model_id not in self.predictions:
            self.predictions[model_id] = []
        
        self.predictions[model_id].append({
            'prediction_id': prediction_id,
            'predicted': predicted_value,
            'confidence': confidence,
            'timestamp': timestamp or datetime.now(),
            'actual': None,
            'evaluated': False
        })
    
    def record_actual(
        self,
        model_id: str,
        prediction_id: str,
        actual_value: float
    ):
        """Record actual outcome for a prediction"""
        if model_id not in self.predictions:
            return
        
        for pred in self.predictions[model_id]:
            if pred['prediction_id'] == prediction_id and not pred['evaluated']:
                pred['actual'] = actual_value
                pred['evaluated'] = True
                
                # Calculate accuracy
                if pred['predicted'] is not None:
                    error = abs(pred['predicted'] - actual_value)
                    # Directional accuracy for binary predictions
                    if isinstance(pred['predicted'], bool) or pred['predicted'] in [0, 1]:
                        accurate = pred['predicted'] == actual_value
                    else:
                        # For continuous predictions, define accuracy threshold
                        accurate = error < 0.05  # 5% threshold
                    
                    if model_id not in self.accuracy_history:
                        self.accuracy_history[model_id] = []
                    self.accuracy_history[model_id].append(1.0 if accurate else 0.0)
                break
    
    def get_accuracy(self, model_id: str, window: int = 100) -> float:
        """Get recent accuracy for a model"""
        if model_id not in self.accuracy_history:
            return 0.5  # Default to 50%
        
        recent = self.accuracy_history[model_id][-window:]
        if not recent:
            return 0.5
        
        return sum(recent) / len(recent)
    
    def get_accuracy_trend(self, model_id: str) -> str:
        """Get accuracy trend (improving, stable, declining)"""
        if model_id not in self.accuracy_history:
            return "unknown"
        
        history = self.accuracy_history[model_id]
        if len(history) < 20:
            return "insufficient_data"
        
        recent_50 = np.mean(history[-50:]) if len(history) >= 50 else np.mean(history)
        older_50 = np.mean(history[-100:-50]) if len(history) >= 100 else np.mean(history[:len(history)//2])
        
        diff = recent_50 - older_50
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"


class SelfImprovementEngine:
    """
    Main engine for continuous self-improvement.
    
    Coordinates drift detection, strategy retirement, 
    and improvement suggestions.
    """
    
    def __init__(self):
        self.drift_detector = ModelDriftDetector()
        self.strategy_engine = StrategyRetirementEngine()
        self.accuracy_tracker = PredictionAccuracyTracker()
        
        self.suggestions: List[ImprovementSuggestion] = []
        self.logger = logging.getLogger("self_improvement")
    
    async def run_improvement_cycle(self) -> Dict[str, Any]:
        """Run a full self-improvement cycle"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'drift_detected': [],
            'underperforming_strategies': [],
            'accuracy_report': {},
            'suggestions': []
        }
        
        # Check for model drift
        drift = await self.drift_detector.check_all_models()
        if drift:
            results['drift_detected'] = list(drift.keys())
        
        # Identify underperforming strategies
        underperformers = await self.strategy_engine.identify_underperformers()
        results['underperforming_strategies'] = underperformers
        
        # Generate improvement suggestions
        suggestions = await self._generate_suggestions(drift, underperformers)
        results['suggestions'] = [s.__dict__ for s in suggestions]
        self.suggestions.extend(suggestions)
        
        return results
    
    async def _generate_suggestions(
        self,
        drift: Dict,
        underperformers: List[Dict]
    ) -> List[ImprovementSuggestion]:
        """Generate improvement suggestions based on findings"""
        suggestions = []
        
        # Drift-based suggestions
        if drift:
            for model_id, drift_info in drift.items():
                suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"drift_{model_id}_{datetime.now().strftime('%Y%m%d')}",
                    category="model",
                    title=f"Retrain model {model_id}",
                    description=f"Model drift detected. Recommendation: {drift_info.get('recommendation', 'Investigate')}",
                    expected_impact="Improved prediction accuracy",
                    priority=3 if drift_info.get('severity', 0) > 0.5 else 2,
                    evidence=drift_info
                ))
        
        # Strategy-based suggestions
        for strategy in underperformers:
            if strategy['performance_score'] < 0.3:
                suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"retire_{strategy['id']}_{datetime.now().strftime('%Y%m%d')}",
                    category="strategy",
                    title=f"Retire strategy {strategy['name']}",
                    description=f"Strategy severely underperforming. {strategy['recommendation']}",
                    expected_impact="Improved overall portfolio performance",
                    priority=4,
                    evidence={
                        'performance_score': strategy['performance_score'],
                        'sharpe_ratio': strategy['sharpe_ratio'],
                        'win_rate': strategy['win_rate']
                    }
                ))
        
        return suggestions
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health report"""
        total_strategies = len(self.strategy_engine.strategies)
        active_strategies = len([
            s for s in self.strategy_engine.strategies.values()
            if s.status in [StrategyStatus.ACTIVE, StrategyStatus.REDUCED]
        ])
        
        return {
            'total_strategies': total_strategies,
            'active_strategies': active_strategies,
            'retired_strategies': total_strategies - active_strategies,
            'pending_suggestions': len([s for s in self.suggestions if s.priority >= 3]),
            'drift_alerts': len(self.drift_detector.alerts),
            'last_improvement_cycle': datetime.now().isoformat()
        }
