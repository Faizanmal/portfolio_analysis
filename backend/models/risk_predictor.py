"""
Financial Risk Prediction Model

This module implements a machine learning model for predicting financial risk
of portfolio companies using historical financial data and market indicators.

Features:
- Multi-class risk classification (Low, Medium, High)
- Feature engineering from financial statements
- Model training, evaluation, and persistence
- API-ready prediction interface
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

class RiskPredictor:
    """
    Financial Risk Prediction Model using ensemble methods.
    
    Attributes:
        model: Trained ML model
        scaler: Feature scaler
        feature_names: List of feature names
        metrics: Model performance metrics
    """
    
    def __init__(self, model_path: str = "data/models/risk_predictor.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.metrics = {}
        
        # Create model directory if it doesn't exist
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer financial features from raw data.
        
        Args:
            df: DataFrame with financial data
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features...")
        
        features = df.copy()
        
        # Financial Ratios
        features['debt_to_equity'] = features['total_debt'] / features['total_equity']
        features['current_ratio'] = features['current_assets'] / features['current_liabilities']
        features['profit_margin'] = features['net_income'] / features['revenue']
        features['roe'] = features['net_income'] / features['total_equity']
        features['roa'] = features['net_income'] / features['total_assets']
        
        # Growth Metrics
        features['revenue_growth'] = features.groupby('company_id')['revenue'].pct_change()
        features['income_growth'] = features.groupby('company_id')['net_income'].pct_change()
        
        # Liquidity Metrics
        features['cash_ratio'] = features['cash'] / features['current_liabilities']
        features['quick_ratio'] = (features['current_assets'] - features['inventory']) / features['current_liabilities']
        
        # Efficiency Metrics
        features['asset_turnover'] = features['revenue'] / features['total_assets']
        features['inventory_turnover'] = features['cogs'] / features['inventory']
        
        # Volatility Features
        features['revenue_volatility'] = features.groupby('company_id')['revenue'].transform(
            lambda x: x.rolling(window=4, min_periods=1).std()
        )
        
        # Fill NaN values
        features = features.fillna(features.median(numeric_only=True))
        
        logger.info(f"Engineered {len(features.columns)} features")
        return features
    
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'risk_level'):
        """
        Prepare data for training/prediction.
        
        Args:
            df: Input DataFrame
            target_col: Name of target column
            
        Returns:
            X, y arrays
        """
        # Remove non-feature columns
        exclude_cols = [target_col, 'company_id', 'date', 'company_name']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols].values
        y = df[target_col].values if target_col in df.columns else None
        
        self.feature_names = feature_cols
        
        return X, y
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2, optimize: bool = True):
        """
        Train the risk prediction model.
        
        Args:
            df: Training DataFrame with features and target
            test_size: Proportion of data for testing
            optimize: Whether to perform hyperparameter optimization
        """
        logger.info("Starting model training...")
        
        # Engineer features
        df_features = self.engineer_features(df)
        
        # Prepare data
        X, y = self.prepare_data(df_features)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        if optimize:
            logger.info("Optimizing hyperparameters...")
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            grid_search = GridSearchCV(
                RandomForestClassifier(random_state=42),
                param_grid,
                cv=5,
                scoring='f1_weighted',
                n_jobs=-1
            )
            
            grid_search.fit(X_train_scaled, y_train)
            self.model = grid_search.best_estimator_
            logger.info(f"Best parameters: {grid_search.best_params_}")
        else:
            # Use default model
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        y_pred = self.model.predict(X_test_scaled)
        
        logger.info(f"Training accuracy: {train_score:.4f}")
        logger.info(f"Testing accuracy: {test_score:.4f}")
        
        # Store metrics
        self.metrics = {
            'train_accuracy': float(train_score),
            'test_accuracy': float(test_score),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': dict(zip(
                self.feature_names,
                self.model.feature_importances_.tolist()
            )),
            'trained_at': datetime.now().isoformat()
        }
        
        # Print classification report
        logger.info("\nClassification Report:")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        
        return self.metrics
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Make risk predictions.
        
        Args:
            df: DataFrame with features
            
        Returns:
            Array of predictions
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first or load a saved model.")
        
        # Engineer features
        df_features = self.engineer_features(df)
        
        # Prepare data
        X, _ = self.prepare_data(df_features)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities.
        
        Args:
            df: DataFrame with features
            
        Returns:
            Array of probability predictions
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first or load a saved model.")
        
        # Engineer features
        df_features = self.engineer_features(df)
        
        # Prepare data
        X, _ = self.prepare_data(df_features)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict probabilities
        probabilities = self.model.predict_proba(X_scaled)
        
        return probabilities
    
    def get_feature_importance(self, top_n: int = 10) -> dict:
        """
        Get top N most important features.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            Dictionary of feature importances
        """
        if self.model is None:
            raise ValueError("Model not trained.")
        
        importance_dict = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # Sort by importance
        sorted_features = sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        return dict(sorted_features)
    
    def save_model(self):
        """Save the trained model and scaler."""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metrics': self.metrics
        }
        
        joblib.dump(model_data, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
        
        # Save metrics separately
        metrics_path = self.model_path.parent / 'risk_predictor_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info(f"Metrics saved to {metrics_path}")
    
    def load_model(self):
        """Load a saved model."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        model_data = joblib.load(self.model_path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.metrics = model_data.get('metrics', {})
        
        logger.info(f"Model loaded from {self.model_path}")


