"""
AutoML Pipeline
===============

Automated machine learning for portfolio analysis:
- Model selection
- Hyperparameter optimization
- Feature engineering automation
- Model validation and comparison
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod


class ModelType(Enum):
    """Types of models"""
    LINEAR_REGRESSION = "linear_regression"
    RIDGE = "ridge"
    LASSO = "lasso"
    ELASTIC_NET = "elastic_net"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    SVM = "svm"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"


class TaskType(Enum):
    """ML task types"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    TIME_SERIES = "time_series"
    ANOMALY_DETECTION = "anomaly_detection"


@dataclass
class ModelConfig:
    """Model configuration"""
    model_type: ModelType
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    
    # Search space for hyperparameters
    search_space: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ModelResult:
    """Results from model training/evaluation"""
    model_type: ModelType
    hyperparameters: Dict[str, Any]
    
    # Metrics
    train_score: float = 0.0
    val_score: float = 0.0
    test_score: float = 0.0
    
    # Additional metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Timing
    training_time: float = 0.0
    inference_time: float = 0.0
    
    # Feature importance
    feature_importance: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_type': self.model_type.value,
            'hyperparameters': self.hyperparameters,
            'scores': {
                'train': self.train_score,
                'validation': self.val_score,
                'test': self.test_score
            },
            'metrics': self.metrics,
            'training_time': self.training_time
        }


class BaseModel(ABC):
    """Base class for models"""
    
    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray):
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        pass


class LinearRegressionModel(BaseModel):
    """Simple linear regression"""
    
    def __init__(self, alpha: float = 0.0):
        self.alpha = alpha
        self.weights = None
        self.bias = None
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        # Add regularization
        n_features = X.shape[1]
        X_b = np.c_[np.ones((X.shape[0], 1)), X]
        
        if self.alpha > 0:
            reg_matrix = self.alpha * np.eye(n_features + 1)
            reg_matrix[0, 0] = 0
            theta = np.linalg.inv(X_b.T @ X_b + reg_matrix) @ X_b.T @ y
        else:
            theta = np.linalg.pinv(X_b) @ y
        
        self.bias = theta[0]
        self.weights = theta[1:]
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self.weights + self.bias
    
    def get_params(self) -> Dict[str, Any]:
        return {'alpha': self.alpha}


