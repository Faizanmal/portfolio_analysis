"""
Safety Guardrails Module
========================

Comprehensive safety system for the CAI platform including:
- Black Swan Sentinel
- Kill Switch System  
- Ethical Guardrails
- Leverage Limits
- Circuit Breakers
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging


class ThreatLevel(Enum):
    """Threat level classification"""
    NONE = 0
    LOW = 1
    ELEVATED = 2
    HIGH = 3
    SEVERE = 4
    CRITICAL = 5


class KillSwitchType(Enum):
    """Types of kill switches"""
    EMERGENCY_STOP = "emergency_stop"
    MARKET_CLOSE = "market_close"
    RISK_LIMIT_BREACH = "risk_limit_breach"
    SYSTEM_ERROR = "system_error"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    CORRELATION_BREAKDOWN = "correlation_breakdown"
    VOLATILITY_SPIKE = "volatility_spike"
    MANUAL_OVERRIDE = "manual_override"


class EthicalViolationType(Enum):
    """Types of ethical violations"""
    OVER_LEVERAGE = "over_leverage"
    MARKET_MANIPULATION = "market_manipulation"
    CONCENTRATED_POSITION = "concentrated_position"
    ILLIQUID_TRADE = "illiquid_trade"
    FRONT_RUNNING = "front_running"
    WASH_TRADING = "wash_trading"


@dataclass
class ThreatAssessment:
    """Assessment of a potential threat"""
    threat_id: str
    threat_type: str
    level: ThreatLevel
    confidence: float
    indicators: Dict[str, float]
    description: str
    recommended_action: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class KillSwitchEvent:
    """Record of a kill switch activation"""
    event_id: str
    switch_type: KillSwitchType
    activated_by: str  # 'system', 'human', 'sentinel'
    reason: str
    timestamp: datetime
    duration: Optional[timedelta] = None
    deactivated_at: Optional[datetime] = None


@dataclass
class EthicalCheck:
    """Result of an ethical guardrail check"""
    check_id: str
    check_type: str
    passed: bool
    violation_type: Optional[EthicalViolationType] = None
    severity: float = 0.0
    description: str = ""
    remediation: Optional[str] = None


class BlackSwanSentinel:
    """
    Monitors for black swan events and extreme market conditions.
    
    Watches for:
    - Volatility term structure inversions
    - Correlation convergence (all assets moving together)
    - Liquidity evaporation
    - Extreme volume spikes
    - Flash crash patterns
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("black_swan_sentinel")
        
        # Thresholds
        self.thresholds = {
            'vix_spike': 40,  # VIX above 40
            'vix_change_1d': 0.40,  # 40% VIX change in a day
            'correlation_convergence': 0.85,  # All correlations above 85%
            'liquidity_ratio': 0.10,  # Bid-ask spread ratio
            'volume_spike_z': 4.0,  # Volume z-score
            'intraday_move': 0.04,  # 4% intraday move
            'term_structure_inversion': -0.05,  # Inverted by 5%
        }
        
        # Historical data for analysis
        self.vix_history: List[float] = []
        self.correlation_history: List[float] = []
        self.liquidity_history: List[float] = []
        
        # Active threats
        self.active_threats: List[ThreatAssessment] = []
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
    
    async def initialize(self):
        """Initialize the sentinel"""
        self.logger.info("Black Swan Sentinel initialized")
    
    async def assess_threat(self, market_data: Dict = None) -> ThreatLevel:
        """
        Assess current threat level from market conditions.
        
        Returns overall threat level based on multiple indicators.
        """
        market_data = market_data or {}
        
        indicators = {}
        
        # Volatility assessment
        indicators['vix_threat'] = await self._assess_volatility_threat(market_data)
        
        # Correlation assessment
        indicators['correlation_threat'] = await self._assess_correlation_threat(market_data)
        
        # Liquidity assessment
        indicators['liquidity_threat'] = await self._assess_liquidity_threat(market_data)
        
        # Volume assessment
        indicators['volume_threat'] = await self._assess_volume_threat(market_data)
        
        # Term structure assessment
        indicators['term_structure_threat'] = await self._assess_term_structure(market_data)
        
        # Calculate overall threat level
        threat_scores = list(indicators.values())
        max_threat = max(t.value for t in threat_scores)
        avg_threat = np.mean([t.value for t in threat_scores])
        
        # Use higher of max and weighted average
        if max_threat >= ThreatLevel.SEVERE.value:
            overall = ThreatLevel.SEVERE
        elif max_threat >= ThreatLevel.HIGH.value or avg_threat >= 2.5:
            overall = ThreatLevel.HIGH
        elif max_threat >= ThreatLevel.ELEVATED.value or avg_threat >= 1.5:
            overall = ThreatLevel.ELEVATED
        elif avg_threat >= 0.5:
            overall = ThreatLevel.LOW
        else:
            overall = ThreatLevel.NONE
        
        # Create threat assessment if elevated
        if overall.value >= ThreatLevel.ELEVATED.value:
            assessment = ThreatAssessment(
                threat_id=f"threat_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                threat_type="market_stress",
                level=overall,
                confidence=0.8,
                indicators={k: v.value for k, v in indicators.items()},
                description=self._generate_threat_description(indicators),
                recommended_action=self._get_recommended_action(overall)
            )
            self.active_threats.append(assessment)
            
            # Trigger callbacks
            for callback in self.alert_callbacks:
                await callback(assessment)
        
        return overall
    
    async def _assess_volatility_threat(self, data: Dict) -> ThreatLevel:
        """Assess threat from volatility indicators"""
        vix = data.get('vix', 20)
        vix_change = data.get('vix_change_1d', 0)
        
        if vix > self.thresholds['vix_spike'] or vix_change > self.thresholds['vix_change_1d']:
            return ThreatLevel.CRITICAL
        elif vix > 30 or vix_change > 0.25:
            return ThreatLevel.HIGH
        elif vix > 25 or vix_change > 0.15:
            return ThreatLevel.ELEVATED
        elif vix > 20:
            return ThreatLevel.LOW
        return ThreatLevel.NONE
    
    async def _assess_correlation_threat(self, data: Dict) -> ThreatLevel:
        """Assess threat from correlation convergence"""
        avg_correlation = data.get('avg_correlation', 0.5)
        correlation_change = data.get('correlation_change', 0)
        
        if avg_correlation > self.thresholds['correlation_convergence']:
            return ThreatLevel.SEVERE
        elif avg_correlation > 0.75:
            return ThreatLevel.HIGH
        elif avg_correlation > 0.65 or correlation_change > 0.2:
            return ThreatLevel.ELEVATED
        return ThreatLevel.NONE
    
    async def _assess_liquidity_threat(self, data: Dict) -> ThreatLevel:
        """Assess threat from liquidity conditions"""
        bid_ask_spread = data.get('avg_bid_ask_spread', 0.001)
        market_depth = data.get('market_depth', 1.0)
        
        if bid_ask_spread > 0.05 or market_depth < 0.2:
            return ThreatLevel.CRITICAL
        elif bid_ask_spread > 0.02 or market_depth < 0.4:
            return ThreatLevel.HIGH
        elif bid_ask_spread > 0.01:
            return ThreatLevel.ELEVATED
        return ThreatLevel.NONE
    
    async def _assess_volume_threat(self, data: Dict) -> ThreatLevel:
        """Assess threat from abnormal volume"""
        volume_z_score = data.get('volume_z_score', 0)
        
        if abs(volume_z_score) > self.thresholds['volume_spike_z']:
            return ThreatLevel.HIGH
        elif abs(volume_z_score) > 3.0:
            return ThreatLevel.ELEVATED
        elif abs(volume_z_score) > 2.0:
            return ThreatLevel.LOW
        return ThreatLevel.NONE
    
    async def _assess_term_structure(self, data: Dict) -> ThreatLevel:
        """Assess threat from volatility term structure"""
        term_structure = data.get('vix_term_structure', 1.0)
        
        if term_structure < (1 + self.thresholds['term_structure_inversion']):
            return ThreatLevel.HIGH
        elif term_structure < 0.98:
            return ThreatLevel.ELEVATED
        return ThreatLevel.NONE
    
    def _generate_threat_description(self, indicators: Dict) -> str:
        """Generate human-readable threat description"""
        threats = []
        
        for name, level in indicators.items():
            if level.value >= ThreatLevel.ELEVATED.value:
                threats.append(f"{name.replace('_', ' ').title()}: {level.name}")
        
        return f"Multiple threat indicators elevated: {', '.join(threats)}"
    
    def _get_recommended_action(self, level: ThreatLevel) -> str:
        """Get recommended action for threat level"""
        actions = {
            ThreatLevel.CRITICAL: "IMMEDIATE HALT - Close all positions, move to cash",
            ThreatLevel.SEVERE: "DEFENSIVE MODE - Reduce all positions by 75%",
            ThreatLevel.HIGH: "REDUCE EXPOSURE - Cut positions by 50%",
            ThreatLevel.ELEVATED: "CAUTION - Reduce new positions, tighten stops",
            ThreatLevel.LOW: "MONITOR - Increase monitoring frequency",
            ThreatLevel.NONE: "NORMAL - Continue standard operations"
        }
        return actions.get(level, "UNKNOWN")
    
    def register_alert_callback(self, callback: Callable):
        """Register a callback for threat alerts"""
        self.alert_callbacks.append(callback)


