# Frontend Complete Setup Guide

This document provides comprehensive instructions for using and developing the Portfolio AI frontend.

## 📋 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Development Guide](#development-guide)
3. [Project Structure](#project-structure)
4. [Components & Features](#components--features)
5. [API Integration](#api-integration)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## Installation & Setup

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

Or with yarn:
```bash
yarn install
```

### Step 2: Configure Environment

Create or update `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Portfolio AI
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
```

### Step 3: Start Development Server

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

### Step 4: Verify Backend Connection

Ensure the backend API is running on `http://localhost:8000` and accessible.

---

## Development Guide

### Running the Application

**Development Mode:**
```bash
npm run dev
```

**Production Build:**
```bash
npm run build
npm start
```

**Type Checking:**
```bash
npm run type-check
```

**Linting:**
```bash
npm run lint
```

### Code Structure

All code is located in `/src`:

- **`app/`** - Page components (Dashboard, Portfolio, Trading, etc.)
- **`components/`** - Reusable React components
- **`lib/`** - Utilities, API client, state management
- **`types/`** - TypeScript type definitions

### Creating New Pages

1. Create a folder under `/src/app` with the page name
2. Add `page.tsx` file
3. Use the Layout component for consistent styling

Example:
```typescript
'use client';

import { Card, Button } from '@/components/common';

export default function NewPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold">New Page</h1>
      <Card title="Welcome">
        <Button variant="primary">Click Me</Button>
      </Card>
    </div>
  );
}
```

---

## Project Structure

### Directory Layout

```
frontend/
├── src/
│   ├── app/
│   │   ├── portfolio/              # Portfolio management
│   │   ├── risk-analysis/          # Risk analysis
│   │   ├── trading/                # Trading management
│   │   ├── agents/                 # Agent monitoring
│   │   ├── market-intelligence/    # Market data
│   │   ├── optimization/           # Optimization
│   │   ├── alerts/                 # Alerts
│   │   ├── reports/                # Reports
│   │   ├── settings/               # Settings
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Dashboard (/)
│   │   └── globals.css             # Global styles
│   ├── components/
│   │   ├── Layout.tsx              # Main layout
│   │   └── common/
│   │       └── index.tsx           # Common UI components
│   ├── lib/
│   │   ├── api.ts                  # API client
│   │   ├── store.ts                # State management
│   │   └── utils.ts                # Utilities
│   └── types/                      # TypeScript types
├── public/                         # Static files
├── package.json
├── .env.example                    # Environment template
├── .env.local                      # Local environment
├── next.config.ts
├── tsconfig.json
└── tailwind.config.js
```

---

## Components & Features

### Core UI Components

Located in `/src/components/common/index.tsx`:

#### Card
Container for content sections
```typescript
<Card title="Portfolio" subtitle="Overview">
  <p>Content here</p>
</Card>
```

#### Stat
Display metric with change
```typescript
<Stat
  label="Portfolio Value"
  value="$1,000,000"
  change={5.2}
  changeLabel="Today"
  icon="💼"
/>
```

#### Table
Data table with columns
```typescript
<Table
  columns={[
    { key: 'name', label: 'Name' },
    { key: 'value', label: 'Value', render: (v) => `$${v}` }
  ]}
  data={data}
/>
```

#### Button
Multi-variant button
```typescript
<Button variant="primary" size="lg">
  Click Me
</Button>
```

Valid variants: `primary`, `secondary`, `danger`, `ghost`
Valid sizes: `sm`, `md`, `lg`

#### Input/Select
Form inputs
```typescript
<Input label="Username" placeholder="Enter username" />
<Select label="Role" options={[{value: 'admin', label: 'Admin'}]} />
```

#### Badge
Status badges
```typescript
<Badge label="Active" variant="success" />
```

Valid variants: `default`, `success`, `warning`, `danger`, `info`

#### Progress
Progress bar
```typescript
<Progress value={75} max={100} label="Loading" />
```

### Feature Pages

#### Dashboard (`/`)
- Portfolio overview
- Key metrics
- Risk metrics
- Agent status
- Recent alerts and trades

#### Portfolio (`/portfolio`)
- Holdings list
- Sector allocation
- Performance metrics
- Add/edit positions
- Rebalancing recommendations

#### Risk Analysis (`/risk-analysis`)
- VaR trends
- Stress tests
- Kill switches
- Correlation matrix

#### Trading (`/trading`)
- Execute trades
- Trade history
- AI recommendations
- Performance tracking

#### Market Intelligence (`/market-intelligence`)
- Market trends
- Top movers
- Regime detection
- News and alerts
- Recommended strategies

#### Agents (`/agents`)
- Agent status
- Performance metrics
- Activity tracking
- Agent controls

#### Optimization (`/optimization`)
- Efficient frontier
- Optimization strategies
- Backtest results
- Rebalancing recommendations

#### Alerts (`/alerts`)
- Alert management
- Search and filter
- Mark as read
- Statistics

#### Reports (`/reports`)
- Report generation
- Report templates
- Scheduled reports
- Report settings

#### Settings (`/settings`)
- Account management
- Notifications
- Trading parameters
- Security settings
- Integrations

---

## API Integration

### API Client

Located at `/src/lib/api.ts`

Using Axios for HTTP requests with automatic error handling.

### Making API Calls

```typescript
import { api } from '@/lib/api';

// Get portfolio data
const portfolio = await api.getPortfolio();

// Get risk metrics
const risk = await api.getRiskMetrics();

// Execute trade
const result = await api.executeTrade({
  symbol: 'AAPL',
  action: 'BUY',
  quantity: 100,
  order_type: 'market'
});
```

### Error Handling

```typescript
try {
  const data = await api.getPortfolio();
} catch (error) {
  console.error('Failed to fetch portfolio:', error);
  // Handle error
}
```

### Available Endpoints

- `api.health()` - Health check
- `api.predictRisk(data)` - Risk prediction
- `api.analyzeSentiment(data)` - Sentiment analysis
- `api.optimizePortfolio(data)` - Portfolio optimization
- `api.getPortfolio()` - Get portfolio
- `api.getRiskMetrics()` - Get risk metrics
- `api.getMarketData(symbol)` - Market data
- `api.getAgentStatus()` - Agent status
- `api.executeTrade(data)` - Execute trade
- `api.getTradeHistory(limit)` - Trade history
- `api.getAlerts()` - Get alerts
- `api.getPerformance()` - Performance data

---

## State Management

### Using Zustand Store

Located at `/src/lib/store.ts`

```typescript
import { useAppStore } from '@/lib/store';

export default function MyComponent() {
  // Get state
  const { portfolio, alerts, addAlert } = useAppStore();

  // Update state
  const handleAction = () => {
    addAlert({
      type: 'success',
      title: 'Success',
      message: 'Operation completed'
    });
  };

  return <div>{portfolio.totalValue}</div>;
}
```

### Store Structure

```typescript
{
  alerts: Alert[],
  portfolio: PortfolioState,
  risk: RiskState,
  agents: AgentState,
  sidebarOpen: boolean,
  theme: 'light' | 'dark'
}
```

---

## Styling & Theme

### Tailwind CSS

The project uses Tailwind CSS for styling. Color scheme:

```css
/* Dark theme (default) */
Background: #111827 (gray-900)
Text: #f3f4f6 (gray-100)
Primary: #3b82f6 (blue-500)
Secondary: #6b7280 (gray-500)
Success: #10b981 (green-500)
Warning: #f59e0b (amber-500)
Danger: #ef4444 (red-500)
```

### Custom Styling

All components support Tailwind classes via `className` prop:

```typescript
<Card className="bg-linear-to-r from-blue-500 to-purple-500">
  Content
</Card>
```

---

## Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Other Platforms

**AWS Amplify:**
```bash
amplify init
amplify publish
```

**Docker:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables for Production

Update `.env.production`:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=Portfolio AI
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 3000 already in use | `npm run dev -- -p 3001` |
| API connection refused | Check NEXT_PUBLIC_API_URL in .env.local |
| TypeScript errors | Run `npm run type-check` to identify issues |
| Build fails | Clear `.next` folder and reinstall: `rm -rf .next node_modules && npm install` |
| Styles not loading | Clear cache: `npm run build && npm start` |

### Debug Mode

Enable debug logging:

```typescript
// In development
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info...');
}
```

### Performance Issues

- Check browser DevTools Performance tab
- Use React DevTools Profiler
- Monitor Network tab for API calls
-Verify backend response times

---

## Next Steps

1. Start the development server: `npm run dev`
2. Open http://localhost:3000
3. Ensure backend is running on http://localhost:8000
4. Begin integrating with backend APIs
5. Customize components and styling as needed
6. Deploy when ready

---

##Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Recharts Examples](https://recharts.org/en-US/examples)

---

**Last Updated:** February 2024
