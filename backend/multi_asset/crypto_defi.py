"""
Cryptocurrency and DeFi Integration
===================================

Comprehensive crypto portfolio management with:
- Multi-chain portfolio tracking
- DeFi yield opportunity detection
- Liquidity pool analytics
- Staking rewards tracking
- Cross-chain bridging optimization
- On-chain analytics integration
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BSC = "bsc"
    AVALANCHE = "avalanche"
    SOLANA = "solana"
    FANTOM = "fantom"
    BASE = "base"


class DeFiProtocolType(Enum):
    """Types of DeFi protocols"""
    DEX = "dex"
    LENDING = "lending"
    YIELD_AGGREGATOR = "yield_aggregator"
    LIQUID_STAKING = "liquid_staking"
    OPTIONS = "options"
    PERPETUALS = "perpetuals"
    BRIDGE = "bridge"
    INSURANCE = "insurance"


@dataclass
class CryptoAsset:
    """Cryptocurrency asset representation"""
    symbol: str
    name: str
    network: BlockchainNetwork
    contract_address: str
    
    # Holdings
    balance: float
    value_usd: float
    price_usd: float
    
    # 24h metrics
    price_change_24h: float = 0.0
    volume_24h: float = 0.0
    
    # Classification
    asset_type: str = "token"  # token, native, nft, lp_token
    sector: str = ""  # defi, gaming, infrastructure, etc.
    
    # Staking/Yield
    is_staked: bool = False
    staking_apy: float = 0.0
    rewards_pending: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'network': self.network.value,
            'contract_address': self.contract_address,
            'balance': self.balance,
            'value_usd': self.value_usd,
            'price_usd': self.price_usd,
            'price_change_24h': self.price_change_24h,
            'asset_type': self.asset_type,
            'sector': self.sector,
            'staking': {
                'is_staked': self.is_staked,
                'apy': self.staking_apy,
                'rewards_pending': self.rewards_pending
            }
        }


@dataclass
class DeFiPosition:
    """DeFi protocol position"""
    position_id: str
    protocol_name: str
    protocol_type: DeFiProtocolType
    network: BlockchainNetwork
    
    # Position details
    position_type: str  # supply, borrow, lp, stake
    assets: List[str]
    amounts: List[float]
    value_usd: float
    
    # Yield information
    apy: float
    rewards_token: str = ""
    rewards_pending: float = 0.0
    rewards_value_usd: float = 0.0
    
    # Risk metrics
    health_factor: float = 0.0  # For lending positions
    impermanent_loss: float = 0.0  # For LP positions
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class YieldOpportunity:
    """DeFi yield farming opportunity"""
    opportunity_id: str
    protocol_name: str
    network: BlockchainNetwork
    
    # Yield details
    pool_name: str
    assets: List[str]
    apy: float
    tvl_usd: float
    
    # Risk assessment
    risk_score: float  # 0-100
    risk_factors: List[str]
    
    # Requirements
    min_deposit: float = 0.0
    lock_period_days: int = 0
    
    # Strategy type
    strategy_type: str = ""  # single_stake, lp, leveraged, vault
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.opportunity_id,
            'protocol': self.protocol_name,
            'network': self.network.value,
            'pool': self.pool_name,
            'assets': self.assets,
            'apy': self.apy,
            'tvl': self.tvl_usd,
            'risk_score': self.risk_score,
            'risk_factors': self.risk_factors,
            'min_deposit': self.min_deposit,
            'lock_period': self.lock_period_days
        }


class CryptoPortfolioManager:
    """
    Manages cryptocurrency portfolio across multiple chains.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("crypto_portfolio")
        self.assets: Dict[str, CryptoAsset] = {}
        self.positions: Dict[str, DeFiPosition] = {}
        self.wallet_addresses: Dict[BlockchainNetwork, List[str]] = {}
        
        # Price cache
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.price_cache_ttl = 60  # seconds
        
    def add_wallet(self, network: BlockchainNetwork, address: str):
        """Add wallet address for tracking"""
        if network not in self.wallet_addresses:
            self.wallet_addresses[network] = []
        
        if address not in self.wallet_addresses[network]:
            self.wallet_addresses[network].append(address)
            self.logger.info(f"Added wallet {address[:10]}... on {network.value}")
    
    async def sync_portfolio(self) -> Dict[str, Any]:
        """Sync portfolio from all connected wallets"""
        total_value = 0.0
        synced_assets = []
        
        for network, addresses in self.wallet_addresses.items():
            for address in addresses:
                assets = await self._fetch_wallet_balances(network, address)
                for asset in assets:
                    self.assets[f"{asset.symbol}_{network.value}"] = asset
                    total_value += asset.value_usd
                    synced_assets.append(asset.to_dict())
        
        return {
            'total_value_usd': total_value,
            'assets_count': len(self.assets),
            'networks': list(self.wallet_addresses.keys()),
            'assets': synced_assets
        }
    
    async def _fetch_wallet_balances(
        self,
        network: BlockchainNetwork,
        address: str
    ) -> List[CryptoAsset]:
        """Fetch balances for a wallet (mock implementation)"""
        # In production, integrate with blockchain RPCs or indexers
        # like Alchemy, Moralis, or The Graph
        
        # Mock data
        mock_assets = [
            CryptoAsset(
                symbol="ETH",
                name="Ethereum",
                network=network,
                contract_address="0x0",
                balance=2.5,
                value_usd=5000,
                price_usd=2000,
                price_change_24h=2.5,
                asset_type="native",
                sector="infrastructure"
            ),
            CryptoAsset(
                symbol="USDC",
                name="USD Coin",
                network=network,
                contract_address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                balance=10000,
                value_usd=10000,
                price_usd=1.0,
                asset_type="token",
                sector="stablecoin"
            )
        ]
        
        return mock_assets
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary by network and sector"""
        by_network = {}
        by_sector = {}
        total_value = 0
        
        for asset in self.assets.values():
            network = asset.network.value
            sector = asset.sector or "Other"
            
            if network not in by_network:
                by_network[network] = 0
            by_network[network] += asset.value_usd
            
            if sector not in by_sector:
                by_sector[sector] = 0
            by_sector[sector] += asset.value_usd
            
            total_value += asset.value_usd
        
        return {
            'total_value_usd': total_value,
            'by_network': by_network,
            'by_sector': by_sector,
            'asset_count': len(self.assets),
            'networks_active': len(by_network)
        }
    
    def get_staking_summary(self) -> Dict[str, Any]:
        """Get summary of staked assets"""
        staked_assets = [a for a in self.assets.values() if a.is_staked]
        
        total_staked = sum(a.value_usd for a in staked_assets)
        total_rewards = sum(a.rewards_pending for a in staked_assets)
        weighted_apy = sum(a.staking_apy * a.value_usd for a in staked_assets) / total_staked if total_staked > 0 else 0
        
        return {
            'total_staked_usd': total_staked,
            'total_rewards_pending': total_rewards,
            'weighted_average_apy': weighted_apy,
            'staked_positions': len(staked_assets)
        }


class DeFiYieldOptimizer:
    """
    Optimizes DeFi yield farming strategies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("defi_optimizer")
        self.opportunities: List[YieldOpportunity] = []
        
        # Risk parameters
        self.max_risk_score = 70
        self.min_tvl = 1_000_000  # $1M minimum TVL
        self.preferred_networks = [
            BlockchainNetwork.ETHEREUM,
            BlockchainNetwork.ARBITRUM,
            BlockchainNetwork.POLYGON
        ]
    
    async def scan_opportunities(
        self,
        assets: List[str],
        networks: Optional[List[BlockchainNetwork]] = None
    ) -> List[YieldOpportunity]:
        """Scan for yield opportunities across protocols"""
        if networks is None:
            networks = self.preferred_networks
        
        opportunities = []
        
        # In production, integrate with DeFiLlama, Zapper, or direct protocol APIs
        # Mock opportunities for demonstration
        mock_opportunities = [
            YieldOpportunity(
                opportunity_id="aave_eth_supply",
                protocol_name="Aave V3",
                network=BlockchainNetwork.ETHEREUM,
                pool_name="ETH Supply",
                assets=["ETH"],
                apy=3.5,
                tvl_usd=500_000_000,
                risk_score=20,
                risk_factors=["smart_contract_risk"],
                strategy_type="single_stake"
            ),
            YieldOpportunity(
                opportunity_id="curve_3pool",
                protocol_name="Curve Finance",
                network=BlockchainNetwork.ETHEREUM,
                pool_name="3Pool (USDC/USDT/DAI)",
                assets=["USDC", "USDT", "DAI"],
                apy=5.2,
                tvl_usd=800_000_000,
                risk_score=25,
                risk_factors=["smart_contract_risk", "depeg_risk"],
                strategy_type="lp"
            ),
            YieldOpportunity(
                opportunity_id="lido_steth",
                protocol_name="Lido",
                network=BlockchainNetwork.ETHEREUM,
                pool_name="stETH Staking",
                assets=["ETH"],
                apy=4.0,
                tvl_usd=15_000_000_000,
                risk_score=15,
                risk_factors=["slashing_risk"],
                strategy_type="liquid_staking"
            ),
            YieldOpportunity(
                opportunity_id="gmx_glp",
                protocol_name="GMX",
                network=BlockchainNetwork.ARBITRUM,
                pool_name="GLP",
                assets=["ETH", "BTC", "USDC"],
                apy=25.0,
                tvl_usd=400_000_000,
                risk_score=45,
                risk_factors=["smart_contract_risk", "market_risk", "trader_pnl_exposure"],
                strategy_type="lp"
            ),
            YieldOpportunity(
                opportunity_id="pendle_steth",
                protocol_name="Pendle",
                network=BlockchainNetwork.ARBITRUM,
                pool_name="stETH PT",
                assets=["stETH"],
                apy=8.5,
                tvl_usd=50_000_000,
                risk_score=40,
                risk_factors=["smart_contract_risk", "liquidity_risk"],
                strategy_type="yield_trading"
            ),
        ]
        
        # Filter by assets and criteria
        for opp in mock_opportunities:
            if opp.network in networks:
                if any(asset in opp.assets for asset in assets) or not assets:
                    if opp.risk_score <= self.max_risk_score and opp.tvl_usd >= self.min_tvl:
                        opportunities.append(opp)
        
        # Sort by APY
        opportunities.sort(key=lambda x: x.apy, reverse=True)
        self.opportunities = opportunities
        
        return opportunities
    
    def optimize_allocation(
        self,
        available_capital: Dict[str, float],
        risk_tolerance: float = 50,
        max_positions: int = 5
    ) -> Dict[str, Any]:
        """
        Optimize capital allocation across yield opportunities.
        
        Args:
            available_capital: Dict of {asset: amount}
            risk_tolerance: 0-100 scale
            max_positions: Maximum number of positions
        """
        if not self.opportunities:
            return {'error': 'No opportunities scanned'}
        
        # Filter by risk tolerance
        eligible = [o for o in self.opportunities if o.risk_score <= risk_tolerance]
        
        if not eligible:
            return {'error': 'No opportunities match risk tolerance'}
        
        # Simple allocation strategy: weighted by risk-adjusted yield
        allocations = []
        
        for opp in eligible[:max_positions]:
            # Risk-adjusted yield score
            risk_adj_yield = opp.apy * (1 - opp.risk_score / 100)
            
            # Find matching capital
            matching_assets = [a for a in opp.assets if a in available_capital]
            if matching_assets:
                for asset in matching_assets:
                    available = available_capital.get(asset, 0)
                    if available > 0:
                        # Allocate portion based on opportunity ranking
                        allocation_pct = min(0.4, 1 / len(eligible[:max_positions]))
                        amount = available * allocation_pct
                        
                        allocations.append({
                            'opportunity': opp.to_dict(),
                            'asset': asset,
                            'amount': amount,
                            'expected_apy': opp.apy,
                            'risk_score': opp.risk_score,
                            'risk_adj_yield': risk_adj_yield
                        })
        
        # Calculate totals
        total_allocated = sum(a['amount'] for a in allocations)
        weighted_apy = sum(a['amount'] * a['expected_apy'] for a in allocations) / total_allocated if total_allocated > 0 else 0
        avg_risk = sum(a['amount'] * a['risk_score'] for a in allocations) / total_allocated if total_allocated > 0 else 0
        
        return {
            'allocations': allocations,
            'summary': {
                'total_allocated': total_allocated,
                'weighted_average_apy': weighted_apy,
                'average_risk_score': avg_risk,
                'positions_count': len(allocations)
            }
        }
    
    def calculate_impermanent_loss(
        self,
        initial_prices: Dict[str, float],
        current_prices: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """Calculate impermanent loss for LP position"""
        if len(initial_prices) != 2:
            return 0.0
        
        assets = list(initial_prices.keys())
        p0_a, p0_b = initial_prices[assets[0]], initial_prices[assets[1]]
        p1_a, p1_b = current_prices[assets[0]], current_prices[assets[1]]
        
        # Price ratio change
        r = (p1_a / p0_a) / (p1_b / p0_b)
        
        # IL formula: 2 * sqrt(r) / (1 + r) - 1
        il = 2 * np.sqrt(r) / (1 + r) - 1
        
        return il
    
    def get_risk_assessment(self, opportunity: YieldOpportunity) -> Dict[str, Any]:
        """Get detailed risk assessment for an opportunity"""
        risk_breakdown = {
            'overall_score': opportunity.risk_score,
            'factors': {}
        }
        
        # Analyze each risk factor
        risk_weights = {
            'smart_contract_risk': 30,
            'liquidity_risk': 20,
            'market_risk': 15,
            'depeg_risk': 25,
            'slashing_risk': 10,
            'trader_pnl_exposure': 20,
            'oracle_risk': 15,
            'governance_risk': 10
        }
        
        for factor in opportunity.risk_factors:
            weight = risk_weights.get(factor, 10)
            risk_breakdown['factors'][factor] = {
                'weight': weight,
                'description': self._get_risk_description(factor)
            }
        
        # TVL-based safety score
        if opportunity.tvl_usd > 1_000_000_000:
            risk_breakdown['tvl_safety'] = 'high'
        elif opportunity.tvl_usd > 100_000_000:
            risk_breakdown['tvl_safety'] = 'medium'
        else:
            risk_breakdown['tvl_safety'] = 'low'
        
        return risk_breakdown
    
    def _get_risk_description(self, factor: str) -> str:
        """Get description for risk factor"""
        descriptions = {
            'smart_contract_risk': 'Risk of bugs or exploits in protocol smart contracts',
            'liquidity_risk': 'Risk of being unable to exit position due to low liquidity',
            'market_risk': 'Risk from adverse market movements affecting position value',
            'depeg_risk': 'Risk of stablecoin or pegged asset losing its peg',
            'slashing_risk': 'Risk of losing staked assets due to validator misbehavior',
            'trader_pnl_exposure': 'Risk exposure to traders PnL in the protocol',
            'oracle_risk': 'Risk of price oracle manipulation or failure',
            'governance_risk': 'Risk from protocol governance decisions'
        }
        return descriptions.get(factor, 'Unknown risk factor')


class CryptoAnalytics:
    """
    Advanced analytics for cryptocurrency portfolios.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("crypto_analytics")
    
    def calculate_metrics(
        self,
        portfolio: CryptoPortfolioManager,
        price_history: pd.DataFrame,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Calculate comprehensive crypto portfolio metrics"""
        if price_history.empty:
            return {}
        
        # Calculate returns
        returns = price_history.pct_change().dropna()
        
        # Volatility (annualized)
        volatility = returns.std() * np.sqrt(365)
        
        # Sharpe ratio (assuming 0% risk-free rate for crypto)
        mean_return = returns.mean() * 365
        sharpe = mean_return / volatility if volatility.any() else 0
        
        # Max drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = cumulative / rolling_max - 1
        max_drawdown = drawdown.min()
        
        # Beta to BTC (if BTC in price history)
        btc_beta = {}
        if 'BTC' in price_history.columns:
            btc_returns = returns['BTC']
            for col in returns.columns:
                if col != 'BTC':
                    cov = returns[col].cov(btc_returns)
                    var = btc_returns.var()
                    btc_beta[col] = cov / var if var > 0 else 0
        
        return {
            'period_days': period_days,
            'volatility': volatility.to_dict(),
            'annualized_return': mean_return.to_dict(),
            'sharpe_ratio': (sharpe if isinstance(sharpe, float) else sharpe.to_dict()),
            'max_drawdown': max_drawdown.to_dict(),
            'btc_beta': btc_beta,
            'correlation_matrix': returns.corr().to_dict()
        }
    
    def analyze_on_chain_metrics(
        self,
        asset: str,
        network: BlockchainNetwork
    ) -> Dict[str, Any]:
        """Analyze on-chain metrics for an asset"""
        # In production, integrate with Glassnode, Nansen, or Dune Analytics
        
        # Mock on-chain data
        return {
            'asset': asset,
            'network': network.value,
            'metrics': {
                'active_addresses_24h': 125000,
                'transaction_count_24h': 450000,
                'transfer_volume_24h': 2500000000,
                'exchange_inflow_24h': 15000,
                'exchange_outflow_24h': 18000,
                'net_exchange_flow': -3000,  # Outflow = bullish
                'whale_transactions_24h': 45,  # >$1M
                'nvt_ratio': 65,  # Network Value to Transactions
                'mvrv_ratio': 1.8,  # Market Value to Realized Value
            },
            'signals': {
                'accumulation_trend': 'strong',  # Based on exchange outflow
                'network_activity': 'high',
                'whale_activity': 'moderate'
            }
        }
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """Get overall crypto market sentiment"""
        # In production, aggregate from multiple sources
        
        return {
            'fear_greed_index': 55,  # 0-100
            'fear_greed_label': 'Neutral',
            'btc_dominance': 52.3,
            'total_market_cap': 2.1e12,
            'altcoin_season_index': 45,  # 0-100
            'trending_narratives': [
                'AI Tokens',
                'Real World Assets',
                'Layer 2',
                'Restaking'
            ],
            'top_gainers_24h': [
                {'symbol': 'PEPE', 'change': 15.2},
                {'symbol': 'RNDR', 'change': 12.5},
                {'symbol': 'ARB', 'change': 8.3}
            ],
            'top_losers_24h': [
                {'symbol': 'SOL', 'change': -4.2},
                {'symbol': 'AVAX', 'change': -3.8},
                {'symbol': 'MATIC', 'change': -3.1}
            ]
        }
    
    def analyze_gas_costs(
        self,
        network: BlockchainNetwork
    ) -> Dict[str, Any]:
        """Analyze current gas costs on a network"""
        # Mock gas data
        gas_prices = {
            BlockchainNetwork.ETHEREUM: {'slow': 15, 'normal': 20, 'fast': 30},
            BlockchainNetwork.POLYGON: {'slow': 30, 'normal': 50, 'fast': 80},
            BlockchainNetwork.ARBITRUM: {'slow': 0.1, 'normal': 0.15, 'fast': 0.2},
            BlockchainNetwork.OPTIMISM: {'slow': 0.01, 'normal': 0.02, 'fast': 0.03},
        }
        
        prices = gas_prices.get(network, {'slow': 1, 'normal': 2, 'fast': 3})
        
        # Estimate common operation costs
        swap_gas = 150000
        transfer_gas = 21000
        approve_gas = 45000
        
        eth_price = 2000  # Mock ETH price
        
        return {
            'network': network.value,
            'gas_prices_gwei': prices,
            'estimated_costs_usd': {
                'swap': {
                    'slow': swap_gas * prices['slow'] * 1e-9 * eth_price,
                    'normal': swap_gas * prices['normal'] * 1e-9 * eth_price,
                    'fast': swap_gas * prices['fast'] * 1e-9 * eth_price
                },
                'transfer': {
                    'slow': transfer_gas * prices['slow'] * 1e-9 * eth_price,
                    'normal': transfer_gas * prices['normal'] * 1e-9 * eth_price,
                    'fast': transfer_gas * prices['fast'] * 1e-9 * eth_price
                },
                'approve': {
                    'slow': approve_gas * prices['slow'] * 1e-9 * eth_price,
                    'normal': approve_gas * prices['normal'] * 1e-9 * eth_price,
                    'fast': approve_gas * prices['fast'] * 1e-9 * eth_price
                }
            },
            'recommendation': 'normal' if prices['normal'] < 50 else 'wait'
        }
