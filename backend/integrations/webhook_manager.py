"""
Webhook Manager
===============

Manage webhooks for real-time notifications:
- Portfolio events
- Price alerts
- Trade executions
- Risk alerts
"""

import uuid
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from queue import Queue
import threading


class WebhookStatus(Enum):
    """Webhook status"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    FAILED = "failed"


class WebhookEvent(Enum):
    """Types of webhook events"""
    # Portfolio events
    PORTFOLIO_CREATED = "portfolio.created"
    PORTFOLIO_UPDATED = "portfolio.updated"
    PORTFOLIO_DELETED = "portfolio.deleted"
    
    # Trade events
    TRADE_EXECUTED = "trade.executed"
    TRADE_FAILED = "trade.failed"
    ORDER_FILLED = "order.filled"
    ORDER_CANCELLED = "order.cancelled"
    
    # Price alerts
    PRICE_ABOVE = "price.above"
    PRICE_BELOW = "price.below"
    PRICE_CHANGE = "price.change"
    
    # Risk alerts
    RISK_LIMIT_EXCEEDED = "risk.limit_exceeded"
    MAX_DRAWDOWN = "risk.max_drawdown"
    VOLATILITY_SPIKE = "risk.volatility_spike"
    
    # Account events
    ACCOUNT_BALANCE_LOW = "account.balance_low"
    MARGIN_CALL = "account.margin_call"
    
    # Strategy events
    STRATEGY_SIGNAL = "strategy.signal"
    BACKTEST_COMPLETED = "backtest.completed"
    
    # System events
    SYSTEM_ERROR = "system.error"
    MAINTENANCE = "system.maintenance"


@dataclass
class WebhookDelivery:
    """Record of a webhook delivery attempt"""
    delivery_id: str
    webhook_id: str
    
    # Attempt info
    attempt_number: int
    attempted_at: datetime
    
    # Result
    success: bool = False
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'delivery_id': self.delivery_id,
            'attempt': self.attempt_number,
            'attempted_at': self.attempted_at.isoformat(),
            'success': self.success,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'error': self.error_message
        }


@dataclass
class Webhook:
    """Webhook configuration"""
    webhook_id: str
    user_id: str
    
    # Endpoint
    url: str
    secret: str  # For signing payloads
    
    # Events
    subscribed_events: List[WebhookEvent] = field(default_factory=list)
    
    # Filters
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: WebhookStatus = WebhookStatus.ACTIVE
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_triggered: Optional[datetime] = None
    
    # Statistics
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    
    # Retry policy
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    def is_subscribed_to(self, event: WebhookEvent) -> bool:
        """Check if webhook is subscribed to an event"""
        return event in self.subscribed_events
    
    def matches_filters(self, event_data: Dict[str, Any]) -> bool:
        """Check if event data matches filters"""
        if not self.filters:
            return True
        
        for key, value in self.filters.items():
            if key not in event_data or event_data[key] != value:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'webhook_id': self.webhook_id,
            'url': self.url,
            'events': [e.value for e in self.subscribed_events],
            'status': self.status.value,
            'statistics': {
                'total_deliveries': self.total_deliveries,
                'successful_deliveries': self.successful_deliveries,
                'failed_deliveries': self.failed_deliveries,
                'success_rate': (self.successful_deliveries / self.total_deliveries * 100) if self.total_deliveries > 0 else 0
            },
            'created_at': self.created_at.isoformat()
        }


class WebhookManager:
    """
    Manages webhooks and event delivery.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("webhook_manager")
        self.webhooks: Dict[str, Webhook] = {}
        self.user_webhooks: Dict[str, List[str]] = {}  # user_id -> webhook_ids
        self.deliveries: Dict[str, List[WebhookDelivery]] = {}  # webhook_id -> deliveries
        
        # Event queue
        self.event_queue: Queue = Queue()
        self.delivery_queue: Queue = Queue()
        
        # Start background workers
        self._start_workers()
    
    def _start_workers(self):
        """Start background worker threads"""
        # Event processor
        event_worker = threading.Thread(target=self._process_events, daemon=True)
        event_worker.start()
        
        # Delivery processor
        delivery_worker = threading.Thread(target=self._process_deliveries, daemon=True)
        delivery_worker.start()
        
        self.logger.info("Started webhook workers")
    
    def create_webhook(
        self,
        user_id: str,
        url: str,
        events: List[WebhookEvent],
        filters: Dict[str, Any] = None
    ) -> Webhook:
        """Create a new webhook"""
        webhook_id = str(uuid.uuid4())
        
        # Generate secret for signing
        secret = hashlib.sha256(f"{webhook_id}{user_id}{datetime.now()}".encode()).hexdigest()
        
        webhook = Webhook(
            webhook_id=webhook_id,
            user_id=user_id,
            url=url,
            secret=secret,
            subscribed_events=events,
            filters=filters or {}
        )
        
        self.webhooks[webhook_id] = webhook
        
        # Track user's webhooks
        if user_id not in self.user_webhooks:
            self.user_webhooks[user_id] = []
        self.user_webhooks[user_id].append(webhook_id)
        
        self.logger.info(f"Created webhook {webhook_id} for user {user_id}")
        
        return webhook
    
    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get a webhook"""
        return self.webhooks.get(webhook_id)
    
    def get_user_webhooks(self, user_id: str) -> List[Webhook]:
        """Get all webhooks for a user"""
        webhook_ids = self.user_webhooks.get(user_id, [])
        return [self.webhooks[wid] for wid in webhook_ids if wid in self.webhooks]
    
    def update_webhook(
        self,
        webhook_id: str,
        url: Optional[str] = None,
        events: Optional[List[WebhookEvent]] = None,
        filters: Optional[Dict[str, Any]] = None,
        status: Optional[WebhookStatus] = None
    ) -> bool:
        """Update a webhook"""
        webhook = self.webhooks.get(webhook_id)
        
        if not webhook:
            return False
        
        if url:
            webhook.url = url
        if events:
            webhook.subscribed_events = events
        if filters is not None:
            webhook.filters = filters
        if status:
            webhook.status = status
        
        webhook.updated_at = datetime.now()
        
        self.logger.info(f"Updated webhook {webhook_id}")
        
        return True
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook"""
        webhook = self.webhooks.pop(webhook_id, None)
        
        if not webhook:
            return False
        
        # Remove from user's webhooks
        if webhook.user_id in self.user_webhooks:
            self.user_webhooks[webhook.user_id].remove(webhook_id)
        
        # Remove deliveries
        self.deliveries.pop(webhook_id, None)
        
        self.logger.info(f"Deleted webhook {webhook_id}")
        
        return True
    
    def trigger_event(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Trigger a webhook event"""
        event_payload = {
            'event': event.value,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        self.event_queue.put(event_payload)
        
        self.logger.debug(f"Triggered event: {event.value}")
    
    def _process_events(self):
        """Process events from queue (background thread)"""
        while True:
            try:
                event_payload = self.event_queue.get(timeout=1)
                
                event = WebhookEvent(event_payload['event'])
                user_id = event_payload.get('user_id')
                
                # Find matching webhooks
                webhooks_to_notify = []
                
                if user_id:
                    # User-specific webhooks
                    webhooks_to_notify = self.get_user_webhooks(user_id)
                else:
                    # All webhooks
                    webhooks_to_notify = list(self.webhooks.values())
                
                # Filter webhooks
                for webhook in webhooks_to_notify:
                    if webhook.status != WebhookStatus.ACTIVE:
                        continue
                    
                    if not webhook.is_subscribed_to(event):
                        continue
                    
                    if not webhook.matches_filters(event_payload['data']):
                        continue
                    
                    # Queue for delivery
                    self.delivery_queue.put({
                        'webhook': webhook,
                        'payload': event_payload,
                        'attempt': 1
                    })
            
            except Exception as e:
                if str(e) != '':
                    self.logger.error(f"Error processing event: {e}")
    
    def _process_deliveries(self):
        """Process webhook deliveries (background thread)"""
        while True:
            try:
                delivery_item = self.delivery_queue.get(timeout=1)
                
                webhook = delivery_item['webhook']
                payload = delivery_item['payload']
                attempt = delivery_item['attempt']
                
                # Deliver webhook
                success = self._deliver_webhook(webhook, payload, attempt)
                
                if not success and attempt < webhook.max_retries:
                    # Retry later
                    self.logger.info(f"Scheduling retry {attempt + 1} for webhook {webhook.webhook_id}")
                    
                    # In production, use a proper retry queue with delays
                    # For now, just re-queue immediately
                    delivery_item['attempt'] = attempt + 1
                    self.delivery_queue.put(delivery_item)
            
            except Exception as e:
                if str(e) != '':
                    self.logger.error(f"Error processing delivery: {e}")
    
    def _deliver_webhook(
        self,
        webhook: Webhook,
        payload: Dict[str, Any],
        attempt: int
    ) -> bool:
        """Deliver webhook to endpoint"""
        delivery_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Sign payload
            self._sign_payload(payload, webhook.secret)
            
            # In production, use requests library to POST
            # import requests
            # headers = {
            #     'Content-Type': 'application/json',
            #     'X-Webhook-Signature': signature,
            #     'X-Webhook-ID': webhook.webhook_id,
            #     'X-Webhook-Delivery': delivery_id
            # }
            # response = requests.post(webhook.url, json=payload, headers=headers, timeout=10)
            
            # Simulate delivery
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            status_code = 200
            success = True
            
            # Record delivery
            delivery = WebhookDelivery(
                delivery_id=delivery_id,
                webhook_id=webhook.webhook_id,
                attempt_number=attempt,
                attempted_at=start_time,
                success=success,
                status_code=status_code,
                response_time_ms=response_time
            )
            
            # Update webhook stats
            webhook.total_deliveries += 1
            webhook.successful_deliveries += 1
            webhook.last_triggered = datetime.now()
            
            # Store delivery
            if webhook.webhook_id not in self.deliveries:
                self.deliveries[webhook.webhook_id] = []
            self.deliveries[webhook.webhook_id].append(delivery)
            
            # Keep only last 100 deliveries
            if len(self.deliveries[webhook.webhook_id]) > 100:
                self.deliveries[webhook.webhook_id] = self.deliveries[webhook.webhook_id][-100:]
            
            self.logger.info(f"Delivered webhook {webhook.webhook_id} (attempt {attempt})")
            
            return True
        
        except Exception as e:
            # Record failed delivery
            delivery = WebhookDelivery(
                delivery_id=delivery_id,
                webhook_id=webhook.webhook_id,
                attempt_number=attempt,
                attempted_at=start_time,
                success=False,
                error_message=str(e)
            )
            
            webhook.total_deliveries += 1
            webhook.failed_deliveries += 1
            
            if webhook.webhook_id not in self.deliveries:
                self.deliveries[webhook.webhook_id] = []
            self.deliveries[webhook.webhook_id].append(delivery)
            
            self.logger.error(f"Failed to deliver webhook {webhook.webhook_id}: {e}")
            
            # Disable webhook after max retries
            if attempt >= webhook.max_retries:
                webhook.status = WebhookStatus.FAILED
                self.logger.warning(f"Disabled webhook {webhook.webhook_id} after {attempt} failed attempts")
            
            return False
    
    def _sign_payload(self, payload: Dict[str, Any], secret: str) -> str:
        """Sign payload with HMAC SHA256"""
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        signature = hmac.new(
            secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        secret: str
    ) -> bool:
        """Verify webhook signature"""
        expected_signature = self._sign_payload(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    def get_delivery_history(
        self,
        webhook_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get delivery history for a webhook"""
        deliveries = self.deliveries.get(webhook_id, [])
        recent = deliveries[-limit:] if len(deliveries) > limit else deliveries
        
        return [d.to_dict() for d in reversed(recent)]
    
    def get_webhook_stats(self, webhook_id: str) -> Dict[str, Any]:
        """Get statistics for a webhook"""
        webhook = self.webhooks.get(webhook_id)
        
        if not webhook:
            return {}
        
        deliveries = self.deliveries.get(webhook_id, [])
        
        # Calculate average response time
        successful_deliveries = [d for d in deliveries if d.success and d.response_time_ms]
        avg_response_time = (
            sum(d.response_time_ms for d in successful_deliveries) / len(successful_deliveries)
            if successful_deliveries else 0
        )
        
        return {
            'webhook_id': webhook_id,
            'status': webhook.status.value,
            'total_deliveries': webhook.total_deliveries,
            'successful_deliveries': webhook.successful_deliveries,
            'failed_deliveries': webhook.failed_deliveries,
            'success_rate': (webhook.successful_deliveries / webhook.total_deliveries * 100) if webhook.total_deliveries > 0 else 0,
            'avg_response_time_ms': avg_response_time,
            'last_triggered': webhook.last_triggered.isoformat() if webhook.last_triggered else None
        }
    
    def test_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Send a test event to a webhook"""
        webhook = self.webhooks.get(webhook_id)
        
        if not webhook:
            return {'success': False, 'error': 'Webhook not found'}
        
        test_payload = {
            'event': 'webhook.test',
            'data': {
                'message': 'This is a test webhook delivery',
                'webhook_id': webhook_id
            },
            'timestamp': datetime.now().isoformat()
        }
        
        success = self._deliver_webhook(webhook, test_payload, 1)
        
        return {
            'success': success,
            'webhook_id': webhook_id,
            'timestamp': datetime.now().isoformat()
        }


# Helper function for easy webhook triggering
def notify_price_alert(
    webhook_manager: WebhookManager,
    user_id: str,
    symbol: str,
    price: float,
    threshold: float,
    direction: str
):
    """Trigger a price alert webhook"""
    event = WebhookEvent.PRICE_ABOVE if direction == 'above' else WebhookEvent.PRICE_BELOW
    
    webhook_manager.trigger_event(
        event=event,
        data={
            'symbol': symbol,
            'current_price': price,
            'threshold': threshold,
            'direction': direction
        },
        user_id=user_id
    )


def notify_trade_execution(
    webhook_manager: WebhookManager,
    user_id: str,
    trade_details: Dict[str, Any]
):
    """Trigger a trade execution webhook"""
    webhook_manager.trigger_event(
        event=WebhookEvent.TRADE_EXECUTED,
        data=trade_details,
        user_id=user_id
    )


def notify_risk_alert(
    webhook_manager: WebhookManager,
    user_id: str,
    alert_type: str,
    details: Dict[str, Any]
):
    """Trigger a risk alert webhook"""
    event_map = {
        'limit_exceeded': WebhookEvent.RISK_LIMIT_EXCEEDED,
        'max_drawdown': WebhookEvent.MAX_DRAWDOWN,
        'volatility_spike': WebhookEvent.VOLATILITY_SPIKE
    }
    
    event = event_map.get(alert_type, WebhookEvent.RISK_LIMIT_EXCEEDED)
    
    webhook_manager.trigger_event(
        event=event,
        data=details,
        user_id=user_id
    )
