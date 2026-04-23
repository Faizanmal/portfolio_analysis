"""
Multi-Tenant Architecture
=========================

Enterprise multi-tenancy support:
- Tenant isolation and management
- Resource quotas and limits
- Data partitioning
- Cross-tenant analytics
- Tenant provisioning and lifecycle
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib


class TenantTier(Enum):
    """Tenant subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class TenantStatus(Enum):
    """Tenant lifecycle status"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    DELETED = "deleted"


class IsolationLevel(Enum):
    """Data isolation levels"""
    SHARED = "shared"  # Shared tables with tenant ID
    SCHEMA = "schema"  # Separate schema per tenant
    DATABASE = "database"  # Separate database per tenant


@dataclass
class ResourceQuota:
    """Resource quotas for a tenant"""
    max_users: int = 5
    max_portfolios: int = 10
    max_assets: int = 1000
    max_api_calls_per_day: int = 10000
    max_storage_gb: float = 1.0
    max_reports_per_month: int = 100
    max_alerts: int = 50
    max_integrations: int = 3
    
    # Compute resources
    max_concurrent_calculations: int = 2
    max_backtest_history_years: int = 5
    max_optimization_assets: int = 50
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'max_users': self.max_users,
            'max_portfolios': self.max_portfolios,
            'max_assets': self.max_assets,
            'max_api_calls_per_day': self.max_api_calls_per_day,
            'max_storage_gb': self.max_storage_gb,
            'max_reports_per_month': self.max_reports_per_month,
            'max_alerts': self.max_alerts,
            'max_integrations': self.max_integrations,
            'max_concurrent_calculations': self.max_concurrent_calculations,
            'max_backtest_history_years': self.max_backtest_history_years,
            'max_optimization_assets': self.max_optimization_assets
        }


@dataclass
class ResourceUsage:
    """Current resource usage for a tenant"""
    users: int = 0
    portfolios: int = 0
    assets: int = 0
    api_calls_today: int = 0
    storage_gb: float = 0.0
    reports_this_month: int = 0
    alerts: int = 0
    integrations: int = 0
    
    def check_quota(self, quota: ResourceQuota) -> Dict[str, bool]:
        """Check which quotas are exceeded"""
        return {
            'users': self.users >= quota.max_users,
            'portfolios': self.portfolios >= quota.max_portfolios,
            'assets': self.assets >= quota.max_assets,
            'api_calls': self.api_calls_today >= quota.max_api_calls_per_day,
            'storage': self.storage_gb >= quota.max_storage_gb,
            'reports': self.reports_this_month >= quota.max_reports_per_month,
            'alerts': self.alerts >= quota.max_alerts,
            'integrations': self.integrations >= quota.max_integrations
        }
    
    def get_utilization(self, quota: ResourceQuota) -> Dict[str, float]:
        """Get resource utilization percentages"""
        return {
            'users': self.users / quota.max_users if quota.max_users > 0 else 0,
            'portfolios': self.portfolios / quota.max_portfolios if quota.max_portfolios > 0 else 0,
            'assets': self.assets / quota.max_assets if quota.max_assets > 0 else 0,
            'api_calls': self.api_calls_today / quota.max_api_calls_per_day if quota.max_api_calls_per_day > 0 else 0,
            'storage': self.storage_gb / quota.max_storage_gb if quota.max_storage_gb > 0 else 0
        }


@dataclass
class Tenant:
    """Tenant entity"""
    tenant_id: str
    name: str
    tier: TenantTier = TenantTier.FREE
    status: TenantStatus = TenantStatus.PENDING
    
    # Contact
    admin_email: str = ""
    company_name: str = ""
    
    # Configuration
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    quota: ResourceQuota = field(default_factory=ResourceQuota)
    usage: ResourceUsage = field(default_factory=ResourceUsage)
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)
    features: Set[str] = field(default_factory=set)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    
    # Billing
    billing_email: str = ""
    subscription_id: str = ""
    subscription_end_date: Optional[datetime] = None
    
    def is_quota_exceeded(self, resource: str) -> bool:
        """Check if a specific quota is exceeded"""
        exceeded = self.usage.check_quota(self.quota)
        return exceeded.get(resource, False)
    
    def has_feature(self, feature: str) -> bool:
        """Check if tenant has a feature enabled"""
        return feature in self.features
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tenant_id': self.tenant_id,
            'name': self.name,
            'tier': self.tier.value,
            'status': self.status.value,
            'company_name': self.company_name,
            'admin_email': self.admin_email,
            'isolation_level': self.isolation_level.value,
            'quota': self.quota.to_dict(),
            'utilization': self.usage.get_utilization(self.quota),
            'features': list(self.features),
            'created_at': self.created_at.isoformat(),
            'activated_at': self.activated_at.isoformat() if self.activated_at else None,
            'last_active_at': self.last_active_at.isoformat() if self.last_active_at else None
        }


class TenantIsolation:
    """
    Handles data isolation between tenants.
    """
    
    def __init__(self, default_level: IsolationLevel = IsolationLevel.SHARED):
        self.logger = logging.getLogger("tenant_isolation")
        self.default_level = default_level
    
    def get_partition_key(self, tenant_id: str) -> str:
        """Get partition key for tenant"""
        return f"tenant_{tenant_id}"
    
    def get_schema_name(self, tenant_id: str) -> str:
        """Get schema name for schema-level isolation"""
        safe_id = tenant_id.replace('-', '_')
        return f"tenant_{safe_id}"
    
    def get_database_name(self, tenant_id: str) -> str:
        """Get database name for database-level isolation"""
        safe_id = tenant_id.replace('-', '_')
        return f"portfolio_tenant_{safe_id}"
    
    def get_connection_config(
        self,
        tenant: Tenant,
        base_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get database connection config for tenant"""
        config = base_config.copy()
        
        if tenant.isolation_level == IsolationLevel.SCHEMA:
            config['schema'] = self.get_schema_name(tenant.tenant_id)
        elif tenant.isolation_level == IsolationLevel.DATABASE:
            config['database'] = self.get_database_name(tenant.tenant_id)
        
        return config
    
    def filter_query(
        self,
        query: str,
        tenant_id: str,
        isolation_level: IsolationLevel
    ) -> str:
        """Add tenant filter to query for shared isolation"""
        if isolation_level == IsolationLevel.SHARED:
            # Add WHERE clause if not present
            if 'WHERE' in query.upper():
                return query.replace('WHERE', f'WHERE tenant_id = \'{tenant_id}\' AND')
            else:
                return f"{query} WHERE tenant_id = '{tenant_id}'"
        return query
    
    def encrypt_sensitive_data(
        self,
        data: str,
        tenant_id: str
    ) -> str:
        """Encrypt sensitive data with tenant-specific key"""
        # In production, use proper encryption with tenant-specific keys
        key = hashlib.sha256(f"tenant_key_{tenant_id}".encode()).hexdigest()[:32]
        # Placeholder - use proper encryption library
        return f"encrypted:{key[:8]}:{data}"
    
    def get_storage_path(self, tenant_id: str) -> str:
        """Get storage path for tenant files"""
        return f"/data/tenants/{tenant_id}"


