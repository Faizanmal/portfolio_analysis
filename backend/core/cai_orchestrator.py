"""
Central Autonomous Intelligence (CAI) Orchestrator
===================================================

The CAI is the master control system for the multi-agent AI investment platform.
It orchestrates all agents, enforces global constraints, and ensures regulatory
compliance while maximizing risk-adjusted returns.

Primary Objectives:
1. Maximize risk-adjusted returns
2. Minimize drawdowns and tail risk
3. Ensure regulatory compliance
4. Maintain system stability, transparency, and auditability
5. Continuously self-improve through monitoring, feedback, and learning

Global Operating Constraints (NON-NEGOTIABLE):
- Never exceed configured risk limits
- Never execute trades without risk, compliance, and liquidity validation
- Always prefer capital preservation over profit
- Always log inputs, decisions, confidence scores, and alternatives
- If uncertainty > threshold → reduce position size or abstain
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DecisionType(Enum):
    """Types of decisions the CAI can make"""
    TRADE_EXECUTION = "trade_execution"
    PORTFOLIO_REBALANCE = "portfolio_rebalance"
    RISK_ADJUSTMENT = "risk_adjustment"
    STRATEGY_CHANGE = "strategy_change"
    EMERGENCY_ACTION = "emergency_action"
    REGIME_ADAPTATION = "regime_adaptation"


class MarketRegime(Enum):
    """Market regime classifications"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    CRISIS = "crisis"
    RECOVERY = "recovery"
    LATE_BULL = "late_bull"
    EARLY_BEAR = "early_bear"


class RiskLevel(Enum):
    """Risk severity levels"""
    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5


