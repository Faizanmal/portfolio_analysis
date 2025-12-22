"""
Portfolio Optimization Model

Implements modern portfolio theory and optimization algorithms for 
asset allocation and portfolio construction.

Features:
- Mean-variance optimization
- Risk parity allocation
- Black-Litterman model
- Portfolio rebalancing recommendations
- Risk metrics calculation
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict
import json
from pathlib import Path
from loguru import logger
import matplotlib.pyplot as plt


class PortfolioOptimizer:
    """
    Portfolio optimization using modern portfolio theory.
    
    Supports multiple optimization strategies:
    - Maximum Sharpe Ratio
    - Minimum Volatility
    - Risk Parity
    - Target Return
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer.
        
        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.risk_free_rate = risk_free_rate
        self.returns = None
        self.mean_returns = None
        self.cov_matrix = None
        self.assets = None
        
    def load_data(self, returns_df: pd.DataFrame):
        """
        Load returns data for optimization.
        
        Args:
            returns_df: DataFrame with asset returns (columns = assets, rows = time periods)
        """
        self.returns = returns_df
        self.assets = returns_df.columns.tolist()
        self.mean_returns = returns_df.mean()
        self.cov_matrix = returns_df.cov()
        
        logger.info(f"Loaded data for {len(self.assets)} assets")
        logger.info(f"Time periods: {len(returns_df)}")
    
    def calculate_portfolio_metrics(self, weights: np.ndarray) -> Dict:
        """
        Calculate portfolio return, volatility, and Sharpe ratio.
        
        Args:
            weights: Array of portfolio weights
            
        Returns:
            Dictionary with portfolio metrics
        """
        portfolio_return = np.sum(self.mean_returns * weights) * 252  # Annualized
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix * 252, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        
        return {
            'return': float(portfolio_return),
            'volatility': float(portfolio_std),
            'sharpe_ratio': float(sharpe_ratio)
        }
    
    def optimize_max_sharpe(self) -> Dict:
        """
        Optimize portfolio for maximum Sharpe ratio.
        
        Returns:
            Optimal weights and portfolio metrics
        """
        logger.info("Optimizing for maximum Sharpe ratio...")
        
        num_assets = len(self.assets)
        
        def neg_sharpe(weights):
            metrics = self.calculate_portfolio_metrics(weights)
            return -metrics['sharpe_ratio']
        
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        
        # Bounds: 0 <= weight <= 1
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        # Initial guess: equal weights
        init_weights = np.array([1/num_assets] * num_assets)
        
        # Optimize
        result = minimize(
            neg_sharpe,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        metrics = self.calculate_portfolio_metrics(optimal_weights)
        
        return {
            'weights': dict(zip(self.assets, optimal_weights.tolist())),
            'metrics': metrics,
            'success': result.success
        }
    
    def optimize_min_volatility(self) -> Dict:
        """
        Optimize portfolio for minimum volatility.
        
        Returns:
            Optimal weights and portfolio metrics
        """
        logger.info("Optimizing for minimum volatility...")
        
        num_assets = len(self.assets)
        
        def portfolio_volatility(weights):
            return self.calculate_portfolio_metrics(weights)['volatility']
        
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(num_assets))
        init_weights = np.array([1/num_assets] * num_assets)
        
        result = minimize(
            portfolio_volatility,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        metrics = self.calculate_portfolio_metrics(optimal_weights)
        
        return {
            'weights': dict(zip(self.assets, optimal_weights.tolist())),
            'metrics': metrics,
            'success': result.success
        }
    
    def optimize_target_return(self, target_return: float) -> Dict:
        """
        Optimize portfolio for minimum risk at target return.
        
        Args:
            target_return: Target annual return
            
        Returns:
            Optimal weights and portfolio metrics
        """
        logger.info(f"Optimizing for target return: {target_return:.2%}")
        
        num_assets = len(self.assets)
        
        def portfolio_volatility(weights):
            return self.calculate_portfolio_metrics(weights)['volatility']
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: self.calculate_portfolio_metrics(x)['return'] - target_return}
        ]
        
        bounds = tuple((0, 1) for _ in range(num_assets))
        init_weights = np.array([1/num_assets] * num_assets)
        
        result = minimize(
            portfolio_volatility,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_weights = result.x
            metrics = self.calculate_portfolio_metrics(optimal_weights)
        else:
            logger.warning("Optimization failed to converge")
            optimal_weights = init_weights
            metrics = self.calculate_portfolio_metrics(optimal_weights)
        
        return {
            'weights': dict(zip(self.assets, optimal_weights.tolist())),
            'metrics': metrics,
            'success': result.success
        }
    
    def risk_parity_optimization(self) -> Dict:
        """
        Optimize portfolio using risk parity approach.
        Each asset contributes equally to portfolio risk.
        
        Returns:
            Optimal weights and portfolio metrics
        """
        logger.info("Optimizing using risk parity...")
        
        num_assets = len(self.assets)
        
        def risk_parity_objective(weights):
            # Calculate risk contribution of each asset
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix * 252, weights)))
            marginal_contrib = np.dot(self.cov_matrix * 252, weights)
            risk_contrib = weights * marginal_contrib / portfolio_vol
            
            # Minimize difference from equal risk contribution
            target_risk = portfolio_vol / num_assets
            return np.sum((risk_contrib - target_risk) ** 2)
        
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0.001, 1) for _ in range(num_assets))  # Small minimum to avoid division by zero
        init_weights = np.array([1/num_assets] * num_assets)
        
        result = minimize(
            risk_parity_objective,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        metrics = self.calculate_portfolio_metrics(optimal_weights)
        
        return {
            'weights': dict(zip(self.assets, optimal_weights.tolist())),
            'metrics': metrics,
            'success': result.success
        }
    
    def efficient_frontier(self, n_points: int = 50) -> pd.DataFrame:
        """
        Generate efficient frontier.
        
        Args:
            n_points: Number of points on the frontier
            
        Returns:
            DataFrame with frontier points
        """
        logger.info(f"Generating efficient frontier with {n_points} points...")
        
        min_return = self.mean_returns.min() * 252
        max_return = self.mean_returns.max() * 252
        
        target_returns = np.linspace(min_return, max_return, n_points)
        
        frontier_results = []
        
        for target in target_returns:
            result = self.optimize_target_return(target)
            if result['success']:
                frontier_results.append({
                    'return': result['metrics']['return'],
                    'volatility': result['metrics']['volatility'],
                    'sharpe_ratio': result['metrics']['sharpe_ratio']
                })
        
        return pd.DataFrame(frontier_results)
    
    def rebalancing_recommendation(self, current_weights: Dict, target_weights: Dict) -> Dict:
        """
        Generate rebalancing recommendations.
        
        Args:
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            
        Returns:
            Rebalancing instructions
        """
        logger.info("Generating rebalancing recommendations...")
        
        trades = {}
        for asset in self.assets:
            current = current_weights.get(asset, 0.0)
            target = target_weights.get(asset, 0.0)
            difference = target - current
            
            if abs(difference) > 0.01:  # Only recommend if difference > 1%
                trades[asset] = {
                    'current': current,
                    'target': target,
                    'change': difference,
                    'action': 'BUY' if difference > 0 else 'SELL'
                }
        
        return trades
    
    def plot_efficient_frontier(self, save_path: str = None):
        """
        Plot the efficient frontier.
        
        Args:
            save_path: Path to save the plot
        """
        frontier_df = self.efficient_frontier()
        
        plt.figure(figsize=(12, 8))
        plt.scatter(frontier_df['volatility'], frontier_df['return'], 
                   c=frontier_df['sharpe_ratio'], cmap='viridis', s=50)
        plt.colorbar(label='Sharpe Ratio')
        plt.xlabel('Volatility (Annual)')
        plt.ylabel('Expected Return (Annual)')
        plt.title('Efficient Frontier')
        plt.grid(True, alpha=0.3)
        
        # Add annotations for max Sharpe ratio
        max_sharpe_idx = frontier_df['sharpe_ratio'].idxmax()
        max_sharpe_point = frontier_df.loc[max_sharpe_idx]
        plt.scatter(max_sharpe_point['volatility'], max_sharpe_point['return'], 
                   color='red', s=200, marker='*', label='Max Sharpe Ratio')
        plt.legend()
        
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def save_results(self, results: Dict, output_path: str):
        """
        Save optimization results.
        
        Args:
            results: Results dictionary
            output_path: Path to save results
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")


def generate_sample_returns(n_assets: int = 5, n_periods: int = 252) -> pd.DataFrame:
    """
    Generate sample return data for demonstration.
    
    Args:
        n_assets: Number of assets
        n_periods: Number of time periods
        
    Returns:
        DataFrame with returns
    """
    np.random.seed(42)
    
    # Generate correlated returns
    mean_returns = np.random.uniform(0.0001, 0.001, n_assets)
    volatilities = np.random.uniform(0.01, 0.03, n_assets)
    
    # Create correlation matrix
    correlation = np.random.uniform(0.3, 0.7, (n_assets, n_assets))
    correlation = (correlation + correlation.T) / 2
    np.fill_diagonal(correlation, 1)
    
    # Generate returns
    returns = np.random.multivariate_normal(
        mean_returns,
        correlation * np.outer(volatilities, volatilities),
        n_periods
    )
    
    asset_names = [f'Asset_{i+1}' for i in range(n_assets)]
    return pd.DataFrame(returns, columns=asset_names)


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/portfolio_optimizer.log", rotation="10 MB")
    
    # Generate sample data
    logger.info("Generating sample returns data...")
    returns_df = generate_sample_returns(n_assets=5, n_periods=252)
    
    # Save sample data
    data_path = Path("data/processed/portfolio_returns.csv")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    returns_df.to_csv(data_path, index=False)
    
    # Initialize optimizer
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    optimizer.load_data(returns_df)
    
    # Run different optimization strategies
    logger.info("\n" + "="*50)
    logger.info("OPTIMIZATION RESULTS")
    logger.info("="*50)
    
    # Maximum Sharpe Ratio
    max_sharpe = optimizer.optimize_max_sharpe()
    logger.info("\n1. Maximum Sharpe Ratio Portfolio:")
    logger.info(f"   Expected Return: {max_sharpe['metrics']['return']:.2%}")
    logger.info(f"   Volatility: {max_sharpe['metrics']['volatility']:.2%}")
    logger.info(f"   Sharpe Ratio: {max_sharpe['metrics']['sharpe_ratio']:.3f}")
    logger.info("   Weights:")
    for asset, weight in max_sharpe['weights'].items():
        logger.info(f"     {asset}: {weight:.2%}")
    
    # Minimum Volatility
    min_vol = optimizer.optimize_min_volatility()
    logger.info("\n2. Minimum Volatility Portfolio:")
    logger.info(f"   Expected Return: {min_vol['metrics']['return']:.2%}")
    logger.info(f"   Volatility: {min_vol['metrics']['volatility']:.2%}")
    logger.info(f"   Sharpe Ratio: {min_vol['metrics']['sharpe_ratio']:.3f}")
    
    # Risk Parity
    risk_parity = optimizer.risk_parity_optimization()
    logger.info("\n3. Risk Parity Portfolio:")
    logger.info(f"   Expected Return: {risk_parity['metrics']['return']:.2%}")
    logger.info(f"   Volatility: {risk_parity['metrics']['volatility']:.2%}")
    logger.info(f"   Sharpe Ratio: {risk_parity['metrics']['sharpe_ratio']:.3f}")
    
    # Save results
    all_results = {
        'max_sharpe': max_sharpe,
        'min_volatility': min_vol,
        'risk_parity': risk_parity
    }
    optimizer.save_results(all_results, "data/processed/optimization_results.json")
    
    # Generate efficient frontier plot
    optimizer.plot_efficient_frontier(save_path="data/processed/efficient_frontier.png")
    
    logger.info("\nOptimization complete!")
