'use client';

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Card, Stat, Button, Badge, Progress } from '@/components/common';
import { TrendingUp, TrendingDown, Zap, AlertTriangle } from 'lucide-react';

const marketTrendData = [
  { date: '9 AM', market: 4250.50, volatility: 8.2, sentiment: 65 },
  { date: '10 AM', market: 4252.30, volatility: 8.5, sentiment: 68 },
  { date: '11 AM', market: 4255.80, volatility: 7.9, sentiment: 72 },
  { date: '12 PM', market: 4253.40, volatility: 8.1, sentiment: 70 },
  { date: '1 PM', market: 4258.90, volatility: 7.6, sentiment: 75 },
  { date: '2 PM', market: 4260.50, volatility: 7.8, sentiment: 78 },
  { date: '3 PM', market: 4262.10, volatility: 8.0, sentiment: 76 },
];

const topMovers = [
  { symbol: 'NVDA', price: 825.50, change: 5.25, changePercent: 0.64, sentiment: 'Very Bullish', volume: '28.5M' },
  { symbol: 'TSLA', price: 242.80, change: 3.20, changePercent: 1.33, sentiment: 'Bullish', volume: '45.2M' },
  { symbol: 'AAPL', price: 150.25, change: -2.10, changePercent: -1.38, sentiment: 'Neutral', volume: '32.1M' },
  { symbol: 'META', price: 499.50, change: -8.75, changePercent: -1.73, sentiment: 'Bearish', volume: '22.8M' },
  { symbol: 'AMZN', price: 195.80, change: -5.40, changePercent: -2.70, sentiment: 'Very Bearish', volume: '38.5M' },
];

const marketRegimes = [
  { name: 'Bull Market', probability: 0.35, indicator: 'Strong' },
  { name: 'Consolidation', probability: 0.45, indicator: 'Moderate' },
  { name: 'Bear Market', probability: 0.15, indicator: 'Weak' },
  { name: 'High Volatility', probability: 0.20, indicator: 'Elevated' },
];

const newsAlerts = [
  { source: 'Reuters', title: 'Fed raises interest rates by 0.25%', sentiment: 'negative', impact: 'High', time: '11:30 AM' },
  { source: 'Bloomberg', title: 'Tech companies post strong earnings', sentiment: 'positive', impact: 'High', time: '10:45 AM' },
  { source: 'CNBC', title: 'Market momentum continues higher', sentiment: 'positive', impact: 'Medium', time: '10:15 AM' },
  { source: 'MarketWatch', title: 'Oil prices surge on supply concerns', sentiment: 'mixed', impact: 'Medium', time: '9:50 AM' },
];

export default function MarketIntelligencePage() {
  const [selectedRegime, setSelectedRegime] = useState('consolidation');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Market Intelligence</h1>
        <p className="text-gray-400 mt-2">Real-time market analysis and insights</p>
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat
          label="S&P 500"
          value="4,262.10"
          change={0.28}
          changeLabel="Today"
          icon="📊"
        />
        <Stat
          label="VIX Index"
          value="12.5"
          change={-5.2}
          changeLabel="Today"
          icon="📉"
        />
        <Stat
          label="Market Sentiment"
          value="Bullish"
          change={8.5}
          changeLabel="vs Neutral"
          icon="💡"
        />
        <Stat
          label="Trading Volume"
          value="2.1B"
          change={2.1}
          changeLabel="Above Average"
          icon="📈"
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Trend */}
        <Card title="Market Trend" subtitle="Real-time index movement">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={marketTrendData}>
                <defs>
                  <linearGradient id="colorMarket" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="market"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#colorMarket)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Volatility & Sentiment */}
        <Card title="Volatility & Sentiment" subtitle="Market indicators">
          <div className="h-64 sm:h-80 lg:h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={marketTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                />
                <Line type="monotone" dataKey="volatility" stroke="#ef4444" name="Volatility" />
                <Line type="monotone" dataKey="sentiment" stroke="#10b981" name="Sentiment" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Market Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Movers */}
        <Card title="Top Movers" subtitle="Biggest gainers and losers">
          <div className="space-y-2">
            {topMovers.map((stock, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-white">{stock.symbol}</p>
                    <Badge label={stock.sentiment} variant="default" size="sm" />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">Vol: {stock.volume}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-white">${stock.price}</p>
                  <div className={stock.changePercent > 0 ? 'text-green-400' : 'text-red-400'}>
                    {stock.changePercent > 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Market Regimes */}
        <Card title="Market Regime Detection" subtitle="Detected market states">
          <div className="space-y-4">
            {marketRegimes.map((regime, idx) => (
              <div key={idx} className="p-3 bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-semibold text-white">{regime.name}</p>
                  <Badge
                    label={regime.indicator}
                    variant={regime.indicator === 'Strong' ? 'success' : regime.indicator === 'Moderate' ? 'info' : 'danger'}
                    size="sm"
                  />
                </div>
                <Progress
                  value={regime.probability * 100}
                  max={100}
                  color="blue"
                />
                <p className="text-xs text-gray-400 mt-2">
                  {(regime.probability * 100).toFixed(1)}% Probability
                </p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* News & Alerts */}
      <Card title="Market News & Alerts" subtitle="Latest market developments">
        <div className="space-y-3">
          {newsAlerts.map((alert, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg border flex items-start gap-3 ${
                alert.sentiment === 'positive'
                  ? 'bg-green-500 bg-opacity-10 border-green-500'
                  : alert.sentiment === 'negative'
                  ? 'bg-red-500 bg-opacity-10 border-red-500'
                  : 'bg-yellow-500 bg-opacity-10 border-yellow-500'
              }`}
            >
              <div className="mt-1">
                {alert.sentiment === 'positive' && (
                  <TrendingUp size={20} className="text-green-400" />
                )}
                {alert.sentiment === 'negative' && (
                  <TrendingDown size={20} className="text-red-400" />
                )}
                {alert.sentiment === 'mixed' && (
                  <AlertTriangle size={20} className="text-yellow-400" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <p className="font-semibold text-white">{alert.title}</p>
                  <span className="text-xs text-gray-400">{alert.time}</span>
                </div>
                <div className="flex gap-2 mt-2">
                  <Badge label={alert.source} variant="default" size="sm" />
                  <Badge
                    label={`Impact: ${alert.impact}`}
                    variant={alert.impact === 'High' ? 'danger' : 'warning'}
                    size="sm"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Market Strategies */}
      <Card title="Recommended Strategies" subtitle="Based on current market regime">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-green-500 bg-opacity-10 rounded-lg border border-green-500">
            <h4 className="font-semibold text-green-400">Momentum Strategy</h4>
            <p className="text-xs text-gray-400 mt-2">Confidence: 85%</p>
            <Button variant="primary" className="w-full mt-3">
              Deploy
            </Button>
          </div>
          <div className="p-4 bg-blue-500 bg-opacity-10 rounded-lg border border-blue-500">
            <h4 className="font-semibold text-blue-400">Mean Reversion</h4>
            <p className="text-xs text-gray-400 mt-2">Confidence: 72%</p>
            <Button variant="primary" className="w-full mt-3">
              Deploy
            </Button>
          </div>
          <div className="p-4 bg-purple-500 bg-opacity-10 rounded-lg border border-purple-500">
            <h4 className="font-semibold text-purple-400">Hedging Strategy</h4>
            <p className="text-xs text-gray-400 mt-2">Confidence: 95%</p>
            <Button variant="primary" className="w-full mt-3">
              Deploy
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