def generate_sample_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate sample financial data for demonstration.
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        DataFrame with sample financial data
    """
    np.random.seed(42)
    
    data = {
        'company_id': np.random.randint(1, 51, n_samples),
        'date': pd.date_range('2020-01-01', periods=n_samples, freq='ME'),
        'revenue': np.random.uniform(1_000_000, 100_000_000, n_samples),
        'cogs': np.random.uniform(500_000, 60_000_000, n_samples),
        'net_income': np.random.uniform(-5_000_000, 20_000_000, n_samples),
        'total_assets': np.random.uniform(5_000_000, 200_000_000, n_samples),
        'total_debt': np.random.uniform(1_000_000, 80_000_000, n_samples),
        'total_equity': np.random.uniform(2_000_000, 120_000_000, n_samples),
        'current_assets': np.random.uniform(2_000_000, 80_000_000, n_samples),
        'current_liabilities': np.random.uniform(1_000_000, 40_000_000, n_samples),
        'cash': np.random.uniform(500_000, 30_000_000, n_samples),
        'inventory': np.random.uniform(200_000, 10_000_000, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate risk levels based on some logic
    df['debt_to_equity_temp'] = df['total_debt'] / df['total_equity']
    df['profit_margin_temp'] = df['net_income'] / df['revenue']
    
    conditions = [
        (df['debt_to_equity_temp'] < 0.5) & (df['profit_margin_temp'] > 0.1),
        (df['debt_to_equity_temp'] < 1.5) & (df['profit_margin_temp'] > 0),
    ]
    choices = ['Low', 'Medium']
    df['risk_level'] = np.select(conditions, choices, default='High')
    
    df = df.drop(['debt_to_equity_temp', 'profit_margin_temp'], axis=1)
    
    return df


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/risk_predictor.log", rotation="10 MB")
    
    # Generate sample data
    logger.info("Generating sample data...")
    df = generate_sample_data(n_samples=2000)
    
    # Save sample data
    data_path = Path("data/processed/financial_data.csv")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(data_path, index=False)
    logger.info(f"Sample data saved to {data_path}")
    
    # Train model
    predictor = RiskPredictor()
    metrics = predictor.train(df, optimize=False)
    
    # Save model
    predictor.save_model()
    
    # Test prediction
    logger.info("\nTesting prediction on new data...")
    test_data = generate_sample_data(n_samples=10)
    predictions = predictor.predict(test_data)
    probabilities = predictor.predict_proba(test_data)
    
    logger.info(f"Predictions: {predictions}")
    logger.info(f"Probabilities shape: {probabilities.shape}")
    
    # Display feature importance
    logger.info("\nTop 10 Important Features:")
    importance = predictor.get_feature_importance(top_n=10)
    for feature, score in importance.items():
        logger.info(f"{feature}: {score:.4f}")
