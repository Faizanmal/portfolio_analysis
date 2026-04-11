# API Integration Guide

This guide explains how to connect the frontend to the backend API and test all endpoints.

## Prerequisites

- ✅ Frontend running: `npm run dev` (http://localhost:3000)
- ✅ Backend running on http://localhost:8000
- ✅ Backend endpoints responding

## Environment Configuration

### Setup `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Portfolio AI
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
```

The API client will automatically use this URL for all requests.

## Testing Backend Connection

### Step 1: Check Health Endpoint

In your browser DevTools Console (F12):

```javascript
import { api } from '@/lib/api';

const health = await api.health();
console.log(health);
// Should return: { status: 'healthy', version: 'X.X.X', timestamp: '...' }
```

If this fails, verify:
- Backend is running on port 8000
- No CORS issues
- Backend `/health` endpoint exists

### Step 2: Test Each API Endpoint

#### Portfolio Data
```javascript
const portfolio = await api.getPortfolio();
console.log(portfolio);
// Expected: { totalValue, cash, positions: [...] }
```

#### Risk Metrics
```javascript
const risk = await api.getRiskMetrics();
console.log(risk);
// Expected: { VaR95, VaR99, CVaR95, maxDrawdown, sharpeRatio }
```

#### Market Data
```javascript
const market = await api.getMarketData('AAPL');
console.log(market);
// Expected: { symbol, price, change, volume, ... }
```

#### Agent Status
```javascript
const agents = await api.getAgentStatus();
console.log(agents);
// Expected: { agents: [...], activeCount, successRate }
```

#### Performance
```javascript
const perf = await api.getPerformance();
console.log(perf);
// Expected: { returns30d, returns1y, maxDrawdown, ... }
```

## Connecting Pages to Backend

### Example: Dashboard Page

**Before (Mock Data):**
```typescript
useEffect(() => {
  // Mock data
  setPortfolio({
    totalValue: 1000000,
    cash: 50000,
    dailyReturn: 5200
  });
}, []);
```

**After (Real API):**
```typescript
import { api } from '@/lib/api';

useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      const [portfolio, risk, agents] = await Promise.all([
        api.getPortfolio(),
        api.getRiskMetrics(),
        api.getAgentStatus()
      ]);
      
      setPortfolio(portfolio);
      setRisk(risk);
      setAgents(agents);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      addAlert({
        type: 'danger',
        title: 'Error',
        message: 'Failed to load dashboard'
      });
    } finally {
      setLoading(false);
    }
  };

  fetchData();
}, [addAlert]);
```

### Example: Trading Page

```typescript
import { api } from '@/lib/api';

const handleExecuteTrade = async (tradingData: TradeExecutionRequest) => {
  try {
    setLoading(true);
    const result = await api.executeTrade(tradingData);
    
    addAlert({
      type: 'success',
      title: 'Trade Executed',
      message: `Successfully executed ${result.quantity} shares of ${result.symbol}`
    });
    
    // Refresh trade history
    const history = await api.getTradeHistory(10);
    setTradeHistory(history);
  } catch (error) {
    addAlert({
      type: 'danger',
      title: 'Trade Failed',
      message: error.message
    });
  } finally {
    setLoading(false);
  }
};
```

## Available API Methods

### Authentication & Health
```typescript
api.health()
// Response: { status, version, timestamp }
```

### Portfolio Operations
```typescript
api.getPortfolio()
// Response: { totalValue, cash, positions: [...] }

api.optimizePortfolio(request)
// Request: { targetReturn, maxRisk, constraints }
// Response: { optimalWeights, expectedReturn, expectedRisk, sharpeRatio }

api.getPerformance()
// Response: { returns30d, returns1y, maxDrawdown, ... }
```

### Risk Analysis
```typescript
api.getRiskMetrics()
// Response: { VaR95, VaR99, CVaR95, maxDrawdown, sharpeRatio }

api.predictRisk(request)
// Request: { companyMetrics, historicalReturns }
// Response: { riskLevel, probability, factors }
```

### Market Data
```typescript
api.getMarketData(symbol)
// Response: { symbol, price, change, volume, ... }
```

### Sentiment Analysis
```typescript
api.analyzeSentiment(request)
// Request: { symbol, documents }
// Response: { sentiment, score, keywords }
```

### Trading
```typescript
api.executeTrade(request)
// Request: { symbol, action, quantity, order_type, price? }
// Response: { orderId, symbol, quantity, executedPrice, status }

api.getTradeHistory(limit)
// Response: TradeExecution[]
```

### Agents & Monitoring
```typescript
api.getAgentStatus()
// Response: { agents: [], activeCount, successRate, pendingDecisions }
```

### Alerts & Notifications
```typescript
api.getAlerts()
// Response: Alert[]
```

## Error Handling Strategy

### Common HTTP Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Login/refresh token |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify endpoint |
| 429 | Rate Limited | Retry with backoff |
| 500 | Server Error | Notify user, retry |

### Retry Logic

```typescript
const retryableRequest = async (fn, maxRetries = 3) => {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;
      
      // Exponential backoff
      const delay = Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};

