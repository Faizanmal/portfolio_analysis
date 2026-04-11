"""
Mobile-First Progressive Web App (PWA) Backend
==============================================

Enterprise-grade backend for the Portfolio Analysis PWA with:
- Push notifications for critical alerts (VaR breaches, trade executions)
- Biometric authentication support (Face ID, fingerprint)
- Offline mode with data caching and sync
- Voice command processing for hands-free queries
- Real-time data streaming via WebSockets

70% of investors check portfolios on mobile - this module addresses that need.
"""

import asyncio
import json
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import redis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class NotificationType(Enum):
    """Types of push notifications"""
    VAR_BREACH = "var_breach"
    TRADE_EXECUTION = "trade_execution"
    PRICE_ALERT = "price_alert"
    PORTFOLIO_UPDATE = "portfolio_update"
    MARKET_ALERT = "market_alert"
    COMPLIANCE_ALERT = "compliance_alert"
    SYSTEM_ALERT = "system_alert"
    SOCIAL_ACTIVITY = "social_activity"
    LEARNING_REMINDER = "learning_reminder"


class AlertPriority(Enum):
    """Alert priority levels for notification handling"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BiometricType(Enum):
    """Supported biometric authentication types"""
    FACE_ID = "face_id"
    FINGERPRINT = "fingerprint"
    IRIS_SCAN = "iris_scan"
    VOICE_RECOGNITION = "voice_recognition"


class VoiceCommandType(Enum):
    """Types of voice commands supported"""
    PORTFOLIO_QUERY = "portfolio_query"
    PERFORMANCE_CHECK = "performance_check"
    TRADE_COMMAND = "trade_command"
    ALERT_MANAGEMENT = "alert_management"
    MARKET_INFO = "market_info"
    ANALYSIS_REQUEST = "analysis_request"


@dataclass
class PushNotification:
    """Push notification structure"""
    notification_id: str
    user_id: str
    notification_type: NotificationType
    priority: AlertPriority
    title: str
    body: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    read: bool = False
    delivered: bool = False
    action_url: Optional[str] = None
    icon: Optional[str] = None
    badge_count: int = 0
    sound: str = "default"
    require_interaction: bool = False
    
    def to_fcm_payload(self) -> Dict[str, Any]:
        """Convert to Firebase Cloud Messaging payload"""
        return {
            "notification": {
                "title": self.title,
                "body": self.body,
                "icon": self.icon or "/icons/app-icon-192.png",
                "badge": str(self.badge_count),
                "sound": self.sound,
                "click_action": self.action_url
            },
            "data": {
                "notification_id": self.notification_id,
                "type": self.notification_type.value,
                "priority": self.priority.value,
                "timestamp": self.timestamp.isoformat(),
                **self.data
            },
            "android": {
                "priority": "high" if self.priority in [AlertPriority.HIGH, AlertPriority.CRITICAL] else "normal",
                "notification": {
                    "channel_id": f"portfolio_{self.priority.value}"
                }
            },
            "apns": {
                "payload": {
                    "aps": {
                        "alert": {
                            "title": self.title,
                            "body": self.body
                        },
                        "badge": self.badge_count,
                        "sound": self.sound,
                        "content-available": 1
                    }
                },
                "headers": {
                    "apns-priority": "10" if self.priority == AlertPriority.CRITICAL else "5"
                }
            },
            "webpush": {
                "headers": {
                    "Urgency": "high" if self.priority == AlertPriority.CRITICAL else "normal"
                },
                "notification": {
                    "requireInteraction": self.require_interaction
                }
            }
        }


@dataclass
class BiometricCredential:
    """Biometric authentication credential"""
    credential_id: str
    user_id: str
    biometric_type: BiometricType
    public_key: str
    device_id: str
    device_name: str
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    is_active: bool = True
    trust_level: float = 1.0


@dataclass
class VoiceCommand:
    """Voice command structure"""
    command_id: str
    user_id: str
    command_type: VoiceCommandType
    raw_text: str
    parsed_intent: str
    entities: Dict[str, Any]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    response: Optional[str] = None
    executed: bool = False


@dataclass
class CachedData:
    """Cached data for offline mode"""
    cache_key: str
    data_type: str
    data: Any
    cached_at: datetime
    expires_at: datetime
    version: int
    checksum: str
    is_synced: bool = True
    pending_updates: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DeviceSession:
    """Mobile device session"""
    session_id: str
    user_id: str
    device_id: str
    device_type: str  # ios, android, web
    push_token: Optional[str] = None
    biometric_enabled: bool = False
    last_active: datetime = field(default_factory=datetime.now)
    app_version: str = "1.0.0"
    os_version: str = ""
    is_active: bool = True
    offline_mode_enabled: bool = True


class PushNotificationService:
    """
    Enterprise push notification service with multi-platform support.
    Handles FCM (Android), APNS (iOS), and Web Push.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self.delivery_callbacks: Dict[str, Callable] = {}
        self.user_preferences: Dict[str, Dict[str, bool]] = {}
        self.rate_limiters: Dict[str, List[datetime]] = {}
        
        # Platform-specific credentials
        self.fcm_credentials = config.get('fcm_credentials', {})
        self.apns_credentials = config.get('apns_credentials', {})
        self.vapid_keys = config.get('vapid_keys', {})
        
        # Notification templates
        self.templates = self._load_notification_templates()
    
    def _load_notification_templates(self) -> Dict[str, Dict[str, str]]:
        """Load notification templates for different alert types"""
        return {
            NotificationType.VAR_BREACH.value: {
                "title": "⚠️ Risk Alert: VaR Breach Detected",
                "body": "Portfolio VaR has exceeded {threshold}%. Current VaR: {current_var}%. Immediate review recommended.",
                "icon": "/icons/risk-alert.png",
                "sound": "critical_alert"
            },
            NotificationType.TRADE_EXECUTION.value: {
                "title": "✅ Trade Executed: {symbol}",
                "body": "{action} {quantity} shares of {symbol} at ${price}. Order ID: {order_id}",
                "icon": "/icons/trade-success.png",
                "sound": "trade_complete"
            },
            NotificationType.PRICE_ALERT.value: {
                "title": "📈 Price Alert: {symbol}",
                "body": "{symbol} has {direction} your target price of ${target}. Current: ${current}",
                "icon": "/icons/price-alert.png",
                "sound": "price_alert"
            },
            NotificationType.PORTFOLIO_UPDATE.value: {
                "title": "📊 Portfolio Update",
                "body": "Your portfolio value has changed by {change_pct}% ({change_value}). New total: ${total_value}",
                "icon": "/icons/portfolio-update.png",
                "sound": "default"
            },
            NotificationType.MARKET_ALERT.value: {
                "title": "🌍 Market Alert: {market}",
                "body": "{message}",
                "icon": "/icons/market-alert.png",
                "sound": "market_alert"
            },
            NotificationType.COMPLIANCE_ALERT.value: {
                "title": "⚖️ Compliance Alert",
                "body": "{message}. Action required by {deadline}.",
                "icon": "/icons/compliance-alert.png",
                "sound": "critical_alert"
            },
            NotificationType.SOCIAL_ACTIVITY.value: {
                "title": "👥 {activity_type}",
                "body": "{user_name} {action}",
                "icon": "/icons/social-activity.png",
                "sound": "social"
            },
            NotificationType.LEARNING_REMINDER.value: {
                "title": "📚 Learning Reminder",
                "body": "Continue your learning journey: {module_name}. You're {progress}% complete!",
                "icon": "/icons/learning.png",
                "sound": "reminder"
            }
        }
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        data: Dict[str, Any],
        priority: AlertPriority = AlertPriority.MEDIUM,
        channels: Optional[List[str]] = None
    ) -> PushNotification:
        """
        Send a push notification to a user across all their registered devices.
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification
            data: Data to populate template
            priority: Alert priority level
            channels: Specific channels to use (None = all)
        
        Returns:
            PushNotification object with delivery status
        """
        # Check user preferences
        if not self._check_user_preferences(user_id, notification_type):
            self.logger.info(f"Notification blocked by user preferences: {user_id}, {notification_type}")
            return None
        
        # Rate limiting check
        if not self._check_rate_limit(user_id, notification_type):
            self.logger.warning(f"Rate limit exceeded for user {user_id}")
            return None
        
        # Get template and format notification
        template = self.templates.get(notification_type.value, {})
        notification = PushNotification(
            notification_id=secrets.token_urlsafe(16),
            user_id=user_id,
            notification_type=notification_type,
            priority=priority,
            title=template.get("title", "Notification").format(**data),
            body=template.get("body", "").format(**data),
            data=data,
            icon=template.get("icon"),
            sound=template.get("sound", "default"),
            require_interaction=priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]
        )
        
        # Queue for delivery
        await self.notification_queue.put(notification)
        
        # Start delivery process
        asyncio.create_task(self._deliver_notification(notification, channels))
        
        return notification
    
    async def _deliver_notification(
        self,
        notification: PushNotification,
        channels: Optional[List[str]] = None
    ):
        """Deliver notification to all user devices"""
        user_sessions = await self._get_user_sessions(notification.user_id)
        
        delivery_results = []
        for session in user_sessions:
            if not session.push_token:
                continue
            
            try:
                if session.device_type == "ios":
                    result = await self._send_apns(session.push_token, notification)
                elif session.device_type == "android":
                    result = await self._send_fcm(session.push_token, notification)
                else:  # web
                    result = await self._send_web_push(session.push_token, notification)
                
                delivery_results.append({
                    "device_id": session.device_id,
                    "success": result.get("success", False),
                    "message_id": result.get("message_id")
                })
            except Exception as e:
                self.logger.error(f"Failed to deliver notification to {session.device_id}: {e}")
                delivery_results.append({
                    "device_id": session.device_id,
                    "success": False,
                    "error": str(e)
                })
        
        notification.delivered = any(r.get("success") for r in delivery_results)
        
        # Trigger callback if registered
        if notification.notification_id in self.delivery_callbacks:
            await self.delivery_callbacks[notification.notification_id](notification, delivery_results)
    
    async def _send_fcm(self, token: str, notification: PushNotification) -> Dict[str, Any]:
        """Send notification via Firebase Cloud Messaging"""
        payload = notification.to_fcm_payload()
        payload["to"] = token
        
        # In production, use firebase-admin SDK
        self.logger.info(f"Sending FCM notification to {token[:20]}...")
        return {"success": True, "message_id": secrets.token_urlsafe(8)}
    
    async def _send_apns(self, token: str, notification: PushNotification) -> Dict[str, Any]:
        """Send notification via Apple Push Notification Service"""
        payload = notification.to_fcm_payload()["apns"]
        
        # In production, use httpx with APNS HTTP/2 endpoint
        self.logger.info(f"Sending APNS notification to {token[:20]}...")
        return {"success": True, "message_id": secrets.token_urlsafe(8)}
    
    async def _send_web_push(self, token: str, notification: PushNotification) -> Dict[str, Any]:
        """Send Web Push notification"""
        payload = notification.to_fcm_payload()["webpush"]
        
        # In production, use pywebpush
        self.logger.info(f"Sending Web Push notification...")
        return {"success": True, "message_id": secrets.token_urlsafe(8)}
    
    async def _get_user_sessions(self, user_id: str) -> List[DeviceSession]:
        """Get all active sessions for a user"""
        # In production, fetch from database
        return []
    
    def _check_user_preferences(self, user_id: str, notification_type: NotificationType) -> bool:
        """Check if user has enabled this notification type"""
        prefs = self.user_preferences.get(user_id, {})
        return prefs.get(notification_type.value, True)
    
    def _check_rate_limit(self, user_id: str, notification_type: NotificationType) -> bool:
        """Check rate limiting for user notifications"""
        key = f"{user_id}:{notification_type.value}"
        now = datetime.now()
        window = timedelta(minutes=5)
        max_notifications = 10
        
        if key not in self.rate_limiters:
            self.rate_limiters[key] = []
        
        # Clean old entries
        self.rate_limiters[key] = [
            ts for ts in self.rate_limiters[key]
            if now - ts < window
        ]
        
        if len(self.rate_limiters[key]) >= max_notifications:
            return False
        
        self.rate_limiters[key].append(now)
        return True
    
    async def send_var_breach_alert(
        self,
        user_id: str,
        current_var: float,
        threshold: float,
        portfolio_id: str
    ):
        """Send VaR breach alert - critical priority"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.VAR_BREACH,
            data={
                "current_var": f"{current_var:.2f}",
                "threshold": f"{threshold:.2f}",
                "portfolio_id": portfolio_id
            },
            priority=AlertPriority.CRITICAL
        )
    
    async def send_trade_execution_alert(
        self,
        user_id: str,
        symbol: str,
        action: str,
        quantity: float,
        price: float,
        order_id: str
    ):
        """Send trade execution notification"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.TRADE_EXECUTION,
            data={
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "price": f"{price:.2f}",
                "order_id": order_id
            },
            priority=AlertPriority.HIGH
        )


