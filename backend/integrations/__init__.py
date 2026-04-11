"""
Integrations Module
===================

Third-party integrations:
- Brokerage connections
- Banking APIs
- Tax software
- CRM systems
- Webhooks
"""

from .brokerage_connections import (
    BrokerageConnection,
    BrokerageType,
    AccountInfo,
    Position,
    Order,
    OrderType,
    OrderSide,
    AlpacaConnector,
    TDAmeritradeConnector,
    InteractiveBrokersConnector
)

from .banking_apis import (
    BankingConnection,
    BankType,
    BankAccount,
    Transaction,
    PlaidConnector,
    YodleeConnector
)

from .tax_integration import (
    TaxIntegration,
    TaxDocument,
    TaxableEvent,
    EventType,
    TurboTaxConnector,
    CoinTrackerConnector
)

from .webhook_manager import (
    WebhookManager,
    Webhook,
    WebhookEvent,
    WebhookDelivery,
    WebhookStatus
)

__all__ = [
    # Brokerage
    'BrokerageConnection',
    'BrokerageType',
    'AccountInfo',
    'Position',
    'Order',
    'OrderType',
    'OrderSide',
    'AlpacaConnector',
    'TDAmeritradeConnector',
    'InteractiveBrokersConnector',
    
    # Banking
    'BankingConnection',
    'BankType',
    'BankAccount',
    'Transaction',
    'PlaidConnector',
    'YodleeConnector',
    
    # Tax
    'TaxIntegration',
    'TaxDocument',
    'TaxableEvent',
    'EventType',
    'TurboTaxConnector',
    'CoinTrackerConnector',
    
    # Webhooks
    'WebhookManager',
    'Webhook',
    'WebhookEvent',
    'WebhookDelivery',
    'WebhookStatus'
]
