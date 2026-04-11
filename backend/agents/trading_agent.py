"""
Enhanced Trading Agent with CAI Integration
============================================

Reinforcement Learning trading agent with full CAI integration:
- Strategy selection (Momentum, Mean Reversion, RL)
- Execution timing
- Position sizing
- Pre-execution simulation
- Kill switch respect
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

from agents.base_agent import BaseAgent, AgentTask, AgentPriority


class StrategyType(Enum):
    """Available trading strategies"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    TREND_FOLLOWING = "trend_following"
    VOLATILITY = "volatility"
    RL_AGENT = "rl_agent"
    FACTOR_BASED = "factor_based"


class TradeAction(Enum):
    """Trade actions"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"
    HEDGE = "hedge"


@dataclass
class TradeSignal:
    """Trading signal from strategy"""
    signal_id: str
    strategy: StrategyType
    asset: str
    action: TradeAction
    confidence: float
    expected_return: float
    expected_risk: float
    time_horizon: str
    key_drivers: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TradeCandidate:
    """Candidate trade for CAI evaluation"""
    id: str
    description: str
    strategy: StrategyType
    asset: str
    action: str
    quantity: float
    expected_return: float
    expected_risk: float
    confidence: float
    sharpe_ratio: float
    risk_reward_ratio: float
    key_drivers: List[str]


@dataclass
class SimulationResult:
    """Result of trade simulation"""
    simulation_id: str
    candidate_id: str
    expected_return: float
    expected_drawdown: float
    win_rate: float
    sharpe: float
    max_loss: float
    scenarios_tested: int
    key_drivers: List[str]
    risk_metrics: Dict[str, float]


class EnhancedTradingAgent(BaseAgent):
    """
    Enhanced trading agent with full CAI integration.
    
    Responsibilities:
    - Strategy selection based on regime
    - Execution timing optimization
    - Position sizing based on confidence
    - Pre-trade simulation
    - Kill switch monitoring
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(
            agent_id="trading_rl",
            name="Enhanced Trading & RL Agent",
            capabilities=[
                "strategy_selection",
                "execution_timing",
                "position_sizing",
                "trade_simulation",
                "rl_trading"
            ]
        )
        
        self.config = config or {}
        self.data_type = "trading"
        
        # Trading constraints from CAI
        self.constraints = {
            'min_sharpe': 0.5,
            'min_risk_reward': 2.0,
            'max_position_size': 0.10,
            'min_confidence': 0.65,
        }
        
        # Available strategies
        self.strategies = {
            StrategyType.MOMENTUM: self._momentum_strategy,
            StrategyType.MEAN_REVERSION: self._mean_reversion_strategy,
            StrategyType.TREND_FOLLOWING: self._trend_following_strategy,
            StrategyType.VOLATILITY: self._volatility_strategy,
        }
        
        # Strategy performance tracking
        self.strategy_performance: Dict[StrategyType, Dict] = {
            s: {'trades': 0, 'wins': 0, 'sharpe': 0.0}
            for s in StrategyType
        }
        
        # Position tracking
        self.positions: Dict[str, Dict] = {}
        
        # Kill switch status
        self.kill_switch_active = False
        
        self.logger = logging.getLogger("agent.trading_rl")
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process trading tasks"""
        task_type = task.task_type
        parameters = task.parameters
        
        try:
            if task_type == "generate_signals":
                return await self._generate_signals(parameters)
            elif task_type == "evaluate_entry":
                return await self._evaluate_entry(parameters)
            elif task_type == "simulate_trade":
                return await self.simulate_execution(parameters.get('candidate', {}), parameters)
            elif task_type == "execute_trade":
                return await self._execute_trade(parameters)
            elif task_type == "position_sizing":
                return await self._calculate_position_size(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Error processing task {task.task_id}: {e}")
            raise
    
    async def analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data for trading opportunities"""
        try:
            return {
                'signals': await self._generate_signals(data),
                'positions': self.positions,
                'strategy_performance': {
                    s.value: p for s, p in self.strategy_performance.items()
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing data: {e}")
            return {'error': str(e)}
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Get current trading data"""
        return {
            "active_positions": len(self.positions),
            "kill_switch_active": self.kill_switch_active,
            "quality_score": 0.90,
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_candidates(
        self,
        data: Dict[str, Any],
        regime: 'MarketRegime'
    ) -> List[Dict]:
        """
        Generate trade candidates for CAI evaluation.
        
        Must:
        - Only trade if expected Sharpe > threshold
        - Only trade if risk-reward >= configured minimum
        - Generate multiple candidates for comparison
        """
        candidates = []
        
        # Select strategies appropriate for regime
        active_strategies = self._select_strategies_for_regime(regime)
        
        for strategy_type in active_strategies:
            signals = await self._run_strategy(strategy_type, data)
            
            for signal in signals:
                # Check minimum thresholds
                if not self._meets_trading_criteria(signal):
                    continue
                
                candidate = TradeCandidate(
                    id=f"cand_{signal.signal_id}",
                    description=f"{signal.action.value.upper()} {signal.asset} via {strategy_type.value}",
                    strategy=strategy_type,
                    asset=signal.asset,
                    action=signal.action.value.upper(),
                    quantity=await self._calculate_optimal_quantity(signal, data),
                    expected_return=signal.expected_return,
                    expected_risk=signal.expected_risk,
                    confidence=signal.confidence,
                    sharpe_ratio=signal.expected_return / max(signal.expected_risk, 0.01),
                    risk_reward_ratio=signal.expected_return / max(signal.expected_risk, 0.01),
                    key_drivers=signal.key_drivers
                )
                
                candidates.append(self._candidate_to_dict(candidate))
        
        return candidates
    
    async def simulate_execution(
        self,
        candidate: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate trade execution before live trading.
        
        Must:
        - Always simulate before live execution
        - Return expected outcomes with confidence intervals
        """
        simulation_id = str(uuid.uuid4())[:8]
        
        # Monte Carlo simulation
        num_scenarios = 1000
        returns = []
        drawdowns = []
        
        expected_return = candidate.get('expected_return', 0.05)
        expected_risk = candidate.get('expected_risk', 0.15)
        
        for _ in range(num_scenarios):
            # Simulate return with uncertainty
            simulated_return = np.random.normal(expected_return, expected_risk)
            returns.append(simulated_return)
            
            # Simulate path for drawdown
            path = np.random.normal(expected_return/252, expected_risk/np.sqrt(252), 20)
            cumulative = np.cumprod(1 + path)
            peak = np.maximum.accumulate(cumulative)
            dd = (cumulative - peak) / peak
            drawdowns.append(dd.min())
        
        returns = np.array(returns)
        drawdowns = np.array(drawdowns)
        
        # Calculate statistics
        win_rate = np.mean(returns > 0)
        avg_return = np.mean(returns)
        avg_drawdown = np.mean(drawdowns)
        sharpe = avg_return / np.std(returns) if np.std(returns) > 0 else 0
        max_loss = np.percentile(returns, 5)  # 5th percentile
        
        result = SimulationResult(
            simulation_id=simulation_id,
            candidate_id=candidate.get('id', 'unknown'),
            expected_return=avg_return,
            expected_drawdown=avg_drawdown,
            win_rate=win_rate,
            sharpe=sharpe,
            max_loss=max_loss,
            scenarios_tested=num_scenarios,
            key_drivers=candidate.get('key_drivers', []),
            risk_metrics={
                'var_95': np.percentile(returns, 5),
                'var_99': np.percentile(returns, 1),
                'cvar_95': np.mean(returns[returns <= np.percentile(returns, 5)]),
                'expected_drawdown': avg_drawdown,
                'volatility': np.std(returns)
            }
        )
        
        return self._simulation_to_dict(result)
    
    async def reduce_all_positions(self, reduction_pct: float = 0.5):
        """Reduce all positions by given percentage (emergency action)"""
        self.logger.warning(f"REDUCING ALL POSITIONS BY {reduction_pct:.0%}")
        
        for asset, position in self.positions.items():
            original_qty = position.get('quantity', 0)
            new_qty = original_qty * (1 - reduction_pct)
            position['quantity'] = new_qty
            
            self.logger.info(f"Reduced {asset}: {original_qty} -> {new_qty}")
    
    def _select_strategies_for_regime(self, regime) -> List[StrategyType]:
        """Select appropriate strategies based on market regime"""
        regime_strategies = {
            'bull': [StrategyType.MOMENTUM, StrategyType.TREND_FOLLOWING],
            'late_bull': [StrategyType.MOMENTUM, StrategyType.VOLATILITY],
            'bear': [StrategyType.MEAN_REVERSION, StrategyType.VOLATILITY],
            'crisis': [StrategyType.VOLATILITY],
            'sideways': [StrategyType.MEAN_REVERSION, StrategyType.FACTOR_BASED],
            'recovery': [StrategyType.TREND_FOLLOWING, StrategyType.MOMENTUM],
        }
        
        regime_value = regime.value if hasattr(regime, 'value') else str(regime)
        return regime_strategies.get(regime_value, [StrategyType.MEAN_REVERSION])
    
    async def _run_strategy(
        self,
        strategy_type: StrategyType,
        data: Dict
    ) -> List[TradeSignal]:
        """Run a specific strategy and get signals"""
        strategy_func = self.strategies.get(strategy_type)
        
        if strategy_func:
            return await strategy_func(data)
        
        return []
    
    async def _momentum_strategy(self, data: Dict) -> List[TradeSignal]:
        """Momentum-based trading strategy"""
        signals = []
        
        assets = data.get('assets', ['SPY', 'QQQ'])
        
        for asset in assets:
            asset_data = data.get(f'{asset}_data', {})
            momentum_20d = asset_data.get('momentum_20d', 0)
            rsi = asset_data.get('rsi', 50)
            
            if momentum_20d > 0.10 and rsi < 70:
                signals.append(TradeSignal(
                    signal_id=f"mom_{asset}_{datetime.now().strftime('%H%M%S')}",
                    strategy=StrategyType.MOMENTUM,
                    asset=asset,
                    action=TradeAction.BUY,
                    confidence=min(0.9, 0.5 + momentum_20d),
                    expected_return=momentum_20d * 0.5,  # Expect half of recent momentum
                    expected_risk=asset_data.get('volatility', 0.15),
                    time_horizon="1-4 weeks",
                    key_drivers=[
                        f"Strong momentum: {momentum_20d:.1%}",
                        f"RSI not overbought: {rsi:.0f}"
                    ]
                ))
            elif momentum_20d < -0.10 and rsi > 30:
                signals.append(TradeSignal(
                    signal_id=f"mom_{asset}_{datetime.now().strftime('%H%M%S')}",
                    strategy=StrategyType.MOMENTUM,
                    asset=asset,
                    action=TradeAction.SELL,
                    confidence=min(0.9, 0.5 + abs(momentum_20d)),
                    expected_return=abs(momentum_20d) * 0.3,
                    expected_risk=asset_data.get('volatility', 0.15),
                    time_horizon="1-2 weeks",
                    key_drivers=[
                        f"Negative momentum: {momentum_20d:.1%}",
                        f"RSI not oversold: {rsi:.0f}"
                    ]
                ))
        
        return signals
    
    async def _mean_reversion_strategy(self, data: Dict) -> List[TradeSignal]:
        """Mean reversion trading strategy"""
        signals = []
        
        assets = data.get('assets', ['SPY'])
        
        for asset in assets:
            asset_data = data.get(f'{asset}_data', {})
            z_score = asset_data.get('price_z_score', 0)
            rsi = asset_data.get('rsi', 50)
            
            if z_score < -2 and rsi < 30:
                signals.append(TradeSignal(
                    signal_id=f"mr_{asset}_{datetime.now().strftime('%H%M%S')}",
                    strategy=StrategyType.MEAN_REVERSION,
                    asset=asset,
                    action=TradeAction.BUY,
                    confidence=min(0.85, 0.5 + abs(z_score) / 4),
                    expected_return=0.05,  # Expect 5% reversion
                    expected_risk=asset_data.get('volatility', 0.15),
                    time_horizon="1-2 weeks",
                    key_drivers=[
                        f"Oversold: z-score {z_score:.1f}",
                        f"RSI extreme: {rsi:.0f}"
                    ]
                ))
            elif z_score > 2 and rsi > 70:
                signals.append(TradeSignal(
                    signal_id=f"mr_{asset}_{datetime.now().strftime('%H%M%S')}",
                    strategy=StrategyType.MEAN_REVERSION,
                    asset=asset,
                    action=TradeAction.SELL,
                    confidence=min(0.85, 0.5 + abs(z_score) / 4),
                    expected_return=0.05,
                    expected_risk=asset_data.get('volatility', 0.15),
                    time_horizon="1-2 weeks",
                    key_drivers=[
                        f"Overbought: z-score {z_score:.1f}",
                        f"RSI extreme: {rsi:.0f}"
                    ]
                ))
        
        return signals
    
    async def _trend_following_strategy(self, data: Dict) -> List[TradeSignal]:
        """Trend following strategy"""
        signals = []
        
        assets = data.get('assets', ['SPY'])
        
        for asset in assets:
            asset_data = data.get(f'{asset}_data', {})
            trend = asset_data.get('trend_strength', 0)
            above_200ma = asset_data.get('above_200ma', False)
            
            if trend > 0.7 and above_200ma:
                signals.append(TradeSignal(
                    signal_id=f"tf_{asset}_{datetime.now().strftime('%H%M%S')}",
                    strategy=StrategyType.TREND_FOLLOWING,
                    asset=asset,
                    action=TradeAction.BUY,
                    confidence=trend,
                    expected_return=0.08,
                    expected_risk=asset_data.get('volatility', 0.12),
                    time_horizon="1-3 months",
                    key_drivers=[
                        f"Strong uptrend: {trend:.0%}",
                        "Price above 200-day MA"
                    ]
                ))
        
        return signals
    
    async def _volatility_strategy(self, data: Dict) -> List[TradeSignal]:
        """Volatility-based strategy"""
        signals = []
        
        vix = data.get('vix', 20)
        vix_percentile = data.get('vix_percentile', 50)
        
        if vix_percentile > 90:
            signals.append(TradeSignal(
                signal_id=f"vol_hedge_{datetime.now().strftime('%H%M%S')}",
                strategy=StrategyType.VOLATILITY,
                asset="HEDGE",
                action=TradeAction.HEDGE,
                confidence=0.75,
                expected_return=0.02,
                expected_risk=0.05,
                time_horizon="1-4 weeks",
                key_drivers=[
                    f"VIX at {vix_percentile:.0f}th percentile",
                    "Elevated market stress"
                ]
            ))
        
        return signals
    
    def _meets_trading_criteria(self, signal: TradeSignal) -> bool:
        """Check if signal meets minimum trading criteria"""
        # Expected Sharpe > threshold
        expected_sharpe = signal.expected_return / max(signal.expected_risk, 0.01)
        if expected_sharpe < self.constraints['min_sharpe']:
            return False
        
        # Risk-reward ratio >= minimum
        if expected_sharpe < self.constraints['min_risk_reward']:
            return False
        
        # Confidence >= minimum
        if signal.confidence < self.constraints['min_confidence']:
            return False
        
        return True
    
    async def _calculate_optimal_quantity(
        self,
        signal: TradeSignal,
        data: Dict
    ) -> float:
        """Calculate optimal position size based on Kelly criterion and constraints"""
        portfolio_value = data.get('portfolio_value', 100000)
        
        # Simplified Kelly fraction
        win_prob = (signal.confidence + 0.5) / 2  # Convert confidence to win probability
        win_loss_ratio = signal.expected_return / max(signal.expected_risk, 0.01)
        
        kelly_fraction = win_prob - (1 - win_prob) / win_loss_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        # Apply position size constraint
        max_position = self.constraints['max_position_size']
        position_fraction = min(kelly_fraction, max_position)
        
        # Scale by confidence
        position_fraction *= signal.confidence
        
        return portfolio_value * position_fraction
    
    async def _generate_signals(self, data: Dict) -> List[Dict]:
        """Generate trading signals from all strategies"""
        all_signals = []
        
        for strategy_type in self.strategies.keys():
            signals = await self._run_strategy(strategy_type, data)
            for signal in signals:
                all_signals.append({
                    'signal_id': signal.signal_id,
                    'strategy': signal.strategy.value,
                    'asset': signal.asset,
                    'action': signal.action.value,
                    'confidence': signal.confidence,
                    'expected_return': signal.expected_return
                })
        
        return all_signals
    
    async def _evaluate_entry(self, params: Dict) -> Dict[str, Any]:
        """Evaluate entry timing"""
        return {
            'optimal_entry': True,
            'timing_score': 0.75,
            'recommendation': 'Execute at market open'
        }
    
    async def _execute_trade(self, params: Dict) -> Dict[str, Any]:
        """Execute a trade (paper trading by default)"""
        if self.kill_switch_active:
            return {
                'executed': False,
                'reason': 'Kill switch active'
            }
        
        asset = params.get('asset')
        action = params.get('action')
        quantity = params.get('quantity', 0)
        
        # Update positions
        if action in ['BUY', 'buy']:
            if asset not in self.positions:
                self.positions[asset] = {'quantity': 0, 'avg_price': 0}
            self.positions[asset]['quantity'] += quantity
        elif action in ['SELL', 'sell']:
            if asset in self.positions:
                self.positions[asset]['quantity'] -= quantity
        
        return {
            'executed': True,
            'asset': asset,
            'action': action,
            'quantity': quantity,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _calculate_position_size(self, params: Dict) -> Dict[str, Any]:
        """Calculate optimal position size"""
        signal = TradeSignal(
            signal_id="temp",
            strategy=StrategyType.MOMENTUM,
            asset=params.get('asset', 'SPY'),
            action=TradeAction.BUY,
            confidence=params.get('confidence', 0.7),
            expected_return=params.get('expected_return', 0.05),
            expected_risk=params.get('expected_risk', 0.15),
            time_horizon="short",
            key_drivers=[]
        )
        
        quantity = await self._calculate_optimal_quantity(signal, params)
        
        return {
            'recommended_quantity': quantity,
            'max_quantity': params.get('portfolio_value', 100000) * self.constraints['max_position_size']
        }
    
    def _candidate_to_dict(self, candidate: TradeCandidate) -> Dict:
        """Convert candidate to dictionary"""
        return {
            'id': candidate.id,
            'description': candidate.description,
            'strategy': candidate.strategy.value,
            'asset': candidate.asset,
            'action': candidate.action,
            'quantity': candidate.quantity,
            'expected_return': candidate.expected_return,
            'expected_risk': candidate.expected_risk,
            'confidence': candidate.confidence,
            'sharpe_ratio': candidate.sharpe_ratio,
            'risk_reward_ratio': candidate.risk_reward_ratio,
            'key_drivers': candidate.key_drivers
        }
    
    def _simulation_to_dict(self, result: SimulationResult) -> Dict:
        """Convert simulation result to dictionary"""
        return {
            'simulation_id': result.simulation_id,
            'candidate_id': result.candidate_id,
            'expected_return': result.expected_return,
            'expected_drawdown': result.expected_drawdown,
            'win_rate': result.win_rate,
            'sharpe': result.sharpe,
            'max_loss': result.max_loss,
            'scenarios_tested': result.scenarios_tested,
            'key_drivers': result.key_drivers,
            'var_95': result.risk_metrics.get('var_95', 0),
            'var_99': result.risk_metrics.get('var_99', 0),
            'cvar_95': result.risk_metrics.get('cvar_95', 0),
            'volatility': result.risk_metrics.get('volatility', 0)
        }