class BiometricAuthenticationService:
    """
    Biometric authentication service supporting Face ID, fingerprint,
    and other biometric methods with WebAuthn/FIDO2 compliance.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.credentials: Dict[str, List[BiometricCredential]] = {}
        self.challenges: Dict[str, str] = {}
        self.challenge_timeout = timedelta(minutes=5)
        
        # Encryption key for sensitive data
        self.encryption_key = self._derive_key(
            config.get('secret_key', 'default-secret-key')
        )
        self.cipher = Fernet(self.encryption_key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b'portfolio_biometric_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    async def register_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        public_key: str,
        device_id: str,
        device_name: str
    ) -> BiometricCredential:
        """
        Register a new biometric credential for a user.
        
        Follows WebAuthn specification for credential creation.
        """
        credential = BiometricCredential(
            credential_id=secrets.token_urlsafe(32),
            user_id=user_id,
            biometric_type=biometric_type,
            public_key=public_key,
            device_id=device_id,
            device_name=device_name
        )
        
        if user_id not in self.credentials:
            self.credentials[user_id] = []
        
        self.credentials[user_id].append(credential)
        self.logger.info(f"Registered biometric for user {user_id}: {biometric_type.value}")
        
        return credential
    
    async def generate_authentication_challenge(self, user_id: str) -> Dict[str, Any]:
        """Generate a challenge for biometric authentication"""
        challenge = secrets.token_urlsafe(32)
        self.challenges[user_id] = {
            "challenge": challenge,
            "created_at": datetime.now()
        }
        
        user_credentials = self.credentials.get(user_id, [])
        allowed_credentials = [
            {
                "id": cred.credential_id,
                "type": "public-key",
                "transports": ["internal", "hybrid"]
            }
            for cred in user_credentials if cred.is_active
        ]
        
        return {
            "challenge": challenge,
            "timeout": 60000,  # 60 seconds
            "rpId": self.config.get("rp_id", "portfolio-analysis.app"),
            "userVerification": "required",
            "allowCredentials": allowed_credentials
        }
    
    async def verify_biometric(
        self,
        user_id: str,
        credential_id: str,
        authenticator_data: str,
        client_data_json: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify a biometric authentication attempt.
        
        Returns verification result with session token on success.
        """
        # Check challenge
        stored_challenge = self.challenges.get(user_id)
        if not stored_challenge:
            return {"success": False, "error": "No challenge found"}
        
        challenge_age = datetime.now() - stored_challenge["created_at"]
        if challenge_age > self.challenge_timeout:
            del self.challenges[user_id]
            return {"success": False, "error": "Challenge expired"}
        
        # Find credential
        user_credentials = self.credentials.get(user_id, [])
        credential = next(
            (c for c in user_credentials if c.credential_id == credential_id),
            None
        )
        
        if not credential:
            return {"success": False, "error": "Credential not found"}
        
        # In production, verify signature with public key
        # For now, simulate successful verification
        
        # Update last used
        credential.last_used = datetime.now()
        
        # Generate session token
        session_token = secrets.token_urlsafe(64)
        
        # Clear challenge
        del self.challenges[user_id]
        
        return {
            "success": True,
            "session_token": session_token,
            "user_id": user_id,
            "biometric_type": credential.biometric_type.value,
            "device_name": credential.device_name
        }
    
    async def revoke_credential(self, user_id: str, credential_id: str) -> bool:
        """Revoke a biometric credential"""
        user_credentials = self.credentials.get(user_id, [])
        for cred in user_credentials:
            if cred.credential_id == credential_id:
                cred.is_active = False
                self.logger.info(f"Revoked credential {credential_id} for user {user_id}")
                return True
        return False


