"""
Compliance Automation
=====================

Automated compliance and regulatory reporting:
- Regulatory report generation
- Compliance rule engine
- Audit trail and logging
- Risk limit monitoring
- Regulatory filing automation
"""

import uuid
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class RegulatoryFramework(Enum):
    """Regulatory frameworks"""
    SEC = "sec"
    FINRA = "finra"
    CFTC = "cftc"
    NFA = "nfa"
    ESMA = "esma"
    FCA = "fca"
    MAS = "mas"
    ASIC = "asic"
    IIROC = "iiroc"
    INTERNAL = "internal"


class ReportType(Enum):
    """Types of regulatory reports"""
    FORM_ADV = "form_adv"
    FORM_PF = "form_pf"
    FORM_13F = "form_13f"
    FORM_13H = "form_13h"
    SCHEDULE_13D = "schedule_13d"
    RULE_606 = "rule_606"
    BEST_EXECUTION = "best_execution"
    TRADE_REPORTING = "trade_reporting"
    POSITION_LIMITS = "position_limits"
    RISK_REPORT = "risk_report"
    AML_SAR = "aml_sar"
    KYC_REVIEW = "kyc_review"


class ComplianceStatus(Enum):
    """Compliance check status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    PENDING = "pending"
    NOT_APPLICABLE = "not_applicable"


class AuditEventType(Enum):
    """Types of audit events"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    TRADE = "trade"
    TRANSFER = "transfer"
    CONFIGURATION = "configuration"
    COMPLIANCE = "compliance"
    APPROVAL = "approval"
    REJECTION = "rejection"


@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    name: str
    description: str
    framework: RegulatoryFramework
    
    # Rule logic
    rule_type: str  # limit, restriction, disclosure, etc.
    condition: str  # Expression or rule definition
    threshold: Optional[float] = None
    
    # Severity
    severity: str = "medium"  # low, medium, high, critical
    auto_remediate: bool = False
    
    # Notification
    notify_on_breach: bool = True
    notification_recipients: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    effective_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'framework': self.framework.value,
            'rule_type': self.rule_type,
            'threshold': self.threshold,
            'severity': self.severity,
            'is_active': self.is_active
        }


@dataclass
class ComplianceCheck:
    """Result of a compliance check"""
    check_id: str
    rule_id: str
    entity_id: str  # Portfolio, account, or user ID
    entity_type: str
    
    status: ComplianceStatus
    current_value: Optional[float] = None
    threshold: Optional[float] = None
    deviation: Optional[float] = None
    
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    checked_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    resolved_by: str = ""


@dataclass
class AuditEvent:
    """Audit log event"""
    event_id: str
    event_type: AuditEventType
    
    # Who
    user_id: str
    user_email: str
    tenant_id: str
    
    # What
    resource_type: str
    resource_id: str
    action: str
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    # Context
    ip_address: str = ""
    user_agent: str = ""
    session_id: str = ""
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'tenant_id': self.tenant_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }
    
    def get_hash(self) -> str:
        """Get tamper-evident hash of event"""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class RegulatoryReport:
    """Regulatory report"""
    report_id: str
    report_type: ReportType
    framework: RegulatoryFramework
    
    # Period
    period_start: datetime
    period_end: datetime
    
    # Content
    title: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: str = "draft"  # draft, pending_review, approved, submitted, rejected
    generated_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None
    
    # Review
    reviewed_by: str = ""
    approved_by: str = ""
    rejection_reason: str = ""
    
    # Filing
    filing_reference: str = ""
    confirmation_number: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_id': self.report_id,
            'report_type': self.report_type.value,
            'framework': self.framework.value,
            'period': {
                'start': self.period_start.isoformat(),
                'end': self.period_end.isoformat()
            },
            'title': self.title,
            'status': self.status,
            'generated_at': self.generated_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


