# Portfolio AI - Frontend

A comprehensive, production-ready Next.js frontend for the AI-powered portfolio analysis and autonomous trading platform.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# or
yarn install

# Start development server
npm run dev

# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📋 Features

### 1. **Dashboard**
- Portfolio performance overview
- Real-time key metrics (portfolio value, returns, cash)
- Risk metrics visualization
- Agent status monitoring
- Recent alerts and trade history
- System health monitoring

### 2. **Portfolio Management**
- View all portfolio holdings
- Real-time position tracking
- Sector allocation visualization
- Gain/loss analysis
- Add/edit/delete positions
- Rebalancing recommendations
- Performance summary

### 3. **Risk Analysis**
- Value at Risk (VaR) calculation and trends
- Conditional VaR monitoring
- Maximum drawdown tracking
- Risk kill switches with thresholds
- Correlation matrix analysis
- Stress test scenarios
- Dynamic risk metrics updated in real-time

### 4. **Trading Management**
- Execute buy/sell orders
- Market and limit order types
- Trade history with full details
- AI-recommended trades
- Trading volume analysis
- Order status tracking
- Trade performance metrics

### 5. **Market Intelligence**
- Real-time market trends
- Volatility and sentiment analysis
- Top movers (gainers and losers)
- Market regime detection
- News and alerts feed
- Recommended strategies
- Market correlation analysis

### 6. **Agent Monitoring**
- Real-time agent status tracking
- Agent performance metrics
- Success rate monitoring
- Decision and trade execution counts
- Agent-specific logs and configuration
- Performance trending charts
- Emergency stop controls

### 7. **Portfolio Optimization**
- Efficient frontier visualization
- Multiple optimization strategies
- Backtest performance analysis
- Rebalancing recommendations
- Custom parameter configuration
- Strategy comparison tools

### 8. **Alerts Management**
- Real-time alert system
- Filter and search alerts
- Alert categorization (success, warning, danger, info)
- Mark alerts as read
- Delete alerts
- Alert statistics

### 9. **Reports**
- Generate custom reports
- Pre-built report templates
- Report scheduling
- Multiple export formats (PDF, Excel)
- Historical report access
- Comprehensive analytics

### 10. **Settings**
- Account management
- Notification preferences
- Trading and risk parameters
- Security settings
- API integrations
- Two-factor authentication

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js app directory
│   │   ├── portfolio/          # Portfolio management pages
│   │   ├── risk-analysis/      # Risk analysis pages
│   │   ├── trading/            # Trading management pages
│   │   ├── agents/             # Agent monitoring pages
│   │   ├── market-intelligence/ # Market data pages
│   │   ├── optimization/       # Optimization pages
│   │   ├── alerts/             # Alerts management
│   │   ├── reports/            # Reports generation
│   │   ├── settings/           # User settings
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Dashboard
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── Layout.tsx          # Main layout component
│   │   └── common/             # Reusable UI components
│   ├── lib/
│   │   ├── api.ts              # API client and endpoints
│   │   ├── store.ts            # Zustand state management
│   │   └── utils.ts            # Utility functions
│   └── types/                  # TypeScript type definitions
├── public/                     # Static assets
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.js
└── README.md
```

## 🎨 UI Components

The frontend includes a comprehensive component library:

- **Card**: Container component for content sections
- **Stat**: Display metric with change indicator
- **Table**: Sortable data table
- **Badge**: Status and label badges
- **Button**: Multi-variant button component
- **Input**: Text input with validation
- **Select**: Dropdown select component
- **Progress**: Progress bar visualization

## 📊 Charts & Visualizations

Built with Recharts for interactive visualizations:

- Area Charts (portfolio performance)
- Line Charts (trends and metrics)
- Bar Charts (volume and activity)
- Pie Charts (allocation)
- Scatter Charts (efficient frontier)

## 🔌 API Integration

The frontend integrates with the backend API through the `/lib/api.ts` client:

### Available Endpoints

- `GET /health` - Health check
- `POST /api/v1/predict/risk` - Risk prediction
- `POST /api/v1/analyze/sentiment` - Sentiment analysis
- `POST /api/v1/optimize/portfolio` - Portfolio optimization
- `GET /api/v1/portfolio` - Get portfolio data
- `GET /api/v1/risk-metrics` - Get risk metrics
- `GET /api/v1/market-data/:symbol` - Market data
- `GET /api/v1/agents/status` - Agent status
- `POST /api/v1/trades/execute` - Execute trade
- `GET /api/v1/trades/history` - Trade history
- `GET /api/v1/alerts` - Get alerts
- `GET /api/v1/performance` - Get performance

## 🎯 State Management

Using Zustand for efficient state management:

```typescript
// Access global store
const { portfolio, risk, agents, addAlert } = useAppStore();

// Update state
setPortfolio({ totalValue: 1000000 });
addAlert({ type: 'success', title: 'Trade Executed', message: '...' });
```

## 🎨 Styling

- **Tailwind CSS** for rapid UI development
- **Dark theme** by default (customizable)
- **Responsive design** for all screen sizes
- **Smooth animations** and transitions
- Custom color scheme for professional appearance

## 🚀 Deployment

### Build Production

```bash
npm run build
```

### Start Production Server

```bash
npm start
```

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Portfolio AI
NEXT_PUBLIC_APP_DESCRIPTION=AI-Powered Investment Platform
```

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Touch-friendly UI
- Optimized for tablet and desktop

## ⚡ Performance Optimization

- Next.js Image optimization
- Code splitting and lazy loading
- Efficient re-rendering with React 18
- Responsive font loading
- Optimized bundle size

## 🔒 Security

- Environment variable protection
- CORS-enabled API integration
- Input validation and sanitization
- Secure state management

## 🛠️ Development Tools

- **TypeScript** for type safety
- **ESLint** for code quality
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Lucide React** for icons
- **Zustand** for state management
- **Axios** for HTTP requests
- **React Hot Toast** for notifications
- **Framer Motion** for animations

## 📦 Dependencies

Key dependencies:

- `next` - React framework
- `react` - UI library
- `recharts` - Charting library
- `tailwindcss` - Utility-first CSS
- `zustand` - State management
- `axios` - HTTP client
- `lucide-react` - Icon library
- `socket.io-client` - Real-time communication
- `react-hot-toast` - Toast notifications
- `framer-motion` - Animation library

## 🚦 Getting Started Guide

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API URL
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   Navigate to http://localhost:3000

## 📝 License

This project is part of the AI Portfolio Analysis Platform.

## 🤝 Contributing

Contributions are welcome! Please follow the existing code style and structure.

## 📞 Support

For issues and questions, please refer to the main project documentation.