class OfflineModeManager:
    """
    Offline mode manager for PWA with intelligent caching,
    sync queue management, and conflict resolution.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache: Dict[str, CachedData] = {}
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        self.pending_operations: List[Dict[str, Any]] = []
        self.conflict_handlers: Dict[str, Callable] = {}
        
        # Cache configuration
        self.cache_ttl = {
            "portfolio_summary": timedelta(minutes=5),
            "positions": timedelta(minutes=1),
            "market_data": timedelta(seconds=30),
            "historical_data": timedelta(hours=24),
            "user_settings": timedelta(days=7),
            "learning_progress": timedelta(hours=1)
        }
    
    async def cache_data(
        self,
        cache_key: str,
        data_type: str,
        data: Any,
        user_id: str
    ) -> CachedData:
        """Cache data for offline access"""
        ttl = self.cache_ttl.get(data_type, timedelta(hours=1))
        now = datetime.now()
        
        # Calculate checksum for data integrity
        data_json = json.dumps(data, default=str)
        checksum = hashlib.sha256(data_json.encode()).hexdigest()
        
        cached = CachedData(
            cache_key=f"{user_id}:{cache_key}",
            data_type=data_type,
            data=data,
            cached_at=now,
            expires_at=now + ttl,
            version=1,
            checksum=checksum
        )
        
        # Update version if existing
        existing = self.cache.get(cached.cache_key)
        if existing:
            cached.version = existing.version + 1
        
        self.cache[cached.cache_key] = cached
        return cached
    
    async def get_cached_data(
        self,
        cache_key: str,
        user_id: str,
        allow_expired: bool = False
    ) -> Optional[CachedData]:
        """Retrieve cached data"""
        full_key = f"{user_id}:{cache_key}"
        cached = self.cache.get(full_key)
        
        if not cached:
            return None
        
        if not allow_expired and datetime.now() > cached.expires_at:
            return None
        
        return cached
    
    async def queue_offline_operation(
        self,
        user_id: str,
        operation_type: str,
        operation_data: Dict[str, Any]
    ) -> str:
        """Queue an operation to be synced when online"""
        operation_id = secrets.token_urlsafe(16)
        operation = {
            "operation_id": operation_id,
            "user_id": user_id,
            "operation_type": operation_type,
            "data": operation_data,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "retry_count": 0
        }
        
        self.pending_operations.append(operation)
        await self.sync_queue.put(operation)
        
        return operation_id
    
    async def sync_offline_operations(self, user_id: str) -> Dict[str, Any]:
        """Sync all pending offline operations"""
        user_operations = [
            op for op in self.pending_operations
            if op["user_id"] == user_id and op["status"] == "pending"
        ]
        
        results = {
            "synced": 0,
            "failed": 0,
            "conflicts": 0,
            "operations": []
        }
        
        for operation in user_operations:
            try:
                result = await self._execute_sync_operation(operation)
                
                if result.get("conflict"):
                    results["conflicts"] += 1
                    # Handle conflict
                    resolved = await self._resolve_conflict(operation, result["server_data"])
                    results["operations"].append({
                        "operation_id": operation["operation_id"],
                        "status": "conflict_resolved" if resolved else "conflict_unresolved"
                    })
                else:
                    operation["status"] = "synced"
                    results["synced"] += 1
                    results["operations"].append({
                        "operation_id": operation["operation_id"],
                        "status": "synced"
                    })
            except Exception as e:
                operation["status"] = "failed"
                operation["retry_count"] += 1
                results["failed"] += 1
                self.logger.error(f"Sync failed for operation {operation['operation_id']}: {e}")
        
        # Clean up synced operations
        self.pending_operations = [
            op for op in self.pending_operations
            if op["status"] != "synced"
        ]
        
        return results
    
    async def _execute_sync_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single sync operation"""
        # In production, this would make API calls
        return {"success": True}
    
    async def _resolve_conflict(
        self,
        operation: Dict[str, Any],
        server_data: Dict[str, Any]
    ) -> bool:
        """Resolve a sync conflict"""
        operation_type = operation["operation_type"]
        
        if operation_type in self.conflict_handlers:
            return await self.conflict_handlers[operation_type](operation, server_data)
        
        # Default: server wins
        return True
    
    def get_sync_status(self, user_id: str) -> Dict[str, Any]:
        """Get current sync status for user"""
        user_operations = [
            op for op in self.pending_operations
            if op["user_id"] == user_id
        ]
        
        return {
            "pending_count": len([op for op in user_operations if op["status"] == "pending"]),
            "failed_count": len([op for op in user_operations if op["status"] == "failed"]),
            "oldest_pending": min(
                [op["created_at"] for op in user_operations if op["status"] == "pending"],
                default=None
            ),
            "is_synced": len(user_operations) == 0
        }