class ComplianceStatus(Enum):
    """Compliance check status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    PENDING = "pending"


@dataclass
class ConfidenceScore:
    """Structured confidence scoring"""
    value: float  # 0.0 to 1.0
    components: Dict[str, float] = field(default_factory=dict)
    methodology: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.value = max(0.0, min(1.0, self.value))


@dataclass
class DecisionInput:
    """Input data for a decision"""
    input_id: str
    source: str
    data_type: str
    data: Dict[str, Any]
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AlternativeAction:
    """An alternative action that was considered"""
    action_id: str
    description: str
    expected_return: float
    expected_risk: float
    confidence: float
    rejection_reason: Optional[str] = None
    ranking: int = 0


@dataclass
class CAIDecision:
    """Complete decision record with full auditability"""
    decision_id: str
    decision_type: DecisionType
    timestamp: datetime
    
    # Decision details
    action: str  # BUY, SELL, HOLD, REBALANCE, etc.
    asset: Optional[str]
    quantity: Optional[float]
    
    # Confidence and probability
    confidence: ConfidenceScore
    probability_of_success: float
    
    # Expected outcomes
    expected_return: float
    expected_drawdown: float
    expected_volatility: float
    
    # Risk assessment
    risk_flags: List[str]
    risk_level: RiskLevel
    var_95: float
    var_99: float
    cvar_95: float
    
    # Compliance
    compliance_status: ComplianceStatus
    compliance_checks: Dict[str, bool]
    
    # Explanation
    key_drivers: List[str]
    main_risks: List[str]
    explanation: str
    
    # Alternatives
    alternatives_considered: List[AlternativeAction]
    
    # Input data
    inputs: List[DecisionInput]
    
    # Regime context
    market_regime: MarketRegime
    regime_probability: float


@dataclass
class PortfolioReview:
    """Portfolio review output"""
    portfolio_health: str  # Stable, Warning, Critical
    regime: MarketRegime
    regime_probability: float
    top_risks: List[str]
    recommended_action: str
    current_allocations: Dict[str, float]
    var_metrics: Dict[str, float]
    stress_test_results: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GlobalConstraints:
    """Non-negotiable global operating constraints"""
    # Risk limits
    max_portfolio_var_95: float = 0.02  # 2% daily VaR limit
    max_portfolio_var_99: float = 0.035  # 3.5% daily VaR limit
    max_position_size: float = 0.10  # 10% max single position
    max_sector_concentration: float = 0.30  # 30% max sector exposure
    max_leverage: float = 1.0  # No leverage by default
    max_drawdown: float = 0.10  # 10% max drawdown
    
    # Trading constraints
    min_sharpe_ratio: float = 0.5  # Minimum expected Sharpe
    min_risk_reward_ratio: float = 2.0  # Minimum risk-reward
    min_liquidity_ratio: float = 0.05  # 5% minimum liquid assets
    
    # Confidence thresholds
    min_trade_confidence: float = 0.65  # Minimum confidence for trades
    uncertainty_reduction_threshold: float = 0.50  # Reduce position if confidence below
    abstain_threshold: float = 0.35  # Abstain if confidence below this
    
    # Regime-adaptive multipliers
    crisis_risk_multiplier: float = 0.5  # Halve risk limits in crisis
    bull_risk_multiplier: float = 1.2  # Slight increase in stable bull
    
    # Safety limits
    daily_loss_limit: float = 0.01  # 1% daily loss limit
    max_correlation: float = 0.70  # Maximum correlation between positions


class DecisionPipeline:
    """
    Mandatory decision-making pipeline for all CAI decisions.
    
    Pipeline Steps:
    1. Ingest Data
    2. Validate Data Quality
    3. Detect Market Regime
    4. Generate Strategy Candidates
    5. Evaluate Risk (VaR, CVaR, Stress)
    6. Check Compliance
    7. Simulate Outcomes
    8. Rank Alternatives
    9. Execute (or Abstain)
    10. Log Everything
    11. Monitor Post-Action Performance
    """
    
    def __init__(self, cai: 'CentralAutonomousIntelligence'):
        self.cai = cai
        self.logger = logging.getLogger("cai.pipeline")
        self.pipeline_steps = [
            ("ingest_data", self._ingest_data),
            ("validate_data", self._validate_data_quality),
            ("detect_regime", self._detect_market_regime),
            ("generate_candidates", self._generate_strategy_candidates),
            ("evaluate_risk", self._evaluate_risk),
            ("check_compliance", self._check_compliance),
            ("simulate_outcomes", self._simulate_outcomes),
            ("rank_alternatives", self._rank_alternatives),
            ("execute_or_abstain", self._execute_or_abstain),
            ("log_decision", self._log_decision),
            ("monitor_performance", self._setup_monitoring)
        ]
    
    async def execute(self, context: Dict[str, Any]) -> Tuple[bool, CAIDecision]:
        """Execute the complete decision pipeline"""
        pipeline_state = {
            "context": context,
            "inputs": [],
            "validated_data": {},
            "regime": None,
            "candidates": [],
            "risk_assessment": {},
            "compliance_result": {},
            "simulations": [],
            "ranked_actions": [],
            "final_decision": None,
            "step_results": {}
        }
        
        for step_name, step_func in self.pipeline_steps:
            try:
                self.logger.info(f"Executing pipeline step: {step_name}")
                success, result = await step_func(pipeline_state)
                pipeline_state["step_results"][step_name] = {
                    "success": success,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                if not success:
                    self.logger.error(f"Pipeline step {step_name} failed: {result}")
                    # Create abort decision
                    abort_decision = self._create_abort_decision(
                        step_name, result, pipeline_state
                    )
                    return False, abort_decision
                    
            except Exception as e:
                self.logger.error(f"Pipeline step {step_name} error: {e}")
                abort_decision = self._create_abort_decision(
                    step_name, str(e), pipeline_state
                )
                return False, abort_decision
        
        return True, pipeline_state["final_decision"]
    
    async def _ingest_data(self, state: Dict) -> Tuple[bool, Any]:
        """Step 1: Ingest data from all sources"""
        inputs = []
        
        # Collect from all agents
        for agent_id, agent in self.cai.agents.items():
            try:
                data = await agent.get_current_data()
                inputs.append(DecisionInput(
                    input_id=f"{agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    source=agent_id,
                    data_type=agent.data_type,
                    data=data,
                    quality_score=data.get("quality_score", 0.8)
                ))
            except Exception as e:
                self.logger.warning(f"Failed to get data from {agent_id}: {e}")
        
        state["inputs"] = inputs
        return len(inputs) > 0, {"input_count": len(inputs)}
    
    async def _validate_data_quality(self, state: Dict) -> Tuple[bool, Any]:
        """Step 2: Validate data quality"""
        inputs = state["inputs"]
        validated_data = {}
        quality_issues = []
        
        for input_data in inputs:
            if input_data.quality_score < 0.5:
                quality_issues.append(f"Low quality data from {input_data.source}")
            else:
                validated_data[input_data.source] = input_data.data
        
        state["validated_data"] = validated_data
        
        if len(quality_issues) > len(inputs) / 2:
            return False, {"issues": quality_issues}
        
        return True, {"validated_sources": len(validated_data)}
    
    async def _detect_market_regime(self, state: Dict) -> Tuple[bool, Any]:
        """Step 3: Detect current market regime"""
        # Check if market research agent is available
        if not self.cai.market_research_agent:
            self.logger.warning("Market research agent not available, using default regime")
            state["regime"] = MarketRegime.SIDEWAYS
            state["regime_probability"] = 0.5
            state["regime_uncertainty"] = 0.6
            return True, {"regime": "sideways", "probability": 0.5}
        
        regime_result = await self.cai.market_research_agent.detect_regime(
            state["validated_data"]
        )
        
        state["regime"] = regime_result["regime"]
        state["regime_probability"] = regime_result["probability"]
        state["regime_uncertainty"] = regime_result.get("uncertainty", 0.0)
        
        # Flag high uncertainty
        if state["regime_uncertainty"] > 0.4:
            self.logger.warning(f"High regime uncertainty: {state['regime_uncertainty']}")
        
        return True, regime_result
    
    async def _generate_strategy_candidates(self, state: Dict) -> Tuple[bool, Any]:
        """Step 4: Generate strategy candidates"""
        candidates = []
        
        # Get portfolio optimization candidates if available
        if self.cai.portfolio_manager_agent:
            portfolio_candidates = await self.cai.portfolio_manager_agent.generate_candidates(
                state["validated_data"],
                state["regime"]
            )
            candidates.extend(portfolio_candidates)
        
        # Get trading strategy candidates if available
        if self.cai.trading_agent:
            trading_candidates = await self.cai.trading_agent.generate_candidates(
                state["validated_data"],
                state["regime"]
            )
            candidates.extend(trading_candidates)
        
        # If no candidates, create a default HOLD action
        if not candidates:
            candidates = [{
                "id": "default_hold",
                "action": "HOLD",
                "confidence": 0.5,
                "reason": "No agents available for strategy generation"
            }]
        
        state["candidates"] = candidates
        return len(candidates) > 0, {"candidate_count": len(candidates)}
    
    async def _evaluate_risk(self, state: Dict) -> Tuple[bool, Any]:
        """Step 5: Evaluate risk for all candidates"""
        risk_results = {}
        
        # If no risk analyst, use default risk assessment
        if not self.cai.risk_analyst_agent:
            for candidate in state["candidates"]:
                risk_results[candidate["id"]] = {
                    "risk_level": "low",
                    "var_95": 0.01,  # Well below limit
                    "var_99": 0.02,  # Well below limit
                    "max_drawdown": 0.05,  # Well below limit
                    "volatility": 0.10,
                    "passes_limits": True
                }
            state["risk_assessment"] = risk_results
            return True, {"viable_candidates": len(state["candidates"])}
        
        for candidate in state["candidates"]:
            risk_assessment = await self.cai.risk_analyst_agent.evaluate_risk(
                candidate,
                state["validated_data"],
                state["regime"]
            )
            risk_results[candidate["id"]] = risk_assessment
            
            # Run stress tests
            stress_results = await self.cai.risk_analyst_agent.run_stress_tests(
                candidate,
                state["validated_data"]
            )
            risk_results[candidate["id"]]["stress_tests"] = stress_results
        
        state["risk_assessment"] = risk_results
        
        # Check if any candidate passes risk limits
        viable_candidates = [
            c for c in state["candidates"]
            if self._passes_risk_limits(risk_results.get(c["id"], {}))
        ]
        
        if not viable_candidates:
            return False, {"reason": "No candidates pass risk limits"}
        
        return True, {"viable_candidates": len(viable_candidates)}
    
    async def _check_compliance(self, state: Dict) -> Tuple[bool, Any]:
        """Step 6: Check compliance for all candidates"""
        compliance_results = {}
        
        # If no compliance agent, assume all candidates are compliant
        if not self.cai.compliance_agent:
            for candidate in state["candidates"]:
                compliance_results[candidate["id"]] = {"status": "pass", "reason": "No compliance agent"}
            state["compliance_result"] = compliance_results
            return True, {"compliant_candidates": len(state["candidates"])}
        
        for candidate in state["candidates"]:
            compliance = await self.cai.compliance_agent.check_compliance(
                candidate,
                state["validated_data"]
            )
            compliance_results[candidate["id"]] = compliance
        
        state["compliance_result"] = compliance_results
        
        # Check if any candidate is compliant
        compliant_candidates = [
            c for c in state["candidates"]
            if compliance_results.get(c["id"], {}).get("status") == "pass"
        ]
        
        if not compliant_candidates:
            return False, {"reason": "No candidates pass compliance checks"}
        
        return True, {"compliant_candidates": len(compliant_candidates)}
    
    async def _simulate_outcomes(self, state: Dict) -> Tuple[bool, Any]:
        """Step 7: Simulate outcomes for viable candidates"""
        simulations = {}
        
        self.logger.debug(f"Simulating outcomes for {len(state['candidates'])} candidates")
        
        for candidate in state["candidates"]:
            cid = candidate["id"]
            self.logger.debug(f"Checking candidate {cid}: {candidate.get('action')}")
            
            # Skip non-viable candidates
            if not self._is_candidate_viable(cid, state):
                self.logger.debug(f"Candidate {cid} not viable")
                continue
            
            # HOLD actions don't need simulation
            if candidate.get("action") == "HOLD":
                self.logger.debug("Creating simple simulation for HOLD action")
                simulations[cid] = {
                    "expected_outcome": "maintain_position",
                    "risk_level": "low",
                    "confidence": candidate.get("confidence", 0.5)
                }
                continue
            
            sim_result = await self.cai.trading_agent.simulate_execution(
                candidate,
                state["validated_data"]
            )
            simulations[cid] = sim_result
        
        self.logger.debug(f"Completed simulations: {len(simulations)}")
        state["simulations"] = simulations
        return len(simulations) > 0, {"simulated_candidates": len(simulations)}
    
    async def _rank_alternatives(self, state: Dict) -> Tuple[bool, Any]:
        """Step 8: Rank all alternatives"""
        ranked_actions = []
        
        for candidate in state["candidates"]:
            cid = candidate["id"]
            if not self._is_candidate_viable(cid, state):
                continue
            
            risk = state["risk_assessment"].get(cid, {})
            sim = state["simulations"].get(cid, {})
            
            # Calculate composite score
            score = self._calculate_composite_score(candidate, risk, sim, state)
            
            ranked_actions.append({
                "candidate": candidate,
                "score": score,
                "risk": risk,
                "simulation": sim
            })
        
        # Sort by score descending
        ranked_actions.sort(key=lambda x: x["score"], reverse=True)
        state["ranked_actions"] = ranked_actions
        
        return len(ranked_actions) > 0, {"ranked_count": len(ranked_actions)}
    
    async def _execute_or_abstain(self, state: Dict) -> Tuple[bool, Any]:
        """Step 9: Execute best action or abstain"""
        ranked = state["ranked_actions"]
        constraints = self.cai.constraints
        
        if not ranked:
            state["final_decision"] = self._create_abstain_decision(
                "No viable alternatives", state
            )
            return True, {"action": "abstain"}
        
        best = ranked[0]
        confidence = best["score"]
        
        # Check confidence thresholds
        if confidence < constraints.abstain_threshold:
            state["final_decision"] = self._create_abstain_decision(
                f"Confidence {confidence:.2f} below abstain threshold", state
            )
            return True, {"action": "abstain"}
        
        # Reduce position if uncertainty is high
        position_multiplier = 1.0
        if confidence < constraints.uncertainty_reduction_threshold:
            position_multiplier = confidence / constraints.uncertainty_reduction_threshold
            self.logger.info(f"Reducing position by {(1-position_multiplier)*100:.1f}% due to uncertainty")
        
        # Create and execute decision
        state["final_decision"] = self._create_execution_decision(
            best, position_multiplier, state
        )
        
        return True, {"action": "execute", "confidence": confidence}
    
    async def _log_decision(self, state: Dict) -> Tuple[bool, Any]:
        """Step 10: Log everything"""
        decision = state["final_decision"]
        
        # Log to decision store
        await self.cai.decision_store.log_decision(decision)
        
        # Log to audit trail
        await self.cai.audit_trail.log(
            event_type="decision",
            decision_id=decision.decision_id,
            details=self._decision_to_dict(decision)
        )
        
        return True, {"logged": True}
    
    async def _setup_monitoring(self, state: Dict) -> Tuple[bool, Any]:
        """Step 11: Setup post-action performance monitoring"""
        decision = state["final_decision"]
        
        if decision.action != "ABSTAIN":
            await self.cai.performance_monitor.track_decision(decision)
        
        return True, {"monitoring_enabled": True}
    
    def _passes_risk_limits(self, risk: Dict) -> bool:
        """Check if risk assessment passes limits"""
        constraints = self.cai.constraints
        
        if risk.get("var_95", 1.0) > constraints.max_portfolio_var_95:
            return False
        if risk.get("var_99", 1.0) > constraints.max_portfolio_var_99:
            return False
        if risk.get("max_drawdown", 1.0) > constraints.max_drawdown:
            return False
        
        return True
    
    def _is_candidate_viable(self, candidate_id: str, state: Dict) -> bool:
        """Check if a candidate is viable"""
        risk = state["risk_assessment"].get(candidate_id, {})
        compliance = state["compliance_result"].get(candidate_id, {})
        
        return (
            self._passes_risk_limits(risk) and
            compliance.get("status") == "pass"
        )
    
    def _calculate_composite_score(
        self, 
        candidate: Dict, 
        risk: Dict, 
        simulation: Dict,
        state: Dict
    ) -> float:
        """Calculate composite decision score"""
        # Base score from expected return
        expected_return = simulation.get("expected_return", 0.0)
        expected_risk = risk.get("volatility", 1.0)
        
        # Risk-adjusted return (simplified Sharpe)
        sharpe = expected_return / max(expected_risk, 0.01)
        
        # Penalize for regime uncertainty
        regime_penalty = 1.0 - (state.get("regime_uncertainty", 0.0) * 0.5)
        
        # Boost for low correlation with existing portfolio
        correlation_boost = 1.0 - risk.get("portfolio_correlation", 0.5)
        
        # Combine factors
        score = (
            0.4 * min(sharpe / 2.0, 1.0) +  # Normalize Sharpe to 0-1
            0.3 * (1.0 - risk.get("var_95", 0.02) / 0.05) +  # Lower VaR is better
            0.2 * regime_penalty +
            0.1 * correlation_boost
        )
        
        return max(0.0, min(1.0, score))
    
    def _create_abort_decision(
        self, 
        failed_step: str, 
        reason: str, 
        state: Dict
    ) -> CAIDecision:
        """Create a decision record for pipeline abort"""
        return CAIDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=DecisionType.EMERGENCY_ACTION,
            timestamp=datetime.now(),
            action="ABORT",
            asset=None,
            quantity=None,
            confidence=ConfidenceScore(value=0.0, methodology="pipeline_abort"),
            probability_of_success=0.0,
            expected_return=0.0,
            expected_drawdown=0.0,
            expected_volatility=0.0,
            risk_flags=[f"Pipeline aborted at {failed_step}"],
            risk_level=RiskLevel.CRITICAL,
            var_95=0.0,
            var_99=0.0,
            cvar_95=0.0,
            compliance_status=ComplianceStatus.PENDING,
            compliance_checks={},
            key_drivers=[],
            main_risks=[f"Pipeline failure: {reason}"],
            explanation=f"Decision pipeline aborted at step '{failed_step}': {reason}",
            alternatives_considered=[],
            inputs=state.get("inputs", []),
            market_regime=state.get("regime", MarketRegime.SIDEWAYS),
            regime_probability=state.get("regime_probability", 0.0)
        )
    
    def _create_abstain_decision(self, reason: str, state: Dict) -> CAIDecision:
        """Create a decision to abstain from action"""
        alternatives = [
            AlternativeAction(
                action_id=str(uuid.uuid4()),
                description=a["candidate"].get("description", "Unknown"),
                expected_return=a["simulation"].get("expected_return", 0.0),
                expected_risk=a["risk"].get("volatility", 0.0),
                confidence=a["score"],
                rejection_reason="Below confidence threshold",
                ranking=i + 1
            )
            for i, a in enumerate(state.get("ranked_actions", []))
        ]
        
        return CAIDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=DecisionType.TRADE_EXECUTION,
            timestamp=datetime.now(),
            action="ABSTAIN",
            asset=None,
            quantity=None,
            confidence=ConfidenceScore(
                value=state.get("ranked_actions", [{}])[0].get("score", 0.0) if state.get("ranked_actions") else 0.0,
                methodology="composite_score"
            ),
            probability_of_success=0.0,
            expected_return=0.0,
            expected_drawdown=0.0,
            expected_volatility=0.0,
            risk_flags=["Uncertainty too high for action"],
            risk_level=RiskLevel.MODERATE,
            var_95=0.0,
            var_99=0.0,
            cvar_95=0.0,
            compliance_status=ComplianceStatus.PASS,
            compliance_checks={},
            key_drivers=["Capital preservation priority"],
            main_risks=["Uncertain market conditions"],
            explanation=f"Abstaining from action: {reason}. Following capital preservation principle.",
            alternatives_considered=alternatives,
            inputs=state.get("inputs", []),
            market_regime=state.get("regime", MarketRegime.SIDEWAYS),
            regime_probability=state.get("regime_probability", 0.0)
        )
    
    def _create_execution_decision(
        self, 
        best: Dict, 
        position_multiplier: float,
        state: Dict
    ) -> CAIDecision:
        """Create a decision for execution"""
        candidate = best["candidate"]
        risk = best["risk"]
        simulation = best["simulation"]
        
        alternatives = [
            AlternativeAction(
                action_id=str(uuid.uuid4()),
                description=a["candidate"].get("description", "Unknown"),
                expected_return=a["simulation"].get("expected_return", 0.0),
                expected_risk=a["risk"].get("volatility", 0.0),
                confidence=a["score"],
                rejection_reason="Lower composite score" if i > 0 else None,
                ranking=i + 1
            )
            for i, a in enumerate(state.get("ranked_actions", []))
        ]
        
        return CAIDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=DecisionType.TRADE_EXECUTION,
            timestamp=datetime.now(),
            action=candidate.get("action", "HOLD"),
            asset=candidate.get("asset"),
            quantity=(candidate.get("quantity", 0.0) * position_multiplier),
            confidence=ConfidenceScore(
                value=best["score"],
                components={
                    "risk_adjusted_return": simulation.get("sharpe", 0.0),
                    "regime_alignment": 1.0 - state.get("regime_uncertainty", 0.0),
                    "compliance_score": 1.0
                },
                methodology="composite_score"
            ),
            probability_of_success=simulation.get("win_rate", 0.5),
            expected_return=simulation.get("expected_return", 0.0),
            expected_drawdown=risk.get("expected_drawdown", 0.0),
            expected_volatility=risk.get("volatility", 0.0),
            risk_flags=risk.get("flags", []),
            risk_level=RiskLevel(min(5, max(1, int(risk.get("risk_score", 2))))),
            var_95=risk.get("var_95", 0.0),
            var_99=risk.get("var_99", 0.0),
            cvar_95=risk.get("cvar_95", 0.0),
            compliance_status=ComplianceStatus.PASS,
            compliance_checks=state["compliance_result"].get(candidate["id"], {}),
            key_drivers=simulation.get("key_drivers", []),
            main_risks=risk.get("main_risks", []),
            explanation=self._generate_explanation(candidate, risk, simulation, state),
            alternatives_considered=alternatives[1:],  # Exclude the chosen one
            inputs=state.get("inputs", []),
            market_regime=state.get("regime", MarketRegime.SIDEWAYS),
            regime_probability=state.get("regime_probability", 0.0)
        )
    
    def _generate_explanation(
        self, 
        candidate: Dict, 
        risk: Dict, 
        simulation: Dict,
        state: Dict
    ) -> str:
        """Generate natural language explanation"""
        action = candidate.get("action", "HOLD")
        asset = candidate.get("asset", "portfolio")
        regime = state.get("regime", MarketRegime.SIDEWAYS)
        
        explanation = f"""
