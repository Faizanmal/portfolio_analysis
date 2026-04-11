"""
Market Research Agent
====================

Specialized agent for market regime detection, factor analysis,
and alpha opportunity discovery.

Responsibilities:
- Regime detection (bull, bear, sideways, crisis)
- Factor analysis
- Macro & sector rotation signals
- Alpha opportunity discovery
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats

from .base_agent import BaseAgent, AgentTask, AgentPriority


class MarketRegime(Enum):
    """Market regime classifications"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    CRISIS = "crisis"
    RECOVERY = "recovery"
    LATE_BULL = "late_bull"
    EARLY_BEAR = "early_bear"


@dataclass
class RegimeDetection:
    """Result of regime detection"""
    regime: MarketRegime
    probability: float
    uncertainty: float
    confidence_interval: Tuple[float, float]
    supporting_factors: List[str]
    risk_factors: List[str]
    factor_scores: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FactorExposure:
    """Factor exposure analysis"""
    factor_name: str
    exposure: float
    contribution: float
    z_score: float
    crowding_risk: float


@dataclass
class AlphaOpportunity:
    """Identified alpha opportunity"""
    opportunity_id: str
    asset: str
    strategy: str
    expected_alpha: float
    confidence: float
    time_horizon: str
    risk_factors: List[str]
    catalysts: List[str]