class RandomForestModel(BaseModel):
    """Simplified random forest implementation"""
    
    def __init__(
        self,
        n_trees: int = 10,
        max_depth: int = 5,
        min_samples_split: int = 2
    ):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees: List[Dict[str, Any]] = []
        self.feature_importances_: np.ndarray = None
    
    def _build_tree(
        self,
        X: np.ndarray,
        y: np.ndarray,
        depth: int = 0
    ) -> Dict[str, Any]:
        """Build a decision tree"""
        n_samples, n_features = X.shape
        
        # Base cases
        if depth >= self.max_depth or n_samples < self.min_samples_split:
            return {'value': np.mean(y)}
        
        # Find best split
        best_feature = None
        best_threshold = None
        best_gain = -float('inf')
        
        for feature in range(n_features):
            thresholds = np.unique(X[:, feature])
            
            for threshold in thresholds[::max(1, len(thresholds) // 10)]:
                left_mask = X[:, feature] <= threshold
                right_mask = ~left_mask
                
                if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
                    continue
                
                # Calculate variance reduction
                left_var = np.var(y[left_mask]) * np.sum(left_mask)
                right_var = np.var(y[right_mask]) * np.sum(right_mask)
                parent_var = np.var(y) * n_samples
                
                gain = parent_var - (left_var + right_var)
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
        
        if best_feature is None:
            return {'value': np.mean(y)}
        
        left_mask = X[:, best_feature] <= best_threshold
        right_mask = ~left_mask
        
        return {
            'feature': best_feature,
            'threshold': best_threshold,
            'left': self._build_tree(X[left_mask], y[left_mask], depth + 1),
            'right': self._build_tree(X[right_mask], y[right_mask], depth + 1)
        }
    
    def _predict_tree(self, tree: Dict[str, Any], x: np.ndarray) -> float:
        """Predict with a single tree"""
        if 'value' in tree:
            return tree['value']
        
        if x[tree['feature']] <= tree['threshold']:
            return self._predict_tree(tree['left'], x)
        else:
            return self._predict_tree(tree['right'], x)
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        self.trees = []
        n_samples = X.shape[0]
        n_features = X.shape[1]
        
        feature_usage = np.zeros(n_features)
        
        for _ in range(self.n_trees):
            # Bootstrap sample
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_boot = X[indices]
            y_boot = y[indices]
            
            tree = self._build_tree(X_boot, y_boot)
            self.trees.append(tree)
        
        # Simple feature importance (placeholder)
        self.feature_importances_ = np.ones(n_features) / n_features
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        predictions = np.zeros((X.shape[0], len(self.trees)))
        
        for i, tree in enumerate(self.trees):
            for j, x in enumerate(X):
                predictions[j, i] = self._predict_tree(tree, x)
        
        return np.mean(predictions, axis=1)
    
    def get_params(self) -> Dict[str, Any]:
        return {
            'n_trees': self.n_trees,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split
        }


class HyperparameterOptimizer:
    """
    Hyperparameter optimization using various strategies.
    """
    
    def __init__(
        self,
        strategy: str = "random",
        n_iterations: int = 20,
        cv_folds: int = 5
    ):
        self.logger = logging.getLogger("hyperopt")
        self.strategy = strategy
        self.n_iterations = n_iterations
        self.cv_folds = cv_folds
        self.results: List[Dict[str, Any]] = []
    
    def optimize(
        self,
        model_class: type,
        search_space: Dict[str, Dict[str, Any]],
        X: np.ndarray,
        y: np.ndarray,
        scoring_fn: Callable
    ) -> Tuple[Dict[str, Any], float]:
        """Optimize hyperparameters"""
        best_params = None
        best_score = -float('inf')
        
        for i in range(self.n_iterations):
            # Sample hyperparameters
            params = self._sample_params(search_space)
            
            # Cross-validation
            scores = []
            fold_size = len(X) // self.cv_folds
            
            for fold in range(self.cv_folds):
                # Split data
                val_start = fold * fold_size
                val_end = val_start + fold_size
                
                X_val = X[val_start:val_end]
                y_val = y[val_start:val_end]
                X_train = np.concatenate([X[:val_start], X[val_end:]])
                y_train = np.concatenate([y[:val_start], y[val_end:]])
                
                # Train and evaluate
                try:
                    model = model_class(**params)
                    model.fit(X_train, y_train)
                    predictions = model.predict(X_val)
                    score = scoring_fn(y_val, predictions)
                    scores.append(score)
                except Exception as e:
                    self.logger.warning(f"Trial failed: {e}")
                    scores.append(-float('inf'))
            
            avg_score = np.mean(scores)
            
            self.results.append({
                'iteration': i,
                'params': params,
                'score': avg_score
            })
            
            if avg_score > best_score:
                best_score = avg_score
                best_params = params
                self.logger.info(f"New best: {best_score:.4f} with {params}")
        
        return best_params, best_score
    
    def _sample_params(
        self,
        search_space: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Sample hyperparameters from search space"""
        params = {}
        
        for param_name, space in search_space.items():
            param_type = space.get('type', 'float')
            
            if param_type == 'int':
                params[param_name] = np.random.randint(
                    space['low'],
                    space['high'] + 1
                )
            elif param_type == 'float':
                if space.get('log', False):
                    log_low = np.log(space['low'])
                    log_high = np.log(space['high'])
                    params[param_name] = np.exp(
                        np.random.uniform(log_low, log_high)
                    )
                else:
                    params[param_name] = np.random.uniform(
                        space['low'],
                        space['high']
                    )
            elif param_type == 'choice':
                params[param_name] = np.random.choice(space['options'])
        
        return params


class ModelSelector:
    """
    Automated model selection.
    """
    
    def __init__(self, task_type: TaskType = TaskType.REGRESSION):
        self.logger = logging.getLogger("model_selector")
        self.task_type = task_type
        self.available_models = self._get_available_models()
        self.results: List[ModelResult] = []
    
    def _get_available_models(self) -> Dict[ModelType, type]:
        """Get available models for task type"""
        if self.task_type == TaskType.REGRESSION:
            return {
                ModelType.LINEAR_REGRESSION: LinearRegressionModel,
                ModelType.RIDGE: lambda **kw: LinearRegressionModel(alpha=kw.get('alpha', 1.0)),
                ModelType.RANDOM_FOREST: RandomForestModel,
            }
        return {}
    
    def _get_search_spaces(self) -> Dict[ModelType, Dict[str, Dict[str, Any]]]:
        """Get hyperparameter search spaces"""
        return {
            ModelType.LINEAR_REGRESSION: {},
            ModelType.RIDGE: {
                'alpha': {'type': 'float', 'low': 0.001, 'high': 100.0, 'log': True}
            },
            ModelType.RANDOM_FOREST: {
                'n_trees': {'type': 'int', 'low': 5, 'high': 50},
                'max_depth': {'type': 'int', 'low': 2, 'high': 10},
                'min_samples_split': {'type': 'int', 'low': 2, 'high': 20}
            }
        }
    
    def select_best_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        metric: str = "mse"
    ) -> Tuple[BaseModel, ModelResult]:
        """Select best model from candidates"""
        scoring_fn = self._get_scoring_function(metric)
        search_spaces = self._get_search_spaces()
        
        optimizer = HyperparameterOptimizer(n_iterations=10)
        
        best_model = None
        best_result = None
        best_val_score = -float('inf')
        
        for model_type, model_class in self.available_models.items():
            self.logger.info(f"Evaluating {model_type.value}")
            
            search_space = search_spaces.get(model_type, {})
            
            if search_space:
                # Hyperparameter optimization
                best_params, _ = optimizer.optimize(
                    model_class, search_space, X_train, y_train, scoring_fn
                )
            else:
                best_params = {}
            
            # Train with best params
            start_time = datetime.now()
            
            model = model_class(**best_params) if callable(model_class) else model_class
            model.fit(X_train, y_train)
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Evaluate
            train_pred = model.predict(X_train)
            val_pred = model.predict(X_val)
            
            train_score = scoring_fn(y_train, train_pred)
            val_score = scoring_fn(y_val, val_pred)
            
            result = ModelResult(
                model_type=model_type,
                hyperparameters=best_params,
                train_score=train_score,
                val_score=val_score,
                training_time=training_time,
                metrics={
                    'mse': -scoring_fn(y_val, val_pred) if metric == 'mse' else 0,
                    'mae': np.mean(np.abs(y_val - val_pred))
                }
            )
            
            self.results.append(result)
            
            if val_score > best_val_score:
                best_val_score = val_score
                best_model = model
                best_result = result
        
        self.logger.info(f"Best model: {best_result.model_type.value} (score: {best_val_score:.4f})")
        
        return best_model, best_result
    
    def _get_scoring_function(self, metric: str) -> Callable:
        """Get scoring function (higher is better)"""
        if metric == "mse":
            return lambda y, pred: -np.mean((y - pred) ** 2)
        elif metric == "mae":
            return lambda y, pred: -np.mean(np.abs(y - pred))
        elif metric == "r2":
            return lambda y, pred: 1 - np.sum((y - pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
        else:
            return lambda y, pred: -np.mean((y - pred) ** 2)


class FeatureEngineer:
    """
    Automated feature engineering.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("feature_engineer")
        self.feature_names: List[str] = []
        self.transformations: List[Dict[str, Any]] = []
    
    def fit_transform(
        self,
        X: np.ndarray,
        feature_names: List[str] = None
    ) -> np.ndarray:
        """Automatically engineer features"""
        n_samples, n_features = X.shape
        
        if feature_names:
            self.feature_names = feature_names
        else:
            self.feature_names = [f"feature_{i}" for i in range(n_features)]
        
        new_features = [X]
        new_names = list(self.feature_names)
        
        # Polynomial features (degree 2)
        for i in range(n_features):
            new_features.append(X[:, i:i+1] ** 2)
            new_names.append(f"{self.feature_names[i]}_squared")
            self.transformations.append({
                'type': 'polynomial',
                'feature': i,
                'degree': 2
            })
        
        # Interaction features
        for i in range(min(n_features, 5)):
            for j in range(i + 1, min(n_features, 5)):
                new_features.append((X[:, i] * X[:, j]).reshape(-1, 1))
                new_names.append(f"{self.feature_names[i]}*{self.feature_names[j]}")
                self.transformations.append({
                    'type': 'interaction',
                    'features': [i, j]
                })
        
        # Log features (for positive values)
        for i in range(n_features):
            if np.all(X[:, i] > 0):
                new_features.append(np.log(X[:, i:i+1] + 1e-8))
                new_names.append(f"log_{self.feature_names[i]}")
                self.transformations.append({
                    'type': 'log',
                    'feature': i
                })
        
        X_transformed = np.hstack(new_features)
        self.feature_names = new_names
        
        self.logger.info(f"Engineered {X_transformed.shape[1]} features from {n_features}")
        
        return X_transformed
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Apply saved transformations"""
        new_features = [X]
        
        for transform in self.transformations:
            if transform['type'] == 'polynomial':
                new_features.append(X[:, transform['feature']:transform['feature']+1] ** transform['degree'])
            elif transform['type'] == 'interaction':
                i, j = transform['features']
                new_features.append((X[:, i] * X[:, j]).reshape(-1, 1))
            elif transform['type'] == 'log':
                new_features.append(np.log(X[:, transform['feature']:transform['feature']+1] + 1e-8))
        
        return np.hstack(new_features)


class AutoMLPipeline:
    """
    Complete AutoML pipeline for financial analysis.
    """
    
    def __init__(
        self,
        task_type: TaskType = TaskType.REGRESSION,
        auto_feature_engineering: bool = True,
        n_hyperopt_iterations: int = 20
    ):
        self.logger = logging.getLogger("automl_pipeline")
        self.task_type = task_type
        self.auto_feature_engineering = auto_feature_engineering
        self.n_hyperopt_iterations = n_hyperopt_iterations
        
        self.feature_engineer = FeatureEngineer() if auto_feature_engineering else None
        self.model_selector = ModelSelector(task_type)
        
        self.best_model: Optional[BaseModel] = None
        self.best_result: Optional[ModelResult] = None
        self.pipeline_results: Dict[str, Any] = {}
    
    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        feature_names: List[str] = None
    ) -> Dict[str, Any]:
        """Fit the AutoML pipeline"""
        start_time = datetime.now()
        
        # Feature engineering
        if self.auto_feature_engineering:
            self.logger.info("Starting feature engineering")
            X_train = self.feature_engineer.fit_transform(X_train, feature_names)
            X_val = self.feature_engineer.transform(X_val)
        
        # Model selection
        self.logger.info("Starting model selection")
        self.best_model, self.best_result = self.model_selector.select_best_model(
            X_train, y_train, X_val, y_val
        )
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        self.pipeline_results = {
            'total_time': total_time,
            'best_model': self.best_result.to_dict(),
            'feature_count': X_train.shape[1],
            'all_results': [r.to_dict() for r in self.model_selector.results]
        }
        
        self.logger.info(f"Pipeline complete in {total_time:.2f}s")
        
        return self.pipeline_results
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with best model"""
        if self.best_model is None:
            raise ValueError("Pipeline not fitted")
        
        if self.auto_feature_engineering:
            X = self.feature_engineer.transform(X)
        
        return self.best_model.predict(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance"""
        if self.best_result and self.best_result.feature_importance:
            return self.best_result.feature_importance
        
        if self.feature_engineer:
            # Return equal importance as placeholder
            return {
                name: 1.0 / len(self.feature_engineer.feature_names)
                for name in self.feature_engineer.feature_names
            }
        
        return {}
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline execution"""
        return {
            'task_type': self.task_type.value,
            'auto_feature_engineering': self.auto_feature_engineering,
            'best_model': self.best_result.model_type.value if self.best_result else None,
            'best_score': self.best_result.val_score if self.best_result else None,
            'models_evaluated': len(self.model_selector.results),
            'total_features': len(self.feature_engineer.feature_names) if self.feature_engineer else 0,
            'results': self.pipeline_results
        }