class KillSwitchSystem:
    """
    System of kill switches for emergency trading halts.
    
    Types of kill switches:
    - Emergency stop (manual)
    - Market close
    - Risk limit breach
    - System error
    - Liquidity crisis
    """
    
    def __init__(self):
        self.logger = logging.getLogger("kill_switches")
        
        # Switch states
        self.switches: Dict[KillSwitchType, bool] = {
            switch_type: False for switch_type in KillSwitchType
        }
        
        # Switch history
        self.events: List[KillSwitchEvent] = []
        
        # Callbacks
        self.activation_callbacks: List[Callable] = []
        self.deactivation_callbacks: List[Callable] = []
    
    async def initialize(self):
        """Initialize kill switch system"""
        self.logger.info("Kill switch system initialized")
    
    def is_any_active(self) -> bool:
        """Check if any kill switch is active"""
        return any(self.switches.values())
    
    def get_active_switches(self) -> List[KillSwitchType]:
        """Get list of active kill switches"""
        return [switch for switch, active in self.switches.items() if active]
    
    async def activate(
        self,
        switch_type: KillSwitchType,
        reason: str,
        activated_by: str = "system"
    ):
        """Activate a kill switch"""
        if self.switches[switch_type]:
            self.logger.warning(f"Kill switch {switch_type.value} already active")
            return
        
        self.switches[switch_type] = True
        
        event = KillSwitchEvent(
            event_id=f"ks_{datetime.now().strftime('%Y%m%d%H%M%S')}_{switch_type.value}",
            switch_type=switch_type,
            activated_by=activated_by,
            reason=reason,
            timestamp=datetime.now()
        )
        self.events.append(event)
        
        self.logger.critical(
            f"KILL SWITCH ACTIVATED: {switch_type.value} - {reason}"
        )
        
        # Trigger callbacks
        for callback in self.activation_callbacks:
            await callback(event)
    
    async def deactivate(
        self,
        switch_type: KillSwitchType,
        deactivated_by: str = "system"
    ):
        """Deactivate a kill switch"""
        if not self.switches[switch_type]:
            return
        
        self.switches[switch_type] = False
        
        # Update event record
        for event in reversed(self.events):
            if event.switch_type == switch_type and event.deactivated_at is None:
                event.deactivated_at = datetime.now()
                event.duration = event.deactivated_at - event.timestamp
                break
        
        self.logger.info(f"Kill switch deactivated: {switch_type.value}")
        
        # Trigger callbacks
        for callback in self.deactivation_callbacks:
            await callback(switch_type)
    
    async def emergency_stop(self, reason: str):
        """Activate emergency stop - halts all trading immediately"""
        await self.activate(
            KillSwitchType.EMERGENCY_STOP,
            reason,
            "emergency_system"
        )
    
    def register_activation_callback(self, callback: Callable):
        """Register callback for switch activation"""
        self.activation_callbacks.append(callback)
    
    def register_deactivation_callback(self, callback: Callable):
        """Register callback for switch deactivation"""
        self.deactivation_callbacks.append(callback)


