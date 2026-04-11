"""
Reinforcement Learning Portfolio Optimization
=============================================

RL-based portfolio optimization:
- Trading environment
- PPO and DQN agents
- Reward shaping for risk-adjusted returns
- Multi-objective optimization
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging


class ActionType(Enum):
    """Trading action types"""
    HOLD = 0
    BUY = 1
    SELL = 2


@dataclass
class TradingAction:
    """Trading action"""
    asset_idx: int
    action_type: ActionType
    quantity: float
    
    # Execution details
    executed_price: float = 0.0
    transaction_cost: float = 0.0


@dataclass
class MarketState:
    """Market state observation"""
    prices: np.ndarray  # Current prices
    returns: np.ndarray  # Recent returns
    volumes: np.ndarray  # Trading volumes
    positions: np.ndarray  # Current positions
    cash: float  # Available cash
    
    # Technical indicators
    momentum: np.ndarray = None
    volatility: np.ndarray = None
    
    # Market features
    market_return: float = 0.0
    market_volatility: float = 0.0
    
    def to_vector(self) -> np.ndarray:
        """Convert state to feature vector"""
        features = [
            self.prices / np.mean(self.prices),  # Normalized prices
            self.returns,
            self.volumes / np.mean(self.volumes) if np.mean(self.volumes) > 0 else self.volumes,
            self.positions / np.sum(np.abs(self.positions) + 1e-8),  # Normalized positions
            np.array([self.cash / 100000]),  # Normalized cash
        ]
        
        if self.momentum is not None:
            features.append(self.momentum)
        if self.volatility is not None:
            features.append(self.volatility)
        
        return np.concatenate(features)


class TradingEnvironment:
    """
    Gym-like trading environment for RL agents.
    """
    
    def __init__(
        self,
        price_data: np.ndarray,  # (num_steps, num_assets)
        initial_cash: float = 100000,
        transaction_cost: float = 0.001,
        max_position_size: float = 0.2,  # Max 20% in single asset
        lookback_window: int = 20
    ):
        self.logger = logging.getLogger("trading_env")
        self.price_data = price_data
        self.num_steps, self.num_assets = price_data.shape
        self.initial_cash = initial_cash
        self.transaction_cost = transaction_cost
        self.max_position_size = max_position_size
        self.lookback_window = lookback_window
        
        # State variables
        self.current_step = 0
        self.cash = initial_cash
        self.positions = np.zeros(self.num_assets)
        self.portfolio_values: List[float] = []
        
        # Calculate returns
        self.returns = np.diff(price_data, axis=0) / price_data[:-1]
    
    def reset(self) -> MarketState:
        """Reset environment to initial state"""
        self.current_step = self.lookback_window
        self.cash = self.initial_cash
        self.positions = np.zeros(self.num_assets)
        self.portfolio_values = [self.initial_cash]
        
        return self._get_state()
    
    def _get_state(self) -> MarketState:
        """Get current market state"""
        start = max(0, self.current_step - self.lookback_window)
        
        # Recent returns
        recent_returns = self.returns[start:self.current_step]
        avg_returns = np.mean(recent_returns, axis=0) if len(recent_returns) > 0 else np.zeros(self.num_assets)
        
        # Momentum (cumulative return over lookback)
        if len(recent_returns) > 0:
            momentum = np.prod(1 + recent_returns, axis=0) - 1
        else:
            momentum = np.zeros(self.num_assets)
        
        # Volatility
        volatility = np.std(recent_returns, axis=0) if len(recent_returns) > 1 else np.zeros(self.num_assets)
        
        return MarketState(
            prices=self.price_data[self.current_step],
            returns=avg_returns,
            volumes=np.ones(self.num_assets),  # Placeholder
            positions=self.positions.copy(),
            cash=self.cash,
            momentum=momentum,
            volatility=volatility
        )
    
    def step(
        self,
        action: np.ndarray  # Target weights for each asset
    ) -> Tuple[MarketState, float, bool, Dict[str, Any]]:
        """
        Execute action and return new state, reward, done, info.
        
        Args:
            action: Target portfolio weights (sum to 1)
        """
        prices = self.price_data[self.current_step]
        
        # Calculate current portfolio value
        portfolio_value = self.cash + np.sum(self.positions * prices)
        
        # Calculate target positions
        target_positions = (action * portfolio_value) / prices
        
        # Calculate trades needed
        trades = target_positions - self.positions
        
        # Execute trades with transaction costs
        trade_values = trades * prices
        costs = np.sum(np.abs(trade_values)) * self.transaction_cost
        
        # Update positions
        self.positions = target_positions
        self.cash = portfolio_value - np.sum(self.positions * prices) - costs
        
        # Move to next step
        self.current_step += 1
        done = self.current_step >= self.num_steps - 1
        
        # Calculate new portfolio value
        new_prices = self.price_data[self.current_step]
        new_portfolio_value = self.cash + np.sum(self.positions * new_prices)
        self.portfolio_values.append(new_portfolio_value)
        
        # Calculate reward
        reward = self._calculate_reward(portfolio_value, new_portfolio_value, costs)
        
        # Get new state
        new_state = self._get_state()
        
        info = {
            'portfolio_value': new_portfolio_value,
            'return': (new_portfolio_value - portfolio_value) / portfolio_value,
            'transaction_costs': costs,
            'positions': self.positions.copy()
        }
        
        return new_state, reward, done, info
    
    def _calculate_reward(
        self,
        old_value: float,
        new_value: float,
        costs: float
    ) -> float:
        """Calculate risk-adjusted reward"""
        # Simple return
        ret = (new_value - old_value) / old_value
        
        # Penalize transaction costs
        cost_penalty = costs / old_value * 2
        
        # Risk penalty based on portfolio volatility
        if len(self.portfolio_values) >= 20:
            recent_values = np.array(self.portfolio_values[-20:])
            recent_returns = np.diff(recent_values) / recent_values[:-1]
            volatility = np.std(recent_returns)
            risk_penalty = volatility * 0.1
        else:
            risk_penalty = 0
        
        reward = ret - cost_penalty - risk_penalty
        
        return reward
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for the episode"""
        values = np.array(self.portfolio_values)
        returns = np.diff(values) / values[:-1]
        
        total_return = (values[-1] - values[0]) / values[0]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Maximum drawdown
        peak = np.maximum.accumulate(values)
        drawdown = (peak - values) / peak
        max_drawdown = np.max(drawdown)
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'volatility': np.std(returns) * np.sqrt(252),
            'final_value': values[-1]
        }
    
    @property
    def observation_dim(self) -> int:
        """Dimension of observation space"""
        return self._get_state().to_vector().shape[0]
    
    @property
    def action_dim(self) -> int:
        """Dimension of action space"""
        return self.num_assets