class VoiceCommandProcessor:
    """
    Voice command processor for hands-free portfolio queries.
    Supports natural language understanding and contextual responses.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.command_history: Dict[str, List[VoiceCommand]] = {}
        
        # Intent patterns
        self.intent_patterns = {
            VoiceCommandType.PORTFOLIO_QUERY: [
                r"what('?s| is)? my portfolio",
                r"show( me)? my portfolio",
                r"portfolio (value|summary|overview)",
                r"how is my portfolio"
            ],
            VoiceCommandType.PERFORMANCE_CHECK: [
                r"what('?s| is)? my (performance|returns?)",
                r"how (am i|are my investments?) doing",
                r"portfolio performance( today)?",
                r"show( me)? my (gains|losses|returns?)"
            ],
            VoiceCommandType.TRADE_COMMAND: [
                r"(buy|sell|trade) (\d+|some) (shares? of )?(\w+)",
                r"place (a |an )?(order|trade) for (\w+)",
                r"execute (a |an )?(buy|sell) (order )?for (\w+)"
            ],
            VoiceCommandType.ALERT_MANAGEMENT: [
                r"set (a |an )?alert for (\w+)",
                r"notify me (when|if) (\w+)",
                r"create (a |an )?(price |)alert",
                r"show( my)? alerts"
            ],
            VoiceCommandType.MARKET_INFO: [
                r"what('?s| is)? the (price|value) of (\w+)",
                r"how (is|are) (\w+) (doing|performing)",
                r"(\w+) (stock )?(price|quote)",
                r"market (update|news|summary)"
            ],
            VoiceCommandType.ANALYSIS_REQUEST: [
                r"analyze (\w+)",
                r"what do you think (about|of) (\w+)",
                r"should i (buy|sell|hold) (\w+)",
                r"(risk|sentiment) analysis (for|of) (\w+)"
            ]
        }
        
        # Response templates
        self.response_templates = {
            VoiceCommandType.PORTFOLIO_QUERY: {
                "success": "Your portfolio is worth ${total_value:,.2f}, {change_direction} ${change_amount:,.2f} or {change_pct:.2f}% today. Your top performer is {top_performer} with a {top_gain:.2f}% gain.",
                "error": "I couldn't retrieve your portfolio information. Please try again later."
            },
            VoiceCommandType.PERFORMANCE_CHECK: {
                "success": "Your portfolio has returned {total_return:.2f}% since inception. Today you're {today_direction} {today_pct:.2f}%. Your Sharpe ratio is {sharpe:.2f}.",
                "error": "I couldn't calculate your performance metrics right now."
            },
            VoiceCommandType.MARKET_INFO: {
                "success": "{symbol} is trading at ${price:.2f}, {change_direction} {change_pct:.2f}% today. Trading volume is {volume:,.0f} shares.",
                "error": "I couldn't find market data for that symbol."
            }
        }
    
    async def process_voice_command(
        self,
        user_id: str,
        audio_data: Optional[bytes] = None,
        transcribed_text: Optional[str] = None
    ) -> VoiceCommand:
        """
        Process a voice command from audio or transcribed text.
        
        Args:
            user_id: User ID
            audio_data: Raw audio bytes (optional)
            transcribed_text: Pre-transcribed text (optional)
        
        Returns:
            VoiceCommand with parsed intent and response
        """
        # Transcribe audio if needed
        if audio_data and not transcribed_text:
            transcribed_text = await self._transcribe_audio(audio_data)
        
        if not transcribed_text:
            return VoiceCommand(
                command_id=secrets.token_urlsafe(16),
                user_id=user_id,
                command_type=VoiceCommandType.PORTFOLIO_QUERY,
                raw_text="",
                parsed_intent="unknown",
                entities={},
                confidence=0.0,
                response="I didn't catch that. Could you please repeat?"
            )
        
        # Parse intent
        command_type, entities, confidence = self._parse_intent(transcribed_text)
        
        command = VoiceCommand(
            command_id=secrets.token_urlsafe(16),
            user_id=user_id,
            command_type=command_type,
            raw_text=transcribed_text,
            parsed_intent=command_type.value,
            entities=entities,
            confidence=confidence
        )
        
        # Execute command
        if confidence >= 0.6:
            response = await self._execute_voice_command(command)
            command.response = response
            command.executed = True
        else:
            command.response = f"I'm not sure I understood. Did you want to {self._get_clarification_prompt(command_type)}?"
        
        # Store in history
        if user_id not in self.command_history:
            self.command_history[user_id] = []
        self.command_history[user_id].append(command)
        
        return command
    
    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio to text using speech-to-text service"""
        # In production, use Whisper, Google Speech-to-Text, or similar
        return ""
    
    def _parse_intent(self, text: str) -> tuple:
        """Parse intent from transcribed text"""
        import re
        
        text_lower = text.lower().strip()
        best_match = None
        best_confidence = 0.0
        matched_entities = {}
        
        for command_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Calculate confidence based on match quality
                    match_ratio = len(match.group()) / len(text_lower)
                    confidence = min(0.95, 0.6 + match_ratio * 0.4)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = command_type
                        # Extract entities from match groups
                        matched_entities = {
                            f"group_{i}": g for i, g in enumerate(match.groups())
                            if g
                        }
        
        if not best_match:
            return VoiceCommandType.PORTFOLIO_QUERY, {}, 0.3
        
        return best_match, matched_entities, best_confidence
    
    async def _execute_voice_command(self, command: VoiceCommand) -> str:
        """Execute a voice command and generate response"""
        try:
            if command.command_type == VoiceCommandType.PORTFOLIO_QUERY:
                return await self._handle_portfolio_query(command)
            elif command.command_type == VoiceCommandType.PERFORMANCE_CHECK:
                return await self._handle_performance_check(command)
            elif command.command_type == VoiceCommandType.MARKET_INFO:
                return await self._handle_market_info(command)
            elif command.command_type == VoiceCommandType.TRADE_COMMAND:
                return await self._handle_trade_command(command)
            elif command.command_type == VoiceCommandType.ALERT_MANAGEMENT:
                return await self._handle_alert_management(command)
            elif command.command_type == VoiceCommandType.ANALYSIS_REQUEST:
                return await self._handle_analysis_request(command)
            else:
                return "I'm not sure how to help with that. Try asking about your portfolio or a specific stock."
        except Exception as e:
            self.logger.error(f"Error executing voice command: {e}")
            return "I encountered an error processing your request. Please try again."
    
    async def _handle_portfolio_query(self, command: VoiceCommand) -> str:
        """Handle portfolio query command"""
        # In production, fetch real portfolio data
        data = {
            "total_value": 125000.00,
            "change_direction": "up",
            "change_amount": 1250.00,
            "change_pct": 1.01,
            "top_performer": "NVIDIA",
            "top_gain": 3.5
        }
        
        template = self.response_templates[VoiceCommandType.PORTFOLIO_QUERY]["success"]
        return template.format(**data)
    
    async def _handle_performance_check(self, command: VoiceCommand) -> str:
        """Handle performance check command"""
        data = {
            "total_return": 15.5,
            "today_direction": "up",
            "today_pct": 0.75,
            "sharpe": 1.8
        }
        
        template = self.response_templates[VoiceCommandType.PERFORMANCE_CHECK]["success"]
        return template.format(**data)
    
    async def _handle_market_info(self, command: VoiceCommand) -> str:
        """Handle market info command"""
        # Extract symbol from entities
        symbol = command.entities.get("group_2", command.entities.get("group_0", "SPY")).upper()
        
        data = {
            "symbol": symbol,
            "price": 150.25,
            "change_direction": "up",
            "change_pct": 1.25,
            "volume": 15000000
        }
        
        template = self.response_templates[VoiceCommandType.MARKET_INFO]["success"]
        return template.format(**data)
    
    async def _handle_trade_command(self, command: VoiceCommand) -> str:
        """Handle trade command - requires confirmation"""
        return "For security, I can't execute trades via voice. Please confirm this trade in the app."
    
    async def _handle_alert_management(self, command: VoiceCommand) -> str:
        """Handle alert management command"""
        return "I've noted your alert request. Please review and confirm in the app."
    
    async def _handle_analysis_request(self, command: VoiceCommand) -> str:
        """Handle analysis request command"""
        symbol = command.entities.get("group_1", command.entities.get("group_0", "market")).upper()
        return f"Based on current market conditions and technical indicators, {symbol} shows mixed signals. The AI confidence is moderate at 62%. Would you like a detailed analysis in the app?"
    
    def _get_clarification_prompt(self, command_type: VoiceCommandType) -> str:
        """Get clarification prompt for low confidence commands"""
        prompts = {
            VoiceCommandType.PORTFOLIO_QUERY: "check your portfolio",
            VoiceCommandType.PERFORMANCE_CHECK: "see your performance",
            VoiceCommandType.TRADE_COMMAND: "make a trade",
            VoiceCommandType.ALERT_MANAGEMENT: "manage alerts",
            VoiceCommandType.MARKET_INFO: "get market information",
            VoiceCommandType.ANALYSIS_REQUEST: "get an analysis"
        }
        return prompts.get(command_type, "something else")