class TenantManager:
    """
    Manages tenant lifecycle and operations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("tenant_manager")
        self.tenants: Dict[str, Tenant] = {}
        self.isolation = TenantIsolation()
        
        # Tier configurations
        self.tier_quotas = {
            TenantTier.FREE: ResourceQuota(
                max_users=1,
                max_portfolios=3,
                max_assets=100,
                max_api_calls_per_day=1000,
                max_storage_gb=0.1
            ),
            TenantTier.STARTER: ResourceQuota(
                max_users=5,
                max_portfolios=10,
                max_assets=500,
                max_api_calls_per_day=10000,
                max_storage_gb=1.0
            ),
            TenantTier.PROFESSIONAL: ResourceQuota(
                max_users=25,
                max_portfolios=50,
                max_assets=5000,
                max_api_calls_per_day=100000,
                max_storage_gb=10.0
            ),
            TenantTier.ENTERPRISE: ResourceQuota(
                max_users=1000,
                max_portfolios=1000,
                max_assets=100000,
                max_api_calls_per_day=10000000,
                max_storage_gb=1000.0
            )
        }
        
        # Tier features
        self.tier_features = {
            TenantTier.FREE: {'basic_analytics', 'portfolio_tracking'},
            TenantTier.STARTER: {'basic_analytics', 'portfolio_tracking', 'risk_metrics', 'basic_reports'},
            TenantTier.PROFESSIONAL: {
                'basic_analytics', 'portfolio_tracking', 'risk_metrics', 'basic_reports',
                'advanced_analytics', 'ai_insights', 'custom_reports', 'api_access'
            },
            TenantTier.ENTERPRISE: {
                'basic_analytics', 'portfolio_tracking', 'risk_metrics', 'basic_reports',
                'advanced_analytics', 'ai_insights', 'custom_reports', 'api_access',
                'white_label', 'dedicated_support', 'sso', 'audit_log', 'compliance'
            }
        }
    
    def create_tenant(
        self,
        name: str,
        admin_email: str,
        tier: TenantTier = TenantTier.FREE,
        company_name: str = "",
        custom_quota: ResourceQuota = None
    ) -> Tenant:
        """Create a new tenant"""
        tenant_id = str(uuid.uuid4())
        
        # Get quota for tier
        quota = custom_quota or self.tier_quotas.get(tier, ResourceQuota())
        
        # Determine isolation level
        if tier in [TenantTier.ENTERPRISE, TenantTier.CUSTOM]:
            isolation = IsolationLevel.SCHEMA
        else:
            isolation = IsolationLevel.SHARED
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            tier=tier,
            admin_email=admin_email,
            company_name=company_name,
            quota=quota,
            isolation_level=isolation,
            features=self.tier_features.get(tier, set())
        )
        
        self.tenants[tenant_id] = tenant
        self.logger.info(f"Created tenant: {name} ({tenant_id})")
        
        return tenant
    
    def activate_tenant(self, tenant_id: str) -> bool:
        """Activate a pending tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        if tenant.status != TenantStatus.PENDING:
            return False
        
        tenant.status = TenantStatus.ACTIVE
        tenant.activated_at = datetime.now()
        
        self._provision_resources(tenant)
        
        self.logger.info(f"Activated tenant: {tenant_id}")
        return True
    
    def suspend_tenant(
        self,
        tenant_id: str,
        reason: str = ""
    ) -> bool:
        """Suspend a tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.SUSPENDED
        tenant.settings['suspension_reason'] = reason
        tenant.settings['suspended_at'] = datetime.now().isoformat()
        
        self.logger.warning(f"Suspended tenant: {tenant_id}, reason: {reason}")
        return True
    
    def reactivate_tenant(self, tenant_id: str) -> bool:
        """Reactivate a suspended tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant or tenant.status != TenantStatus.SUSPENDED:
            return False
        
        tenant.status = TenantStatus.ACTIVE
        tenant.settings.pop('suspension_reason', None)
        tenant.settings.pop('suspended_at', None)
        
        self.logger.info(f"Reactivated tenant: {tenant_id}")
        return True
    
    def upgrade_tier(
        self,
        tenant_id: str,
        new_tier: TenantTier
    ) -> bool:
        """Upgrade tenant to a higher tier"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        old_tier = tenant.tier
        tenant.tier = new_tier
        tenant.quota = self.tier_quotas.get(new_tier, tenant.quota)
        tenant.features = self.tier_features.get(new_tier, tenant.features)
        
        self.logger.info(f"Upgraded tenant {tenant_id} from {old_tier.value} to {new_tier.value}")
        return True
    
    def _provision_resources(self, tenant: Tenant):
        """Provision resources for tenant"""
        # Create storage directory
        self.isolation.get_storage_path(tenant.tenant_id)
        
        # If schema isolation, create schema
        if tenant.isolation_level == IsolationLevel.SCHEMA:
            schema_name = self.isolation.get_schema_name(tenant.tenant_id)
            self.logger.info(f"Would create schema: {schema_name}")
        
        # If database isolation, create database
        if tenant.isolation_level == IsolationLevel.DATABASE:
            db_name = self.isolation.get_database_name(tenant.tenant_id)
            self.logger.info(f"Would create database: {db_name}")
    
    def record_activity(self, tenant_id: str):
        """Record tenant activity"""
        tenant = self.tenants.get(tenant_id)
        if tenant:
            tenant.last_active_at = datetime.now()
    
    def increment_usage(
        self,
        tenant_id: str,
        resource: str,
        amount: int = 1
    ) -> bool:
        """Increment resource usage"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        usage = tenant.usage
        
        if resource == 'users':
            usage.users += amount
        elif resource == 'portfolios':
            usage.portfolios += amount
        elif resource == 'assets':
            usage.assets += amount
        elif resource == 'api_calls':
            usage.api_calls_today += amount
        elif resource == 'reports':
            usage.reports_this_month += amount
        elif resource == 'alerts':
            usage.alerts += amount
        elif resource == 'integrations':
            usage.integrations += amount
        
        return True
    
    def check_quota(
        self,
        tenant_id: str,
        resource: str
    ) -> Dict[str, Any]:
        """Check if tenant can use more of a resource"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {'allowed': False, 'reason': 'Tenant not found'}
        
        if tenant.status != TenantStatus.ACTIVE:
            return {'allowed': False, 'reason': 'Tenant not active'}
        
        exceeded = tenant.usage.check_quota(tenant.quota)
        
        if exceeded.get(resource, False):
            return {
                'allowed': False,
                'reason': f'{resource} quota exceeded',
                'current': getattr(tenant.usage, resource, 0),
                'limit': getattr(tenant.quota, f'max_{resource}', 0)
            }
        
        return {
            'allowed': True,
            'current': getattr(tenant.usage, resource, 0),
            'limit': getattr(tenant.quota, f'max_{resource}', 0)
        }
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)
    
    def list_tenants(
        self,
        status: TenantStatus = None,
        tier: TenantTier = None
    ) -> List[Tenant]:
        """List tenants with optional filters"""
        tenants = list(self.tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        if tier:
            tenants = [t for t in tenants if t.tier == tier]
        
        return tenants
    
    def get_usage_report(self, tenant_id: str) -> Dict[str, Any]:
        """Get detailed usage report for tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {}
        
        utilization = tenant.usage.get_utilization(tenant.quota)
        exceeded = tenant.usage.check_quota(tenant.quota)
        
        return {
            'tenant_id': tenant_id,
            'tier': tenant.tier.value,
            'quota': tenant.quota.to_dict(),
            'current_usage': {
                'users': tenant.usage.users,
                'portfolios': tenant.usage.portfolios,
                'assets': tenant.usage.assets,
                'api_calls_today': tenant.usage.api_calls_today,
                'storage_gb': tenant.usage.storage_gb,
                'reports_this_month': tenant.usage.reports_this_month
            },
            'utilization': utilization,
            'exceeded': exceeded,
            'recommendations': self._get_recommendations(utilization, tenant.tier)
        }
    
    def _get_recommendations(
        self,
        utilization: Dict[str, float],
        tier: TenantTier
    ) -> List[str]:
        """Get recommendations based on usage"""
        recommendations = []
        
        high_usage_resources = [k for k, v in utilization.items() if v > 0.8]
        
        if high_usage_resources:
            if tier == TenantTier.FREE:
                recommendations.append("Consider upgrading to Starter tier for more resources")
            elif tier == TenantTier.STARTER:
                recommendations.append("Professional tier offers 10x more capacity")
            
            for resource in high_usage_resources:
                recommendations.append(f"High usage of {resource} ({utilization[resource]:.0%})")
        
        return recommendations
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform-wide statistics"""
        total_tenants = len(self.tenants)
        
        by_tier = {}
        by_status = {}
        
        for tenant in self.tenants.values():
            tier = tenant.tier.value
            status = tenant.status.value
            
            by_tier[tier] = by_tier.get(tier, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            'total_tenants': total_tenants,
            'by_tier': by_tier,
            'by_status': by_status,
            'active_today': sum(
                1 for t in self.tenants.values()
                if t.last_active_at and t.last_active_at.date() == datetime.now().date()
            )
        }