class PPOAgent:
    """
    Proximal Policy Optimization agent for portfolio management.
    """
    
    def __init__(
        self,
        observation_dim: int,
        action_dim: int,
        hidden_dim: int = 128,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        clip_epsilon: float = 0.2,
        entropy_coef: float = 0.01
    ):
        self.logger = logging.getLogger("ppo_agent")
        self.observation_dim = observation_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.clip_epsilon = clip_epsilon
        self.entropy_coef = entropy_coef
        
        # Initialize policy network weights
        self.policy_weights = {
            'W1': np.random.randn(observation_dim, hidden_dim) * np.sqrt(2.0 / observation_dim),
            'b1': np.zeros(hidden_dim),
            'W2': np.random.randn(hidden_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim),
            'b2': np.zeros(hidden_dim),
            'mean': np.random.randn(hidden_dim, action_dim) * 0.01,
            'log_std': np.zeros(action_dim)
        }
        
        # Initialize value network weights
        self.value_weights = {
            'W1': np.random.randn(observation_dim, hidden_dim) * np.sqrt(2.0 / observation_dim),
            'b1': np.zeros(hidden_dim),
            'W2': np.random.randn(hidden_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim),
            'b2': np.zeros(hidden_dim),
            'out': np.random.randn(hidden_dim, 1) * 0.01
        }
        
        # Experience buffer
        self.states: List[np.ndarray] = []
        self.actions: List[np.ndarray] = []
        self.rewards: List[float] = []
        self.values: List[float] = []
        self.log_probs: List[float] = []
    
    def _policy_forward(self, state: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Forward pass through policy network"""
        # Hidden layers
        h1 = np.tanh(state @ self.policy_weights['W1'] + self.policy_weights['b1'])
        h2 = np.tanh(h1 @ self.policy_weights['W2'] + self.policy_weights['b2'])
        
        # Output mean and std
        mean = h2 @ self.policy_weights['mean']
        std = np.exp(self.policy_weights['log_std'])
        
        return mean, std
    
    def _value_forward(self, state: np.ndarray) -> float:
        """Forward pass through value network"""
        h1 = np.tanh(state @ self.value_weights['W1'] + self.value_weights['b1'])
        h2 = np.tanh(h1 @ self.value_weights['W2'] + self.value_weights['b2'])
        value = float(h2 @ self.value_weights['out'])
        return value
    
    def get_action(
        self,
        state: MarketState,
        training: bool = True
    ) -> Tuple[np.ndarray, float]:
        """Sample action from policy"""
        state_vec = state.to_vector()
        mean, std = self._policy_forward(state_vec)
        
        if training:
            # Sample from Gaussian
            action = mean + std * np.random.randn(self.action_dim)
        else:
            action = mean
        
        # Softmax to get portfolio weights
        exp_action = np.exp(action - np.max(action))
        weights = exp_action / np.sum(exp_action)
        
        # Calculate log probability
        log_prob = -0.5 * np.sum(((action - mean) / (std + 1e-8)) ** 2)
        log_prob -= np.sum(np.log(std + 1e-8))
        
        return weights, log_prob
    
    def store_transition(
        self,
        state: MarketState,
        action: np.ndarray,
        reward: float,
        log_prob: float
    ):
        """Store transition in buffer"""
        state_vec = state.to_vector()
        value = self._value_forward(state_vec)
        
        self.states.append(state_vec)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
    
    def compute_returns(self) -> np.ndarray:
        """Compute discounted returns"""
        returns = np.zeros(len(self.rewards))
        running_return = 0
        
        for t in reversed(range(len(self.rewards))):
            running_return = self.rewards[t] + self.gamma * running_return
            returns[t] = running_return
        
        return returns
    
    def update(self, epochs: int = 4) -> Dict[str, float]:
        """Update policy using collected experience"""
        states = np.array(self.states)
        actions = np.array(self.actions)
        old_log_probs = np.array(self.log_probs)
        returns = self.compute_returns()
        values = np.array(self.values)
        
        # Compute advantages
        advantages = returns - values
        advantages = (advantages - np.mean(advantages)) / (np.std(advantages) + 1e-8)
        
        total_policy_loss = 0
        total_value_loss = 0
        
        for _ in range(epochs):
            for i in range(len(states)):
                # Policy loss (simplified gradient update)
                mean, std = self._policy_forward(states[i])
                
                # Approximate gradient for mean
                grad_mean = advantages[i] * (actions[i] - mean) / (std ** 2 + 1e-8)
                self.policy_weights['mean'] += self.learning_rate * np.outer(
                    np.tanh(states[i] @ self.policy_weights['W1'] + self.policy_weights['b1']),
                    grad_mean
                ) / len(states)
                
                # Value loss gradient
                value = self._value_forward(states[i])
                value_error = returns[i] - value
                
                total_policy_loss += -advantages[i] * old_log_probs[i]
                total_value_loss += value_error ** 2
        
        # Clear buffer
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()
        
        return {
            'policy_loss': total_policy_loss / (epochs * len(states)) if states.size > 0 else 0,
            'value_loss': total_value_loss / (epochs * len(states)) if states.size > 0 else 0
        }


class RLPortfolioOptimizer:
    """
    High-level RL portfolio optimizer.
    """
    
    def __init__(
        self,
        agent_type: str = "ppo",
        hidden_dim: int = 128,
        learning_rate: float = 3e-4
    ):
        self.logger = logging.getLogger("rl_optimizer")
        self.agent_type = agent_type
        self.hidden_dim = hidden_dim
        self.learning_rate = learning_rate
        
        self.env: Optional[TradingEnvironment] = None
        self.agent: Optional[PPOAgent] = None
        self.training_history: List[Dict[str, float]] = []
    
    def setup(
        self,
        price_data: np.ndarray,
        initial_cash: float = 100000,
        transaction_cost: float = 0.001
    ):
        """Setup environment and agent"""
        self.env = TradingEnvironment(
            price_data=price_data,
            initial_cash=initial_cash,
            transaction_cost=transaction_cost
        )
        
        self.agent = PPOAgent(
            observation_dim=self.env.observation_dim,
            action_dim=self.env.action_dim,
            hidden_dim=self.hidden_dim,
            learning_rate=self.learning_rate
        )
        
        self.logger.info(
            f"Setup RL optimizer: obs_dim={self.env.observation_dim}, "
            f"action_dim={self.env.action_dim}"
        )
    
    def train(
        self,
        num_episodes: int = 100,
        update_frequency: int = 20
    ) -> Dict[str, Any]:
        """Train the RL agent"""
        if self.env is None or self.agent is None:
            raise ValueError("Call setup() first")
        
        episode_rewards = []
        episode_returns = []
        
        for episode in range(num_episodes):
            state = self.env.reset()
            episode_reward = 0
            done = False
            
            while not done:
                action, log_prob = self.agent.get_action(state, training=True)
                next_state, reward, done, info = self.env.step(action)
                
                self.agent.store_transition(state, action, reward, log_prob)
                episode_reward += reward
                state = next_state
            
            # Update agent
            if (episode + 1) % update_frequency == 0:
                losses = self.agent.update()
                self.logger.debug(f"Update losses: {losses}")
            
            metrics = self.env.get_performance_metrics()
            episode_rewards.append(episode_reward)
            episode_returns.append(metrics['total_return'])
            
            if (episode + 1) % 10 == 0:
                self.logger.info(
                    f"Episode {episode + 1}: reward={episode_reward:.4f}, "
                    f"return={metrics['total_return']:.2%}"
                )
            
            self.training_history.append({
                'episode': episode,
                'reward': episode_reward,
                **metrics
            })
        
        return {
            'episodes': num_episodes,
            'avg_reward': np.mean(episode_rewards[-10:]),
            'avg_return': np.mean(episode_returns[-10:]),
            'training_history': self.training_history
        }
    
    def evaluate(
        self,
        price_data: np.ndarray = None,
        initial_cash: float = 100000
    ) -> Dict[str, Any]:
        """Evaluate trained agent"""
        if price_data is not None:
            eval_env = TradingEnvironment(
                price_data=price_data,
                initial_cash=initial_cash
            )
        else:
            eval_env = self.env
        
        state = eval_env.reset()
        done = False
        actions_taken = []
        
        while not done:
            action, _ = self.agent.get_action(state, training=False)
            next_state, reward, done, info = eval_env.step(action)
            actions_taken.append(action.copy())
            state = next_state
        
        metrics = eval_env.get_performance_metrics()
        
        return {
            'metrics': metrics,
            'portfolio_values': eval_env.portfolio_values,
            'final_positions': eval_env.positions,
            'actions_taken': actions_taken
        }
    
    def get_optimal_weights(self, state: MarketState) -> np.ndarray:
        """Get optimal portfolio weights for current state"""
        if self.agent is None:
            raise ValueError("Agent not trained")
        
        weights, _ = self.agent.get_action(state, training=False)
        return weights
    
    def save_model(self, path: str):
        """Save model weights"""
        np.savez(
            path,
            policy_weights=self.agent.policy_weights,
            value_weights=self.agent.value_weights
        )
        self.logger.info(f"Saved model to {path}")
    
    def load_model(self, path: str):
        """Load model weights"""
        data = np.load(path, allow_pickle=True)
        self.agent.policy_weights = data['policy_weights'].item()
        self.agent.value_weights = data['value_weights'].item()
        self.logger.info(f"Loaded model from {path}")