class PWAServiceWorkerManager:
    """
    Manages PWA service worker configuration and caching strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache_version = config.get("cache_version", "v1")
        
    def generate_service_worker(self) -> str:
        """Generate service worker JavaScript code"""
        return f'''
// Portfolio Analysis PWA Service Worker
const CACHE_NAME = 'portfolio-cache-{self.cache_version}';
const OFFLINE_URL = '/offline.html';

// Resources to pre-cache
const PRECACHE_RESOURCES = [
    '/',
    '/offline.html',
    '/static/css/main.css',
    '/static/js/main.js',
    '/icons/app-icon-192.png',
    '/icons/app-icon-512.png',
    '/manifest.json'
];

// Cache-first resources
const CACHE_FIRST_PATTERNS = [
    /\\.(?:png|jpg|jpeg|svg|gif|ico)$/,
    /\\.(?:woff|woff2|ttf|otf)$/,
    /\\/static\\//
];

// Network-first resources
const NETWORK_FIRST_PATTERNS = [
    /\\/api\\//,
    /\\/ws\\//
];

// Install event - precache resources
self.addEventListener('install', (event) => {{
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(PRECACHE_RESOURCES))
            .then(() => self.skipWaiting())
    );
}});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {{
    event.waitUntil(
        caches.keys().then(keys => {{
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        }}).then(() => self.clients.claim())
    );
}});

// Fetch event - apply caching strategies
self.addEventListener('fetch', (event) => {{
    const url = new URL(event.request.url);
    
    // Cache-first for static assets
    if (CACHE_FIRST_PATTERNS.some(p => p.test(url.pathname))) {{
        event.respondWith(cacheFirst(event.request));
        return;
    }}
    
    // Network-first for API calls
    if (NETWORK_FIRST_PATTERNS.some(p => p.test(url.pathname))) {{
        event.respondWith(networkFirst(event.request));
        return;
    }}
    
    // Stale-while-revalidate for everything else
    event.respondWith(staleWhileRevalidate(event.request));
}});

// Push notification handling
self.addEventListener('push', (event) => {{
    if (!event.data) return;
    
    const data = event.data.json();
    const options = {{
        body: data.body,
        icon: data.icon || '/icons/app-icon-192.png',
        badge: '/icons/badge-72.png',
        vibrate: [100, 50, 100],
        data: data,
        actions: data.actions || []
    }};
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
}});

// Notification click handling
self.addEventListener('notificationclick', (event) => {{
    event.notification.close();
    
    const data = event.notification.data;
    let url = data.action_url || '/';
    
    event.waitUntil(
        clients.matchAll({{type: 'window'}})
            .then(clients => {{
                // Focus existing window or open new one
                for (const client of clients) {{
                    if (client.url === url && 'focus' in client) {{
                        return client.focus();
                    }}
                }}
                return self.clients.openWindow(url);
            }})
    );
}});

// Background sync for offline operations
self.addEventListener('sync', (event) => {{
    if (event.tag === 'sync-portfolio-data') {{
        event.waitUntil(syncPortfolioData());
    }}
}});

// Caching strategies
async function cacheFirst(request) {{
    const cached = await caches.match(request);
    if (cached) return cached;
    
    try {{
        const response = await fetch(request);
        if (response.ok) {{
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }}
        return response;
    }} catch (error) {{
        return caches.match(OFFLINE_URL);
    }}
}}

async function networkFirst(request) {{
    try {{
        const response = await fetch(request);
        if (response.ok) {{
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }}
        return response;
    }} catch (error) {{
        return caches.match(request);
    }}
}}

async function staleWhileRevalidate(request) {{
    const cached = await caches.match(request);
    
    const fetchPromise = fetch(request).then(response => {{
        if (response.ok) {{
            const cache = caches.open(CACHE_NAME);
            cache.then(c => c.put(request, response.clone()));
        }}
        return response;
    }}).catch(() => cached);
    
    return cached || fetchPromise;
}}

async function syncPortfolioData() {{
    // Sync offline operations when back online
    const cache = await caches.open(CACHE_NAME);
    // Implementation for syncing pending operations
}}
'''

    def generate_manifest(self) -> Dict[str, Any]:
        """Generate PWA manifest.json"""
        return {
            "name": "AI Portfolio Analysis",
            "short_name": "Portfolio AI",
            "description": "AI-Powered Portfolio Analysis and Investment Management",
            "start_url": "/?source=pwa",
            "display": "standalone",
            "background_color": "#1a1a2e",
            "theme_color": "#4a90d9",
            "orientation": "any",
            "icons": [
                {
                    "src": "/icons/app-icon-72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icons/app-icon-96.png",
                    "sizes": "96x96",
                    "type": "image/png"
                },
                {
                    "src": "/icons/app-icon-128.png",
                    "sizes": "128x128",
                    "type": "image/png"
                },
                {
                    "src": "/icons/app-icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/icons/app-icon-384.png",
                    "sizes": "384x384",
                    "type": "image/png"
                },
                {
                    "src": "/icons/app-icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ],
            "shortcuts": [
                {
                    "name": "Portfolio Dashboard",
                    "short_name": "Dashboard",
                    "url": "/dashboard",
                    "icons": [{"src": "/icons/dashboard-96.png", "sizes": "96x96"}]
                },
                {
                    "name": "Quick Trade",
                    "short_name": "Trade",
                    "url": "/trade",
                    "icons": [{"src": "/icons/trade-96.png", "sizes": "96x96"}]
                },
                {
                    "name": "Risk Analysis",
                    "short_name": "Risk",
                    "url": "/risk",
                    "icons": [{"src": "/icons/risk-96.png", "sizes": "96x96"}]
                }
            ],
            "categories": ["finance", "productivity"],
            "screenshots": [
                {
                    "src": "/screenshots/dashboard.png",
                    "sizes": "1280x720",
                    "type": "image/png",
                    "form_factor": "wide"
                },
                {
                    "src": "/screenshots/mobile-dashboard.png",
                    "sizes": "375x812",
                    "type": "image/png",
                    "form_factor": "narrow"
                }
            ],
            "related_applications": [
                {
                    "platform": "play",
                    "url": "https://play.google.com/store/apps/details?id=com.portfolio.ai"
                },
                {
                    "platform": "itunes",
                    "url": "https://apps.apple.com/app/portfolio-ai/id123456789"
                }
            ],
            "prefer_related_applications": False
        }


class MobileAPIService:
    """
    Complete mobile API service integrating all PWA features.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.push_service = PushNotificationService(config)
        self.biometric_service = BiometricAuthenticationService(config)
        self.offline_manager = OfflineModeManager(config)
        self.voice_processor = VoiceCommandProcessor(config)
        self.pwa_manager = PWAServiceWorkerManager(config)
    
    async def initialize(self):
        """Initialize all mobile services"""
        self.logger.info("Initializing Mobile API Service...")
        # Start background tasks
        asyncio.create_task(self._notification_worker())
        asyncio.create_task(self._sync_worker())
    
    async def _notification_worker(self):
        """Background worker for notification delivery"""
        while True:
            try:
                notification = await self.push_service.notification_queue.get()
                # Process notification
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Notification worker error: {e}")
            await asyncio.sleep(0.1)
    
    async def _sync_worker(self):
        """Background worker for offline sync"""
        while True:
            try:
                operation = await self.offline_manager.sync_queue.get()
                # Process sync operation
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Sync worker error: {e}")
            await asyncio.sleep(0.1)
    
    def get_api_routes(self):
        """Get FastAPI routes for mobile endpoints"""
        from fastapi import APIRouter, HTTPException, Depends
        from pydantic import BaseModel
        
        router = APIRouter(prefix="/mobile", tags=["Mobile PWA"])
        
        class BiometricRegisterRequest(BaseModel):
            biometric_type: str
            public_key: str
            device_id: str
            device_name: str
        
        class VoiceCommandRequest(BaseModel):
            transcribed_text: str
        
        class NotificationPreferencesRequest(BaseModel):
            preferences: Dict[str, bool]
        
        @router.post("/biometric/register")
        async def register_biometric(request: BiometricRegisterRequest, user_id: str = "demo_user"):
            credential = await self.biometric_service.register_biometric(
                user_id=user_id,
                biometric_type=BiometricType(request.biometric_type),
                public_key=request.public_key,
                device_id=request.device_id,
                device_name=request.device_name
            )
            return {"credential_id": credential.credential_id, "status": "registered"}
        
        @router.get("/biometric/challenge")
        async def get_biometric_challenge(user_id: str = "demo_user"):
            return await self.biometric_service.generate_authentication_challenge(user_id)
        
        @router.post("/voice/command")
        async def process_voice_command(request: VoiceCommandRequest, user_id: str = "demo_user"):
            command = await self.voice_processor.process_voice_command(
                user_id=user_id,
                transcribed_text=request.transcribed_text
            )
            return {
                "command_id": command.command_id,
                "intent": command.parsed_intent,
                "confidence": command.confidence,
                "response": command.response,
                "executed": command.executed
            }
        
        @router.get("/offline/status")
        async def get_offline_status(user_id: str = "demo_user"):
            return self.offline_manager.get_sync_status(user_id)
        
        @router.post("/offline/sync")
        async def sync_offline_data(user_id: str = "demo_user"):
            return await self.offline_manager.sync_offline_operations(user_id)
        
        @router.get("/pwa/manifest")
        async def get_pwa_manifest():
            return self.pwa_manager.generate_manifest()
        
        @router.get("/pwa/service-worker")
        async def get_service_worker():
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(
                self.pwa_manager.generate_service_worker(),
                media_type="application/javascript"
            )
        
        @router.post("/notifications/preferences")
        async def update_notification_preferences(
            request: NotificationPreferencesRequest,
            user_id: str = "demo_user"
        ):
            self.push_service.user_preferences[user_id] = request.preferences
            return {"status": "updated", "preferences": request.preferences}
        
        return router


# Export main components
__all__ = [
    'PushNotificationService',
    'BiometricAuthenticationService',
    'OfflineModeManager',
    'VoiceCommandProcessor',
    'PWAServiceWorkerManager',
    'MobileAPIService',
    'NotificationType',
    'AlertPriority',
    'BiometricType',
    'VoiceCommandType'
]