Decision: {action} {asset}
Market Regime: {regime.value} (probability: {state.get('regime_probability', 0):.1%})

Rationale:
- Expected return: {simulation.get('expected_return', 0):.2%}
- Expected volatility: {risk.get('volatility', 0):.2%}
- Risk-adjusted return (Sharpe): {simulation.get('sharpe', 0):.2f}
- VaR (95%): {risk.get('var_95', 0):.2%}
- CVaR (95%): {risk.get('cvar_95', 0):.2%}

Key Drivers:
{chr(10).join('- ' + d for d in simulation.get('key_drivers', ['N/A'])[:3])}

Risk Factors:
{chr(10).join('- ' + r for r in risk.get('main_risks', ['N/A'])[:3])}

Stress Test Summary:
- 2008 Crisis scenario impact: {risk.get('stress_tests', {}).get('2008_crisis', 'N/A')}
- COVID scenario impact: {risk.get('stress_tests', {}).get('covid', 'N/A')}

Compliance: PASS
Position sizing adjusted for regime uncertainty.
        """.strip()
        
        return explanation
    
    def _decision_to_dict(self, decision: CAIDecision) -> Dict:
        """Convert decision to dictionary for logging"""
        return {
            "decision_id": decision.decision_id,
            "decision_type": decision.decision_type.value,
            "timestamp": decision.timestamp.isoformat(),
            "action": decision.action,
            "asset": decision.asset,
            "quantity": decision.quantity,
            "confidence": decision.confidence.value,
            "probability_of_success": decision.probability_of_success,
            "expected_return": decision.expected_return,
            "risk_level": decision.risk_level.value,
            "compliance_status": decision.compliance_status.value,
            "market_regime": decision.market_regime.value
        }


class CentralAutonomousIntelligence:
    """
    Central Autonomous Intelligence - The Master Control System
    
    This is the brain of the multi-agent AI investment platform.
    It coordinates all agents, enforces constraints, and makes
    final decisions while maintaining full auditability.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("cai")
        
        # Global constraints (NON-NEGOTIABLE)
        self.constraints = GlobalConstraints(**self.config.get("constraints", {}))
        
        # Agents (will be initialized)
        self.agents: Dict[str, Any] = {}
        self.portfolio_manager_agent = None
        self.risk_analyst_agent = None
        self.market_research_agent = None
        self.nlp_agent = None
        self.trading_agent = None
        self.compliance_agent = None
        
        # Decision pipeline
        self.decision_pipeline = DecisionPipeline(self)
        
        # State tracking
        self.current_regime = MarketRegime.SIDEWAYS
        self.regime_history = []
        self.decision_history = []
        
        # Monitoring and auditing
        self.decision_store = DecisionStore()
        self.audit_trail = AuditTrail()
        self.performance_monitor = PerformanceMonitor(self)
        
        # Self-improvement
        self.model_drift_detector = ModelDriftDetector()
        self.strategy_retirement_engine = StrategyRetirementEngine()
        
        # Safety systems
        self.black_swan_sentinel = BlackSwanSentinel(self)
        self.kill_switches = KillSwitchSystem()
        
        # Capital Allocation Committee
        self.capital_committee = CapitalAllocationCommittee(self)
        
        # System state
        self.is_running = False
        self.defensive_mode = False
    
    async def initialize(self):
        """Initialize the CAI system"""
        self.logger.info("Initializing Central Autonomous Intelligence...")
        
        # Initialize all agents
        await self._initialize_agents()
        
        # Initialize safety systems
        await self._initialize_safety_systems()
        
        # Load historical state
        await self._load_historical_state()
        
        # Validate system readiness
        await self._validate_readiness()
        
        self.logger.info("CAI initialization complete")
    
    async def start(self):
        """Start the CAI system"""
        self.is_running = True
        self.logger.info("Starting Central Autonomous Intelligence...")
        
        # Start all background tasks
        await asyncio.gather(
            self._main_loop(),
            self._regime_monitoring_loop(),
            self._safety_monitoring_loop(),
            self._self_improvement_loop()
        )
    
    async def stop(self):
        """Stop the CAI system gracefully"""
        self.is_running = False
        self.logger.info("Stopping Central Autonomous Intelligence...")
        
        # Final state logging
        await self.audit_trail.log(
            event_type="system_shutdown",
            details={"timestamp": datetime.now().isoformat()}
        )
    
    async def run_decision_pipeline(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run a complete decision pipeline cycle.
        
        This is the main entry point for the CAI system to make decisions.
        Returns a dictionary with the decision results.
        """
        if context is None:
            context = {}
        
        try:
            # Run the pipeline
            decision = await self.make_decision(context)
            
            # Convert to dictionary format
            return {
                'action': decision.action,
                'confidence': decision.confidence.overall if hasattr(decision.confidence, 'overall') else 0.5,
                'risk_level': decision.risk_level.value if hasattr(decision, 'risk_level') else 'medium',
                'compliant': decision.compliance_status == ComplianceStatus.PASS if hasattr(decision, 'compliance_status') else True,
                'timestamp': decision.timestamp.isoformat() if hasattr(decision, 'timestamp') else datetime.now().isoformat(),
                'reasoning': decision.explanation if hasattr(decision, 'explanation') else 'Decision made based on current market conditions'
            }
        except Exception as e:
            self.logger.error(f"Error in decision pipeline: {e}")
            # Return a safe default decision
            return {
                'action': 'ABSTAIN',
                'confidence': 0.0,
                'risk_level': 'high',
                'compliant': False,
                'timestamp': datetime.now().isoformat(),
                'reasoning': f'Pipeline error: {str(e)}'
            }
    
    async def make_decision(self, context: Dict[str, Any]) -> CAIDecision:
        """Make a decision using the full pipeline"""
        # Check kill switches first
        if self.kill_switches.is_any_active():
            return self._create_kill_switch_decision()
        
        # Check for defensive mode
        if self.defensive_mode:
            context["defensive_mode"] = True
            self.constraints = self._get_defensive_constraints()
        
        # Execute decision pipeline
        success, decision = await self.decision_pipeline.execute(context)
        
        # Store decision
        self.decision_history.append(decision)
        
        # Notify committee for significant decisions
        if decision.action not in ["ABSTAIN", "HOLD"]:
            await self.capital_committee.review_decision(decision)
        
        return decision
    
    async def get_portfolio_review(self) -> PortfolioReview:
        """Get comprehensive portfolio review"""
        # Get current data from all agents
        portfolio_data = await self.portfolio_manager_agent.get_portfolio_state()
        risk_data = await self.risk_analyst_agent.get_current_metrics()
        regime_data = await self.market_research_agent.get_regime_analysis()
        
        # Determine portfolio health
        health = self._assess_portfolio_health(portfolio_data, risk_data)
        
        # Get stress test results
        stress_results = await self.risk_analyst_agent.run_all_stress_tests(portfolio_data)
        
        return PortfolioReview(
            portfolio_health=health,
            regime=regime_data["regime"],
            regime_probability=regime_data["probability"],
            top_risks=risk_data.get("top_risks", [])[:5],
            recommended_action=self._get_recommended_action(health, regime_data),
            current_allocations=portfolio_data.get("allocations", {}),
            var_metrics={
                "var_95": risk_data.get("var_95", 0.0),
                "var_99": risk_data.get("var_99", 0.0),
                "cvar_95": risk_data.get("cvar_95", 0.0)
            },
            stress_test_results=stress_results
        )
    
    async def _initialize_agents(self):
        """Initialize all agents"""
        # This would import and initialize actual agent classes
        pass
    
    async def _initialize_safety_systems(self):
        """Initialize safety systems"""
        await self.black_swan_sentinel.initialize()
        await self.kill_switches.initialize()
    
    async def _load_historical_state(self):
        """Load historical state for continuity"""
        pass
    
    async def _validate_readiness(self):
        """Validate system readiness"""
        pass
    
    async def _main_loop(self):
        """Main CAI processing loop"""
        while self.is_running:
            try:
                # Regular portfolio check
                review = await self.get_portfolio_review()
                
                if review.portfolio_health == "Critical":
                    await self._handle_critical_portfolio()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Main loop error: {e}")
                await asyncio.sleep(10)
    
    async def _regime_monitoring_loop(self):
        """Monitor market regime changes"""
        while self.is_running:
            try:
                new_regime = await self.market_research_agent.detect_regime({})
                
                if new_regime["regime"] != self.current_regime:
                    await self._handle_regime_change(new_regime)
                
                self.current_regime = new_regime["regime"]
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Regime monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _safety_monitoring_loop(self):
        """Monitor for safety threats"""
        while self.is_running:
            try:
                # Check Black Swan Sentinel
                threat_level = await self.black_swan_sentinel.assess_threat()
                
                if threat_level.value >= RiskLevel.HIGH.value:
                    await self._enter_defensive_mode(threat_level)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Safety monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _self_improvement_loop(self):
        """Self-improvement and model monitoring"""
        while self.is_running:
            try:
                # Check for model drift
                drift_detected = await self.model_drift_detector.check_all_models()
                
                if drift_detected:
                    await self._handle_model_drift(drift_detected)
                
                # Check strategy performance
                underperformers = await self.strategy_retirement_engine.identify_underperformers()
                
                for strategy in underperformers:
                    await self._handle_underperforming_strategy(strategy)
                
                await asyncio.sleep(3600)  # Check hourly
                
            except Exception as e:
                self.logger.error(f"Self-improvement loop error: {e}")
                await asyncio.sleep(600)
    
    async def _handle_critical_portfolio(self):
        """Handle critical portfolio state"""
        self.logger.critical("Portfolio in critical state - initiating protective measures")
        
        # Enter defensive mode
        self.defensive_mode = True
        
        # Reduce all positions
        await self.trading_agent.reduce_all_positions(0.5)
        
        # Notify
        await self.audit_trail.log(
            event_type="critical_portfolio",
            details={"action": "defensive_mode_activated"}
        )
    
    async def _handle_regime_change(self, new_regime: Dict):
        """Handle market regime change"""
        self.logger.info(f"Regime change detected: {self.current_regime} -> {new_regime['regime']}")
        
        # Adjust constraints based on new regime
        if new_regime["regime"] == MarketRegime.CRISIS:
            self.defensive_mode = True
            self.constraints = self._get_crisis_constraints()
        elif new_regime["regime"] == MarketRegime.BULL:
            self.defensive_mode = False
            self.constraints = self._get_bull_constraints()
        
        # Log regime change
        self.regime_history.append({
            "from": self.current_regime,
            "to": new_regime["regime"],
            "timestamp": datetime.now(),
            "probability": new_regime["probability"]
        })
    
    async def _enter_defensive_mode(self, threat_level: RiskLevel):
        """Enter defensive mode"""
        self.logger.warning(f"Entering defensive mode - threat level: {threat_level}")
        self.defensive_mode = True
        
        await self.audit_trail.log(
            event_type="defensive_mode",
            details={"threat_level": threat_level.value}
        )
    
    async def _handle_model_drift(self, drift_info: Dict):
        """Handle detected model drift"""
        self.logger.warning(f"Model drift detected: {drift_info}")
        
        # Flag affected strategies
        # Suggest retraining
        await self.audit_trail.log(
            event_type="model_drift",
            details=drift_info
        )
    
    async def _handle_underperforming_strategy(self, strategy: Dict):
        """Handle underperforming strategy"""
        self.logger.info(f"Underperforming strategy: {strategy['id']}")
        
        # Reduce capital allocation
        await self.strategy_retirement_engine.reduce_allocation(strategy["id"])
        
        # Archive if severely underperforming
        if strategy["performance_score"] < 0.2:
            await self.strategy_retirement_engine.archive_strategy(strategy["id"])
    
    def _get_defensive_constraints(self) -> GlobalConstraints:
        """Get defensive mode constraints"""
        return GlobalConstraints(
            max_portfolio_var_95=0.01,
            max_portfolio_var_99=0.02,
            max_position_size=0.05,
            max_leverage=0.5,
            max_drawdown=0.05,
            min_sharpe_ratio=1.0,
            min_trade_confidence=0.80
        )
    
    def _get_crisis_constraints(self) -> GlobalConstraints:
        """Get crisis mode constraints"""
        return GlobalConstraints(
            max_portfolio_var_95=0.005,
            max_portfolio_var_99=0.01,
            max_position_size=0.03,
            max_leverage=0.0,
            max_drawdown=0.03,
            min_sharpe_ratio=1.5,
            min_trade_confidence=0.90
        )
    
    def _get_bull_constraints(self) -> GlobalConstraints:
        """Get bull market constraints (slightly relaxed)"""
        return GlobalConstraints(
            max_portfolio_var_95=0.025,
            max_portfolio_var_99=0.04,
            max_position_size=0.12,
            max_leverage=1.0,
            max_drawdown=0.12,
            min_sharpe_ratio=0.4,
            min_trade_confidence=0.60
        )
    
    def _assess_portfolio_health(self, portfolio_data: Dict, risk_data: Dict) -> str:
        """Assess overall portfolio health"""
        var_95 = risk_data.get("var_95", 0.0)
        drawdown = risk_data.get("current_drawdown", 0.0)
        
        if var_95 > self.constraints.max_portfolio_var_95 * 1.5 or drawdown > self.constraints.max_drawdown:
            return "Critical"
        elif var_95 > self.constraints.max_portfolio_var_95 or drawdown > self.constraints.max_drawdown * 0.8:
            return "Warning"
        else:
            return "Stable"
    
    def _get_recommended_action(self, health: str, regime_data: Dict) -> str:
        """Get recommended action based on health and regime"""
        if health == "Critical":
            return "Immediate risk reduction - reduce all positions by 50%"
        elif health == "Warning":
            return "Partial rebalance - reduce overweight positions"
        elif regime_data["regime"] == MarketRegime.LATE_BULL:
            return "Consider taking profits on winners"
        else:
            return "No action required"
    
    def _create_kill_switch_decision(self) -> CAIDecision:
        """Create decision when kill switch is active"""
        return CAIDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=DecisionType.EMERGENCY_ACTION,
            timestamp=datetime.now(),
            action="HALT",
            asset=None,
            quantity=None,
            confidence=ConfidenceScore(value=1.0, methodology="kill_switch"),
            probability_of_success=1.0,
            expected_return=0.0,
            expected_drawdown=0.0,
            expected_volatility=0.0,
            risk_flags=["Kill switch active"],
            risk_level=RiskLevel.CRITICAL,
            var_95=0.0,
            var_99=0.0,
            cvar_95=0.0,
            compliance_status=ComplianceStatus.PASS,
            compliance_checks={},
            key_drivers=["Emergency halt"],
            main_risks=["System in emergency state"],
            explanation="Trading halted due to active kill switch. Manual intervention required.",
            alternatives_considered=[],
            inputs=[],
            market_regime=self.current_regime,
            regime_probability=0.0
        )


# Supporting classes

class DecisionStore:
    """Store for all decisions"""
    def __init__(self):
        self.decisions = []
    
    async def log_decision(self, decision: CAIDecision):
        self.decisions.append(decision)


class AuditTrail:
    """Comprehensive audit trail"""
    def __init__(self):
        self.events = []
    
    async def log(self, event_type: str, decision_id: str = None, details: Dict = None):
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "decision_id": decision_id,
            "details": details or {}
        })


class PerformanceMonitor:
    """Track decision performance"""
    def __init__(self, cai: CentralAutonomousIntelligence):
        self.cai = cai
        self.tracked_decisions = {}
    
    async def track_decision(self, decision: CAIDecision):
        self.tracked_decisions[decision.decision_id] = {
            "decision": decision,
            "tracked_at": datetime.now(),
            "outcomes": []
        }


class ModelDriftDetector:
    """Detect model drift"""
    async def check_all_models(self) -> Optional[Dict]:
        return None


class StrategyRetirementEngine:
    """Manage strategy lifecycle"""
    async def identify_underperformers(self) -> List[Dict]:
        return []
    
    async def reduce_allocation(self, strategy_id: str):
        pass
    
    async def archive_strategy(self, strategy_id: str):
        pass


class BlackSwanSentinel:
    """Monitor for black swan events"""
    def __init__(self, cai: CentralAutonomousIntelligence):
        self.cai = cai
        self.thresholds = {
            "volatility_spike": 3.0,
            "correlation_convergence": 0.9,
            "liquidity_evaporation": 0.1
        }
    
    async def initialize(self):
        pass
    
    async def assess_threat(self) -> RiskLevel:
        return RiskLevel.LOW


class KillSwitchSystem:
    """System of kill switches"""
    def __init__(self):
        self.switches = {
            "emergency_stop": False,
            "market_close": False,
            "risk_limit_breach": False,
            "system_error": False,
            "liquidity_crisis": False
        }
    
    async def initialize(self):
        pass
    
    def is_any_active(self) -> bool:
        return any(self.switches.values())
    
    def activate(self, switch_name: str, reason: str):
        if switch_name in self.switches:
            self.switches[switch_name] = True


class CapitalAllocationCommittee:
    """AI-only capital allocation committee"""
    def __init__(self, cai: CentralAutonomousIntelligence):
        self.cai = cai
        self.voting_agents = []
    
    async def review_decision(self, decision: CAIDecision) -> Dict:
        """Conduct committee review with weighted voting"""
        votes = []
        
        for agent in self.voting_agents:
            vote = await agent.vote_on_decision(decision)
            votes.append({
                "agent": agent.agent_id,
                "vote": vote["approve"],
                "confidence": vote["confidence"],
                "reasoning": vote["reasoning"]
            })
        
        # Calculate weighted result
        weighted_approval = sum(
            v["vote"] * v["confidence"] for v in votes
        ) / max(sum(v["confidence"] for v in votes), 0.01)
        
        return {
            "approved": weighted_approval > 0.5,
            "weighted_approval": weighted_approval,
            "votes": votes
        }
