"""
Federated Learning
==================

Privacy-preserving federated learning for portfolio analysis:
- Decentralized model training
- Secure aggregation
- Differential privacy
- Multi-party computation concepts
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
import hashlib


class AggregationStrategy(Enum):
    """Model aggregation strategies"""
    FEDAVG = "federated_averaging"
    WEIGHTED_AVG = "weighted_averaging"
    MEDIAN = "median"
    TRIMMED_MEAN = "trimmed_mean"
    KRUM = "krum"


class PrivacyMechanism(Enum):
    """Privacy mechanisms"""
    NONE = "none"
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    SECURE_AGGREGATION = "secure_aggregation"
    HOMOMORPHIC = "homomorphic"


@dataclass
class ModelUpdate:
    """Model update from a federated client"""
    client_id: str
    round_number: int
    weights: Dict[str, np.ndarray]
    num_samples: int
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_weight_hash(self) -> str:
        """Get hash of weights for verification"""
        weight_bytes = b"".join(w.tobytes() for w in self.weights.values())
        return hashlib.sha256(weight_bytes).hexdigest()[:16]


@dataclass
class FederatedRound:
    """A round of federated learning"""
    round_id: str
    round_number: int
    
    # Configuration
    min_clients: int = 2
    target_clients: int = 10
    
    # State
    updates: List[ModelUpdate] = field(default_factory=list)
    aggregated_weights: Dict[str, np.ndarray] = field(default_factory=dict)
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Metrics
    global_metrics: Dict[str, float] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        return len(self.updates) >= self.min_clients


class PrivacyPreserving:
    """
    Privacy-preserving mechanisms for federated learning.
    """
    
    def __init__(
        self,
        mechanism: PrivacyMechanism = PrivacyMechanism.DIFFERENTIAL_PRIVACY,
        epsilon: float = 1.0,
        delta: float = 1e-5
    ):
        self.logger = logging.getLogger("privacy")
        self.mechanism = mechanism
        self.epsilon = epsilon  # Privacy budget
        self.delta = delta  # Failure probability
    
    def add_noise(
        self,
        weights: Dict[str, np.ndarray],
        sensitivity: float = 1.0
    ) -> Dict[str, np.ndarray]:
        """Add differential privacy noise to weights"""
        if self.mechanism != PrivacyMechanism.DIFFERENTIAL_PRIVACY:
            return weights
        
        # Gaussian mechanism
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        
        noisy_weights = {}
        for name, weight in weights.items():
            noise = np.random.normal(0, sigma, weight.shape)
            noisy_weights[name] = weight + noise
        
        self.logger.debug(f"Added DP noise with sigma={sigma:.4f}")
        return noisy_weights
    
    def clip_gradients(
        self,
        gradients: Dict[str, np.ndarray],
        max_norm: float = 1.0
    ) -> Dict[str, np.ndarray]:
        """Clip gradients for differential privacy"""
        # Calculate total gradient norm
        total_norm = np.sqrt(sum(
            np.sum(g ** 2) for g in gradients.values()
        ))
        
        # Clip if necessary
        clip_factor = min(1.0, max_norm / (total_norm + 1e-6))
        
        return {
            name: grad * clip_factor
            for name, grad in gradients.items()
        }
    
    def secure_aggregate(
        self,
        updates: List[Dict[str, np.ndarray]]
    ) -> Dict[str, np.ndarray]:
        """
        Secure aggregation (simplified version).
        In production, use proper MPC protocols.
        """
        if not updates:
            return {}
        
        # Simple averaging (production would use secret sharing)
        aggregated = {}
        
        for key in updates[0].keys():
            stacked = np.stack([u[key] for u in updates])
            aggregated[key] = np.mean(stacked, axis=0)
        
        return aggregated


class FederatedClient:
    """
    Federated learning client that trains locally.
    """
    
    def __init__(
        self,
        client_id: str,
        privacy: PrivacyPreserving = None
    ):
        self.client_id = client_id
        self.logger = logging.getLogger(f"fed_client_{client_id[:8]}")
        self.privacy = privacy or PrivacyPreserving()
        
        # Local model weights
        self.local_weights: Dict[str, np.ndarray] = {}
        self.training_data: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
    
    def set_model_weights(self, weights: Dict[str, np.ndarray]):
        """Set model weights from server"""
        self.local_weights = {k: v.copy() for k, v in weights.items()}
    
    def set_training_data(
        self,
        data: np.ndarray,
        labels: np.ndarray
    ):
        """Set local training data"""
        self.training_data = data
        self.labels = labels
    
    def train_local(
        self,
        epochs: int = 1,
        learning_rate: float = 0.01,
        batch_size: int = 32
    ) -> ModelUpdate:
        """Train on local data"""
        if self.training_data is None:
            raise ValueError("No training data set")
        
        num_samples = len(self.training_data)
        
        # Simulate training (in production, use actual training loop)
        for epoch in range(epochs):
            for i in range(0, num_samples, batch_size):
                batch_data = self.training_data[i:i+batch_size]
                batch_labels = self.labels[i:i+batch_size]
                
                # Compute gradients (simplified)
                for name, weight in self.local_weights.items():
                    gradient = np.random.randn(*weight.shape) * 0.01
                    clipped_grad = self.privacy.clip_gradients(
                        {name: gradient}
                    )[name]
                    self.local_weights[name] -= learning_rate * clipped_grad
        
        # Calculate local metrics
        metrics = {
            'loss': np.random.uniform(0.1, 0.5),
            'accuracy': np.random.uniform(0.7, 0.95)
        }
        
        # Apply privacy mechanisms
        private_weights = self.privacy.add_noise(self.local_weights)
        
        update = ModelUpdate(
            client_id=self.client_id,
            round_number=0,  # Will be set by coordinator
            weights=private_weights,
            num_samples=num_samples,
            metrics=metrics
        )
        
        self.logger.info(f"Local training complete, samples: {num_samples}")
        return update


class FederatedLearningCoordinator:
    """
    Coordinates federated learning across multiple clients.
    """
    
    def __init__(
        self,
        aggregation: AggregationStrategy = AggregationStrategy.FEDAVG,
        privacy: PrivacyPreserving = None,
        min_clients: int = 2
    ):
        self.logger = logging.getLogger("fed_coordinator")
        self.aggregation = aggregation
        self.privacy = privacy or PrivacyPreserving()
        self.min_clients = min_clients
        
        # State
        self.global_weights: Dict[str, np.ndarray] = {}
        self.clients: Dict[str, FederatedClient] = {}
        self.rounds: List[FederatedRound] = []
        self.current_round: Optional[FederatedRound] = None
        
        # Metrics
        self.global_metrics_history: List[Dict[str, float]] = []
    
    def initialize_model(self, architecture: Dict[str, Tuple[int, ...]]):
        """Initialize global model weights"""
        for name, shape in architecture.items():
            # Xavier initialization
            if len(shape) >= 2:
                fan_in = shape[0] if len(shape) > 1 else 1
                fan_out = shape[1] if len(shape) > 1 else shape[0]
                std = np.sqrt(2.0 / (fan_in + fan_out))
            else:
                std = 0.1
            
            self.global_weights[name] = np.random.randn(*shape) * std
        
        self.logger.info(f"Initialized model with {len(architecture)} layers")
    
    def register_client(self, client: FederatedClient):
        """Register a federated client"""
        self.clients[client.client_id] = client
        client.set_model_weights(self.global_weights)
        self.logger.info(f"Registered client: {client.client_id[:8]}")
    
    def start_round(self) -> FederatedRound:
        """Start a new training round"""
        round_number = len(self.rounds) + 1
        
        self.current_round = FederatedRound(
            round_id=str(uuid.uuid4()),
            round_number=round_number,
            min_clients=self.min_clients,
            target_clients=len(self.clients)
        )
        
        # Distribute current global weights to clients
        for client in self.clients.values():
            client.set_model_weights(self.global_weights)
        
        self.logger.info(f"Started round {round_number}")
        return self.current_round
    
    def submit_update(self, update: ModelUpdate) -> bool:
        """Submit a model update from a client"""
        if self.current_round is None:
            self.logger.error("No active round")
            return False
        
        if update.client_id not in self.clients:
            self.logger.error(f"Unknown client: {update.client_id[:8]}")
            return False
        
        update.round_number = self.current_round.round_number
        self.current_round.updates.append(update)
        
        self.logger.info(
            f"Received update from {update.client_id[:8]}, "
            f"total updates: {len(self.current_round.updates)}"
        )
        
        return True
    
    def aggregate_updates(self) -> Dict[str, np.ndarray]:
        """Aggregate updates from clients"""
        if not self.current_round or not self.current_round.updates:
            return {}
        
        updates = self.current_round.updates
        
        if self.aggregation == AggregationStrategy.FEDAVG:
            aggregated = self._federated_averaging(updates)
        elif self.aggregation == AggregationStrategy.WEIGHTED_AVG:
            aggregated = self._weighted_averaging(updates)
        elif self.aggregation == AggregationStrategy.MEDIAN:
            aggregated = self._median_aggregation(updates)
        elif self.aggregation == AggregationStrategy.TRIMMED_MEAN:
            aggregated = self._trimmed_mean(updates)
        else:
            aggregated = self._federated_averaging(updates)
        
        return aggregated
    
    def _federated_averaging(
        self,
        updates: List[ModelUpdate]
    ) -> Dict[str, np.ndarray]:
        """Standard FedAvg aggregation"""
        total_samples = sum(u.num_samples for u in updates)
        
        aggregated = {}
        for key in updates[0].weights.keys():
            weighted_sum = sum(
                u.weights[key] * u.num_samples
                for u in updates
            )
            aggregated[key] = weighted_sum / total_samples
        
        return aggregated
    
    def _weighted_averaging(
        self,
        updates: List[ModelUpdate]
    ) -> Dict[str, np.ndarray]:
        """Weighted averaging based on sample count"""
        return self._federated_averaging(updates)
    
    def _median_aggregation(
        self,
        updates: List[ModelUpdate]
    ) -> Dict[str, np.ndarray]:
        """Median aggregation (Byzantine-robust)"""
        aggregated = {}
        
        for key in updates[0].weights.keys():
            stacked = np.stack([u.weights[key] for u in updates])
            aggregated[key] = np.median(stacked, axis=0)
        
        return aggregated
    
    def _trimmed_mean(
        self,
        updates: List[ModelUpdate],
        trim_ratio: float = 0.1
    ) -> Dict[str, np.ndarray]:
        """Trimmed mean aggregation"""
        n_updates = len(updates)
        n_trim = max(1, int(n_updates * trim_ratio))
        
        aggregated = {}
        for key in updates[0].weights.keys():
            stacked = np.stack([u.weights[key] for u in updates])
            sorted_weights = np.sort(stacked, axis=0)
            trimmed = sorted_weights[n_trim:-n_trim] if n_trim > 0 else sorted_weights
            aggregated[key] = np.mean(trimmed, axis=0)
        
        return aggregated
    
    def complete_round(self) -> Dict[str, Any]:
        """Complete the current round and update global model"""
        if not self.current_round:
            return {'error': 'No active round'}
        
        if len(self.current_round.updates) < self.min_clients:
            return {
                'error': f'Not enough updates ({len(self.current_round.updates)}/{self.min_clients})'
            }
        
        # Aggregate updates
        aggregated = self.aggregate_updates()
        
        # Update global weights
        self.global_weights = aggregated
        self.current_round.aggregated_weights = aggregated
        self.current_round.completed_at = datetime.now()
        
        # Calculate global metrics
        avg_loss = np.mean([u.metrics.get('loss', 0) for u in self.current_round.updates])
        avg_accuracy = np.mean([u.metrics.get('accuracy', 0) for u in self.current_round.updates])
        
        global_metrics = {
            'round': self.current_round.round_number,
            'num_clients': len(self.current_round.updates),
            'total_samples': sum(u.num_samples for u in self.current_round.updates),
            'avg_loss': avg_loss,
            'avg_accuracy': avg_accuracy
        }
        
        self.current_round.global_metrics = global_metrics
        self.global_metrics_history.append(global_metrics)
        
        # Archive round
        self.rounds.append(self.current_round)
        self.current_round = None
        
        self.logger.info(
            f"Round {global_metrics['round']} complete: "
            f"loss={avg_loss:.4f}, accuracy={avg_accuracy:.4f}"
        )
        
        return global_metrics
    
    def train_rounds(
        self,
        num_rounds: int,
        local_epochs: int = 1
    ) -> List[Dict[str, float]]:
        """Run multiple rounds of federated training"""
        results = []
        
        for _ in range(num_rounds):
            # Start round
            self.start_round()
            
            # Each client trains locally
            for client in self.clients.values():
                if client.training_data is not None:
                    update = client.train_local(epochs=local_epochs)
                    self.submit_update(update)
            
            # Complete round
            metrics = self.complete_round()
            if 'error' not in metrics:
                results.append(metrics)
        
        return results
    
    def get_model_for_inference(self) -> Dict[str, np.ndarray]:
        """Get current global model for inference"""
        return {k: v.copy() for k, v in self.global_weights.items()}
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get summary of federated training"""
        return {
            'total_rounds': len(self.rounds),
            'total_clients': len(self.clients),
            'aggregation_strategy': self.aggregation.value,
            'privacy_mechanism': self.privacy.mechanism.value,
            'metrics_history': self.global_metrics_history,
            'final_metrics': self.global_metrics_history[-1] if self.global_metrics_history else {}
        }
