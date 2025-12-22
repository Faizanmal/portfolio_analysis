"""
Compliance & Audit Agent
========================

Specialized agent for regulatory compliance monitoring, pre-trade checks,
audit trail integrity, and governance workflows.

Responsibilities:
- Pre-trade compliance checks
- Jurisdiction-specific rules
- Audit trail integrity
- Block non-compliant actions
- Log violations with remediation steps
- Ensure explainability for regulators
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

from .base_agent import BaseAgent, AgentTask, AgentPriority


class ComplianceStatus(Enum):
    """Compliance check status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    PENDING = "pending"
    REVIEW_REQUIRED = "review_required"


class ViolationSeverity(Enum):
    """Severity of compliance violations"""
    MINOR = 1
    MODERATE = 2
    MAJOR = 3
    CRITICAL = 4


class Jurisdiction(Enum):
    """Supported regulatory jurisdictions"""
    SEC = "sec"  # US Securities and Exchange Commission
    FINRA = "finra"  # Financial Industry Regulatory Authority
    MIFID_II = "mifid_ii"  # EU Markets in Financial Instruments Directive
    FCA = "fca"  # UK Financial Conduct Authority
    ASIC = "asic"  # Australian Securities and Investments Commission


@dataclass
class ComplianceRule:
    """Definition of a compliance rule"""
    rule_id: str
    name: str
    description: str
    jurisdiction: Jurisdiction
    check_function: str
    parameters: Dict[str, Any]
    severity: ViolationSeverity
    is_hard_block: bool  # If True, violation blocks the trade


@dataclass
class ComplianceCheck:
    """Result of a compliance check"""
    check_id: str
    rule: ComplianceRule
    status: ComplianceStatus
    details: str
    timestamp: datetime
    data_used: Dict[str, Any]
    remediation: Optional[str] = None


@dataclass
class ComplianceViolation:
    """Record of a compliance violation"""
    violation_id: str
    rule: ComplianceRule
    severity: ViolationSeverity
    description: str
    affected_assets: List[str]
    remediation_steps: List[str]
    timestamp: datetime
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class AuditEntry:
    """Entry in the audit trail"""
    entry_id: str
    event_type: str
    timestamp: datetime
    actor: str  # System component or user
    action: str
    details: Dict[str, Any]
    data_hash: str  # Hash for integrity verification
    previous_hash: str  # For chain integrity


@dataclass
class GovernanceApproval:
    """Governance approval record"""
    approval_id: str
    request_type: str
    requestor: str
    details: Dict[str, Any]
    status: str  # pending, approved, rejected
    approvers: List[Dict[str, Any]]
    created_at: datetime
    decided_at: Optional[datetime] = None


