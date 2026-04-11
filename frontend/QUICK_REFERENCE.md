# Quick Reference Guide

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser
# http://localhost:3000
```

## Common Commands

```bash
# Development
npm run dev              # Start dev server on port 3000
npm run build            # Create production build
npm start                # Start production server

# Type checking & Linting
npm run type-check       # Check TypeScript types
npm run lint             # Run ESLint

# Clean build
rm -rf .next node_modules
npm install
npm run build
```

## Project File Locations

- **Pages:** `src/app/*/page.tsx`
- **Components:** `src/components/`
- **API Client:** `src/lib/api.ts`
- **State Management:** `src/lib/store.ts`
- **Utilities:** `src/lib/utils.ts`
- **Styles:** `src/app/globals.css`
- **Configuration:** `next.config.ts`, `tsconfig.json`

## Component Usage

### Stat Card
```typescript
import { Stat } from '@/components/common';

<Stat 
  label="Portfolio Value" 
  value="$1M" 
  change={2.5}
  changeLabel="Today"
  icon="📊"
/>
```

### Data Table
```typescript
import { Table } from '@/components/common';

<Table
  columns={[
    { key: 'symbol', label: 'Symbol' },
    { key: 'price', label: 'Price' }
  ]}
  data={holdings}
/>
```

### Card Container
```typescript
import { Card } from '@/components/common';

<Card title="Portfolio" subtitle="Summary">
  Content here
</Card>
```

### Button
```typescript
import { Button } from '@/components/common';

<Button variant="primary" size="lg" onClick={handleClick}>
  Action
</Button>
```

## API Integration

### Making Calls
```typescript
import { api } from '@/lib/api';

// Get portfolio
const portfolio = await api.getPortfolio();

// Execute trade
await api.executeTrade({
  symbol: 'AAPL',
  action: 'BUY',
  quantity: 100,
  order_type: 'market'
});
```

## State Management

### Using Store
```typescript
import { useAppStore } from '@/lib/store';

const { portfolio, alerts, addAlert } = useAppStore();

addAlert({
  type: 'success',
  title: 'Success',
  message: 'Done!'
});
```

## Debugging

### Check API Connection
```typescript
import { api } from '@/lib/api';

const health = await api.health();
console.log(health);
```

### View Console Logs
Open browser DevTools: Press **F12** or **Right-click → Inspect**

### Check Network Requests
DevTools → Network tab → Filter by XHR

## Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Portfolio AI
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
```

## Styling

### Tailwind Classes
```html
<!-- Size -->
<div className="w-full h-screen">

<!-- Colors -->
<div className="bg-blue-500 text-white">

<!-- Spacing -->
<div className="p-4 m-2 gap-4">

<!-- Flexbox -->
<div className="flex justify-between items-center">

<!-- Grid -->
<div className="grid grid-cols-3 gap-4">

<!-- Responsive -->
<div className="flex flex-col md:flex-row">
```

## Pages Navigation

- **Dashboard:** `/` - Home page
- **Portfolio:** `/portfolio` - Holdings and allocation
- **Risk Analysis:** `/risk-analysis` - Risk metrics
- **Trading:** `/trading` - Trade execution
- **Market Intelligence:** `/market-intelligence` - Market data
- **Agents:** `/agents` - Agent monitoring
- **Optimization:** `/optimization` - Rebalancing
- **Alerts:** `/alerts` - Alert management
- **Reports:** `/reports` - Report generation
- **Settings:** `/settings` - User settings

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 3000 in use | `npm run dev -- -p 3001` |
| API error 500 | Check backend is running on port 8000 |
| Styles broken | Clear cache: `rm -rf .next && npm run build` |
| Can't find module | Run `npm install` again |
| TypeScript errors | Run `npm run type-check` |

## Available Features

✅ Dashboard with charts and metrics
✅ Portfolio management with holdings table
✅ Risk analysis with VaR and stress tests
✅ Trading with order execution
✅ Market intelligence with trend analysis
✅ Agent monitoring with 6 agents
✅ Portfolio optimization with efficient frontier
✅ Alert management with search/filter
✅ Reports with templates
✅ Settings with account and security

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Configure `.env.local` with backend URL
3. ✅ Start frontend: `npm run dev`
4. ✅ Start backend on port 8000
5. 🔄 Test API endpoints
6. 🔄 Enable real-time updates (WebSocket)
7. 🔄 Add authentication
8. 🔄 Deploy to production

---
**Frontend Version:** 1.0.0
**Last Updated:** February 2024