class EthicalGuardrails:
    """
    Ethical and safety guardrails for the trading system.
    
    Prevents:
    - Over-leverage
    - Market manipulation
    - Exploitative behavior
    - Concentrated positions
    - Illiquid trades that could move markets
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("ethical_guardrails")
        
        # Limits
        self.limits = {
            'max_leverage': 1.0,
            'max_position_pct': 0.10,
            'max_market_impact': 0.01,  # 1% of daily volume
            'min_liquidity_ratio': 0.05,
            'max_concentration': 0.25,
            'max_trade_frequency_per_minute': 10,
        }
        
        # Tracking
        self.recent_trades: List[Dict] = []
        self.violations: List[EthicalCheck] = []
    
    async def check_trade(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> EthicalCheck:
        """Run all ethical checks on a proposed trade"""
        checks = []
        
        # Leverage check
        checks.append(await self._check_leverage(trade, portfolio))
        
        # Position concentration check
        checks.append(await self._check_concentration(trade, portfolio))
        
        # Market impact check
        checks.append(await self._check_market_impact(trade, market_data))
        
        # Wash trading check
        checks.append(await self._check_wash_trading(trade))
        
        # Trading frequency check
        checks.append(await self._check_trading_frequency(trade))
        
        # Find the most severe violation
        violations = [c for c in checks if not c.passed]
        
        if violations:
            worst = max(violations, key=lambda x: x.severity)
            self.violations.append(worst)
            return worst
        
        return EthicalCheck(
            check_id=f"eth_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            check_type="all_checks",
            passed=True,
            description="All ethical checks passed"
        )
    
    async def _check_leverage(
        self,
        trade: Dict,
        portfolio: Dict
    ) -> EthicalCheck:
        """Check if trade would exceed leverage limits"""
        current_leverage = portfolio.get('leverage', 1.0)
        trade_leverage_impact = trade.get('leverage_impact', 0)
        new_leverage = current_leverage + trade_leverage_impact
        
        max_leverage = self.limits['max_leverage']
        
        if new_leverage > max_leverage:
            return EthicalCheck(
                check_id=f"lev_{datetime.now().strftime('%H%M%S')}",
                check_type="leverage",
                passed=False,
                violation_type=EthicalViolationType.OVER_LEVERAGE,
                severity=min(1.0, (new_leverage - max_leverage) / max_leverage),
                description=f"Trade would increase leverage to {new_leverage:.2f}x (limit: {max_leverage:.2f}x)",
                remediation="Reduce position size or close existing leveraged positions"
            )
        
        return EthicalCheck(
            check_id=f"lev_{datetime.now().strftime('%H%M%S')}",
            check_type="leverage",
            passed=True
        )
    
    async def _check_concentration(
        self,
        trade: Dict,
        portfolio: Dict
    ) -> EthicalCheck:
        """Check if trade would create excessive concentration"""
        asset = trade.get('asset')
        trade_value = trade.get('value', 0)
        portfolio_value = portfolio.get('total_value', 1)
        
        current_position = portfolio.get('positions', {}).get(asset, {}).get('value', 0)
        new_position_pct = (current_position + trade_value) / portfolio_value
        
        max_concentration = self.limits['max_concentration']
        
        if new_position_pct > max_concentration:
            return EthicalCheck(
                check_id=f"conc_{datetime.now().strftime('%H%M%S')}",
                check_type="concentration",
                passed=False,
                violation_type=EthicalViolationType.CONCENTRATED_POSITION,
                severity=min(1.0, (new_position_pct - max_concentration) / max_concentration),
                description=f"Trade would create {new_position_pct:.1%} concentration (limit: {max_concentration:.1%})",
                remediation="Reduce position size to stay within concentration limits"
            )
        
        return EthicalCheck(
            check_id=f"conc_{datetime.now().strftime('%H%M%S')}",
            check_type="concentration",
            passed=True
        )
    
    async def _check_market_impact(
        self,
        trade: Dict,
        market_data: Dict
    ) -> EthicalCheck:
        """Check if trade would have excessive market impact"""
        trade_size = trade.get('quantity', 0)
        avg_daily_volume = market_data.get('avg_daily_volume', float('inf'))
        
        market_impact = trade_size / avg_daily_volume if avg_daily_volume > 0 else 0
        max_impact = self.limits['max_market_impact']
        
        if market_impact > max_impact:
            return EthicalCheck(
                check_id=f"impact_{datetime.now().strftime('%H%M%S')}",
                check_type="market_impact",
                passed=False,
                violation_type=EthicalViolationType.ILLIQUID_TRADE,
                severity=min(1.0, market_impact / 0.05),
                description=f"Trade represents {market_impact:.1%} of daily volume (limit: {max_impact:.1%})",
                remediation="Split trade across multiple days or reduce size"
            )
        
        return EthicalCheck(
            check_id=f"impact_{datetime.now().strftime('%H%M%S')}",
            check_type="market_impact",
            passed=True
        )
    
    async def _check_wash_trading(self, trade: Dict) -> EthicalCheck:
        """Check for potential wash trading patterns"""
        asset = trade.get('asset')
        action = trade.get('action')
        
        # Check recent trades for opposite action on same asset
        recent_opposite = [
            t for t in self.recent_trades[-10:]
            if t.get('asset') == asset and t.get('action') != action
        ]
        
        if len(recent_opposite) >= 2:
            return EthicalCheck(
                check_id=f"wash_{datetime.now().strftime('%H%M%S')}",
                check_type="wash_trading",
                passed=False,
                violation_type=EthicalViolationType.WASH_TRADING,
                severity=0.7,
                description="Potential wash trading pattern detected",
                remediation="Review trading pattern and wait before executing"
            )
        
        return EthicalCheck(
            check_id=f"wash_{datetime.now().strftime('%H%M%S')}",
            check_type="wash_trading",
            passed=True
        )
    
    async def _check_trading_frequency(self, trade: Dict) -> EthicalCheck:
        """Check for excessive trading frequency"""
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_count = len([
            t for t in self.recent_trades
            if t.get('timestamp', datetime.min) > one_minute_ago
        ])
        
        max_frequency = self.limits['max_trade_frequency_per_minute']
        
        if recent_count >= max_frequency:
            return EthicalCheck(
                check_id=f"freq_{datetime.now().strftime('%H%M%S')}",
                check_type="trading_frequency",
                passed=False,
                violation_type=EthicalViolationType.MARKET_MANIPULATION,
                severity=0.5,
                description=f"Trading frequency ({recent_count}/min) exceeds limit ({max_frequency}/min)",
                remediation="Reduce trading frequency"
            )
        
        return EthicalCheck(
            check_id=f"freq_{datetime.now().strftime('%H%M%S')}",
            check_type="trading_frequency",
            passed=True
        )
    
    def record_trade(self, trade: Dict):
        """Record a trade for pattern analysis"""
        trade['timestamp'] = datetime.now()
        self.recent_trades.append(trade)
        
        # Keep only last 1000 trades
        if len(self.recent_trades) > 1000:
            self.recent_trades = self.recent_trades[-1000:]


class SafetyOrchestrator:
    """
    Orchestrates all safety systems.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("safety")
        
        self.sentinel = BlackSwanSentinel(config)
        self.kill_switches = KillSwitchSystem()
        self.ethical_guardrails = EthicalGuardrails(config)
        
        # Register sentinel alerts to potentially trigger kill switches
        self.sentinel.register_alert_callback(self._handle_threat_alert)
    
    async def initialize(self):
        """Initialize all safety systems"""
        await self.sentinel.initialize()
        await self.kill_switches.initialize()
        self.logger.info("Safety orchestrator initialized")
    
    async def check_trade_safety(
        self,
        trade: Dict,
        portfolio: Dict,
        market_data: Dict
    ) -> Dict[str, Any]:
        """Comprehensive safety check for a trade"""
        
        # Check kill switches first
        if self.kill_switches.is_any_active():
            active = self.kill_switches.get_active_switches()
            return {
                'safe': False,
                'reason': f"Kill switch(es) active: {[s.value for s in active]}",
                'action': 'HALT'
            }
        
        # Check threat level
        threat = await self.sentinel.assess_threat(market_data)
        if threat.value >= ThreatLevel.SEVERE.value:
            return {
                'safe': False,
                'reason': f"Threat level {threat.name} - trading suspended",
                'action': 'HALT'
            }
        
        # Run ethical checks
        ethical_check = await self.ethical_guardrails.check_trade(
            trade, portfolio, market_data
        )
        if not ethical_check.passed:
            return {
                'safe': False,
                'reason': ethical_check.description,
                'violation': ethical_check.violation_type.value if ethical_check.violation_type else None,
                'remediation': ethical_check.remediation,
                'action': 'BLOCK'
            }
        
        # All checks passed
        return {
            'safe': True,
            'threat_level': threat.name,
            'action': 'PROCEED'
        }
    
    async def _handle_threat_alert(self, assessment: ThreatAssessment):
        """Handle threat alerts from sentinel"""
        if assessment.level.value >= ThreatLevel.CRITICAL.value:
            await self.kill_switches.activate(
                KillSwitchType.VOLATILITY_SPIKE,
                f"Black Swan Sentinel: {assessment.description}",
                "sentinel"
            )
        elif assessment.level.value >= ThreatLevel.SEVERE.value:
            await self.kill_switches.activate(
                KillSwitchType.RISK_LIMIT_BREACH,
                f"Elevated threat: {assessment.description}",
                "sentinel"
            )