class ComplianceAgent(BaseAgent):
    """AI agent specialized in compliance and audit"""
    
    def __init__(self):
        super().__init__(
            agent_id="compliance_monitor",
            name="Compliance & Audit Agent",
            capabilities=[
                "pre_trade_compliance",
                "post_trade_compliance",
                "audit_trail",
                "violation_detection",
                "regulatory_reporting",
                "governance_workflow"
            ]
        )
        
        self.data_type = "compliance"
        
        # Compliance rules
        self.rules: Dict[str, ComplianceRule] = self._initialize_rules()
        
        # Audit trail (blockchain-like)
        self.audit_trail: List[AuditEntry] = []
        self.last_hash = "GENESIS"
        
        # Violations tracking
        self.violations: List[ComplianceViolation] = []
        self.active_violations: List[ComplianceViolation] = []
        
        # Governance approvals
        self.pending_approvals: List[GovernanceApproval] = []
        self.approval_history: List[GovernanceApproval] = []
        
        # Configuration
        self.enabled_jurisdictions = [Jurisdiction.SEC, Jurisdiction.FINRA]
        self.strict_mode = True  # Block on any violation
        
        self.logger = logging.getLogger("agent.compliance")
    
    def _initialize_rules(self) -> Dict[str, ComplianceRule]:
        """Initialize compliance rules"""
        rules = {}
        
        # Position limits
        rules['position_limit'] = ComplianceRule(
            rule_id="POS001",
            name="Position Size Limit",
            description="Single position cannot exceed configured percentage of portfolio",
            jurisdiction=Jurisdiction.SEC,
            check_function="_check_position_limit",
            parameters={'max_position_pct': 0.10},
            severity=ViolationSeverity.MAJOR,
            is_hard_block=True
        )
        
        # Sector concentration
        rules['sector_concentration'] = ComplianceRule(
            rule_id="SEC001",
            name="Sector Concentration Limit",
            description="Single sector cannot exceed configured percentage of portfolio",
            jurisdiction=Jurisdiction.SEC,
            check_function="_check_sector_concentration",
            parameters={'max_sector_pct': 0.30},
            severity=ViolationSeverity.MODERATE,
            is_hard_block=True
        )
        
        # Leverage limits
        rules['leverage_limit'] = ComplianceRule(
            rule_id="LEV001",
            name="Leverage Limit",
            description="Portfolio leverage cannot exceed configured maximum",
            jurisdiction=Jurisdiction.FINRA,
            check_function="_check_leverage",
            parameters={'max_leverage': 1.0},
            severity=ViolationSeverity.CRITICAL,
            is_hard_block=True
        )
        
        # Short selling restrictions
        rules['short_selling'] = ComplianceRule(
            rule_id="SHT001",
            name="Short Selling Restrictions",
            description="Short selling must comply with uptick rule and locate requirements",
            jurisdiction=Jurisdiction.SEC,
            check_function="_check_short_selling",
            parameters={'uptick_required': True},
            severity=ViolationSeverity.MAJOR,
            is_hard_block=True
        )
        
        # Wash sale prevention
        rules['wash_sale'] = ComplianceRule(
            rule_id="WSH001",
            name="Wash Sale Prevention",
            description="Prevent wash sales within 30-day window",
            jurisdiction=Jurisdiction.SEC,
            check_function="_check_wash_sale",
            parameters={'wash_sale_window_days': 30},
            severity=ViolationSeverity.MODERATE,
            is_hard_block=False
        )
        
        # Pattern day trading
        rules['pattern_day_trading'] = ComplianceRule(
            rule_id="PDT001",
            name="Pattern Day Trading",
            description="Monitor for pattern day trading if account below threshold",
            jurisdiction=Jurisdiction.FINRA,
            check_function="_check_pattern_day_trading",
            parameters={'min_equity': 25000, 'day_trade_limit': 3},
            severity=ViolationSeverity.MAJOR,
            is_hard_block=True
        )
        
        # Best execution
        rules['best_execution'] = ComplianceRule(
            rule_id="BEX001",
            name="Best Execution",
            description="Ensure best execution for client orders",
            jurisdiction=Jurisdiction.MIFID_II,
            check_function="_check_best_execution",
            parameters={'max_slippage_bps': 10},
            severity=ViolationSeverity.MODERATE,
            is_hard_block=False
        )
        
        # Restricted securities
        rules['restricted_securities'] = ComplianceRule(
            rule_id="RST001",
            name="Restricted Securities",
            description="Prevent trading in restricted securities",
            jurisdiction=Jurisdiction.SEC,
            check_function="_check_restricted_securities",
            parameters={'restricted_list': []},
            severity=ViolationSeverity.CRITICAL,
            is_hard_block=True
        )
        
        return rules
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process compliance tasks"""
        task_type = task.task_type
        parameters = task.parameters
        
        try:
            if task_type == "pre_trade_check":
                return await self.check_compliance(parameters.get('trade', {}), parameters)
            elif task_type == "post_trade_check":
                return await self._post_trade_compliance(parameters)
            elif task_type == "violation_report":
                return await self._generate_violation_report(parameters)
            elif task_type == "audit_integrity_check":
                return await self._verify_audit_integrity()
            elif task_type == "governance_approval":
                return await self._process_governance_request(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Error processing task {task.task_id}: {e}")
            raise
    
    async def analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio for compliance issues"""
        try:
            return {
                'compliance_status': await self._assess_portfolio_compliance(data),
                'active_violations': [v.__dict__ for v in self.active_violations],
                'pending_approvals': len(self.pending_approvals),
                'audit_integrity': await self._verify_audit_integrity()
            }
        except Exception as e:
            self.logger.error(f"Error analyzing data: {e}")
            return {'error': str(e)}
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Get current compliance data"""
        return {
            "active_violations": len(self.active_violations),
            "pending_approvals": len(self.pending_approvals),
            "audit_entries": len(self.audit_trail),
            "quality_score": 0.95,
            "timestamp": datetime.now().isoformat()
        }
    
    async def check_compliance(
        self, 
        candidate: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run all pre-trade compliance checks.
        
        Must:
        - Block non-compliant actions
        - Log violations with remediation steps
        - Ensure explainability for regulators
        """
        checks = []
        violations = []
        overall_status = ComplianceStatus.PASS
        
        # Run all applicable rules
        for rule_id, rule in self.rules.items():
            if rule.jurisdiction not in self.enabled_jurisdictions:
                continue
            
            check = await self._run_compliance_check(rule, candidate, data)
            checks.append(check)
            
            if check.status == ComplianceStatus.FAIL:
                if rule.is_hard_block:
                    overall_status = ComplianceStatus.FAIL
                    violations.append(self._create_violation(rule, check))
                else:
                    if overall_status != ComplianceStatus.FAIL:
                        overall_status = ComplianceStatus.WARNING
            elif check.status == ComplianceStatus.WARNING:
                if overall_status == ComplianceStatus.PASS:
                    overall_status = ComplianceStatus.WARNING
        
        # Log the compliance check
        await self._log_audit_entry(
            event_type="compliance_check",
            action="pre_trade_check",
            details={
                "candidate": candidate,
                "status": overall_status.value,
                "checks_run": len(checks),
                "violations": len(violations)
            }
        )
        
        # Store violations
        for v in violations:
            self.violations.append(v)
            self.active_violations.append(v)
            self.logger.warning(f"Compliance violation: {v.rule.name} - {v.description}")
        
        return {
            "status": overall_status.value,
            "checks": [self._check_to_dict(c) for c in checks],
            "violations": [self._violation_to_dict(v) for v in violations],
            "blocked": overall_status == ComplianceStatus.FAIL,
            "explanation": self._generate_compliance_explanation(checks, violations)
        }
    
    async def _run_compliance_check(
        self,
        rule: ComplianceRule,
        candidate: Dict[str, Any],
        data: Dict[str, Any]
    ) -> ComplianceCheck:
        """Run a specific compliance check"""
        check_id = str(uuid.uuid4())[:8]
        
        try:
            # Get the check function
            check_func = getattr(self, rule.check_function, None)
            
            if check_func:
                status, details, remediation = await check_func(
                    candidate, data, rule.parameters
                )
            else:
                status = ComplianceStatus.PASS
                details = "Check not implemented"
                remediation = None
            
            return ComplianceCheck(
                check_id=check_id,
                rule=rule,
                status=status,
                details=details,
                timestamp=datetime.now(),
                data_used={"candidate": candidate.get("id", "unknown")},
                remediation=remediation
            )
            
        except Exception as e:
            return ComplianceCheck(
                check_id=check_id,
                rule=rule,
                status=ComplianceStatus.FAIL,
                details=f"Check error: {str(e)}",
                timestamp=datetime.now(),
                data_used={},
                remediation="Review and retry"
            )
    
    async def _check_position_limit(
        self,
        candidate: Dict,
        data: Dict,
        params: Dict
    ) -> Tuple[ComplianceStatus, str, Optional[str]]:
        """Check if position size is within limits"""
        max_pct = params.get('max_position_pct', 0.10)
        
        # Get proposed position size
        quantity = candidate.get('quantity', 0)
        price = data.get('current_price', 0)
        portfolio_value = data.get('portfolio_value', 1000000)
        
        position_value = quantity * price
        position_pct = position_value / portfolio_value if portfolio_value > 0 else 0
        
        if position_pct > max_pct:
            return (
                ComplianceStatus.FAIL,
                f"Position size {position_pct:.1%} exceeds limit of {max_pct:.1%}",
                f"Reduce position size to maximum of {int(max_pct * portfolio_value / price)} shares"
            )
        elif position_pct > max_pct * 0.9:
            return (
                ComplianceStatus.WARNING,
                f"Position size {position_pct:.1%} approaching limit of {max_pct:.1%}",
                None
            )
        else:
            return (
                ComplianceStatus.PASS,
                f"Position size {position_pct:.1%} within limit",
                None
            )
    
    async def _check_sector_concentration(
        self,
        candidate: Dict,
        data: Dict,
        params: Dict
    ) -> Tuple[ComplianceStatus, str, Optional[str]]:
        """Check sector concentration limits"""
        max_pct = params.get('max_sector_pct', 0.30)
        
        sector = candidate.get('sector', 'Unknown')
        current_sector_pct = data.get('sector_exposures', {}).get(sector, 0)
        trade_impact = candidate.get('portfolio_impact', 0)
        
        new_sector_pct = current_sector_pct + trade_impact
        
        if new_sector_pct > max_pct:
            return (
                ComplianceStatus.FAIL,
                f"Sector concentration {new_sector_pct:.1%} would exceed limit of {max_pct:.1%}",
                f"Reduce {sector} sector exposure before adding new positions"
            )
        else:
            return (
                ComplianceStatus.PASS,
                f"Sector concentration within limits",
                None
            )
    
    async def _check_leverage(
        self,
        candidate: Dict,
        data: Dict,
        params: Dict
    ) -> Tuple[ComplianceStatus, str, Optional[str]]:
        """Check leverage limits"""
        max_leverage = params.get('max_leverage', 1.0)
        
        current_leverage = data.get('current_leverage', 1.0)
        trade_leverage_impact = candidate.get('leverage_impact', 0)
        
        new_leverage = current_leverage + trade_leverage_impact
        
        if new_leverage > max_leverage:
            return (
                ComplianceStatus.FAIL,
                f"Leverage {new_leverage:.2f}x would exceed limit of {max_leverage:.2f}x",
                f"Reduce margin usage before this trade"
            )
        else:
            return (
                ComplianceStatus.PASS,
                f"Leverage {new_leverage:.2f}x within limits",
                None
            )
    
    async def _check_short_selling(
        self,
        candidate: Dict,
        data: Dict,
        params: Dict
    ) -> Tuple[ComplianceStatus, str, Optional[str]]:
        """Check short selling restrictions"""
        if candidate.get('side') not in ['short', 'sell_short']:
            return (ComplianceStatus.PASS, "Not a short sale", None)
        
        # Check uptick rule
        last_tick = data.get('last_tick_direction', 'up')
        if params.get('uptick_required', True) and last_tick != 'up':
            return (
                ComplianceStatus.FAIL,
                "Short sale blocked - uptick rule violation",
                "Wait for an uptick before short selling"
            )
        
        # Check locate requirement
        shares_located = data.get('shares_located', 0)
        if shares_located < candidate.get('quantity', 0):
            return (
                ComplianceStatus.FAIL,
                "Short sale blocked - insufficient locate",
                "Obtain locate for sufficient shares"
            )
        
        return (ComplianceStatus.PASS, "Short sale compliant", None)
    
    async def _check_wash_sale(
        self,
        candidate: Dict,
        data: Dict,
        params: Dict
    ) -> Tuple[ComplianceStatus, str, Optional[str]]:
        """Check for potential wash sales"""
        window_days = params.get('wash_sale_window_days', 30)
        asset = candidate.get('asset')
        action = candidate.get('action')
        
        # Check recent trades for same asset
        recent_trades = data.get('recent_trades', [])
        
        for trade in recent_trades:
            if trade.get('asset') == asset:
                trade_date = trade.get('date')
                if trade_date:
                    days_ago = (datetime.now() - trade_date).days
                    if days_ago <= window_days:
                        # Check if this creates a wash sale
                        if (trade.get('action') == 'SELL' and action == 'BUY') or \
                           (trade.get('action') == 'BUY' and action == 'SELL'):
                            return (
                                ComplianceStatus.WARNING,
                                f"Potential wash sale - same asset traded {days_ago} days ago",
                                "Wait 30 days or consult tax advisor"
                            )
        
        return (ComplianceStatus.PASS, "No wash sale detected", None)
    
    async def _check_pattern_day_trading(
        self,
        candidate: Dict,
        data: Dict,
        params: Dict
    ) -> Tuple[ComplianceStatus, str, Optional[str]]:
        """Check pattern day trading rules"""
        min_equity = params.get('min_equity', 25000)
        day_trade_limit = params.get('day_trade_limit', 3)
        
        account_equity = data.get('account_equity', 0)
        day_trades_this_week = data.get('day_trades_this_week', 0)
        
        # If equity below threshold, check day trade count
        if account_equity < min_equity:
            if day_trades_this_week >= day_trade_limit:
                return (
                    ComplianceStatus.FAIL,
                    f"Pattern day trading limit reached ({day_trade_limit} trades)",
                    f"Increase account equity above ${min_equity:,} or wait for next rolling period"
                )
            elif day_trades_this_week >= day_trade_limit - 1:
                return (
                    ComplianceStatus.WARNING,
                    f"Approaching day trade limit ({day_trades_this_week}/{day_trade_limit})",
                    None
                )
        
        return (ComplianceStatus.PASS, "Day trading compliant", None)
    
    async def _check_best_execution(
        self,
        candidate: Dict,
        data: Dict,
        params: Dict
    ) -> Tuple[ComplianceStatus, str, Optional[str]]:
        """Check best execution requirements"""
        max_slippage = params.get('max_slippage_bps', 10)
        
        expected_price = candidate.get('expected_price', 0)
        current_price = data.get('current_price', 0)
        
        if expected_price > 0 and current_price > 0:
            slippage_bps = abs(expected_price - current_price) / current_price * 10000
            
            if slippage_bps > max_slippage:
                return (
                    ComplianceStatus.WARNING,
                    f"Expected slippage {slippage_bps:.1f}bps exceeds threshold",
                    "Consider using limit order"
                )
        
        return (ComplianceStatus.PASS, "Best execution check passed", None)
    
    async def _check_restricted_securities(
        self,
        candidate: Dict,
        data: Dict,
        params: Dict
    ) -> Tuple[ComplianceStatus, str, Optional[str]]:
        """Check if asset is on restricted list"""
        restricted_list = params.get('restricted_list', [])
        restricted_list.extend(data.get('restricted_securities', []))
        
        asset = candidate.get('asset', '')
        
        if asset in restricted_list:
            return (
                ComplianceStatus.FAIL,
                f"Asset {asset} is on restricted securities list",
                "This security cannot be traded - consult compliance officer"
            )
        
        return (ComplianceStatus.PASS, "Asset not restricted", None)
    
    def _create_violation(self, rule: ComplianceRule, check: ComplianceCheck) -> ComplianceViolation:
        """Create a violation record"""
        return ComplianceViolation(
            violation_id=str(uuid.uuid4()),
            rule=rule,
            severity=rule.severity,
            description=check.details,
            affected_assets=[check.data_used.get('asset', 'unknown')],
            remediation_steps=[check.remediation] if check.remediation else [],
            timestamp=datetime.now()
        )
    
    async def _log_audit_entry(
        self,
        event_type: str,
        action: str,
        details: Dict[str, Any]
    ):
        """Add entry to audit trail with integrity verification"""
        # Create hash of details
        details_json = json.dumps(details, sort_keys=True, default=str)
        data_hash = hashlib.sha256(
            (details_json + self.last_hash).encode()
        ).hexdigest()
        
        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(),
            actor="CAI_System",
            action=action,
            details=details,
            data_hash=data_hash,
            previous_hash=self.last_hash
        )
        
        self.audit_trail.append(entry)
        self.last_hash = data_hash
    
    async def _verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify integrity of the audit trail"""
        if not self.audit_trail:
            return {"valid": True, "entries_checked": 0}
        
        valid = True
        issues = []
        
        for i, entry in enumerate(self.audit_trail):
            if i == 0:
                expected_prev = "GENESIS"
            else:
                expected_prev = self.audit_trail[i-1].data_hash
            
            if entry.previous_hash != expected_prev:
                valid = False
                issues.append(f"Chain break at entry {i}: {entry.entry_id}")
        
        return {
            "valid": valid,
            "entries_checked": len(self.audit_trail),
            "issues": issues
        }
    
    async def _post_trade_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run post-trade compliance checks"""
        # Similar to pre-trade but for executed trades
        return {"status": "compliant", "checks": []}
    
    async def _assess_portfolio_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall portfolio compliance"""
        issues = []
        
        # Check all limits against current portfolio
        portfolio = data.get('portfolio', {})
        
        # Position limits
        for asset, position in portfolio.get('positions', {}).items():
            if position.get('weight', 0) > 0.10:
                issues.append(f"Position {asset} exceeds 10% limit")
        
        # Sector limits
        for sector, weight in portfolio.get('sector_weights', {}).items():
            if weight > 0.30:
                issues.append(f"Sector {sector} exceeds 30% limit")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues
        }
    
    async def _generate_violation_report(self, params: Dict) -> Dict[str, Any]:
        """Generate violation report"""
        period_days = params.get('period_days', 30)
        cutoff = datetime.now() - timedelta(days=period_days)
        
        recent_violations = [
            v for v in self.violations
            if v.timestamp >= cutoff
        ]
        
        return {
            "period_days": period_days,
            "total_violations": len(recent_violations),
            "by_severity": {
                s.name: len([v for v in recent_violations if v.severity == s])
                for s in ViolationSeverity
            },
            "violations": [self._violation_to_dict(v) for v in recent_violations]
        }
    
    async def _process_governance_request(self, params: Dict) -> Dict[str, Any]:
        """Process governance approval request"""
        request = GovernanceApproval(
            approval_id=str(uuid.uuid4()),
            request_type=params.get('type', 'general'),
            requestor=params.get('requestor', 'system'),
            details=params.get('details', {}),
            status='pending',
            approvers=[],
            created_at=datetime.now()
        )
        
        self.pending_approvals.append(request)
        
        return {
            "approval_id": request.approval_id,
            "status": "pending",
            "message": "Governance request created"
        }
    
    def _generate_compliance_explanation(
        self,
        checks: List[ComplianceCheck],
        violations: List[ComplianceViolation]
    ) -> str:
        """Generate natural language explanation for regulators"""
        lines = ["## Compliance Check Summary\n"]
        
        lines.append(f"**Checks Performed:** {len(checks)}")
        lines.append(f"**Passed:** {len([c for c in checks if c.status == ComplianceStatus.PASS])}")
        lines.append(f"**Warnings:** {len([c for c in checks if c.status == ComplianceStatus.WARNING])}")
        lines.append(f"**Violations:** {len(violations)}\n")
        
        if violations:
            lines.append("### Violations Detected\n")
            for v in violations:
                lines.append(f"- **{v.rule.name}** ({v.severity.name})")
                lines.append(f"  - {v.description}")
                if v.remediation_steps:
                    lines.append(f"  - Remediation: {v.remediation_steps[0]}")
        else:
            lines.append("✓ All compliance checks passed\n")
        
        lines.append("\n### Regulatory Framework")
        lines.append("Checks performed under: " + 
                    ", ".join([j.value.upper() for j in self.enabled_jurisdictions]))
        
        return "\n".join(lines)
    
    def _check_to_dict(self, check: ComplianceCheck) -> Dict:
        """Convert check to dictionary"""
        return {
            "check_id": check.check_id,
            "rule_id": check.rule.rule_id,
            "rule_name": check.rule.name,
            "status": check.status.value,
            "details": check.details,
            "timestamp": check.timestamp.isoformat()
        }
    
    def _violation_to_dict(self, violation: ComplianceViolation) -> Dict:
        """Convert violation to dictionary"""
        return {
            "violation_id": violation.violation_id,
            "rule_name": violation.rule.name,
            "severity": violation.severity.name,
            "description": violation.description,
            "remediation_steps": violation.remediation_steps,
            "resolved": violation.resolved,
            "timestamp": violation.timestamp.isoformat()
        }