class AuditTrail:
    """
    Immutable audit trail for compliance.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("audit_trail")
        self.events: List[AuditEvent] = []
        self.hash_chain: List[str] = []
    
    def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        user_email: str,
        tenant_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        details: Dict[str, Any] = None,
        old_value: str = None,
        new_value: str = None,
        ip_address: str = "",
        user_agent: str = "",
        session_id: str = ""
    ) -> AuditEvent:
        """Log an audit event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            user_email=user_email,
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details or {},
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        # Add to chain with previous hash
        event_hash = event.get_hash()
        if self.hash_chain:
            combined = self.hash_chain[-1] + event_hash
            chain_hash = hashlib.sha256(combined.encode()).hexdigest()
        else:
            chain_hash = event_hash
        
        self.events.append(event)
        self.hash_chain.append(chain_hash)
        
        self.logger.info(
            f"Audit: {event_type.value} - {user_email} - {resource_type}/{resource_id}"
        )
        
        return event
    
    def verify_integrity(self) -> Dict[str, Any]:
        """Verify audit trail integrity"""
        if not self.events:
            return {'valid': True, 'message': 'Empty audit trail'}
        
        computed_chain = []
        for i, event in enumerate(self.events):
            event_hash = event.get_hash()
            
            if i == 0:
                chain_hash = event_hash
            else:
                combined = computed_chain[-1] + event_hash
                chain_hash = hashlib.sha256(combined.encode()).hexdigest()
            
            computed_chain.append(chain_hash)
        
        if computed_chain == self.hash_chain:
            return {
                'valid': True,
                'message': 'Audit trail integrity verified',
                'event_count': len(self.events)
            }
        else:
            # Find first mismatch
            for i, (computed, stored) in enumerate(zip(computed_chain, self.hash_chain)):
                if computed != stored:
                    return {
                        'valid': False,
                        'message': f'Integrity violation at event {i}',
                        'event_id': self.events[i].event_id
                    }
            
            return {
                'valid': False,
                'message': 'Chain length mismatch'
            }
    
    def search_events(
        self,
        user_id: str = None,
        tenant_id: str = None,
        event_type: AuditEventType = None,
        resource_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Search audit events"""
        results = []
        
        for event in reversed(self.events):
            if user_id and event.user_id != user_id:
                continue
            if tenant_id and event.tenant_id != tenant_id:
                continue
            if event_type and event.event_type != event_type:
                continue
            if resource_type and event.resource_type != resource_type:
                continue
            if start_date and event.timestamp < start_date:
                continue
            if end_date and event.timestamp > end_date:
                continue
            
            results.append(event)
            if len(results) >= limit:
                break
        
        return results
    
    def export_for_regulators(
        self,
        start_date: datetime,
        end_date: datetime,
        framework: RegulatoryFramework = None
    ) -> Dict[str, Any]:
        """Export audit trail for regulatory review"""
        events = self.search_events(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        return {
            'export_id': str(uuid.uuid4()),
            'exported_at': datetime.now().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'event_count': len(events),
            'events': [e.to_dict() for e in events],
            'integrity': self.verify_integrity()
        }


class ComplianceEngine:
    """
    Automated compliance monitoring and enforcement.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("compliance_engine")
        self.rules: Dict[str, ComplianceRule] = {}
        self.checks: List[ComplianceCheck] = []
        self.audit_trail = AuditTrail()
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default compliance rules"""
        default_rules = [
            ComplianceRule(
                rule_id="position-limit-equity",
                name="Equity Position Limit",
                description="Single equity position cannot exceed 10% of portfolio",
                framework=RegulatoryFramework.INTERNAL,
                rule_type="limit",
                condition="position_weight <= 0.10",
                threshold=0.10,
                severity="high"
            ),
            ComplianceRule(
                rule_id="sector-concentration",
                name="Sector Concentration Limit",
                description="Single sector cannot exceed 25% of portfolio",
                framework=RegulatoryFramework.INTERNAL,
                rule_type="limit",
                condition="sector_weight <= 0.25",
                threshold=0.25,
                severity="medium"
            ),
            ComplianceRule(
                rule_id="var-limit",
                name="Value at Risk Limit",
                description="Portfolio VaR cannot exceed 5% at 95% confidence",
                framework=RegulatoryFramework.INTERNAL,
                rule_type="limit",
                condition="var_95 <= 0.05",
                threshold=0.05,
                severity="critical"
            ),
            ComplianceRule(
                rule_id="leverage-limit",
                name="Leverage Limit",
                description="Portfolio leverage cannot exceed 2x",
                framework=RegulatoryFramework.INTERNAL,
                rule_type="limit",
                condition="leverage <= 2.0",
                threshold=2.0,
                severity="critical"
            ),
            ComplianceRule(
                rule_id="restricted-securities",
                name="Restricted Securities",
                description="Trading in restricted securities is prohibited",
                framework=RegulatoryFramework.SEC,
                rule_type="restriction",
                condition="security not in restricted_list",
                severity="critical"
            ),
            ComplianceRule(
                rule_id="best-execution",
                name="Best Execution",
                description="Trades must achieve best execution",
                framework=RegulatoryFramework.FINRA,
                rule_type="disclosure",
                condition="execution_quality >= benchmark",
                severity="high"
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
    
    def add_rule(self, rule: ComplianceRule):
        """Add a compliance rule"""
        self.rules[rule.rule_id] = rule
        self.logger.info(f"Added compliance rule: {rule.name}")
    
    def check_position_limit(
        self,
        portfolio_id: str,
        position_weight: float,
        security_id: str,
        rule_id: str = "position-limit-equity"
    ) -> ComplianceCheck:
        """Check position limit compliance"""
        rule = self.rules.get(rule_id)
        if not rule or not rule.is_active:
            return None
        
        check = ComplianceCheck(
            check_id=str(uuid.uuid4()),
            rule_id=rule_id,
            entity_id=portfolio_id,
            entity_type="portfolio",
            current_value=position_weight,
            threshold=rule.threshold
        )
        
        if position_weight <= rule.threshold:
            check.status = ComplianceStatus.COMPLIANT
            check.message = f"Position weight {position_weight:.1%} within limit"
        elif position_weight <= rule.threshold * 1.1:  # 10% buffer for warning
            check.status = ComplianceStatus.WARNING
            check.message = f"Position weight {position_weight:.1%} approaching limit"
            check.deviation = position_weight - rule.threshold
        else:
            check.status = ComplianceStatus.NON_COMPLIANT
            check.message = f"Position weight {position_weight:.1%} exceeds limit of {rule.threshold:.1%}"
            check.deviation = position_weight - rule.threshold
        
        check.details = {
            'security_id': security_id,
            'rule_name': rule.name
        }
        
        self.checks.append(check)
        
        if check.status == ComplianceStatus.NON_COMPLIANT and rule.notify_on_breach:
            self._send_breach_notification(rule, check)
        
        return check
    
    def check_portfolio_compliance(
        self,
        portfolio_id: str,
        portfolio_data: Dict[str, Any]
    ) -> List[ComplianceCheck]:
        """Run all applicable compliance checks on a portfolio"""
        results = []
        
        # Position limits
        positions = portfolio_data.get('positions', [])
        for position in positions:
            check = self.check_position_limit(
                portfolio_id,
                position.get('weight', 0),
                position.get('security_id', '')
            )
            if check:
                results.append(check)
        
        # Sector concentration
        sectors = portfolio_data.get('sector_weights', {})
        for sector, weight in sectors.items():
            rule = self.rules.get('sector-concentration')
            if rule and rule.is_active:
                check = ComplianceCheck(
                    check_id=str(uuid.uuid4()),
                    rule_id='sector-concentration',
                    entity_id=portfolio_id,
                    entity_type='portfolio',
                    current_value=weight,
                    threshold=rule.threshold,
                    details={'sector': sector}
                )
                
                if weight <= rule.threshold:
                    check.status = ComplianceStatus.COMPLIANT
                else:
                    check.status = ComplianceStatus.NON_COMPLIANT
                    check.deviation = weight - rule.threshold
                
                self.checks.append(check)
                results.append(check)
        
        # VaR limit
        var = portfolio_data.get('var_95', 0)
        rule = self.rules.get('var-limit')
        if rule and rule.is_active:
            check = ComplianceCheck(
                check_id=str(uuid.uuid4()),
                rule_id='var-limit',
                entity_id=portfolio_id,
                entity_type='portfolio',
                current_value=var,
                threshold=rule.threshold
            )
            
            if var <= rule.threshold:
                check.status = ComplianceStatus.COMPLIANT
            else:
                check.status = ComplianceStatus.NON_COMPLIANT
                check.deviation = var - rule.threshold
            
            self.checks.append(check)
            results.append(check)
        
        return results
    
    def _send_breach_notification(
        self,
        rule: ComplianceRule,
        check: ComplianceCheck
    ):
        """Send notification for compliance breach"""
        self.logger.warning(
            f"Compliance breach: {rule.name} - {check.message}"
        )
        # In production, send email/Slack notification
    
    def get_compliance_summary(
        self,
        entity_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get compliance summary"""
        checks = self.checks
        
        if entity_id:
            checks = [c for c in checks if c.entity_id == entity_id]
        if start_date:
            checks = [c for c in checks if c.checked_at >= start_date]
        if end_date:
            checks = [c for c in checks if c.checked_at <= end_date]
        
        by_status = {}
        by_rule = {}
        
        for check in checks:
            status = check.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            rule = check.rule_id
            if rule not in by_rule:
                by_rule[rule] = {'compliant': 0, 'non_compliant': 0, 'warning': 0}
            
            if check.status == ComplianceStatus.COMPLIANT:
                by_rule[rule]['compliant'] += 1
            elif check.status == ComplianceStatus.NON_COMPLIANT:
                by_rule[rule]['non_compliant'] += 1
            elif check.status == ComplianceStatus.WARNING:
                by_rule[rule]['warning'] += 1
        
        total = len(checks)
        compliant = by_status.get('compliant', 0)
        
        return {
            'total_checks': total,
            'compliance_rate': compliant / total if total > 0 else 1.0,
            'by_status': by_status,
            'by_rule': by_rule,
            'active_breaches': [
                c for c in checks 
                if c.status == ComplianceStatus.NON_COMPLIANT and not c.resolved_at
            ]
        }
    
    def generate_report(
        self,
        report_type: ReportType,
        framework: RegulatoryFramework,
        period_start: datetime,
        period_end: datetime,
        data: Dict[str, Any]
    ) -> RegulatoryReport:
        """Generate a regulatory report"""
        report = RegulatoryReport(
            report_id=str(uuid.uuid4()),
            report_type=report_type,
            framework=framework,
            period_start=period_start,
            period_end=period_end,
            title=f"{report_type.value.upper()} Report - {period_start.strftime('%Y-%m')}",
            data=data
        )
        
        self.logger.info(f"Generated report: {report.report_id}")
        return report
    
    def generate_form_13f(
        self,
        holdings: List[Dict[str, Any]],
        period_end: datetime
    ) -> RegulatoryReport:
        """Generate SEC Form 13F"""
        period_start = period_end - timedelta(days=90)
        
        # Filter for 13F securities (institutional investment managers with >$100M)
        qualifying_holdings = [
            h for h in holdings
            if h.get('security_type') in ['equity', 'option', 'convertible']
            and h.get('value', 0) > 0
        ]
        
        data = {
            'filing_type': 'Form 13F-HR',
            'period': period_end.strftime('%Y-%m-%d'),
            'total_value': sum(h.get('value', 0) for h in qualifying_holdings),
            'holdings_count': len(qualifying_holdings),
            'holdings': [
                {
                    'name': h.get('name'),
                    'cusip': h.get('cusip'),
                    'value': h.get('value'),
                    'shares': h.get('shares'),
                    'investment_discretion': h.get('discretion', 'SOLE'),
                    'voting_authority': h.get('voting_authority', 'SOLE')
                }
                for h in qualifying_holdings
            ]
        }
        
        return self.generate_report(
            ReportType.FORM_13F,
            RegulatoryFramework.SEC,
            period_start,
            period_end,
            data
        )
    
    def generate_risk_report(
        self,
        portfolio_data: Dict[str, Any],
        period_end: datetime
    ) -> RegulatoryReport:
        """Generate internal risk report"""
        period_start = period_end - timedelta(days=30)
        
        data = {
            'portfolio_value': portfolio_data.get('total_value'),
            'risk_metrics': {
                'var_95_1d': portfolio_data.get('var_95', 0),
                'var_99_1d': portfolio_data.get('var_99', 0),
                'expected_shortfall': portfolio_data.get('es_95', 0),
                'beta': portfolio_data.get('beta', 1.0),
                'volatility': portfolio_data.get('volatility', 0)
            },
            'stress_tests': portfolio_data.get('stress_tests', {}),
            'concentration': {
                'top_10_weight': portfolio_data.get('top_10_weight', 0),
                'hhi': portfolio_data.get('hhi', 0)
            },
            'compliance_summary': self.get_compliance_summary(
                start_date=period_start,
                end_date=period_end
            )
        }
        
        return self.generate_report(
            ReportType.RISK_REPORT,
            RegulatoryFramework.INTERNAL,
            period_start,
            period_end,
            data
        )