class MarketResearchAgent(BaseAgent):
    """AI agent specialized in market research and regime detection"""
    
    def __init__(self):
        super().__init__(
            agent_id="market_researcher",
            name="Market Research Agent",
            capabilities=[
                "regime_detection",
                "factor_analysis",
                "sector_rotation",
                "alpha_discovery",
                "macro_analysis",
                "crowding_detection"
            ]
        )
        
        self.data_type = "market_research"
        
        # Regime detection parameters
        self.regime_thresholds = {
            'volatility_crisis': 0.35,  # VIX equivalent threshold
            'drawdown_bear': -0.20,  # 20% drawdown for bear
            'trend_bull': 0.10,  # 10% gain threshold
            'volume_spike': 2.0,  # Volume z-score for regime change
        }
        
        # Factor definitions
        self.factors = [
            'momentum', 'value', 'size', 'quality', 'volatility',
            'growth', 'dividend', 'liquidity'
        ]
        
        # Historical regime data
        self.regime_history: List[RegimeDetection] = []
        self.factor_history: Dict[str, List[float]] = {f: [] for f in self.factors}
        
        # Current state
        self.current_regime = MarketRegime.SIDEWAYS
        self.regime_probability = 0.5
        
        self.logger = logging.getLogger("agent.market_researcher")
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process market research tasks"""
        task_type = task.task_type
        parameters = task.parameters
        
        try:
            if task_type == "regime_detection":
                return await self.detect_regime(parameters)
            elif task_type == "factor_analysis":
                return await self._analyze_factors(parameters)
            elif task_type == "sector_rotation":
                return await self._analyze_sector_rotation(parameters)
            elif task_type == "alpha_discovery":
                return await self._discover_alpha_opportunities(parameters)
            elif task_type == "macro_analysis":
                return await self._analyze_macro_conditions(parameters)
            elif task_type == "crowding_detection":
                return await self._detect_crowding(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Error processing task {task.task_id}: {e}")
            raise
    
    async def analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive market analysis"""
        try:
            return {
                'regime': await self.detect_regime(data),
                'factors': await self._analyze_factors(data),
                'sectors': await self._analyze_sector_rotation(data),
                'opportunities': await self._discover_alpha_opportunities(data),
                'crowding_risks': await self._detect_crowding(data)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing data: {e}")
            return {'error': str(e)}
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Get current market research data"""
        return {
            "current_regime": self.current_regime.value,
            "regime_probability": self.regime_probability,
            "quality_score": 0.85,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_regime_analysis(self) -> Dict[str, Any]:
        """Get detailed regime analysis"""
        return {
            "regime": self.current_regime,
            "probability": self.regime_probability,
            "history": self.regime_history[-10:] if self.regime_history else []
        }
    
    async def detect_regime(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect current market regime with probability score.
        
        Must:
        - Identify regime with probability score
        - Flag regime uncertainty
        - Detect factor crowding risk
        """
        try:
            # Extract market data
            price_data = data.get('price_data', pd.DataFrame())
            volume_data = data.get('volume_data', pd.DataFrame())
            volatility_data = data.get('volatility_data', {})
            
            # Calculate regime indicators
            indicators = await self._calculate_regime_indicators(
                price_data, volume_data, volatility_data
            )
            
            # Determine regime using ensemble of methods
            regime_scores = await self._ensemble_regime_detection(indicators)
            
            # Get best regime and probability
            best_regime = max(regime_scores, key=regime_scores.get)
            probability = regime_scores[best_regime]
            
            # Calculate uncertainty (entropy-based)
            uncertainty = self._calculate_regime_uncertainty(regime_scores)
            
            # Detect factor crowding
            crowding_risk = await self._detect_factor_crowding(data)
            
            # Build result
            detection = RegimeDetection(
                regime=MarketRegime(best_regime),
                probability=probability,
                uncertainty=uncertainty,
                confidence_interval=(
                    max(0, probability - uncertainty),
                    min(1, probability + uncertainty)
                ),
                supporting_factors=self._get_supporting_factors(indicators, best_regime),
                risk_factors=self._get_risk_factors(indicators, crowding_risk),
                factor_scores=indicators
            )
            
            # Update state
            self.current_regime = detection.regime
            self.regime_probability = detection.probability
            self.regime_history.append(detection)
            
            # Log if high uncertainty
            if uncertainty > 0.3:
                self.logger.warning(f"High regime uncertainty: {uncertainty:.2f}")
            
            return {
                'regime': detection.regime,
                'probability': detection.probability,
                'uncertainty': detection.uncertainty,
                'confidence_interval': detection.confidence_interval,
                'supporting_factors': detection.supporting_factors,
                'risk_factors': detection.risk_factors,
                'crowding_risks': crowding_risk,
                'all_regime_scores': regime_scores
            }
            
        except Exception as e:
            self.logger.error(f"Regime detection error: {e}")
            return {
                'regime': MarketRegime.SIDEWAYS,
                'probability': 0.5,
                'uncertainty': 0.5,
                'error': str(e)
            }
    
    async def _calculate_regime_indicators(
        self,
        price_data: pd.DataFrame,
        volume_data: pd.DataFrame,
        volatility_data: Dict
    ) -> Dict[str, float]:
        """Calculate indicators for regime detection"""
        indicators = {}
        
        # If we have price data, calculate indicators
        if not price_data.empty and 'Close' in price_data.columns:
            returns = price_data['Close'].pct_change().dropna()
            
            # Trend indicators
            indicators['trend_20d'] = (price_data['Close'].iloc[-1] / 
                                       price_data['Close'].iloc[-20] - 1) if len(price_data) >= 20 else 0
            indicators['trend_60d'] = (price_data['Close'].iloc[-1] / 
                                       price_data['Close'].iloc[-60] - 1) if len(price_data) >= 60 else 0
            
            # Volatility indicators
            indicators['volatility_20d'] = returns.tail(20).std() * np.sqrt(252)
            indicators['volatility_ratio'] = (
                returns.tail(10).std() / returns.tail(60).std()
            ) if len(returns) >= 60 else 1.0
            
            # Momentum indicators
            indicators['momentum_rsi'] = self._calculate_rsi(price_data['Close'])
            indicators['momentum_macd'] = self._calculate_macd_signal(price_data['Close'])
            
            # Drawdown
            rolling_max = price_data['Close'].expanding().max()
            drawdown = (price_data['Close'] - rolling_max) / rolling_max
            indicators['current_drawdown'] = drawdown.iloc[-1]
            indicators['max_drawdown_30d'] = drawdown.tail(30).min()
        else:
            # Default values
            indicators = {
                'trend_20d': 0,
                'trend_60d': 0,
                'volatility_20d': 0.15,
                'volatility_ratio': 1.0,
                'momentum_rsi': 50,
                'momentum_macd': 0,
                'current_drawdown': 0,
                'max_drawdown_30d': 0
            }
        
        # Volume indicators
        if not volume_data.empty:
            indicators['volume_z_score'] = (
                (volume_data.iloc[-1] - volume_data.mean()) / volume_data.std()
            ).mean()
        else:
            indicators['volume_z_score'] = 0
        
        # Volatility from external data (e.g., VIX)
        indicators['vix_level'] = volatility_data.get('vix', 20)
        indicators['vix_term_structure'] = volatility_data.get('vix_term_structure', 1.0)
        
        return indicators
    
    async def _ensemble_regime_detection(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """Use ensemble of methods for regime detection"""
        scores = {regime.value: 0.0 for regime in MarketRegime}
        
        # Method 1: Trend-based classification
        trend_regime = self._trend_based_regime(indicators)
        scores[trend_regime.value] += 0.3
        
        # Method 2: Volatility-based classification
        vol_regime = self._volatility_based_regime(indicators)
        scores[vol_regime.value] += 0.25
        
        # Method 3: Momentum-based classification
        mom_regime = self._momentum_based_regime(indicators)
        scores[mom_regime.value] += 0.25
        
        # Method 4: Drawdown-based classification
        dd_regime = self._drawdown_based_regime(indicators)
        scores[dd_regime.value] += 0.2
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        return scores
    
    def _trend_based_regime(self, indicators: Dict) -> MarketRegime:
        """Classify regime based on trend"""
        trend_20d = indicators.get('trend_20d', 0)
        trend_60d = indicators.get('trend_60d', 0)
        
        if trend_20d > 0.15 and trend_60d > 0.20:
            return MarketRegime.BULL
        elif trend_20d > 0.10 and trend_60d > 0.30:
            return MarketRegime.LATE_BULL
        elif trend_20d < -0.15 and trend_60d < -0.20:
            return MarketRegime.BEAR
        elif trend_20d < -0.10 and trend_60d > 0:
            return MarketRegime.EARLY_BEAR
        elif trend_20d > 0.05 and trend_60d < -0.10:
            return MarketRegime.RECOVERY
        else:
            return MarketRegime.SIDEWAYS
    
    def _volatility_based_regime(self, indicators: Dict) -> MarketRegime:
        """Classify regime based on volatility"""
        vol = indicators.get('volatility_20d', 0.15)
        vix = indicators.get('vix_level', 20)
        vol_ratio = indicators.get('volatility_ratio', 1.0)
        
        if vix > 35 or vol > 0.35:
            return MarketRegime.CRISIS
        elif vix > 25 or vol > 0.25:
            return MarketRegime.BEAR
        elif vol_ratio > 1.5:
            return MarketRegime.EARLY_BEAR
        elif vix < 15 and vol < 0.12:
            return MarketRegime.BULL
        else:
            return MarketRegime.SIDEWAYS
    
    def _momentum_based_regime(self, indicators: Dict) -> MarketRegime:
        """Classify regime based on momentum"""
        rsi = indicators.get('momentum_rsi', 50)
        macd = indicators.get('momentum_macd', 0)
        
        if rsi > 70 and macd > 0:
            return MarketRegime.LATE_BULL
        elif rsi > 60 and macd > 0:
            return MarketRegime.BULL
        elif rsi < 30 and macd < 0:
            return MarketRegime.CRISIS
        elif rsi < 40 and macd < 0:
            return MarketRegime.BEAR
        elif rsi > 40 and rsi < 60:
            return MarketRegime.SIDEWAYS
        else:
            return MarketRegime.RECOVERY
    
    def _drawdown_based_regime(self, indicators: Dict) -> MarketRegime:
        """Classify regime based on drawdown"""
        current_dd = indicators.get('current_drawdown', 0)
        max_dd = indicators.get('max_drawdown_30d', 0)
        
        if current_dd < -0.30 or max_dd < -0.30:
            return MarketRegime.CRISIS
        elif current_dd < -0.15:
            return MarketRegime.BEAR
        elif current_dd < -0.05:
            return MarketRegime.EARLY_BEAR
        elif current_dd > -0.02:
            return MarketRegime.BULL
        else:
            return MarketRegime.SIDEWAYS
    
    def _calculate_regime_uncertainty(self, regime_scores: Dict[str, float]) -> float:
        """Calculate uncertainty using entropy"""
        probs = np.array(list(regime_scores.values()))
        probs = probs[probs > 0]  # Remove zeros for log
        
        if len(probs) == 0:
            return 1.0
        
        # Normalize
        probs = probs / probs.sum()
        
        # Entropy (normalized)
        entropy = -np.sum(probs * np.log(probs))
        max_entropy = np.log(len(MarketRegime))
        
        return entropy / max_entropy
    
    async def _detect_factor_crowding(self, data: Dict) -> Dict[str, float]:
        """Detect factor crowding risk"""
        crowding = {}
        
        for factor in self.factors:
            # Simplified crowding detection
            # In production, would analyze factor valuations and flows
            factor_data = data.get(f'{factor}_data', {})
            z_score = factor_data.get('z_score', 0)
            flow = factor_data.get('flow', 0)
            
            # Crowding risk based on extreme valuations and high flows
            crowding[factor] = min(1.0, abs(z_score) / 3 * 0.5 + abs(flow) * 0.5)
        
        return crowding
    
    def _get_supporting_factors(self, indicators: Dict, regime: str) -> List[str]:
        """Get factors supporting the regime classification"""
        factors = []
        
        if regime in ['bull', 'late_bull']:
            if indicators.get('trend_20d', 0) > 0.05:
                factors.append(f"Positive 20-day trend: {indicators.get('trend_20d', 0):.1%}")
            if indicators.get('momentum_rsi', 50) > 55:
                factors.append(f"Strong momentum RSI: {indicators.get('momentum_rsi', 50):.0f}")
        elif regime in ['bear', 'crisis']:
            if indicators.get('volatility_20d', 0.15) > 0.25:
                factors.append(f"Elevated volatility: {indicators.get('volatility_20d', 0.15):.1%}")
            if indicators.get('current_drawdown', 0) < -0.10:
                factors.append(f"Significant drawdown: {indicators.get('current_drawdown', 0):.1%}")
        
        return factors
    
    def _get_risk_factors(self, indicators: Dict, crowding: Dict) -> List[str]:
        """Get risk factors to watch"""
        risks = []
        
        if indicators.get('vix_term_structure', 1.0) < 0.9:
            risks.append("Inverted VIX term structure - potential volatility spike")
        
        if indicators.get('volatility_ratio', 1.0) > 1.3:
            risks.append("Rising short-term volatility")
        
        # High crowding in any factor
        high_crowding = [f for f, v in crowding.items() if v > 0.7]
        if high_crowding:
            risks.append(f"Factor crowding in: {', '.join(high_crowding)}")
        
        return risks
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_macd_signal(self, prices: pd.Series) -> float:
        """Calculate MACD signal"""
        if len(prices) < 26:
            return 0.0
        
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return float(macd.iloc[-1] - signal.iloc[-1])
    
    async def _analyze_factors(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze factor exposures and performance"""
        factor_analysis = {}
        
        for factor in self.factors:
            exposure = await self._calculate_factor_exposure(factor, data)
            factor_analysis[factor] = {
                'exposure': exposure.exposure,
                'contribution': exposure.contribution,
                'z_score': exposure.z_score,
                'crowding_risk': exposure.crowding_risk
            }
        
        return factor_analysis
    
    async def _calculate_factor_exposure(self, factor: str, data: Dict) -> FactorExposure:
        """Calculate exposure to a specific factor"""
        # Simplified calculation
        return FactorExposure(
            factor_name=factor,
            exposure=np.random.uniform(-1, 1),  # Would be actual calculation
            contribution=np.random.uniform(-0.05, 0.05),
            z_score=np.random.uniform(-2, 2),
            crowding_risk=np.random.uniform(0, 1)
        )
    
    async def _analyze_sector_rotation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sector rotation signals"""
        sectors = ['Technology', 'Healthcare', 'Financials', 'Consumer', 
                   'Energy', 'Industrials', 'Materials', 'Utilities']
        
        rotation_signals = {}
        for sector in sectors:
            rotation_signals[sector] = {
                'momentum': np.random.uniform(-1, 1),
                'relative_strength': np.random.uniform(0.8, 1.2),
                'signal': 'overweight' if np.random.random() > 0.5 else 'underweight'
            }
        
        return rotation_signals
    
    async def _discover_alpha_opportunities(self, data: Dict[str, Any]) -> List[Dict]:
        """Discover potential alpha opportunities"""
        opportunities = []
        
        # This would involve sophisticated screening in production
        # Placeholder for demonstration
        
        return opportunities
    
    async def _analyze_macro_conditions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze macroeconomic conditions"""
        return {
            'gdp_growth': 'moderate',
            'inflation': 'elevated',
            'interest_rates': 'rising',
            'credit_conditions': 'tightening',
            'overall_assessment': 'cautious'
        }
    
    async def _detect_crowding(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Detect overall crowding risks"""
        return await self._detect_factor_crowding(data)
    
    async def generate_candidates(
        self, 
        data: Dict[str, Any], 
        regime: 'MarketRegime'
    ) -> List[Dict]:
        """Generate strategy candidates based on market research"""
        candidates = []
        
        # Generate regime-appropriate candidates
        if regime in [MarketRegime.BULL, MarketRegime.LATE_BULL]:
            candidates.append({
                "id": "momentum_strategy",
                "description": "Momentum-based equity strategy",
                "action": "BUY",
                "expected_return": 0.12
            })
        elif regime in [MarketRegime.BEAR, MarketRegime.CRISIS]:
            candidates.append({
                "id": "defensive_strategy",
                "description": "Defensive positioning with hedges",
                "action": "HEDGE",
                "expected_return": 0.02
            })
        
        return candidates
