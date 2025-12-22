"""
Core CAI System Components

This package contains the core components of the Central Autonomous Intelligence (CAI)
system for autonomous portfolio management.

Modules:
    - cai_orchestrator: Main CAI orchestration and decision pipeline
    - safety_guardrails: Black Swan Sentinel, Kill Switches, Ethical Guardrails
    - explainability: SHAP-based explanations and natural language reports
    - self_improvement: Drift detection, strategy retirement, continuous learning
"""

from core.cai_orchestrator import (
    CentralAutonomousIntelligence,
    CAIDecision,
    ConfidenceScore,
    DecisionInput,
    MarketRegime,
    RiskLevel,
    GlobalConstraints,
    CapitalAllocationCommittee,
    DecisionPipeline,
)

from core.safety_guardrails import (
    SafetyOrchestrator,
    BlackSwanSentinel,
    KillSwitchSystem,
    EthicalGuardrails,
    ThreatLevel,
    KillSwitchType,
)

from core.explainability import (
    ExplainabilityEngine,
    FeatureAttribution,
    DecisionExplanation,
    TradeExplanation,
)

from core.self_improvement import (
    SelfImprovementEngine,
    ModelDriftDetector,
    StrategyRetirementEngine,
    PredictionAccuracyTracker,
)

__all__ = [
    # CAI Orchestrator
    'CentralAutonomousIntelligence',
    'CAIDecision',
    'ConfidenceScore',
    'DecisionInput',
    'MarketRegime',
    'RiskLevel',
    'GlobalConstraints',
    'CapitalAllocationCommittee',
    'DecisionPipeline',
    
    # Safety Guardrails
    'SafetyOrchestrator',
    'BlackSwanSentinel',
    'KillSwitchSystem',
    'EthicalGuardrails',
    'ThreatLevel',
    'KillSwitchType',
    
    # Explainability
    'ExplainabilityEngine',
    'FeatureAttribution',
    'DecisionExplanation',
    'TradeExplanation',
    
    # Self-Improvement
    'SelfImprovementEngine',
    'ModelDriftDetector',
    'StrategyRetirementEngine',
    'PredictionAccuracyTracker',
]
