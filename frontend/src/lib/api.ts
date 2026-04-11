import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export interface RiskPredictionRequest {
  company_id: number;
  revenue: number;
  cogs: number;
  net_income: number;
  total_assets: number;
  total_debt: number;
  total_equity: number;
  current_assets: number;
  current_liabilities: number;
  cash: number;
  inventory: number;
}

export interface RiskPredictionResponse {
  risk_level: 'Low' | 'Medium' | 'High';
  confidence: number;
  probabilities: {
    Low: number;
    Medium: number;
    High: number;
  };
  timestamp: string;
}

export interface SentimentAnalysisRequest {
  text: string;
}

export interface SentimentAnalysisResponse {
  sentiment: 'positive' | 'negative' | 'neutral';
  score: number;
  confidence: number;
  entities: Array<{
    entity: string;
    type: string;
  }>;
}

export interface PortfolioOptimizationRequest {
  assets: Array<{
    symbol: string;
    price: number;
    expected_return: number;
    std_dev: number;
  }>;
  correlations: number[][];
  risk_free_rate: number;
  target_return?: number;
}

export interface PortfolioOptimizationResponse {
  optimal_weights: Record<string, number>;
  expected_return: number;
  expected_volatility: number;
  sharpe_ratio: number;
  efficient_frontier: Array<{
    return: number;
    volatility: number;
  }>;
}

export interface PortfolioResponse {
  id: string;
  name: string;
  total_value: number;
  cash: number;
  positions: Array<{
    symbol: string;
    quantity: number;
    current_price: number;
    total_value: number;
    gain_loss: number;
    gain_loss_percent: number;
  }>;
  performance: {
    daily_return: number;
    ytd_return: number;
    total_return: number;
  };
}

export interface RiskMetricsResponse {
  var_95: number;
  var_99: number;
  cvar_95: number;
  max_drawdown: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  beta: number;
  correlation_market: number;
}

export interface MarketDataResponse {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  dividend_yield: number;
}

export interface AgentStatusResponse {
  agent_name: string;
  status: 'active' | 'inactive' | 'error';
  last_activity: string;
  decisions_made: number;
  success_rate: number;
}

export interface TradeExecutionRequest {
  symbol: string;
  action: 'buy' | 'sell';
  quantity: number;
  price?: number;
  order_type: 'market' | 'limit';
}

export interface TradeExecutionResponse {
  order_id: string;
  symbol: string;
  action: string;
  quantity: number;
  price: number;
  status: 'pending' | 'executed' | 'failed';
  timestamp: string;
}

// API Methods
export const api = {
  // Health
  health: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Risk Prediction
  predictRisk: async (data: RiskPredictionRequest): Promise<RiskPredictionResponse> => {
    const response = await apiClient.post('/api/v1/predict/risk', data);
    return response.data;
  },

  // Sentiment Analysis
  analyzeSentiment: async (data: SentimentAnalysisRequest): Promise<SentimentAnalysisResponse> => {
    const response = await apiClient.post('/api/v1/analyze/sentiment', data);
    return response.data;
  },

  // Portfolio Optimization
  optimizePortfolio: async (data: PortfolioOptimizationRequest): Promise<PortfolioOptimizationResponse> => {
    const response = await apiClient.post('/api/v1/optimize/portfolio', data);
    return response.data;
  },

  // Portfolio Data
  getPortfolio: async (): Promise<PortfolioResponse> => {
    const response = await apiClient.get('/api/v1/portfolio');
    return response.data;
  },

  // Risk Metrics
  getRiskMetrics: async (): Promise<RiskMetricsResponse> => {
    const response = await apiClient.get('/api/v1/risk-metrics');
    return response.data;
  },

  // Market Data
  getMarketData: async (symbol: string): Promise<MarketDataResponse> => {
    const response = await apiClient.get(`/api/v1/market-data/${symbol}`);
    return response.data;
  },

  // Agent Status
  getAgentStatus: async (): Promise<AgentStatusResponse[]> => {
    const response = await apiClient.get('/api/v1/agents/status');
    return response.data;
  },

  // Execute Trade
  executeTrade: async (data: TradeExecutionRequest): Promise<TradeExecutionResponse> => {
    const response = await apiClient.post('/api/v1/trades/execute', data);
    return response.data;
  },

  // Get Trade History
  getTradeHistory: async (limit: number = 50): Promise<TradeExecutionResponse[]> => {
    const response = await apiClient.get(`/api/v1/trades/history?limit=${limit}`);
    return response.data;
  },

  // Get Alerts
  getAlerts: async (): Promise<any[]> => {
    const response = await apiClient.get('/api/v1/alerts');
    return response.data;
  },

  // Get Performance
  getPerformance: async (): Promise<any> => {
    const response = await apiClient.get('/api/v1/performance');
    return response.data;
  },
};

export default apiClient;
