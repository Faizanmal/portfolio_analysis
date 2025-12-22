"""
Advanced ML Module
==================

Advanced AI/ML capabilities:
- Federated learning for privacy
- Graph neural networks for relationships
- Reinforcement learning optimization
- Multi-modal AI analysis
- AutoML for model selection
"""

from .federated_learning import FederatedLearningCoordinator, FederatedClient, PrivacyPreserving
from .graph_networks import GraphNeuralNetwork, PortfolioGraph, RelationshipAnalyzer
from .reinforcement_learning import RLPortfolioOptimizer, TradingEnvironment, PPOAgent
from .multi_modal import MultiModalAnalyzer, DocumentProcessor, ImageAnalyzer
from .automl import AutoMLPipeline, ModelSelector, HyperparameterOptimizer

__all__ = [
    # Federated Learning
    'FederatedLearningCoordinator',
    'FederatedClient',
    'PrivacyPreserving',
    
    # Graph Networks
    'GraphNeuralNetwork',
    'PortfolioGraph',
    'RelationshipAnalyzer',
    
    # Reinforcement Learning
    'RLPortfolioOptimizer',
    'TradingEnvironment',
    'PPOAgent',
    
    # Multi-Modal
    'MultiModalAnalyzer',
    'DocumentProcessor',
    'ImageAnalyzer',
    
    # AutoML
    'AutoMLPipeline',
    'ModelSelector',
    'HyperparameterOptimizer',
]