// Usage
const portfolio = await retryableRequest(() => api.getPortfolio());
```

### Error Type Handling

```typescript
try {
  await api.getPortfolio();
} catch (error) {
  if (error.response?.status === 401) {
    // Redirect to login
    router.push('/auth/login');
  } else if (error.response?.status === 429) {
    // Rate limited - show message
    addAlert({
      type: 'warning',
      message: 'Too many requests. Please try again later.'
    });
  } else if (!error.response) {
    // Network error
    addAlert({
      type: 'danger',
      message: 'Connection failed. Check your internet.'
    });
  } else {
    // Other error
    addAlert({
      type: 'danger',
      message: error.response?.data?.message || 'Request failed'
    });
  }
}
```

## Real-Time Data Updates (WebSocket)

### Configuration

Socket.io client is already installed. To enable real-time updates:

```typescript
// Create src/hooks/useWebSocket.ts
import { useEffect } from 'react';
import io from 'socket.io-client';
import { useAppStore } from '@/lib/store';

export function useWebSocket() {
  const { portfolio, addAlert } = useAppStore();

  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_API_URL, {
      path: '/socket.io'
    });

    // Portfolio updates
    socket.on('portfolio:update', (data) => {
      useAppStore.setState({ portfolio: data });
    });

    // Risk alerts
    socket.on('risk:alert', (alert) => {
      addAlert({
        type: 'warning',
        title: 'Risk Alert',
        message: alert.message
      });
    });

    // Trade executed
    socket.on('trade:executed', (trade) => {
      addAlert({
        type: 'success',
        title: 'Trade Executed',
        message: `${trade.quantity} shares of ${trade.symbol}`
      });
    });

    return () => socket.disconnect();
  }, [addAlert]);
}
```

### Using WebSocket Hook in Pages

```typescript
// In your page component
import { useWebSocket } from '@/hooks/useWebSocket';

export default function Dashboard() {
  useWebSocket();
  
  // Component renders with real-time updates
}
```

## Performance Optimization

### Caching Strategies

```typescript
let portfolioCache: PortfolioResponse | null = null;
let cacheTime = 0;
const CACHE_DURATION = 60000; // 1 minute

async function getCachedPortfolio() {
  const now = Date.now();
  if (portfolioCache && now - cacheTime < CACHE_DURATION) {
    return portfolioCache;
  }
  
  portfolioCache = await api.getPortfolio();
  cacheTime = now;
  return portfolioCache;
}
```

### Request Batching

```typescript
// Fetch multiple endpoints in parallel
const [portfolio, risk, market] = await Promise.all([
  api.getPortfolio(),
  api.getRiskMetrics(),
  api.getMarketData('SPY')
]);
```

### Request Debouncing

```typescript
import { useMemo } from 'react';
import { debounce } from '@/lib/utils';

const debouncedSearch = useMemo(
  () => debounce(async (query) => {
    const results = await api.searchAssets(query);
    setResults(results);
  }, 300),
  []
);
```

## Testing Checklist

Before deploying, verify all endpoints work:

- [ ] Health check passes
- [ ] Portfolio data loads
- [ ] Risk metrics display
- [ ] Trade execution works
- [ ] Agent status updates
- [ ] Alerts display
- [ ] Market data refreshes
- [ ] Performance calculations correct
- [ ] Error handling works
- [ ] Loading states visible
- [ ] Toast notifications appear

## Debugging Tips

### Enable Request Logging

```typescript
// Add to src/lib/api.ts
api.interceptors.request.use(request => {
  console.log('→ Request:', request.url, request.data);
  return request;
});

api.interceptors.response.use(response => {
  console.log('← Response:', response.url, response.data);
  return response;
});
```

### Monitor Performance

Open DevTools → Network tab to see:
- Request duration
- Response size
- Waterfall chart
- Headers and response data

### Check State Updates

```typescript
import { useAppStore } from '@/lib/store';

// Log store changes
const store = useAppStore();
useEffect(() => {
  console.log('Store updated:', store);
}, [store]);
```

## Production Deployment

### Environment Variables

Update `1env.production`:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
NEXT_PUBLIC_APP_NAME=Portfolio AI
```

### Build & Start

```bash
npm run build
npm start
```

### Monitoring

- Monitor API response times
- Track error rates
- Monitor WebSocket connections
- Alert on high latency
- Log failed requests

---

## Next Steps

1. ✅ Verify backend is running
2. ✅ Set `NEXT_PUBLIC_API_URL` in `.env.local`
3. ✅ Test `api.health()` in console
4. ✅ Start replacing mock data with API calls
5. ✅ Test each page with real data
6. ✅ Wire up WebSocket for real-time updates
7. ✅ Implement error handling
8. ✅ Deploy to production

---

**Last Updated:** February 2024
